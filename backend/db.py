from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

try:
    client = MongoClient(MONGO_URL)
    db = client["secure_share"]
    print("✅ Verbindung zu MongoDB Atlas erfolgreich")
except Exception as e:
    print("❌ Verbindung fehlgeschlagen:", e)
