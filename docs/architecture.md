# AUTOSAR HLD Insight Architecture

## Purpose

AUTOSAR HLD Insight turns a text-based PDF high-level design document into a project-scoped retrieval workspace. Users upload a document, ask questions against its indexed content, extract named architecture entities, and review likely inconsistencies with page-aware source metadata.

## System Overview

```text
Streamlit dashboard
        |
        v
FastAPI API
  |       |        |
  v       v        v
Ingest  Query   Extraction
  |       |        |
  v       v        v
PDF parser -> chunks -> sentence embeddings -> ChromaDB
                              |
                              v
                         top-k retrieval
                              |
                              v
                         Groq LLM

FastAPI also writes document and query audit records to SQLite.
```

## Runtime Components

### Frontend

`frontend/streamlit_app.py` provides the dashboard navigation and shared project selection. The pages support document upload, grounded questions, entity extraction, and inconsistency review. `frontend/api_client.py` communicates with the local FastAPI service at `http://localhost:8000` and applies a 120-second request timeout for model-backed operations.

### API layer

The FastAPI application in `backend/app/main.py` registers three route modules:

- `POST /ingest` accepts a PDF and a `project_id` as multipart form data.
- `POST /query` accepts a `project_id` and question, then returns an answer and sources.
- `GET /extract-entities/{project_id}` returns merged component and interface entities.
- `GET /inconsistencies/{project_id}` returns likely conflicts found in repeated descriptions.

The ingest route sanitizes the uploaded filename, stores the PDF under `data/raw_documents`, and rolls back the database session when processing fails.

### Document processing

`pdf_parser.py` uses PyMuPDF to read text blocks, estimates the body font size, and treats bold or larger text as section headings. Documents without detectable headings fall back to one section per page. Each section carries its heading, text, start page, and end page.

`chunking.py` splits section text into whitespace-based windows of up to the configured `CHUNK_MAX_TOKENS` value. Windows overlap by 10 percent, preserving nearby context across retrieval boundaries while retaining the section and page metadata.

### Retrieval and generation

`EmbeddingService` uses the configured Sentence Transformers model, cached per model name, to create document and query vectors. `VectorStoreService` stores chunks in persistent ChromaDB collections. The collection name is derived from a SHA-256 hash of the project ID, isolating retrieval between projects without exposing the raw ID in the collection name.

The RAG pipeline embeds a question, retrieves the five nearest chunks, and sends their text, headings, and page ranges to `LLMClient`. The Groq prompt requires answers to use only the supplied context and cite each claim in a section/page format. When evidence is insufficient, the prompt instructs the model to say that the answer cannot be found in the document.

### Entity and inconsistency analysis

Entity extraction processes stored chunks in batches of four. The LLM returns structured JSON containing component names, interfaces, and descriptions; results are merged case-insensitively by component name.

Inconsistency analysis first extracts repeated mentions with source chunk IDs. Only entities with provenance and differing descriptions become candidates for a second LLM comparison. The final issues include the entity name, explanation, and source locations. This is a likely-conflict detector, not a formal requirements or semantic proof system.

### Persistence

SQLite stores `Document` records for ingested files and `QueryLog` records containing questions, generated answers, and serialized source citations. ChromaDB stores the searchable chunk text, embeddings, and retrieval metadata. The local vector store, SQLite database, environments, and secrets are excluded from version control; the parser fixture is explicitly retained.

## Configuration and Data Flow

Settings are loaded from `backend/.env` through Pydantic Settings. The important values are the Groq API key, embedding model name, Chroma persistence path, SQLite path, and chunk size. Relative paths are resolved from the repository layout when the backend starts.

A normal request flow is:

1. The user selects a project and uploads a PDF.
2. FastAPI saves the file and extracts sections with page metadata.
3. Sections become overlapping chunks and vector embeddings.
4. Chunks and metadata are written to the project's Chroma collection.
5. A query is embedded and matched against that collection.
6. The top five chunks are supplied to Groq for a constrained answer.
7. The answer and its sources are returned to Streamlit and logged in SQLite.

## Operational Boundaries

The current implementation expects text-based PDFs. Scanned documents require OCR before parsing. First use downloads the embedding model and requires network access; questions, extraction, and inconsistency checks require a valid Groq API key. The local configuration is suitable for development and verification, but production deployment would need authentication, durable managed storage, upload limits, background processing, and stronger observability.
