from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

def create_engine_and_session(db_url):
    engine = create_engine(
        db_url, connect_args={"check_same_thread": False}
    )

    # each instance of SessionLocal will be a database session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return engine, SessionLocal


settings = get_settings()

engine, SessionLocal = create_engine_and_session(
    db_url=settings.SQLALCHEMY_DATABASE_URL
)

Base = declarative_base()
