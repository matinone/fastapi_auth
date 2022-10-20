import secrets
from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):

    PROJECT_NAME: str = "Simple To-Do API"
    ENVIRONMENT: str = "dev"

    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./sql_dev.db"

    GOOGLE_CLIENT_ID: str = "dummy_id"
    GOOGLE_CLIENT_SECRET: str = "dummy_secret"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
