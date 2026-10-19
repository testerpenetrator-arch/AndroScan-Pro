"""persist human-reviewed AI assistance drafts
Revision ID: 0009_ai_assistance
Revises: 0008_reports
"""
from alembic import op
import sqlalchemy as sa
revision = "0009_ai_assistance"
down_revision = "0008_reports"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "ai_assistance",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("analysis_id", sa.String(36), nullable=False),
        sa.Column("requested_by_user_id", sa.String(36), nullable=True),
        sa.Column("provider", sa.String(80), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("input_finding_ids", sa.JSON(), nullable=False),
        sa.Column("result_json", sa.JSON(), nullable=False),
        sa.Column("disclaimer", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["analysis_id"], ["analyses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_ai_assistance_organization_id", "ai_assistance", ["organization_id"])
    op.create_index("ix_ai_assistance_analysis_id", "ai_assistance", ["analysis_id"])
    op.create_index("ix_ai_assistance_requested_by_user_id", "ai_assistance", ["requested_by_user_id"])

def downgrade():
    op.drop_index("ix_ai_assistance_requested_by_user_id", table_name="ai_assistance")
    op.drop_index("ix_ai_assistance_analysis_id", table_name="ai_assistance")
    op.drop_index("ix_ai_assistance_organization_id", table_name="ai_assistance")
    op.drop_table("ai_assistance")
