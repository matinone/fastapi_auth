from pydantic import BaseSettings

import secrets
from functools import lru_cache


class Settings(BaseSettings):

    PROJECT_NAME: str = "Simple To-Do API"
    ENVIRONMENT: str = "test"

    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./test.db"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
