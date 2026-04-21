from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.tenant_portal_config import TenantPortalConfig
from app.schemas.auth import BrandingResponse


class BrandingService:
    def get_branding(self, *, db: Session, tenant_id: str | None) -> BrandingResponse:
        config = None
        normalized_tenant_id = tenant_id.strip() if tenant_id else None
        if normalized_tenant_id:
            config = db.execute(
                select(TenantPortalConfig).where(
                    TenantPortalConfig.tenant_id == normalized_tenant_id,
                    TenantPortalConfig.is_active.is_(True),
                )
            ).scalar_one_or_none()

        return BrandingResponse(
            tenant_id=normalized_tenant_id,
            logo_url=config.logo_url if config and config.logo_url else None,
            welcome_message=(
                config.welcome_message or settings.default_welcome_message
                if config
                else settings.default_welcome_message
            ),
            portal_base_url=config.portal_base_url if config and config.portal_base_url else settings.portal_ui_url,
        )
