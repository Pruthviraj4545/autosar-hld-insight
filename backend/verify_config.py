from app.core.config import Settings


settings = Settings()

assert settings.embedding_model_name is not None
assert settings.chunk_max_tokens is not None

print(f"EMBEDDING_MODEL_NAME: {settings.embedding_model_name}")
print(f"CHUNK_MAX_TOKENS: {settings.chunk_max_tokens}")
print("STAGE 1 PASSED")
