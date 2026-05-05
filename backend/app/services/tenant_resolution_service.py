from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.auth_user import AuthUser


def resolve_primary_tenant_id(db: Session, user: AuthUser) -> str | None:
    try:
        tenant_id = db.execute(
            text(
                """
                SELECT tenant_id
                FROM user_tenant_membership
                WHERE user_id_hash = :user_id_hash
                  AND is_primary = true
                  AND status != 'deleted'
                ORDER BY updated_at DESC, created_at DESC
                LIMIT 1
                """
            ),
            {"user_id_hash": user.user_id_hash},
        ).scalar_one_or_none()
    except SQLAlchemyError:
        tenant_id = None

    if tenant_id is not None:
        return str(tenant_id)
    return user.tenant_id
