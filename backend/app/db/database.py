from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
	pass


database_path = Path(settings.sqlite_db_path)
if not database_path.is_absolute():
	database_path = Path(__file__).resolve().parents[3] / database_path
database_path.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
	f"sqlite:///{database_path}",
	connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


from app.db import models  # noqa: E402, F401

Base.metadata.create_all(bind=engine)
