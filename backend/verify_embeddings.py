from app.services.embeddings import EmbeddingService


class VerificationModel:
    def encode(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(text)), 1.0, 0.5] for text in texts]


sentences = [
    "AUTOSAR components communicate through defined interfaces.",
    "The document describes the system architecture.",
]
embeddings = EmbeddingService(model=VerificationModel()).embed_texts(sentences)

assert len(embeddings) == 2
assert all(isinstance(embedding, list) for embedding in embeddings)
assert all(isinstance(value, float) for embedding in embeddings for value in embedding)
dimension = len(embeddings[0])
assert dimension > 0
assert all(len(embedding) == dimension for embedding in embeddings)

print(f"EMBEDDING DIMENSION: {dimension}")
print("STAGE 4 PASSED")
