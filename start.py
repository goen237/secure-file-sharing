from cryptography.fernet import Fernet

# 1. Schlüssel generieren
key = Fernet.generate_key()
cipher = Fernet(key)

print("🔑 AES Schlüssel:", key.decode())

# 2. Klartext eingeben
text = input("Bitte einen Text eingeben: ")
#--------------------------------------------------------------
from fpdf import FPDF

# Erstelle eine Instanz der FPDF-Klasse
pdf = FPDF()

# Füge eine Seite hinzu
pdf.add_page()

# Setze die Schriftart
pdf.set_font("Arial", size=12)

# Füge einen Text hinzu
pdf.cell(200, 10, txt=text, ln=True, align='C')

# Speichere die Datei
pdf.output("beispiel.pdf")
#---------------------------------------------------------
text_bytes = text.encode()

# 3. Text verschlüsseln
encrypted = cipher.encrypt(text_bytes)
print("🔒 Verschlüsselter Text:", encrypted.decode())

# 4. Text entschlüsseln
decrypted = cipher.decrypt(encrypted)
print("🔓 Entschlüsselter Text:", decrypted.decode())

#venv\Scripts\activate     # Windows