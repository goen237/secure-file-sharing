from passlib.context import CryptContext # dient zur Hashing von Passwörtern
from jose import jwt # dient zur Erstellung von JSON Web Tokens
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256" # Algorithmus zur Erstellung des Tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Gültigkeitsdauer des Tokens (30 Minuten)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hasht das übergebene Passwort und gibt es als String zurück.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Überprüft, ob das übergebene Passwort mit dem gehashten Passwort übereinstimmt.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """
    Erstellt ein JSON Web Token mit den übergebenen Daten und gibt es als String zurück.
    """
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
