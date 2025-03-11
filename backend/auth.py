from passlib.context import CryptContext # dient zur Hashing von Passwörtern
from jose import jwt # dient zur Erstellung von JSON Web Tokens
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256" # Algorithmus zur Erstellung des Tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 15 # Gültigkeitsdauer des Tokens (30 Minuten)
REFRESH_TOKEN_EXPIRE_DAYS = 1 # Gültigkeitsdauer des Refresh Tokens (30 Tage)

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
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str) -> dict:
    """
    Überprüft das übergebene Token und gibt die enthaltenen Daten zurück.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token abgelaufen")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Ungültiger Token")

def create_refresh_token(data: dict) -> str:
    """
    Erstellt ein Refresh Token mit den übergebenen Daten und gibt es als String zurück.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)