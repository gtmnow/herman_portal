from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/hermanprompt",
        validation_alias=AliasChoices("DATABASE_URL", "DATABASE_PUBLIC_URL"),
    )
    app_env: str = Field(default="development", alias="APP_ENV")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8010, alias="PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    hermanprompt_ui_url: str = Field(default="http://localhost:5173", alias="HERMANPROMPT_UI_URL")
    hermanadmin_ui_url: str = Field(
        default="https://hermanprompt-admin-tool-production.up.railway.app/",
        validation_alias=AliasChoices("HERMANADMIN_UI_URL", "HERMAN_ADMIN_UI_URL"),
    )
    portal_ui_url: str = Field(default="http://localhost:5174", alias="PORTAL_UI_URL")
    hermanprompt_launch_secret: str = Field(default="dev-launch-secret", alias="HERMANPROMPT_LAUNCH_SECRET")
    hermanadmin_launch_secret: str = Field(
        default="test-admin-launch-secret",
        validation_alias=AliasChoices("HERMANADMIN_LAUNCH_SECRET", "HERMAN_ADMIN_LAUNCH_SECRET"),
    )
    hermanadmin_launch_issuer: str = Field(
        default="herman_portal_local",
        validation_alias=AliasChoices("HERMANADMIN_LAUNCH_ISSUER", "HERMAN_ADMIN_LAUNCH_ISSUER"),
    )
    hermanadmin_launch_audience: str = Field(
        default="herman_admin",
        validation_alias=AliasChoices("HERMANADMIN_LAUNCH_AUDIENCE", "HERMAN_ADMIN_LAUNCH_AUDIENCE"),
    )
    hermanadmin_launch_token_use: str = Field(
        default="admin_launch",
        validation_alias=AliasChoices("HERMANADMIN_LAUNCH_TOKEN_USE", "HERMAN_ADMIN_LAUNCH_TOKEN_USE"),
    )
    launch_token_ttl_seconds: int = Field(default=3600, alias="LAUNCH_TOKEN_TTL_SECONDS")
    portal_session_cookie_name: str = Field(default="herman_portal_session", alias="PORTAL_SESSION_COOKIE_NAME")
    portal_session_ttl_seconds: int = Field(default=43200, alias="PORTAL_SESSION_TTL_SECONDS")
    portal_session_secure: bool = Field(default=False, alias="PORTAL_SESSION_SECURE")
    portal_session_same_site: str = Field(default="lax", alias="PORTAL_SESSION_SAME_SITE")
    admin_mfa_code_ttl_seconds: int = Field(default=600, alias="ADMIN_MFA_CODE_TTL_SECONDS")
    admin_mfa_verified_ttl_seconds: int = Field(default=900, alias="ADMIN_MFA_VERIFIED_TTL_SECONDS")
    admin_mfa_max_attempts: int = Field(default=5, alias="ADMIN_MFA_MAX_ATTEMPTS")
    resend_api_key: str | None = Field(default=None, alias="RESEND_API_KEY")
    resend_api_base_url: str = Field(default="https://api.resend.com", alias="RESEND_API_BASE_URL")
    admin_mfa_from_email: str = Field(default="onboarding@resend.dev", alias="ADMIN_MFA_FROM_EMAIL")
    admin_mfa_from_name: str = Field(default="Herman Portal", alias="ADMIN_MFA_FROM_NAME")
    admin_mfa_reply_to: str | None = Field(default=None, alias="ADMIN_MFA_REPLY_TO")
    dev_show_mfa_codes: bool = Field(default=True, alias="DEV_SHOW_MFA_CODES")
    password_reset_token_ttl_seconds: int = Field(default=1800, alias="PASSWORD_RESET_TOKEN_TTL_SECONDS")
    invitation_token_fallback_ttl_seconds: int = Field(default=604800, alias="INVITATION_TOKEN_FALLBACK_TTL_SECONDS")
    dev_show_reset_links: bool = Field(default=True, alias="DEV_SHOW_RESET_LINKS")
    default_welcome_message: str = Field(
        default="Welcome to Herman Prompt. Please login to begin.",
        alias="DEFAULT_WELCOME_MESSAGE",
    )
    cors_allowed_origins_raw: str = Field(
        default="http://localhost:5174,http://127.0.0.1:5174",
        alias="CORS_ALLOWED_ORIGINS",
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins_raw.split(",") if origin.strip()]

    @property
    def sqlalchemy_database_url(self) -> str:
        return _normalize_database_url(self.database_url)

    @property
    def effective_portal_session_same_site(self) -> str:
        configured = self.portal_session_same_site.strip().lower()
        if configured in {"lax", "strict", "none"}:
            if self.app_env.lower() == "production" and configured == "lax":
                return "none"
            return configured
        return "none" if self.app_env.lower() == "production" else "lax"

    @property
    def effective_portal_session_secure(self) -> bool:
        return self.portal_session_secure or self.app_env.lower() == "production"

    @property
    def allow_dev_mfa_codes(self) -> bool:
        return self.dev_show_mfa_codes and self.app_env.lower() != "production"

    @property
    def allow_dev_reset_links(self) -> bool:
        return self.dev_show_reset_links and self.app_env.lower() != "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def _normalize_database_url(raw_url: str) -> str:
    if raw_url.startswith("postgresql+"):
        return raw_url
    if raw_url.startswith("postgresql://"):
        return raw_url.replace("postgresql://", "postgresql+psycopg://", 1)
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql+psycopg://", 1)
    return raw_url
