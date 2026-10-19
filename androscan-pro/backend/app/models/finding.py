from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

def utc_now(): return datetime.now(timezone.utc)

CATEGORIES = {"STORAGE","CRYPTO","AUTH","NETWORK","PLATFORM","CODE","RESILIENCE","PRIVACY","OTHER"}
SEVERITIES = {"INFO","LOW","MEDIUM","HIGH","CRITICAL"}
PRIORITIES = {"P4","P3","P2","P1"}
REVIEW_STATES = {"PENDING","CONFIRMED","DISMISSED"}

class Finding(Base):
    __tablename__ = "findings"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    analysis_id: Mapped[str] = mapped_column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    tool_execution_id: Mapped[str] = mapped_column(String(36), ForeignKey("tool_executions.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    correlation_key: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    category: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(10), nullable=False, index=True, default="P3")
    evidence_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    raw_result_ref: Mapped[str | None] = mapped_column(String(500), nullable=True)
    review_state: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING", index=True)
    analyst_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    tool_execution = relationship("ToolExecution")
    reviews = relationship("FindingReview", cascade="all, delete-orphan", order_by="FindingReview.created_at")

class FindingReview(Base):
    __tablename__ = "finding_reviews"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    finding_id: Mapped[str] = mapped_column(String(36), ForeignKey("findings.id", ondelete="CASCADE"), nullable=False, index=True)
    analyst_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(30), nullable=False)
    justification: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
