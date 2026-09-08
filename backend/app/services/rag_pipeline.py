from app.services.embeddings import EmbeddingService
from app.services.llm_client import LLMClient
from app.services.vector_store import VectorStoreService


def _context_chunks(results: dict) -> list[dict]:
	documents = (results.get("documents") or [[]])[0]
	metadatas = (results.get("metadatas") or [[]])[0]
	return [
		{
			"text": document,
			"heading": metadata["heading"],
			"page_start": metadata["page_start"],
			"page_end": metadata["page_end"],
			"chunk_id": metadata.get("chunk_id"),
		}
		for document, metadata in zip(documents, metadatas)
	]


def answer_question(project_id: str, question: str) -> dict:
	embedding_service = EmbeddingService()
	vector_store = VectorStoreService()
	llm_client = LLMClient()

	query_embedding = embedding_service.embed_query(question)
	results = vector_store.query(project_id, query_embedding, top_k=5)
	context_chunks = _context_chunks(results)
	answer = llm_client.generate_answer(question, context_chunks)

	sources = [
		{
			"heading": chunk["heading"],
			"page_start": chunk["page_start"],
			"page_end": chunk["page_end"],
		}
		for chunk in context_chunks
	]
	return {"answer": answer, "sources": sources}
