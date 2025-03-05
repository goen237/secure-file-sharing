from fastapi import FastAPI, UploadFile, HTTPException, File, Depends
from pydantic import BaseModel # dient zur Validierung von Daten
from backend.encryption import encrypt_file, decrypt_file
from backend.auth import create_access_token, verify_password, hash_password, ALGORITHM, SECRET_KEY
from backend.db import save_file, get_file, users, files
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from io import BytesIO

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Ungültiger Token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token abgelaufen")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Ungültiger Token")

def find_media_type(filename: str):
    if filename.endswith(".pdf"):
        return "application/pdf"
    elif filename.endswith((".png", ".jpg", ".jpeg")):
        return "image/jpeg"
    else:
        return "text/plain"

class User(BaseModel):
    username: str
    password: str

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

@app.post("/register")
async def register(user: User):
    if users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Nutzer existiert bereits")

    # Passwort hashen
    hashed_password = hash_password(user.password)
    # Nutzer in MongoDB speichern
    users.insert_one({
        "username": user.username,
        "password": hashed_password
    })
    print(f"✅ Nutzer-{user.username} erfolgreich registriert")
    return {"message": "Nutzer erfolgreich registriert"}

@app.post("/login")
async def login(user: User):
    user_db = users.find_one({"username": user.username})
    if not user_db or not verify_password(user.password, user_db["password"]):
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

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