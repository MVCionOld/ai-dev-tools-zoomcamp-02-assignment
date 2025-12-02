"""create sessions and users tables

Revision ID: 20241201_01
Revises:
Create Date: 2025-12-01 21:09:00.000000
"""

from __future__ import annotations

from alembic import op  # type: ignore[attr-defined]
import sqlalchemy as sa

from app.models.session import GUID

# revision identifiers, used by Alembic.
revision = "20241201_01"
down_revision = None
branch_labels = None
depends_on = None


# Using string field instead of enum for simplicity


def upgrade() -> None:
    op.create_table(
        "sessions",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("language", sa.String(length=64), nullable=False),
        sa.Column("code_snapshot", sa.Text(), nullable=True),
        sa.Column("problem_text", sa.Text(), nullable=True),
        sa.Column("creator_id", GUID(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sessions")),
    )

    # Enum already created manually

    op.create_table(
        "users",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("session_id", GUID(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["sessions.id"],
            name=op.f("fk_users_session_id_sessions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(op.f("ix_users_session_id"), "users", ["session_id"], unique=False)

    op.create_foreign_key(
        op.f("fk_sessions_creator_id_users"),
        "sessions",
        "users",
        ["creator_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_sessions_creator_id_users"), "sessions", type_="foreignkey"
    )
    op.drop_index(op.f("ix_users_session_id"), table_name="users")
    op.drop_table("users")
    op.drop_table("sessions")
