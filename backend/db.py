import os
from pymongo import MongoClient
from dotenv import load_dotenv

# .env-Datei laden
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

try:
    client = MongoClient(MONGO_URL)
    db = client["secure_share"]
    files = db["files"]
    users = db["users"]
    files.create_index("owner") # Index für die Spalte "owner" erstellen(schnellere Benutzerabfrage)
    print("✅ Verbindung zu MongoDB Atlas erfolgreich")
except Exception as e:
    print("❌ Verbindung fehlgeschlagen:", e)

def save_file(filename, content, key,username, file_type):
    files.insert_one({
        "filename": filename,
        "content": content,
        "key": key,
        "owner": username,
        "type": file_type
    })
    print(f"✅ Datei-{filename} erfolgreich gespeichert")

def get_file(filename: str, username: str):
    file = files.find_one(
        {
            "filename": filename,
            "owner": username
        }
    )
    return file