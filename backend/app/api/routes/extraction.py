from fastapi import APIRouter

from app.services.entity_extraction import extract_entities, find_inconsistencies


router = APIRouter()


@router.get("/extract-entities/{project_id}")
def extract_project_entities(project_id: str) -> dict:
	return extract_entities(project_id)


@router.get("/inconsistencies/{project_id}")
def find_project_inconsistencies(project_id: str) -> list[dict]:
	return find_inconsistencies(project_id)
