# query_logs.py
import sys
import requests
import chromadb
from chromadb.config import Settings, DEFAULT_TENANT, DEFAULT_DATABASE

# Konfiguration
CHROMA_HOST = "localhost"
CHROMA_PORT = 8000
OLLAMA_URL  = "http://localhost:11434"
EMB_MODEL   = "nomic-embed-text"
LLM_MODEL   = "llama3"
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
coll = client.get_collection(COLLECTION)

def embed(text: str):
    """Holt das Embedding und gibt garantiert eine 1-D-Liste zurück."""
    resp = requests.post(
        f"{OLLAMA_URL}/api/embed",
        json={"model": EMB_MODEL, "input": text}
    )
    resp.raise_for_status()
    emb = resp.json().get("embeddings")
    if isinstance(emb, list) and emb and isinstance(emb[0], list):
        return emb[0]
    return emb

def chat(system_msg: str, user_msg: str):
    """Sendet den Chat-Request an den richtigen Endpoint."""
    resp = requests.post(
        f"{OLLAMA_URL}/v1/chat/completions",
        json={
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user",   "content": user_msg}
            ]
        }
    )
    resp.raise_for_status()
    data = resp.json()
    # OpenAI-kompatible Antwortstruktur
    return data["choices"][0]["message"]["content"]

if __name__ == "__main__":
    # Frage einlesen
    prompt = " ".join(sys.argv[1:]) or input("Frage: ")

    # Embedding erzeugen
    q_emb = embed(prompt)

    # Retrieval
    results = coll.query(query_embeddings=[q_emb], n_results=3)
    docs = results["documents"][0]
    context = "\n---\n".join(docs)

    # Antwort generieren
    full_prompt = (
        f"Verwende die folgenden Log-Einträge als Kontext:\n\n{context}"
        f"\n\nBeantworte dann die Frage: {prompt}"
    )
    answer = chat("Du bist ein hilfreicher Agent.", full_prompt)

    print("\n➡️ Antwort:\n", answer)
