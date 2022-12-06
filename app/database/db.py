from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings


def create_engine_and_session(db_url):
    if "sqlite" in db_url:
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(db_url)

    # each instance of SessionLocal will be a database session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return engine, SessionLocal


settings = get_settings()

engine, SessionLocal = create_engine_and_session(
    db_url=settings.get_postgres_database_url()
)

Base = declarative_base()
