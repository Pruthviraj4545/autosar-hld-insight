from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	groq_api_key: str
	embedding_model_name: str = "all-MiniLM-L6-v2"
	chroma_persist_dir: str = "../data/vector_store"
	sqlite_db_path: str = "../data/app.db"
	chunk_max_tokens: int = 500

	model_config = SettingsConfigDict(
		env_file=Path(__file__).resolve().parents[2] / ".env",
		env_file_encoding="utf-8",
		extra="ignore",
	)


settings = Settings()
