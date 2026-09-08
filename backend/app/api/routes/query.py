import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import QueryLog
from app.schemas.query import QueryRequest
from app.services.rag_pipeline import answer_question


router = APIRouter()


@router.post("/query")
def query_document(request: QueryRequest, db: Session = Depends(get_db)) -> dict:
	result = answer_question(request.project_id, request.question)
	db.add(
		QueryLog(
			project_id=request.project_id,
			question=request.question,
			answer=result["answer"],
			sources_json=json.dumps(result["sources"]),
		)
	)
	db.commit()
	return result
