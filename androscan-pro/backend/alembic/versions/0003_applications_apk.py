"""applications and APK versions

Revision ID: 0003_applications_apk
Revises: 0002_identity
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_applications_apk"
down_revision = "0002_identity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "applications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("package_name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("organization_id", "package_name", name="uq_applications_org_package"),
    )
    op.create_index("ix_applications_organization_id", "applications", ["organization_id"], unique=False)

    op.create_table(
        "apk_versions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("application_id", sa.String(36), sa.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("mime_type", sa.String(120), nullable=False),
        sa.Column("storage_key", sa.String(500), nullable=False),
        sa.Column("version_name", sa.String(120), nullable=True),
        sa.Column("version_code", sa.String(120), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("validation_status", sa.String(40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("application_id", "sha256", name="uq_apk_versions_application_sha256"),
        sa.UniqueConstraint("storage_key"),
    )
    op.create_index("ix_apk_versions_application_id", "apk_versions", ["application_id"], unique=False)
    op.create_index("ix_apk_versions_sha256", "apk_versions", ["sha256"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_apk_versions_sha256", table_name="apk_versions")
    op.drop_index("ix_apk_versions_application_id", table_name="apk_versions")
    op.drop_table("apk_versions")
    op.drop_index("ix_applications_organization_id", table_name="applications")
    op.drop_table("applications")
