from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class AIAssistance(Base):
    __tablename__ = "ai_assistance"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_id: Mapped[str] = mapped_column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    requested_by_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    provider: Mapped[str] = mapped_column(String(80), nullable=False, default="local-rule-assistant")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="REVIEW_REQUIRED")
    input_finding_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    result_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    disclaimer: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
