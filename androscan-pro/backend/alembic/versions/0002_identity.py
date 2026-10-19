"""identity and tenant model

Revision ID: 0002_identity
Revises:
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

revision = "0002_identity"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("slug", sa.String(160), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_organizations_name", "organizations", ["name"], unique=False)
    op.create_index("ix_organizations_slug", "organizations", ["slug"], unique=False)

    op.create_table(
        "roles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("description", sa.String(255), nullable=False),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_roles_name", "roles", ["name"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("full_name", sa.String(160), nullable=False),
        sa.Column("password_hash", sa.String(512), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)

    op.create_table(
        "user_organization_roles",
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role_id", sa.String(36), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("actor_user_id", sa.String(36), nullable=True),
        sa.Column("organization_id", sa.String(36), nullable=True),
        sa.Column("action", sa.String(120), nullable=False),
        sa.Column("resource_type", sa.String(80), nullable=False),
        sa.Column("resource_id", sa.String(36), nullable=True),
        sa.Column("result", sa.String(40), nullable=False),
        sa.Column("trace_id", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_events_actor_user_id", "audit_events", ["actor_user_id"], unique=False)
    op.create_index("ix_audit_events_organization_id", "audit_events", ["organization_id"], unique=False)
    op.create_index("ix_audit_events_action", "audit_events", ["action"], unique=False)
    op.create_index("ix_audit_events_trace_id", "audit_events", ["trace_id"], unique=False)

    roles = table("roles", column("id", sa.String), column("name", sa.String), column("description", sa.String))
    op.bulk_insert(
        roles,
        [
            {"id": "role-admin", "name": "ADMIN", "description": "Administrador de la organización."},
            {"id": "role-analyst", "name": "ANALYST", "description": "Analista de seguridad."},
            {"id": "role-developer", "name": "DEVELOPER", "description": "Desarrollador con acceso autorizado a resultados."},
            {"id": "role-it-manager", "name": "IT_MANAGER", "description": "Gestor de TI de la organización."},
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_audit_events_trace_id", table_name="audit_events")
    op.drop_index("ix_audit_events_action", table_name="audit_events")
    op.drop_index("ix_audit_events_organization_id", table_name="audit_events")
    op.drop_index("ix_audit_events_actor_user_id", table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_table("user_organization_roles")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_roles_name", table_name="roles")
    op.drop_table("roles")
    op.drop_index("ix_organizations_slug", table_name="organizations")
    op.drop_index("ix_organizations_name", table_name="organizations")
    op.drop_table("organizations")
