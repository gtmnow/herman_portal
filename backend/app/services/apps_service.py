from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.auth_user import AuthUser
from app.schemas.auth import AppDescriptor, AppsResponse, PortalUserSummary
from app.services.tenant_resolution_service import resolve_primary_tenant_id


class AppsService:
    def get_available_apps(self, *, db: Session, user: AuthUser) -> AppsResponse:
        has_admin_access = self.has_admin_access(db=db, user_id_hash=user.user_id_hash)
        return AppsResponse(
            user=self._to_user_summary(db, user),
            apps=[
                AppDescriptor(
                    app_key="herman_prompt",
                    label="Herman Prompt",
                    description="Open the Herman Prompt workspace.",
                    enabled=True,
                    launch_mode="direct",
                    requires_mfa=False,
                ),
                AppDescriptor(
                    app_key="herman_admin",
                    label="Herman Admin",
                    description="Admin access is available only for active admin users.",
                    enabled=has_admin_access,
                    launch_mode="mfa_required",
                    requires_mfa=True,
                ),
            ],
        )

    def has_admin_access(self, *, db: Session, user_id_hash: str) -> bool:
        try:
            result = db.execute(
                text(
                    """
                    SELECT 1
                    FROM admin_users
                    WHERE user_id_hash = :user_id_hash
                      AND is_active = true
                    LIMIT 1
                    """
                ),
                {"user_id_hash": user_id_hash},
            ).first()
        except SQLAlchemyError:
            return False
        return result is not None

    def _to_user_summary(self, db: Session, user: AuthUser) -> PortalUserSummary:
        return PortalUserSummary(
            email=user.email,
            user_id_hash=user.user_id_hash,
            display_name=user.display_name,
            tenant_id=resolve_primary_tenant_id(db, user),
        )
