# query_logs.py
import sys
import requests
from chromadb import HttpClient
from chromadb.config import Settings, DEFAULT_TENANT, DEFAULT_DATABASE

# Konfiguration
CHROMA_HOST = "localhost"
CHROMA_PORT = 8000
OLLAMA_URL  = "http://localhost:11434"
EMB_MODEL   = "nomic-embed-text"
LLM_MODEL   = "llama2:7b-chat-q4_0"
COLLECTION  = "logs"

# Chroma HTTP-Client
client = HttpClient(
    host=CHROMA_HOST,
    port=CHROMA_PORT,
    ssl=False,
    settings=Settings(),
    tenant=DEFAULT_TENANT,
    database=DEFAULT_DATABASE,
)
coll = client.get_collection(COLLECTION)

def embed(text: str):
    resp = requests.post(
        f"{OLLAMA_URL}/api/embed",
        json={"model": EMB_MODEL, "input": text}
    )
    resp.raise_for_status()
    # Extract and flatten the embeddings array
    return resp.json()["embeddings"][0]

def chat(system_msg: str, user_msg: str):
    resp = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user",   "content": user_msg}
            ]
        }
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

if __name__ == "__main__":
    # Frage aus CLI-Argumenten oder interaktiv
    prompt = " ".join(sys.argv[1:]) or input("Frage: ")

    # 1) Embedding der Frage
    q_emb = embed(prompt)

    # 2) Ähnlichste Log-Chunks abfragen
    results = coll.query(query_embeddings=[q_emb], n_results=3)
    docs = results["documents"][0]
    context = "\n---\n".join(docs)

    # 3) LLM-Prompt bauen und ausführen
    full_prompt = f"Verwende die folgenden Log-Einträge als Kontext:\n\n{context}\n\nBeantworte dann die Frage: {prompt}"
    answer = chat("Du bist ein hilfreicher Agent.", full_prompt)

    print("\n➡️ Antwort:\n", answer)
