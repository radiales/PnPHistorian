# PnPHistorian RAG-App

Dieses Projekt stellt eine lokal gehostete RAG‑(Retrieval-Augmented‑Generation) App bereit. Es kombiniert Chroma (Vektordatenbank) und Ollama (Local LLM) in Docker‑Containern mit einem Python‑Ingestion- und Query‑Skript.

---

## Übersicht

1. **Chroma**: Vektordatenbank unter Port `8000` für Persistenz von Embeddings.
2. **Ollama**: LLM‑Server unter Port `11434` für Embedding und Chat.
3. **Python‑Skripte**:

   * `ingest_logs.py`: Liest `deine_logs.txt` Zeile für Zeile ein, erzeugt Embeddings via Ollama und speichert sie in Chroma.
   * `query_logs.py`: Nimmt eine natürliche Frage, holt Embedding, retrievt relevante Logs und generiert Antwort via LLM.

---

## Voraussetzungen

* **Windows 10/11** mit aktiviertem **WSL 2** (Ubuntu empfohlen)
* **Docker Desktop** mit WSL‑Integration
* **Python 3.8+** (systemweit oder in WSL)

Optional:

* Home‑Verwaltung: `pipx`, `pyenv`, o. Ä.

---

## 1. Projekt vorbereiten

```bash
# In WSL: Home‑Verzeichnis
cd ~

# 1.1: Repository klonen oder Projektkopie
# Beispiel mit Git:
git clone <DEIN_REPO_URL> PnPHistorian
cd PnPHistorian
```

Verzeichnisstruktur:

```
PnPHistorian/
├── docker-compose.yml
├── ingest_logs.py
├── query_logs.py
├── deine_logs.txt    # deine Log-Einträge (eine Zeile = ein Dokument)
└── README.md         # (diese Datei)
```

## 2. Docker-Services starten

Docker container hochfahren:

```bash
docker compose up -d
```

* **Chroma** läuft auf `localhost:8000`
* **Ollama** läuft auf `localhost:11434`

#### 2.1 Modelle ziehen

```bash
# Embedding-Modell
docker exec -it ollama ollama pull nomic-embed-text

# LLM-Modell
docker exec -it ollama ollama pull llama3

# Prüfen
docker exec -it ollama ollama list
```

---

## 3. Docker-Berechtigungen (optional)

Damit du Docker ohne `sudo` nutzt:

```bash
# In WSL
sudo usermod -aG docker $USER
# Terminal schließen und neu öffnen oder:
newgrp docker
```

Danach sollte `docker ps` ohne Fehler laufen.

---

## 4. Python‑Umgebung einrichten

1. **System‑Abhängigkeiten installieren** (falls fehlen):

   ```bash
   sudo apt update
   sudo apt install python3 python3-venv python3-pip
   ```

2. **Virtuelles Environment** anlegen:

   ```bash
   cd ~/PnPHistorian
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Pakete installieren**:

   ```bash
   pip install --upgrade pip
   pip install requests chromadb
   ```

---

## 5. Logs importieren

1. Lege deine Log-Zeilen in `deine_logs.txt` (eine Zeile = ein Eintrag).
2. Skript ausführen:

   ```bash
   python ingest_logs.py
   ```
3. Ausgabe sollte sein:

   ```
   ✅ Logs in Chroma importiert.
   ```

---

## 6. Natürliche Fragen stellen

```bash
# Direkte Frage
python query_logs.py "Wann wurde der letzte Eintrag erstellt?"

# Interaktiv
python query_logs.py
# Frage: Wer war beim letzten Abenteuer dabei?
```

Das Skript:

* erzeugt Query‑Embedding
* retrievt Top‑3 relevante Logs aus Chroma
* baut einen system+user-Prompt
* ruft Ollama Chat-API auf
* zeigt Antwort im Terminal

---

## 7. Troubleshooting

* **Fehler `permission denied`:** siehe Abschnitt 3 (Docker-Gruppe).
* **404 auf Chat-Endpoint:** sicherstellen, dass in `query_logs.py` `/v1/chat/completions` verwendet wird.
* **PEP 668 Fehler:** immer im `.venv` installieren, nicht systemweit.
* **OpenSSL-Warnung:** kann ignoriert werden, betrifft nur `LibreSSL` vs. `OpenSSL`.

---

## 8. Anpassungen

* **Weitere Modelle:** In `ENV OLLAMA_MODELS` in `docker-compose.yml` eintragen.
* **Andere Chunk-Strategien:** `load_chunks()` in `ingest_logs.py` anpassen (z. B. nach Timestamp, Größe).
* **Parameter Tuning:** `n_results` erhöhen, Model-Prompts ändern.

