from __future__ import annotations

from app.core.config import settings
from app.core.security import issue_admin_launch_token
from app.models.auth_user import AuthUser


class AdminLaunchService:
    def create_launch_token(self, *, user: AuthUser) -> str:
        return issue_admin_launch_token(
            user_id_hash=user.user_id_hash,
            email=user.email,
            display_name=user.display_name or user.email,
        )

    def build_redirect_url(self, launch_token: str) -> str:
        separator = "&" if "?" in settings.hermanadmin_ui_url else "?"
        return f"{settings.hermanadmin_ui_url}{separator}launch_token={launch_token}"
