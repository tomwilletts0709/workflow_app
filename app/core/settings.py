
import logging
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

log = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = Field(default="development", validation_alias="ENV")
    database_url: str = Field(validation_alias="DATABASE_URL")
    app_name: str = "Workflow"
    log_level: str = Field(default="WARNING", validation_alias="LOG_LEVEL")

    redis_url: str = Field(default="redis://localhost:6379/", validation_alias="REDIS_URL")
    celery_broker_url: str = Field(default="redis://localhost:6379/", validation_alias="CELERY_RESULT_BACKEND")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
