from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


ANALYSIS_STATES = {
    "CREATED",
    "QUEUED",
    "PREPARING",
    "RUNNING",
    "PROCESSING_RESULTS",
    "COMPLETED",
    "FAILED",
    "CANCELLED",
}


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    apk_version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("apk_versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    state: Mapped[str] = mapped_column(String(40), nullable=False, default="CREATED", index=True)
    requested_by_user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    trace_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    queued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    sandbox_container_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    sandbox_status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    apk_version = relationship("APKVersion")
