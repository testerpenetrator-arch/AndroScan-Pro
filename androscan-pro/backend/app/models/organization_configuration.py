from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class OrganizationConfiguration(Base):
    __tablename__ = "organization_configurations"
    __table_args__ = (UniqueConstraint("organization_id", name="uq_org_configuration_org"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    settings_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    tool_policy_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    updated_by_user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)
