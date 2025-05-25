import chromadb
from chromadb.config import Settings, DEFAULT_TENANT, DEFAULT_DATABASE
import requests

# Konfiguration
CHROMA_HOST = "localhost"
CHROMA_PORT = 8000
OLLAMA_URL  = "http://localhost:11434"
EMB_MODEL   = "nomic-embed-text"
COLLECTION  = "logs"

# HTTP-Client für Chroma
client = chromadb.HttpClient(
    host=CHROMA_HOST,
    port=CHROMA_PORT,
    ssl=False,
    settings=Settings(),
    tenant=DEFAULT_TENANT,
    database=DEFAULT_DATABASE,
)

# Collection erstellen oder abrufen
coll = client.get_or_create_collection(COLLECTION)

def load_chunks(path: str):
    """
    Liest eine Textdatei zeilenweise ein und liefert Paare (id, text).
    """
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            text = line.strip()
            if text:
                yield str(i), text

if __name__ == "__main__":
    # Einlesen und Importieren der Logs
    for _id, text in load_chunks("testlog.txt"):
        # Embedding via Ollama-REST
        resp = requests.post(
            f"{OLLAMA_URL}/api/embed",
            json={"model": EMB_MODEL, "input": text}
        )
        resp.raise_for_status()
        # Extract and flatten the embeddings array
        emb = resp.json().get("embeddings")[0]  # Get first (and only) embedding

        # Hinzufügen zu Chroma
        coll.add(
            ids=[_id],
            embeddings=[emb],  # Should now be a flat list of numbers
            documents=[text]
        )

    print("✅ Logs in Chroma importiert.")
