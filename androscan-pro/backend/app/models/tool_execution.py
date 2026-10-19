from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ToolExecution(Base):
    __tablename__ = "tool_executions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    analysis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tool_id: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    tool_name: Mapped[str] = mapped_column(String(120), nullable=False)
    tool_version: Mapped[str] = mapped_column(String(80), nullable=False)
    state: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stdout: Mapped[str] = mapped_column(Text, nullable=False, default="")
    stderr: Mapped[str] = mapped_column(Text, nullable=False, default="")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
