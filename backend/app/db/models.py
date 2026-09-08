from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Document(Base):
	__tablename__ = "documents"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	filename: Mapped[str] = mapped_column(String(255), nullable=False)
	project_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
	uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
	status: Mapped[str] = mapped_column(String(50), nullable=False, default="uploaded")


class QueryLog(Base):
	__tablename__ = "query_logs"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	project_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
	question: Mapped[str] = mapped_column(Text, nullable=False)
	answer: Mapped[str] = mapped_column(Text, nullable=False)
	sources_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
