from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(default="postgresql+psycopg://postgres:postgres@localhost:5432/hermanprompt", alias="DATABASE_URL")
    app_env: str = Field(default="development", alias="APP_ENV")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8010, alias="PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    hermanprompt_ui_url: str = Field(default="http://localhost:5173", alias="HERMANPROMPT_UI_URL")
    hermanprompt_launch_secret: str = Field(default="dev-launch-secret", alias="HERMANPROMPT_LAUNCH_SECRET")
    launch_token_ttl_seconds: int = Field(default=3600, alias="LAUNCH_TOKEN_TTL_SECONDS")
    password_reset_token_ttl_seconds: int = Field(default=1800, alias="PASSWORD_RESET_TOKEN_TTL_SECONDS")
    dev_show_reset_links: bool = Field(default=True, alias="DEV_SHOW_RESET_LINKS")
    cors_allowed_origins_raw: str = Field(
        default="http://localhost:5174,http://127.0.0.1:5174",
        alias="CORS_ALLOWED_ORIGINS",
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins_raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
