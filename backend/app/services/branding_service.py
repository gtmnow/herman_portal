from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.auth import BrandingResponse


class BrandingService:
    def get_branding(self, *, db: Session, tenant_id: str | None) -> BrandingResponse:
        normalized_tenant_id = tenant_id.strip() if tenant_id else None
        config: dict[str, str | None] | None = None
        if normalized_tenant_id:
            config = self._get_config_row(db, normalized_tenant_id)

        return BrandingResponse(
            tenant_id=normalized_tenant_id,
            logo_url=config["logo_url"] if config and config.get("logo_url") else None,
            welcome_message=(
                config["welcome_message"] or settings.default_welcome_message
                if config
                else settings.default_welcome_message
            ),
            portal_base_url=(
                config["portal_base_url"]
                if config and config.get("portal_base_url")
                else settings.portal_ui_url
            ),
        )

    def _get_config_row(self, db: Session, tenant_id: str) -> dict[str, str | None] | None:
        queries = [
            text(
                """
                SELECT tenant_id, portal_base_url, logo_url, welcome_message
                FROM tenant_portal_configs
                WHERE tenant_id = :tenant_id AND is_active = true
                LIMIT 1
                """
            ),
            text(
                """
                SELECT tenant_id, portal_base_url, logo_url, welcome_message
                FROM tenant_portal_configs
                WHERE tenant_id = :tenant_id
                LIMIT 1
                """
            ),
        ]

        for query in queries:
            try:
                row = db.execute(query, {"tenant_id": tenant_id}).mappings().first()
            except Exception:
                continue
            if row is not None:
                return dict(row)

        return None
