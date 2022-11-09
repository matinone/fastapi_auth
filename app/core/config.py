import secrets
from functools import lru_cache

from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):

    PROJECT_NAME: str = "Simple To-Do API"
    ENVIRONMENT: str = "dev"

    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "postgres"
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DATABASE_URL: str = (
        f"postgresql+psycopg2://"
        f"{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    SQLITE_DATABASE_URL: str = "sqlite:///./sql_dev.db"

    SUPERUSER_EMAIL: EmailStr = "superuser@secretdomain.com"
    SUPERUSER_PASSWORD: str = "secret_password"

    GOOGLE_CLIENT_ID: str = "dummy_id"
    GOOGLE_CLIENT_SECRET: str = "dummy_secret"

    EMAIL_ENABLED: bool = False
    EMAIL_SENDER: str = "noreply@gmail.com"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
