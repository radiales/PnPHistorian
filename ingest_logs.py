# ingest_logs.py (file-wise ingestion)
import os
import requests
import chromadb
from chromadb.config import Settings, DEFAULT_TENANT, DEFAULT_DATABASE

# Konfiguration
CHROMA_HOST = "localhost"
CHROMA_PORT = 8000
OLLAMA_URL  = "http://localhost:11434"
EMB_MODEL   = "nomic-embed-text"
COLLECTION  = "logs"
LOGS_DIR    = "logs"  # Ordner mit deinen Log-Dateien (.txt)

# HTTP-Client für Chroma
client = chromadb.HttpClient(
    host=CHROMA_HOST,
    port=CHROMA_PORT,
    ssl=False,
    settings=Settings(),
    tenant=DEFAULT_TENANT,
    database=DEFAULT_DATABASE,
)
coll = client.get_or_create_collection(COLLECTION)


def load_documents(directory: str):
    """
    Liest alle .txt-Dateien in einem Verzeichnis ein und gibt Paare (filename, content).
    """
    for fname in os.listdir(directory):
        if not fname.lower().endswith(".txt"):
            continue
        path = os.path.join(directory, fname)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().strip()
            if text:
                yield fname, text


if __name__ == "__main__":
    # Stelle sicher, dass der Logs-Ordner existiert
    if not os.path.isdir(LOGS_DIR):
        raise FileNotFoundError(f"Logs-Verzeichnis '{LOGS_DIR}' nicht gefunden.")

    # Einlesen und Importieren der Logs fileweise
    for fname, content in load_documents(LOGS_DIR):
        # Embedding via Ollama-REST
        resp = requests.post(
            f"{OLLAMA_URL}/api/embed",
            json={"model": EMB_MODEL, "input": content}
        )
        resp.raise_for_status()
        emb = resp.json().get("embeddings")
        # In Einzelfällen als Liste in Liste
        if isinstance(emb, list) and emb and isinstance(emb[0], list):
            emb = emb[0]

        # Hinzufügen zu Chroma
        coll.add(
            ids=[fname],
            embeddings=[emb],
            documents=[content]
        )

    print("✅ Alle Dateien in Chroma importiert.")
