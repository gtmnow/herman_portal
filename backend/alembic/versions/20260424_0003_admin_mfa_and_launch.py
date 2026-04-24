"""Add admin MFA challenges and session state

Revision ID: 20260424_0003
Revises: 20260423_0002
Create Date: 2026-04-24 11:00:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260424_0003"
down_revision = "20260423_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("auth_sessions", sa.Column("admin_mfa_verified_at", sa.DateTime(), nullable=True))

    op.create_table(
        "auth_mfa_challenges",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id_hash", sa.String(length=255), nullable=False),
        sa.Column("challenge_type", sa.String(length=64), nullable=False, server_default="email_code"),
        sa.Column("requested_app", sa.String(length=64), nullable=False, server_default="herman_admin"),
        sa.Column("code_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("consumed_at", sa.DateTime(), nullable=True),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_auth_mfa_challenges_user_id_hash", "auth_mfa_challenges", ["user_id_hash"], unique=False)
    op.create_index("ix_auth_mfa_challenges_requested_app", "auth_mfa_challenges", ["requested_app"], unique=False)
    op.create_index("ix_auth_mfa_challenges_expires_at", "auth_mfa_challenges", ["expires_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_auth_mfa_challenges_expires_at", table_name="auth_mfa_challenges")
    op.drop_index("ix_auth_mfa_challenges_requested_app", table_name="auth_mfa_challenges")
    op.drop_index("ix_auth_mfa_challenges_user_id_hash", table_name="auth_mfa_challenges")
    op.drop_table("auth_mfa_challenges")
    op.drop_column("auth_sessions", "admin_mfa_verified_at")
