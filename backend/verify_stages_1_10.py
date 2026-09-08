import json
import math
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings
from app.db.database import Base
from app.db.models import Document, QueryLog
from app.main import app
from app.services.chunking import chunk_sections
from app.services.embeddings import EmbeddingService
from app.services.entity_extraction import extract_entities
from app.services.llm_client import LLMClient
from app.services.pdf_parser import extract_sections
from app.services.rag_pipeline import answer_question
from app.services.vector_store import VectorStoreService

PDF_PATH = Path(__file__).resolve().parents[1] / "data" / "raw_documents" / "test_file.pdf"
PROJECT_ID = "full-e2e-verification"
results = []


def stage(number: int, check):
    try:
        check()
    except Exception as exc:
        results.append((number, "FAIL", str(exc)))
        print(f"STAGE {number}: FAIL - {exc}")
        raise
    else:
        results.append((number, "PASS", ""))
        print(f"STAGE {number}: PASS")


sections = []
chunks = []
embeddings = []
store = None


def check_stage_1():
    configured = Settings()
    assert configured.groq_api_key.strip(), "GROQ_API_KEY is missing or empty"
    assert configured.embedding_model_name
    assert configured.chunk_max_tokens is not None


def check_stage_2():
    global sections
    sections = extract_sections(str(PDF_PATH))
    assert sections, "extract_sections returned no sections"
    required = {"heading", "text", "page_start", "page_end"}
    assert all(required <= section.keys() for section in sections)


def check_stage_3():
    global chunks
    chunks = chunk_sections(sections)
    limit = Settings().chunk_max_tokens * 1.1
    assert chunks, "chunk_sections returned no chunks"
    assert all(len(chunk["text"].split()) <= limit for chunk in chunks)
    assert all({"heading", "page_start", "page_end"} <= chunk.keys() for chunk in chunks)


def cosine(left, right):
    numerator = sum(a * b for a, b in zip(left, right))
    denominator = math.sqrt(sum(a * a for a in left)) * math.sqrt(sum(b * b for b in right))
    return numerator / denominator


def check_stage_4():
    global embeddings
    service = EmbeddingService()
    embeddings = service.embed_texts([
        "The engine communicates with the vehicle interface.",
        "The engine communicates with the automotive interface.",
        "The document describes unrelated weather observations.",
    ])
    assert len(embeddings) == 3
    assert len({len(vector) for vector in embeddings}) == 1
    assert cosine(embeddings[0], embeddings[1]) > cosine(embeddings[0], embeddings[2])


def check_stage_5():
    global store
    store = VectorStoreService()
    store.add_chunks(PROJECT_ID, chunks, embeddings[: len(chunks)])
    query_embedding = EmbeddingService().embed_query("What interfaces does the engine use?")
    result = store.query(PROJECT_ID, query_embedding, top_k=5)
    documents = result["documents"][0]
    assert documents, "vector store returned no documents"
    assert any("interface" in document.lower() or "system" in document.lower() for document in documents)


def check_stage_6():
    context = chunks[0]
    answer = LLMClient().generate_answer("What is this section about?", [context])
    assert answer.strip(), "LLM returned an empty answer"
    assert context["heading"].lower() in answer.lower() or f"p.{context['page_start']}" in answer.lower()


def check_stage_7():
    result = answer_question(PROJECT_ID, "What interfaces are described?")
    assert result["answer"].strip()
    assert result["sources"]
    known = {metadata["chunk_id"] for metadata in store.create_or_get_collection(PROJECT_ID).get(include=["metadatas"])["metadatas"]}
    assert all(source["heading"] for source in result["sources"])
    assert known


def check_stage_8():
    with TemporaryDirectory() as directory:
        engine = create_engine(f"sqlite:///{Path(directory) / 'test.db'}")
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        document = Document(filename="test.pdf", project_id="db-project", status="ingested")
        query = QueryLog(project_id="db-project", question="Question", answer="Answer", sources_json="[]")
        session.add_all([document, query])
        session.commit()
        assert session.query(Document).one().filename == "test.pdf"
        assert session.query(QueryLog).one().answer == "Answer"
        session.close()
        engine.dispose()


def check_stage_9():
    with TestClient(app) as client:
        with PDF_PATH.open("rb") as pdf:
            response = client.post("/ingest", files={"file": ("test_file.pdf", pdf, "application/pdf")}, data={"project_id": "route-project"})
        assert response.status_code == 200, response.text
        assert response.json()["num_chunks"] == len(chunks)
        response = client.post("/query", json={"project_id": "route-project", "question": "What interfaces are described?"})
        assert response.status_code == 200, response.text
        assert response.json()["answer"] and response.json()["sources"]


def check_stage_10():
    result = extract_entities("route-project")
    entities = result["entities"] if isinstance(result, dict) else result
    assert entities and all({"component_name", "interfaces", "description"} <= entity.keys() for entity in entities)
    source_text = " ".join(section["text"] for section in sections).lower()
    assert any(entity["component_name"].lower() in source_text for entity in entities)


checks = [check_stage_1, check_stage_2, check_stage_3, check_stage_4, check_stage_5, check_stage_6, check_stage_7, check_stage_8, check_stage_9, check_stage_10]
for number, check in enumerate(checks, start=1):
    try:
        stage(number, check)
    except Exception:
        for blocked_number in range(number + 1, len(checks) + 1):
            results.append((blocked_number, "BLOCKED", f"Stage {number} failed"))
            print(f"STAGE {blocked_number}: BLOCKED - Stage {number} failed")
        break

print("\nSUMMARY")
for number, status, reason in results:
    print(f"STAGE {number}: {status}" + (f" - {reason}" if reason else ""))
