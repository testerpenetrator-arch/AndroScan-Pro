"""tool execution provenance

Revision ID: 0006_tool_execution
Revises: 0005_sandbox
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_tool_execution"
down_revision = "0005_sandbox"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tool_executions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("analysis_id", sa.String(length=36), nullable=False),
        sa.Column("tool_id", sa.String(length=80), nullable=False),
        sa.Column("tool_name", sa.String(length=120), nullable=False),
        sa.Column("tool_version", sa.String(length=80), nullable=False),
        sa.Column("state", sa.String(length=40), nullable=False),
        sa.Column("exit_code", sa.Integer(), nullable=True),
        sa.Column("stdout", sa.Text(), nullable=False),
        sa.Column("stderr", sa.Text(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["analysis_id"], ["analyses.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_tool_executions_analysis_id", "tool_executions", ["analysis_id"])
    op.create_index("ix_tool_executions_tool_id", "tool_executions", ["tool_id"])
    op.create_index("ix_tool_executions_state", "tool_executions", ["state"])


def downgrade() -> None:
    op.drop_index("ix_tool_executions_state", table_name="tool_executions")
    op.drop_index("ix_tool_executions_tool_id", table_name="tool_executions")
    op.drop_index("ix_tool_executions_analysis_id", table_name="tool_executions")
    op.drop_table("tool_executions")
