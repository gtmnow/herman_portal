from app.core.config import settings
from app.core.security import issue_launch_token


class LaunchTokenService:
    def create_launch_token(
        self,
        *,
        external_user_id: str,
        display_name: str,
        tenant_id: str,
        user_id_hash: str,
    ) -> str:
        return issue_launch_token(
            external_user_id=external_user_id,
            display_name=display_name,
            tenant_id=tenant_id,
            user_id_hash=user_id_hash,
        )

    def build_redirect_url(self, launch_token: str) -> str:
        return f"{settings.hermanprompt_ui_url}?launch_token={launch_token}"
