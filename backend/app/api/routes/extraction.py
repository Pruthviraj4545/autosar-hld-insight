from fastapi import APIRouter

from app.services.entity_extraction import extract_entities


router = APIRouter()


@router.get("/extract-entities/{project_id}")
def extract_project_entities(project_id: str) -> dict:
	return extract_entities(project_id)
