# AUTOSAR HLD Insight Project Report

## 1. Executive Summary

AUTOSAR HLD Insight is a document intelligence assistant for high-level design reviews. It combines structural PDF extraction, semantic retrieval, a constrained large-language-model response step, and source metadata so an engineer can ask questions about an architecture document without losing the link back to the relevant section and pages.

The delivered application includes a FastAPI backend, a Streamlit dashboard, persistent ChromaDB retrieval storage, SQLite audit records, entity extraction, and an inconsistency review workflow.

## 2. Problem and Goals

High-level design documents are often long, inconsistently structured, and difficult to search during review. The project addresses four practical tasks:

- Make PDF content searchable by meaning rather than exact words.
- Answer architecture questions using retrieved document evidence.
- Identify named components and interfaces for review.
- Surface repeated descriptions that may conflict, with source locations.

The design goal is traceable assistance: generated answers should expose the section and page range used as evidence, and the system should decline to invent information when retrieval does not provide enough context.

## 3. Delivered Functionality

### Ingestion

A user selects a project ID and uploads a PDF from the Streamlit dashboard. The API validates the project ID and content type, sanitizes the filename, extracts sections, creates overlapping chunks, generates embeddings, stores the chunks in a project-isolated Chroma collection, and records an ingested document in SQLite.

### Grounded questions

A question is embedded with the same sentence-transformer model used for ingestion. ChromaDB returns the five closest chunks. The Groq client receives only those chunks and a system prompt requiring section/page citations and an explicit insufficient-evidence response. The question, answer, and returned sources are recorded in SQLite.

### Entity extraction

Stored chunks are sent to the LLM in batches. Structured JSON responses are parsed defensively and merged case-insensitively, producing component names, interface lists, and descriptions for the selected project.

### Inconsistency review

The service extracts repeated component or interface mentions with chunk provenance, filters for differing descriptions, and asks the LLM to explain only those candidate mismatches. Results include source chunk IDs, headings, and page ranges where available.

## 4. Technical Design

The backend follows a small layered structure:

- API routes handle HTTP validation, dependencies, and response shaping.
- Services own parsing, chunking, embeddings, retrieval, generation, and analysis.
- SQLAlchemy models define document and query audit tables.
- Pydantic settings load environment configuration.
- ChromaDB stores semantic search data independently per project.

The frontend is intentionally lightweight. Streamlit pages call the backend through a shared requests client, keep the active project and chat history in session state, and display source metadata alongside answers.

## 5. Verification Approach

`backend/verify_stages_1_10.py` runs the implemented path in order:

1. Configuration values are available.
2. The PDF parser returns section and page metadata.
3. Chunking respects the configured size and preserves metadata.
4. Embeddings have consistent dimensions and semantic similarity behavior.
5. ChromaDB accepts and retrieves indexed chunks.
6. The Groq client returns a cited answer.
7. The RAG pipeline returns an answer and sources.
8. SQLAlchemy can create and query the audit models.
9. The FastAPI ingest and query routes work end to end.
10. Entity extraction returns the expected structured fields.

The verification uses `data/raw_documents/test_file.pdf`. The repository ignore rules therefore preserve that fixture while still excluding arbitrary uploaded PDFs and generated vector data. Frontend Python syntax can be checked independently with `compileall`.

## 6. Security and Data Handling

Secrets are loaded from `backend/.env` and are excluded from Git. Uploaded customer documents, SQLite data, Chroma persistence, and Python environments are also excluded by the repository rules. The upload filename is reduced to a safe basename before it is written to disk, and project IDs determine separate vector collections.

The current development implementation does not provide user authentication or authorization. A production deployment must add identity and project-level access controls, validate file size and PDF content more strictly, protect the API from unrestricted access, and use managed secret and storage services.

## 7. Known Limitations

- Text extraction is based on PDF text layout and does not perform OCR for scanned PDFs.
- Heading detection uses font size and boldness heuristics, so unusual document formatting may affect section boundaries.
- Chunking is whitespace-based rather than tokenizer-based despite the token-oriented setting name.
- Answer quality depends on the embedding model, retrieved context, and Groq availability.
- Entity and inconsistency outputs are model-generated and should be reviewed by an engineer.
- The local SQLite and ChromaDB setup is intended for a single development environment, not concurrent production scale.
- The verification script exercises real model and API integrations, so credentials, network access, and the fixture are required for a complete run.

## 8. Recommended Next Steps

1. Add unit tests for parser edge cases, chunk boundaries, malformed model JSON, and project isolation.
2. Add OCR support and document validation for scanned or malformed PDFs.
3. Move long ingestion and analysis operations to background jobs with progress reporting.
4. Add authentication, authorization, rate limits, upload limits, and structured logging.
5. Introduce evaluation documents and citation/groundedness metrics for retrieval and answer quality.
6. Replace local persistence with managed storage and add backup and retention policies for deployment.

## 9. Conclusion

The project delivers a coherent development-ready workflow for exploring AUTOSAR HLD documents. Its main architectural strength is the explicit evidence path from PDF section to chunk, embedding, retrieved context, generated answer, and page-aware source record. The next phase should focus on production controls and measured quality evaluation rather than expanding the user workflow before those foundations are in place.
