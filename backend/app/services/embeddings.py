from threading import Lock
from typing import Any, ClassVar

from app.core.config import settings


class EmbeddingService:
	"""Create text embeddings using a cached sentence-transformers model."""

	_models: ClassVar[dict[str, Any]] = {}
	_models_lock: ClassVar[Lock] = Lock()

	def __init__(self, model: Any | None = None, model_name: str | None = None) -> None:
		self.model_name = model_name or settings.embedding_model_name
		self._injected_model = model

	@property
	def _model(self) -> Any:
		if self._injected_model is not None:
			return self._injected_model

		if self.model_name not in self._models:
			with self._models_lock:
				if self.model_name not in self._models:
					from sentence_transformers import SentenceTransformer

					self._models[self.model_name] = SentenceTransformer(self.model_name)

		return self._models[self.model_name]

	@staticmethod
	def _as_lists(encoded: Any) -> list[list[float]]:
		if hasattr(encoded, "tolist"):
			encoded = encoded.tolist()
		return [list(vector) for vector in encoded]

	def embed_texts(self, texts: list[str]) -> list[list[float]]:
		if not texts:
			return []
		return self._as_lists(self._model.encode(texts))

	def embed_query(self, text: str) -> list[float]:
		return self.embed_texts([text])[0]
