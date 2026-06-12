
from functools import lru_cache

import logging
from starlette.config import Config
from pydantic_settings import SettingsConfigDict, BaseSettings

log = logging.getLogger(__name__)
config = Config(".env")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    ENV: str = "development"
    DB_URL: str
    app_name: str = "Document Processor"

    #Logging
    LOG_LEVEL = config("LOG_LEVEL", default=logging.WARNING)

    #Database
    DATABASE_NAME = config("DATABASE_NAME", default='workflow')
    DATABASE_PORT = config("DATABASE_PORT", default="5432")
    DATABASE_HOSTNAME = config("DATABASE_HOSTNAME")
    DATABASE_CREDENTIALS = config("DATABASE_CREDENTIALS")
    SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2//:postgres:workflow@postgres5432/worflow"


@lru_cache()
def get_settings() -> "Settings":
    return Settings()
