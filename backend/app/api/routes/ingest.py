import re
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Document
from app.services.chunking import chunk_sections
from app.services.embeddings import EmbeddingService
from app.services.pdf_parser import extract_sections
from app.services.vector_store import VectorStoreService


router = APIRouter()
RAW_DOCUMENTS_DIR = Path(__file__).resolve().parents[4] / "data" / "raw_documents"


def _safe_filename(filename: str | None) -> str:
	name = Path(filename or "document.pdf").name
	name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
	return name or "document.pdf"


@router.post("/ingest")
async def ingest_document(
	file: UploadFile = File(...),
	project_id: str = Form(...),
	db: Session = Depends(get_db),
) -> dict:
	if not project_id.strip():
		raise HTTPException(status_code=400, detail="project_id must not be empty")
	if file.content_type not in {"application/pdf", "application/octet-stream"}:
		raise HTTPException(status_code=400, detail="Only PDF uploads are supported")

	RAW_DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
	destination = RAW_DOCUMENTS_DIR / _safe_filename(file.filename)
	try:
		destination.write_bytes(await file.read())
		sections = extract_sections(str(destination))
		chunks = chunk_sections(sections)
		embeddings = EmbeddingService().embed_texts([chunk["text"] for chunk in chunks])
		VectorStoreService().add_chunks(project_id, chunks, embeddings)

		db.add(
			Document(
				filename=destination.name,
				project_id=project_id,
				status="ingested",
			)
		)
		db.commit()
		return {"status": "ingested", "num_chunks": len(chunks)}
	except Exception as exc:
		db.rollback()
		raise HTTPException(status_code=500, detail=f"Document ingestion failed: {exc}") from exc
