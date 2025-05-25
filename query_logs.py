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
    return data["choices"][0]["message"]["content"]

if __name__ == "__main__":
    # Frage einlesen
    prompt = " ".join(sys.argv[1:]) or input("Frage: ")

    # 1) Embedding der Frage holen
    q_emb = embed(prompt)

    # 2) Retrieval relevanter Dokumente
    results = coll.query(query_embeddings=[q_emb], n_results=3)
    docs = results["documents"][0]
    context = "\n---\n".join(docs)

    # 3) Prompt für Curse of Strahd DnD 5e mit Spieler-Info verfeinern
    system_prompt = (
        "Du bist ein erfahrener Dungeons & Dragons 5e Assistent für die Kampagne 'Curse of Strahd'. "
        "Nutze ausschließlich die bereitgestellten Log-Einträge als Wissensquelle. "
        "Die Spieler und ihre Charaktere sind: "
        "Kevin spielt Alril, Patrick spielt Dendros, Olli spielt Alwyn, Fabi spielt Wellys, "
        "Max spielt Daeran; Grumsh und Hansrik sind NSCs; Lexa spielt Moosnager, Gretel und Glim. "
        "Antworte stets auf Deutsch, es sei denn, die Frage ist in einer anderen Sprache gestellt."
    )
    user_prompt = (
        f"Verwende die folgenden Log-Einträge als Kontext für Curse of Strahd (D&D 5e):\n{context}\n\n"
        f"Frage: {prompt}"
    )

    # 4) Antwort generieren
    answer = chat(system_prompt, user_prompt)

    print("\n➡️ Antwort:\n", answer)
