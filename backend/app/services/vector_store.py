import hashlib
from typing import Any

from app.core.config import settings


class VectorStoreService:
	"""Persist and query document chunks in project-isolated Chroma collections."""

	def __init__(self, client: Any | None = None) -> None:
		if client is None:
			import chromadb

			client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
		self.client = client

	@staticmethod
	def _collection_name(project_id: str) -> str:
		project_hash = hashlib.sha256(project_id.encode("utf-8")).hexdigest()
		return f"project_{project_hash}"

	def create_or_get_collection(self, project_id: str) -> Any:
		if not project_id:
			raise ValueError("project_id must not be empty")
		return self.client.get_or_create_collection(
			name=self._collection_name(project_id)
		)

	def add_chunks(
		self,
		project_id: str,
		chunks: list[dict],
		embeddings: list[list[float]],
	) -> None:
		if len(chunks) != len(embeddings):
			raise ValueError("chunks and embeddings must have the same length")
		if not chunks:
			return

		collection = self.create_or_get_collection(project_id)
		collection.add(
			ids=[chunk["chunk_id"] for chunk in chunks],
			documents=[chunk["text"] for chunk in chunks],
			embeddings=embeddings,
			metadatas=[
				{
					"heading": chunk["heading"],
					"page_start": chunk["page_start"],
					"page_end": chunk["page_end"],
					"chunk_id": chunk["chunk_id"],
				}
				for chunk in chunks
			],
		)

	def query(
		self,
		project_id: str,
		query_embedding: list[float],
		top_k: int = 5,
	) -> dict[str, Any]:
		if top_k < 1:
			raise ValueError("top_k must be at least 1")

		collection = self.create_or_get_collection(project_id)
		return collection.query(
			query_embeddings=[query_embedding],
			n_results=top_k,
			include=["documents", "metadatas", "distances"],
		)
