"""Create portal-owned auth tables

Revision ID: 20260417_0001
Revises:
Create Date: 2026-04-17 06:45:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260417_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auth_user_credentials",
        sa.Column("user_id_hash", sa.String(length=255), primary_key=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("password_algorithm", sa.String(length=64), nullable=False, server_default="bcrypt"),
        sa.Column("password_set_at", sa.DateTime(), nullable=True),
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime(), nullable=True),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id_hash", sa.String(length=255), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_password_reset_tokens_user_id_hash", "password_reset_tokens", ["user_id_hash"], unique=False)
    op.create_index(
        "ix_password_reset_tokens_token_hash",
        "password_reset_tokens",
        ["token_hash"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_password_reset_tokens_token_hash", table_name="password_reset_tokens")
    op.drop_index("ix_password_reset_tokens_user_id_hash", table_name="password_reset_tokens")
    op.drop_table("password_reset_tokens")
    op.drop_table("auth_user_credentials")
