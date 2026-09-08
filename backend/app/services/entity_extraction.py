import json
import re

from app.services.llm_client import LLMClient
from app.services.vector_store import VectorStoreService


BATCH_SIZE = 10
EXTRACTION_SYSTEM_PROMPT = (
	"Extract entities only from the supplied document chunks. "
	"Return valid JSON only: an array of objects with exactly these fields: "
	"component_name (string), interfaces (array of strings), "
	"description (string). Do not invent entities or details."
)


def _parse_entities(response_text: str) -> list[dict]:
	cleaned = response_text.strip()
	cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE)
	parsed = json.loads(cleaned)
	if isinstance(parsed, dict):
		parsed = parsed.get("entities", [])
	if not isinstance(parsed, list):
		raise ValueError("LLM entity response must be a JSON array")
	return [entity for entity in parsed if isinstance(entity, dict)]


def _merge_entities(entity_batches: list[list[dict]]) -> list[dict]:
	merged: dict[str, dict] = {}
	for batch in entity_batches:
		for entity in batch:
			name = str(entity.get("component_name", "")).strip()
			if not name:
				continue
			key = name.casefold()
			if key not in merged:
				merged[key] = {
					"component_name": name,
					"interfaces": [],
					"description": str(entity.get("description", "")).strip(),
				}
			current = merged[key]
			for interface in entity.get("interfaces", []):
				interface = str(interface).strip()
				if interface and interface.casefold() not in {
					item.casefold() for item in current["interfaces"]
				}:
					current["interfaces"].append(interface)
			if not current["description"] and entity.get("description"):
				current["description"] = str(entity["description"]).strip()
	return list(merged.values())


def extract_entities(project_id: str) -> dict:
	collection = VectorStoreService().create_or_get_collection(project_id)
	stored = collection.get(include=["documents", "metadatas"])
	documents = stored.get("documents") or []
	metadatas = stored.get("metadatas") or []
	chunks = [
		{
			"text": document,
			"heading": metadata.get("heading", "Unknown"),
			"page_start": metadata.get("page_start", 0),
			"page_end": metadata.get("page_end", 0),
		}
		for document, metadata in zip(documents, metadatas)
	]

	llm_client = LLMClient()
	batches = []
	for start in range(0, len(chunks), BATCH_SIZE):
		batch = chunks[start : start + BATCH_SIZE]
		context = "\n\n".join(
			f"Section: {chunk['heading']} (p.{chunk['page_start']}-{chunk['page_end']})\n"
			f"Text: {chunk['text']}"
			for chunk in batch
		)
		prompt = f"Document chunks:\n{context}\n\nExtract the entities as JSON."
		batches.append(_parse_entities(llm_client.generate_text(prompt, EXTRACTION_SYSTEM_PROMPT)))

	return {"project_id": project_id, "entities": _merge_entities(batches)}
