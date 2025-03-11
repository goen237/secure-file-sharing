# Basis-Image für die Anwendung (Python + FastAPI)
FROM python:3.11

# Arbeitsverzeichnis für die Anwendung
WORKDIR /app

# Code in das Arbeitsverzeichnis kopieren
COPY . /app

# Abhängigkeiten installieren
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Port 8000 freigeben und server starten
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]