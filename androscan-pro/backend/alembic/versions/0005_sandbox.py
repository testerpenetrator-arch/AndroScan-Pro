"""add sandbox metadata

Revision ID: 0005_sandbox
Revises: 0004_analysis_orchestration
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_sandbox"
down_revision = "0004_analysis_orchestration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("analyses", sa.Column("sandbox_container_id", sa.String(length=128), nullable=True))
    op.add_column("analyses", sa.Column("sandbox_status", sa.String(length=40), nullable=True))
    op.create_index("ix_analyses_sandbox_container_id", "analyses", ["sandbox_container_id"])


def downgrade() -> None:
    op.drop_index("ix_analyses_sandbox_container_id", table_name="analyses")
    op.drop_column("analyses", "sandbox_status")
    op.drop_column("analyses", "sandbox_container_id")
