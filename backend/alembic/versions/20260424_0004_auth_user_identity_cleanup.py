"""Finalize auth user credential split and identity constraints.

Revision ID: 20260424_0004
Revises: 20260424_0003
Create Date: 2026-04-24 18:30:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260424_0004"
down_revision = "20260424_0003"
branch_labels = None
depends_on = None


def _has_table(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _column_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def _has_constraint(inspector: sa.Inspector, table_name: str, constraint_name: str) -> bool:
    for constraint in inspector.get_unique_constraints(table_name):
        if constraint.get("name") == constraint_name:
            return True
    for constraint in inspector.get_foreign_keys(table_name):
        if constraint.get("name") == constraint_name:
            return True
    return False


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _has_table(inspector, "auth_user_credentials"):
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
        inspector = sa.inspect(bind)

    auth_user_columns = _column_names(inspector, "auth_users")

    if "password_hash" in auth_user_columns:
        bind.execute(
            sa.text(
                """
                INSERT INTO auth_user_credentials (
                  user_id_hash,
                  password_hash,
                  password_algorithm,
                  password_set_at,
                  failed_login_attempts,
                  locked_until,
                  last_login_at
                )
                SELECT
                  a.user_id_hash,
                  a.password_hash,
                  'bcrypt',
                  a.password_changed_at,
                  0,
                  NULL,
                  a.last_login_at
                FROM auth_users a
                WHERE a.password_hash IS NOT NULL
                  AND NOT EXISTS (
                    SELECT 1
                    FROM auth_user_credentials c
                    WHERE c.user_id_hash = a.user_id_hash
                  )
                """
            )
        )

    duplicate_count = bind.execute(
        sa.text(
            """
            SELECT count(*)
            FROM (
              SELECT user_id_hash
              FROM auth_users
              GROUP BY user_id_hash
              HAVING count(*) > 1
            ) duplicates
            """
        )
    ).scalar_one()
    if duplicate_count:
        raise RuntimeError(
            "Cannot finalize auth identity cleanup while duplicate auth_users.user_id_hash rows exist."
        )

    if not _has_constraint(inspector, "auth_users", "auth_users_user_id_hash_key"):
        op.create_unique_constraint("auth_users_user_id_hash_key", "auth_users", ["user_id_hash"])
        inspector = sa.inspect(bind)

    if not _has_constraint(inspector, "auth_user_credentials", "fk_auth_user_credentials_user"):
        op.create_foreign_key(
            "fk_auth_user_credentials_user",
            "auth_user_credentials",
            "auth_users",
            ["user_id_hash"],
            ["user_id_hash"],
        )

    inspector = sa.inspect(bind)
    auth_user_columns = _column_names(inspector, "auth_users")

    if "password_changed_at" in auth_user_columns:
        op.drop_column("auth_users", "password_changed_at")
        inspector = sa.inspect(bind)
        auth_user_columns = _column_names(inspector, "auth_users")

    if "password_hash" in auth_user_columns:
        op.drop_column("auth_users", "password_hash")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    auth_user_columns = _column_names(inspector, "auth_users")
    if "password_hash" not in auth_user_columns:
        op.add_column("auth_users", sa.Column("password_hash", sa.String(length=255), nullable=True))
        inspector = sa.inspect(bind)
        auth_user_columns = _column_names(inspector, "auth_users")

    if "password_changed_at" not in auth_user_columns:
        op.add_column("auth_users", sa.Column("password_changed_at", sa.DateTime(), nullable=True))

    if _has_constraint(inspector, "auth_user_credentials", "fk_auth_user_credentials_user"):
        op.drop_constraint("fk_auth_user_credentials_user", "auth_user_credentials", type_="foreignkey")

    inspector = sa.inspect(bind)
    if _has_constraint(inspector, "auth_users", "auth_users_user_id_hash_key"):
        op.drop_constraint("auth_users_user_id_hash_key", "auth_users", type_="unique")
