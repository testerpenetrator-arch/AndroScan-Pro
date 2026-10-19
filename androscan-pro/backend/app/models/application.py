from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint("organization_id", "package_name", name="uq_applications_org_package"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    package_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    versions: Mapped[list["APKVersion"]] = relationship(
        back_populates="application", cascade="all, delete-orphan", order_by="APKVersion.created_at"
    )


class APKVersion(Base):
    __tablename__ = "apk_versions"
    __table_args__ = (
        UniqueConstraint("application_id", "sha256", name="uq_apk_versions_application_sha256"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    application_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    version_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    version_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    validation_status: Mapped[str] = mapped_column(String(40), nullable=False, default="VALIDATED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    application: Mapped[Application] = relationship(back_populates="versions")
