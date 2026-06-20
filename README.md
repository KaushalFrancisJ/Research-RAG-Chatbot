# RAG Chatbot (Vanilla)

A Retrieval-Augmented Generation (RAG) chatbot that lets you upload PDF documents and ask questions against them. The backend exposes a REST API via FastAPI, and the frontend is a Streamlit web app.

---

## Table of Contents

- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Starting the Servers](#starting-the-servers)
- [Deploying the Frontend to Streamlit Cloud](#deploying-the-frontend-to-streamlit-cloud)
- [API Endpoints](#api-endpoints)
- [Environment Variables](#environment-variables)
- [How It Works](#how-it-works)
- [Supported PDFs](#supported-pdfs)

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Streamlit Frontend              │
│              (frontend/app.py :8501)             │
└──────────────────────┬──────────────────────────┘
                       │ HTTP (REST) + X-Session-Id header
                       ▼
┌─────────────────────────────────────────────────┐
│               FastAPI Backend                    │
│               (api/app.py :8000)                 │
│                                                  │
│  POST /api/upload   → chunk & index PDF          │
│  POST /api/generate → retrieve + generate answer │
│  POST /api/evaluate → score faithfulness &       │
│                        answer relevancy          │
└──────┬──────────────────────┬───────────────────┘
       │                      │
       ▼                      ▼
┌────────────┐      ┌──────────────────────┐
│  FAISS     │      │  LLM                 │
│ Vector     │      │  local:  Ollama      │
│ Store      │      │  cloud:  Groq API    │
│ (per       │      │                      │
│ session)   │      │  Eval:   Groq API    │
└────────────┘      └──────────────────────┘
```

**Flow:**
1. A PDF is uploaded → read into memory → parsed → split into overlapping text chunks.
2. Each chunk is embedded with `sentence-transformers` and stored in a FAISS index scoped to the current browser session.
3. On a query, the top-k nearest chunks are retrieved and passed as context to the LLM.
4. The LLM generates a grounded answer. The evaluate endpoint runs fixed diagnostic questions and scores each answer with a Groq-powered LLM judge.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | [Streamlit](https://streamlit.io/) |
| Backend API | [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) |
| Embeddings | [sentence-transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2` by default) |
| Vector Store | [FAISS](https://github.com/facebookresearch/faiss) (CPU, in-memory per session) |
| PDF Parsing | [pypdf](https://pypdf.readthedocs.io/) |
| LLM (local) | [Ollama](https://ollama.com/) (`mistral:7b-instruct-q4_0` by default) |
| LLM (cloud) | [Groq API](https://groq.com/) (`llama-3.1-8b-instant` for generation) |
| Evaluation | Groq API (`llama-3.3-70b-versatile` as LLM judge) |
| Config | python-dotenv + Streamlit Secrets |

---

## Project Structure

```
Chatbot Vanilla/
├── api/                    # FastAPI application
│   ├── app.py              # App factory, lifespan, router registration
│   ├── state.py            # Session-scoped RAGPipeline store
│   └── routes/
│       ├── upload.py       # POST /api/upload
│       ├── generate.py     # POST /api/generate
│       └── evaluate.py     # POST /api/evaluate
├── frontend/
│   └── app.py              # Streamlit UI
├── src/                    # Core RAG logic
│   ├── pdf_processor.py    # PDF → text (accepts path, bytes, or BytesIO)
│   ├── text_chunker.py     # Recursive split with overlap
│   ├── embedding.py        # sentence-transformers wrapper
│   ├── vector_store.py     # FAISS index wrapper
│   ├── rag_pipeline.py     # Orchestrates embed + search
│   ├── generator.py        # Ollama / Groq generation
│   └── evaluator.py        # Groq LLM-as-judge evaluation
├── .streamlit/
│   └── secrets.toml        # Local Streamlit secrets (gitignored)
├── pdfContext/             # Drop PDFs here for batch CLI processing
├── main.py                 # Batch CLI: process all PDFs in pdfContext/
├── config.py               # Centralised config via .env
├── requirements.txt
└── .env.example
```

---

## Prerequisites

- Python 3.9+
- [Ollama](https://ollama.com/) installed and running locally (for `ENV=local`)
  - Pull the model: `ollama pull mistral:7b-instruct-q4_0`
- A [Groq API key](https://console.groq.com) (required for evaluation, and for `ENV=production`)

---

## Setup

**1. Clone and enter the project directory.**

**2. Create and activate a virtual environment:**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables:**
```bash
copy .env.example .env
```
Then edit `.env` and fill in your values (see [Environment Variables](#environment-variables)).

**5. Configure the frontend API base URL:**

Edit `.streamlit/secrets.toml`:
```toml
API_BASE = "http://localhost:8000/api"
```

---

## Starting the Servers

You need two terminals — one for the backend, one for the frontend.

### Backend (FastAPI)

> **Note:** Do not use `--reload` on Windows. It causes the numpy/faiss Fortran runtime to crash on file-change signals. Restart the server manually when you make code changes.

```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive API docs: `http://localhost:8000/docs`

### Frontend (Streamlit)

```bash
streamlit run frontend/app.py
```

The UI will open automatically at `http://localhost:8501`.

---

### (Optional) Batch-process PDFs via CLI

Drop PDFs into `pdfContext/` and run:

```bash
python main.py
```

This processes all PDFs, builds a FAISS index, and runs a test query.

---

## Deploying the Frontend to Streamlit Cloud

Streamlit Cloud hosts the frontend only. The FastAPI backend must be deployed separately (e.g. Railway, Render, Fly.io) and its URL configured as a secret.

**Steps:**
1. Push your repo — `.streamlit/secrets.toml` and `.env` are gitignored and won't be included.
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo.
3. In the app dashboard go to **Settings → Secrets** and add:
   ```toml
   API_BASE = "https://your-deployed-backend-url.com/api"
   ```
4. Set the main file path to `frontend/app.py`.

---

## API Endpoints

All endpoints require an `X-Session-Id` header (UUID string). The frontend generates and manages this automatically per browser session.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/upload` | Upload a PDF into memory, chunk it, build the session's vector index |
| `POST` | `/api/generate` | Ask a question; returns answer + retrieved chunks |
| `POST` | `/api/evaluate` | Run fixed diagnostic questions and score answers with an LLM judge |

### POST `/api/upload`
- **Headers:** `X-Session-Id: <uuid>`
- **Body:** `multipart/form-data` with a `file` field (PDF only)
- **Response:** `{ "filename": "...", "chunks": <int> }`

### POST `/api/generate`
- **Headers:** `X-Session-Id: <uuid>`
```json
{ "query": "What is memory caching?", "k": 5 }
```
Response includes `answer`, `query`, and the retrieved `chunks` with source/page metadata.

### POST `/api/evaluate`
- **Headers:** `X-Session-Id: <uuid>`
- No request body required.

Runs 5 built-in diagnostic questions against the indexed document and returns per-question scores:
- `faithfulness` (1–5): is the answer grounded in the retrieved context?
- `answer_relevancy` (1–5): does the answer address the question?

---

## Environment Variables

### Backend (`.env`)

| Variable | Default | Description |
|---|---|---|
| `ENV` | `local` | `local` uses Ollama; `production` uses Groq for generation |
| `CHUNK_SIZE` | `1000` | Max characters per text chunk |
| `OVERLAP` | `200` | Overlap between consecutive chunks |
| `PDF_DIR` | `.\pdfContext` | Directory scanned by `main.py` for batch processing |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | sentence-transformers model name |
| `GENERATION_MODEL` | `mistral:7b-instruct-q4_0` | Ollama model used when `ENV=local` |
| `GROQ_GENERATION_MODEL` | `llama-3.1-8b-instant` | Groq model used when `ENV=production` |
| `EVALUATION_MODEL` | `llama-3.3-70b-versatile` | Groq model used for LLM-as-judge evaluation |
| `GROQ_API_KEY` | *(required)* | Your Groq API key from [console.groq.com](https://console.groq.com) |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server URL |

### Frontend (`.streamlit/secrets.toml`)

| Variable | Default | Description |
|---|---|---|
| `API_BASE` | `http://localhost:8000/api` | Base URL of the FastAPI backend |

---

## How It Works

1. **Upload** — The PDF is read into memory (no disk writes), parsed page-by-page with `pypdf`, then split using a recursive text splitter that respects natural boundaries (paragraphs → sentences → words → characters) with configurable overlap.

2. **Session isolation** — Each browser session gets its own `RAGPipeline` instance identified by a UUID sent as `X-Session-Id` on every request. Uploading a new PDF replaces only that session's index. All session data is freed when the server shuts down.

3. **Embed** — Each chunk is encoded into a dense vector using `sentence-transformers`. All vectors are loaded into a FAISS flat L2 index held in memory.

4. **Retrieve** — On a query, the question is embedded the same way and FAISS returns the top-k most similar chunks by L2 distance.

5. **Generate** — The retrieved chunks are concatenated as context and passed with the question to the LLM. In `local` mode this calls Ollama; in `production` mode it calls Groq (`llama-3.1-8b-instant`).

6. **Evaluate** — Five fixed diagnostic questions are run through the full retrieve → generate pipeline. A separate Groq call (`llama-3.3-70b-versatile`) acts as an LLM judge, scoring each answer on **Faithfulness** and **Answer Relevancy** (1–5). Results are displayed as a table in the UI — no CSV download.

---

## Supported PDFs

The parser is built on `pypdf` and works with most standard PDFs. Here's a quick reference:

| PDF Type | Supported | Notes |
|---|---|---|
| Digitally created (Word export, LaTeX, etc.) | ✅ Yes | Best results; clean text extraction |
| Native PDF (Adobe Acrobat, etc.) | ✅ Yes | Works well |
| Multi-column layouts | ⚠️ Partial | Text may be extracted out of reading order |
| PDFs with embedded tables | ⚠️ Partial | Table content extracted as plain text, no structure preserved |
| Password-protected PDFs | ❌ No | Raises an error unless decrypted first |
| Scanned / image-only PDFs | ❌ No | No text layer; returns empty chunks (OCR not included) |

**Scanned PDFs:** To support scanned documents, add OCR using `pdf2image` + `pytesseract` as a pre-processing step in `src/pdf_processor.py`.
