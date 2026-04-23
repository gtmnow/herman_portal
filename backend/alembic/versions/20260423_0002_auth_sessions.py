"""Add portal auth sessions

Revision ID: 20260423_0002
Revises: 20260417_0001
Create Date: 2026-04-23 10:00:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260423_0002"
down_revision = "20260417_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auth_sessions",
        sa.Column("session_token_hash", sa.String(length=255), primary_key=True),
        sa.Column("user_id_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_auth_sessions_user_id_hash", "auth_sessions", ["user_id_hash"], unique=False)
    op.create_index("ix_auth_sessions_expires_at", "auth_sessions", ["expires_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_auth_sessions_expires_at", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_user_id_hash", table_name="auth_sessions")
    op.drop_table("auth_sessions")
