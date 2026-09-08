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
INCONSISTENCY_SYSTEM_PROMPT = (
	"Review the supplied repeated component or interface descriptions. "
	"Return valid JSON only as an array of objects with exactly these fields: "
	"entity_name (string), explanation (string), sources (array of objects with "
	"chunk_id, heading, page_start, and page_end). Flag only likely mismatches."
)
MENTION_EXTRACTION_SYSTEM_PROMPT = (
	"Extract named components or interfaces only from the supplied chunks. "
	"Return valid JSON only as an array of objects with exactly these fields: "
	"component_name (string), interfaces (array of strings), "
	"description (string), source_chunk_ids (array of strings)."
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


def _load_chunks(project_id: str) -> list[dict]:
	collection = VectorStoreService().create_or_get_collection(project_id)
	stored = collection.get(include=["documents", "metadatas"])
	return [
		{
			"text": document,
			"chunk_id": metadata.get("chunk_id", f"chunk-{index}"),
			"heading": metadata.get("heading", "Unknown"),
			"page_start": metadata.get("page_start", 0),
			"page_end": metadata.get("page_end", 0),
		}
		for index, (document, metadata) in enumerate(
			zip(stored.get("documents") or [], stored.get("metadatas") or []),
			start=1,
		)
	]


def extract_entities(project_id: str) -> dict:
	chunks = _load_chunks(project_id)

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


def find_inconsistencies(project_id: str) -> list[dict]:
	chunks = _load_chunks(project_id)
	if not chunks:
		return []

	llm_client = LLMClient()
	mentions = []
	for start in range(0, len(chunks), BATCH_SIZE):
		batch = chunks[start : start + BATCH_SIZE]
		context = "\n\n".join(
			f"Chunk ID: {chunk['chunk_id']}\n"
			f"Section: {chunk['heading']} (p.{chunk['page_start']}-{chunk['page_end']})\n"
			f"Text: {chunk['text']}"
			for chunk in batch
		)
		prompt = (
			"Extract every named component or interface and its description from "
			f"these chunks. Include source_chunk_ids for each mention.\n\n{context}"
		)
		for entity in _parse_entities(
			llm_client.generate_text(prompt, MENTION_EXTRACTION_SYSTEM_PROMPT)
		):
			entity["source_chunk_ids"] = entity.get("source_chunk_ids", [])
			mentions.append(entity)

		# The extraction prompt may return the source field even though older
		# model responses omit it; omitted provenance cannot form a comparison.
	by_name: dict[str, list[dict]] = {}
	for mention in mentions:
		name = str(mention.get("component_name", "")).strip()
		if name and mention.get("source_chunk_ids"):
			by_name.setdefault(name.casefold(), []).append(mention)
	candidates = []
	for group in by_name.values():
		descriptions = {str(item.get("description", "")).strip() for item in group}
		if len(descriptions) > 1:
			candidates.append(group)
	if not candidates:
		return []

	comparison = json.dumps(candidates, indent=2)
	response = llm_client.generate_text(
		f"Repeated entities with differing descriptions:\n{comparison}",
		INCONSISTENCY_SYSTEM_PROMPT,
	)
	return _parse_entities(response)
