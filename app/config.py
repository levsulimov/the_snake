from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql+asyncpg://unibot:unibot@localhost:5432/unibot"
    redis_url: str = "redis://localhost:6379/0"
    max_token: str = ""
    max_webhook_url: str = ""
    max_webhook_secret: str = ""
    max_api_base_url: str = "https://platform-api.max.ru"
    admin_max_user_ids: str = ""

    @property
    def admin_ids(self) -> set[int]:
        return {int(value.strip()) for value in self.admin_max_user_ids.split(",") if value.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
