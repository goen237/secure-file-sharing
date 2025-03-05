import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env') # .env-Datei laden
if not os.path.exists(dotenv_path):
    print(f"❌ Die Datei {dotenv_path} wurde nicht gefunden!")
    exit(1)

load_dotenv(dotenv_path)

MASTER_KEY = os.getenv("SECRET_KEY") # Master Key aus .env-Datei laden

def generate_key() -> str:
    """
    Generiert einen neuen Fernet-Schlüssel und gibt ihn als String zurück.
    """
    return Fernet.generate_key().decode()


if not MASTER_KEY:
    print("❌ Kein Master Key gefunden! Neuer Schlüssel wird generiert... 🔑")
    MASTER_KEY = generate_key()
    with open(dotenv_path, "a") as env_file:
        env_file.write(f"\nSECRET_KEY={MASTER_KEY}")
    print("✅ Master Key wurde generiert: ", MASTER_KEY)


print(f"Geladener MASTER_KEY: {MASTER_KEY}")  # Debug-Ausgabe

try:
    master_cipher = Fernet(MASTER_KEY) # Master Key verschlüsseln
except ValueError:
    raise Exception("Ungültiger Master Key")


def encrypt_file(content: bytes):
    """
    Verschlüsselt den Inhalt einer Datei und gibt den verschlüsselten Inhalt und den verschlüsselten Schlüssel zurück.
    """
    file_key = generate_key()
    cipher = Fernet(file_key.encode())  # Konvertiere file_key zu Bytes
    encrypted_content = cipher.encrypt(content)
    # Datei-Schlüssel verschlüsseln
    encrypted_key = master_cipher.encrypt(file_key.encode())  # Konvertiere file_key zu Bytes
    return encrypted_content, encrypted_key


def decrypt_file(content: bytes, encrypted_key: bytes) -> bytes:
    """
    Entschlüsselt den Inhalt einer Datei mit dem verschlüsselten Schlüssel und gibt den entschlüsselten Inhalt zurück.
    """
    # Datei-Schlüssel entschlüsseln
    file_key = master_cipher.decrypt(encrypted_key)
    cipher = Fernet(file_key)
    return cipher.decrypt(content)