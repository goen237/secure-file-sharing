from fastapi import FastAPI, UploadFile, HTTPException, File, Depends
from pydantic import BaseModel # dient zur Validierung von Daten
from backend.encryption import encrypt_file, decrypt_file
from backend.auth import create_access_token, verify_password, hash_password, verify_access_token, create_refresh_token
from backend.db import save_file, get_file, save_user, files, delete_file, get_user, all_users, users
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware # dient zur Konfiguration von CORS damit der Frontend-Client auf die API zugreifen kann
from fastapi.staticfiles import StaticFiles
from io import BytesIO


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Ungültiger Token")
    return username

def find_media_type(filename: str):
    if filename.endswith(".pdf"):
        return "application/pdf"
    elif filename.endswith((".png", ".jpg", ".jpeg")):
        return "image/jpeg"
    else:
        return "text/plain"

def is_admin(user: str):
    user_db = get_user(user)
    return user_db["role"] == "admin"

class User(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class updateRole(BaseModel):
    username: str
    new_role: str

@app.get("/")
def read_root():
    return {"message": "Secure File Sharing Plattform läuft!"}

@app.post("/upload/")
async def upload_file(file: UploadFile= File(...), username: str = Depends(get_current_user)):
    content = await file.read()
    encrypted_content, encrypt_key = encrypt_file(content)
    save_file(file.filename, encrypted_content, encrypt_key, username, file.content_type)
    return {"message": f"Datei von {username} erfolgreich hochgeladen"}

@app.get("/download/{filename}")
async def download_file(filename: str, username: str = Depends(get_current_user)):
    # datei aus MongoDB holendownloadfile
    file = get_file(filename, username)

    if not file:
        raise HTTPException(status_code=404, detail="Datei nicht gefunden")

    # datei entschlüsseln
    decrypted_content = decrypt_file(file["content"], file["key"])

    # return {
    #     "filename": filename,
    #     "decrypted_content": decrypted_content.decode()
    # }
    return StreamingResponse(
        BytesIO(decrypted_content),
        media_type = find_media_type(filename),
        # media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.post("/register/")
async def register(user: User):
    if get_user( user.username):
        raise HTTPException(status_code=400, detail="Nutzer existiert bereits")

    # Passwort hashen
    hashed_password = hash_password(user.password)
    # Nutzer in MongoDB speichern
    save_user(user.username, hashed_password)
    return {"message": "Nutzer erfolgreich registriert"}

@app.post("/login/")
async def login(user: User):
    user_db = get_user( user.username)
    if not user_db or not verify_password(user.password, user_db["password"]):
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    rolle = user_db["role"]
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "role": rolle}

@app.post("/refresh/")
async def refresh_token(refresh_token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(refresh_token)

    username: str = payload.get("sub")

    if username is None:
        raise HTTPException(status_code=401, detail="Ungültiger Token")

    new_access_token = create_access_token(data={"sub": username})
    return {"access_token": new_access_token, "token_type": "bearer"}

@app.get("/preview/{filename}")
async def preview_file(filename: str, username: str = Depends(get_current_user)):
    file = get_file(filename, username)

    if not file:
        raise HTTPException(status_code=404, detail="Datei nicht gefunden oder keine Berechtigung")

    # Datei entschlüsseln
    decrypted_content = decrypt_file(file["content"], file["key"])
    media = find_media_type(filename)
    return StreamingResponse(
        BytesIO(decrypted_content),
        media_type = media
    )

@app.get("/files/")
async def list_files(username: str = Depends(get_current_user)):
    if is_admin(username):
        user_files = files.find()
        return {
            "files": [{"filename": file["filename"], "owner": file["owner"]} for file in user_files]
        }

    else:
        user_files = files.find({"owner": username})
        return {
            "files": [file["filename"] for file in user_files]
        }

@app.delete("/delete/{filename}")
async def delete_file_by_user(filename: str, username: str = Depends(get_current_user)):
    result = get_file(filename, username)
    if not result:
        raise HTTPException(status_code=404, detail="Datei nicht gefunden oder keine Berechtigung")

    if result["owner"] != username:
        raise HTTPException(status_code=403, detail="Keine Berechtigung")

    delete_file(filename, username)
    return {"message": f"Datei-{filename} erfolgreich gelöscht"}

@app.delete("/delete/{username}/{filename}")
async def delete_file_by_admin(username: str, filename: str, current_user: str = Depends(get_current_user)):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")

    result = get_file(filename, username)
    if not result:
        raise HTTPException(status_code=404, detail="Datei nicht gefunden")

    delete_file(filename, username)
    return {"message": f"Datei-{filename} von {username} erfolgreich gelöscht"}

@app.put("/change-password/")
async def change_password(
    request: ChangePasswordRequest,
    user: str = Depends(get_current_user)
):
    user_db = get_user( user)
    if not user_db or not verify_password(request.current_password, user_db["password"]):
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")

    hashed_password = hash_password(request.new_password)
    users.update_one({"username": user}, {"$set": {"password": hashed_password}})
    return {"message": "Passwort erfolgreich geändert"}

@app.get("/users/",dependencies=[Depends(get_current_user)])
async def list_users(username: str = Depends(get_current_user)):
    if not is_admin(username):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    all_user = all_users()
    return {
        "users": [{"username": user["username"], "role": user["role"]} for user in all_user]
    }

@app.put("/users/{username}/role", dependencies=[Depends(get_current_user)])
async def change_user_role(request: updateRole, current_user: str = Depends(get_current_user)):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    user = users.find_one({"username": request.username})
    if not user:
        raise HTTPException(status_code=404, detail="Nutzer nicht gefunden")
    users.update_one({"username": request.username}, {"$set": {"role": request.new_role}})
    return {"message": f"Rolle von {request.username} erfolgreich geändert"}

@app.delete("/users/{username}", dependencies=[Depends(get_current_user)])
async def delete_user(username: str, current_user: str = Depends(get_current_user)):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    user = users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="Nutzer nicht gefunden")
    users.delete_one({"username": username})
    return {"message": f"Nutzer-{username} erfolgreich gelöscht"}


#     python -m venv venv
# source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

#         uvicorn backend.main:app --reload
