# AUTOSAR HLD Insight

AI-powered document intelligence for AUTOSAR high-level design documents. Upload a PDF, ask grounded questions, extract architecture entities, and identify conflicting definitions with page-aware citations.

## Capabilities

- PDF section extraction with heading and page metadata
- Overlapping, section-aware text chunking
- Sentence-transformer embeddings with ChromaDB persistence
- Groq-powered grounded question answering
- Component and interface extraction
- Inconsistency detection with source citations
- FastAPI backend and Streamlit dashboard
- SQLite document and query audit logging

## Architecture

```text
Streamlit UI
	|
	v
FastAPI routes
	|
	+--> PDF parser --> chunker --> embeddings --> ChromaDB
	|
	+--> RAG pipeline --> Groq LLM
	|
	+--> SQLite audit log
```

## Requirements

- Python 3.11 or newer
- A Groq API key
- Internet access on first run to download `all-MiniLM-L6-v2`

## Setup

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

Create `backend/.env` locally. Never commit this file or share the key:

```env
GROQ_API_KEY=your_groq_key
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
CHROMA_PERSIST_DIR=../data/vector_store
SQLITE_DB_PATH=../data/app.db
CHUNK_MAX_TOKENS=500
```

## Run The Application

Start the API from the repository root:

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000` and Swagger UI at `http://localhost:8000/docs`.

In a second terminal, start the dashboard:

```powershell
..\.venv\Scripts\python.exe -m streamlit run frontend\streamlit_app.py --server.port 8502
```

Open `http://localhost:8502` and follow the workflow: set a Project ID, upload a PDF, ask questions, extract entities, and run the inconsistency check.

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/ingest` | Upload and index a PDF for a project |
| `POST` | `/query` | Ask a grounded question |
| `GET` | `/extract-entities/{project_id}` | Extract components and interfaces |
| `GET` | `/inconsistencies/{project_id}` | Find conflicting definitions |

## Verification

Run the ordered backend verification from `backend`:

```powershell
cd backend
..\.venv\Scripts\python.exe verify_stages_1_10.py
```

The check validates configuration, parsing, chunking, embeddings, vector search, Groq responses, RAG, SQLite, FastAPI routes, and entity extraction in order. It stops at the first real failure and prints a summary.

Frontend syntax can be checked with:

```powershell
..\.venv\Scripts\python.exe -m compileall -q frontend
```

## Project Layout

```text
backend/app/       FastAPI application, services, database, and schemas
frontend/          Streamlit dashboard and reusable API/style helpers
data/raw_documents Uploaded PDFs and the small parser test fixture
data/vector_store  Local ChromaDB persistence, ignored by Git
tests/             Unit-test location
docs/              Architecture and project report documents
```

## Security Notes

- Store secrets only in `backend/.env` or the deployment platform's secret manager.
- `backend/.env.example` contains placeholders only.
- Do not commit uploaded customer documents, SQLite databases, Chroma data, or Python environments.
- Rotate any API key that has been exposed in chat, logs, screenshots, or source control.
