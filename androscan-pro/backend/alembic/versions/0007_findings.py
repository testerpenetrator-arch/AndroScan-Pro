"""normalized findings and analyst reviews
Revision ID: 0007_findings
Revises: 0006_tool_execution
"""
from alembic import op
import sqlalchemy as sa
revision="0007_findings"; down_revision="0006_tool_execution"; branch_labels=None; depends_on=None

def upgrade():
    op.create_table("findings",
        sa.Column("id",sa.String(36),primary_key=True), sa.Column("analysis_id",sa.String(36),nullable=False),
        sa.Column("tool_execution_id",sa.String(36),nullable=False), sa.Column("rule_id",sa.String(120)),
        sa.Column("correlation_key",sa.String(255),nullable=False), sa.Column("title",sa.String(255),nullable=False),
        sa.Column("description",sa.Text(),nullable=False), sa.Column("category",sa.String(40),nullable=False),
        sa.Column("severity",sa.String(20),nullable=False), sa.Column("priority",sa.String(10),nullable=False),
        sa.Column("evidence_json",sa.JSON(),nullable=False), sa.Column("raw_result_ref",sa.String(500)),
        sa.Column("review_state",sa.String(30),nullable=False), sa.Column("analyst_notes",sa.Text()),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False), sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False),
        sa.ForeignKeyConstraint(["analysis_id"],["analyses.id"],ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tool_execution_id"],["tool_executions.id"],ondelete="CASCADE"))
    for n,c in [("analysis_id","analysis_id"),("tool_execution_id","tool_execution_id"),("rule_id","rule_id"),("category","category"),("severity","severity"),("priority","priority"),("review_state","review_state")]: op.create_index("ix_findings_"+n,"findings",[c])
    op.create_table("finding_reviews",
        sa.Column("id",sa.String(36),primary_key=True), sa.Column("finding_id",sa.String(36),nullable=False),
        sa.Column("analyst_user_id",sa.String(36),nullable=False), sa.Column("state",sa.String(30),nullable=False),
        sa.Column("justification",sa.Text(),nullable=False), sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
        sa.ForeignKeyConstraint(["finding_id"],["findings.id"],ondelete="CASCADE"), sa.ForeignKeyConstraint(["analyst_user_id"],["users.id"],ondelete="RESTRICT"))
    op.create_index("ix_finding_reviews_finding_id","finding_reviews",["finding_id"]); op.create_index("ix_finding_reviews_analyst_user_id","finding_reviews",["analyst_user_id"])

def downgrade():
    op.drop_index("ix_finding_reviews_analyst_user_id",table_name="finding_reviews"); op.drop_index("ix_finding_reviews_finding_id",table_name="finding_reviews"); op.drop_table("finding_reviews")
    for n in ["review_state","priority","severity","category","rule_id","tool_execution_id","analysis_id"]: op.drop_index("ix_findings_"+n,table_name="findings")
    op.drop_table("findings")
