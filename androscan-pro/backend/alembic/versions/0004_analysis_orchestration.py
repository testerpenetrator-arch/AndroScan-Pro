"""analysis orchestration

Revision ID: 0004_analysis_orchestration
Revises: 0003_applications_apk
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_analysis_orchestration"
down_revision = "0003_applications_apk"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "analyses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("apk_version_id", sa.String(length=36), nullable=False),
        sa.Column("state", sa.String(length=40), nullable=False),
        sa.Column("requested_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("trace_id", sa.String(length=64), nullable=True),
        sa.Column("attempt", sa.Integer(), nullable=False),
        sa.Column("queued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("summary_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["apk_version_id"], ["apk_versions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analyses_organization_id", "analyses", ["organization_id"])
    op.create_index("ix_analyses_apk_version_id", "analyses", ["apk_version_id"])
    op.create_index("ix_analyses_state", "analyses", ["state"])
    op.create_index("ix_analyses_requested_by_user_id", "analyses", ["requested_by_user_id"])
    op.create_index("ix_analyses_trace_id", "analyses", ["trace_id"])


def downgrade() -> None:
    op.drop_index("ix_analyses_trace_id", table_name="analyses")
    op.drop_index("ix_analyses_requested_by_user_id", table_name="analyses")
    op.drop_index("ix_analyses_state", table_name="analyses")
    op.drop_index("ix_analyses_apk_version_id", table_name="analyses")
    op.drop_index("ix_analyses_organization_id", table_name="analyses")
    op.drop_table("analyses")
