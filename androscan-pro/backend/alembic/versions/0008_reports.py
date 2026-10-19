"""persist generated security reports
Revision ID: 0008_reports
Revises: 0007_findings
"""
from alembic import op
import sqlalchemy as sa
revision = "0008_reports"
down_revision = "0007_findings"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "reports",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("analysis_id", sa.String(36), nullable=False),
        sa.Column("requested_by_user_id", sa.String(36), nullable=True),
        sa.Column("format", sa.String(10), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(120), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["analysis_id"], ["analyses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_reports_organization_id", "reports", ["organization_id"])
    op.create_index("ix_reports_analysis_id", "reports", ["analysis_id"])
    op.create_index("ix_reports_requested_by_user_id", "reports", ["requested_by_user_id"])

def downgrade():
    op.drop_index("ix_reports_requested_by_user_id", table_name="reports")
    op.drop_index("ix_reports_analysis_id", table_name="reports")
    op.drop_index("ix_reports_organization_id", table_name="reports")
    op.drop_table("reports")
