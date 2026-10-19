"""organization-scoped administration settings and tool policy
Revision ID: 0010_admin_configuration
Revises: 0009_ai_assistance
"""
from alembic import op
import sqlalchemy as sa

revision = "0010_admin_configuration"
down_revision = "0009_ai_assistance"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "organization_configurations",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("organization_id", sa.String(length=36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("settings_json", sa.JSON(), nullable=False),
        sa.Column("tool_policy_json", sa.JSON(), nullable=False),
        sa.Column("updated_by_user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("organization_id", name="uq_org_configuration_org"),
    )
    op.create_index("ix_organization_configurations_organization_id", "organization_configurations", ["organization_id"])


def downgrade():
    op.drop_index("ix_organization_configurations_organization_id", table_name="organization_configurations")
    op.drop_table("organization_configurations")
