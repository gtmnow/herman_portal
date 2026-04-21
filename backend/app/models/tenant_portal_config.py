from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TenantPortalConfig(Base):
    __tablename__ = "tenant_portal_configs"

    tenant_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    portal_base_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    welcome_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
