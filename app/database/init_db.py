from app.core.config import get_settings
from app.models import User
from app.schemas import UserCreate

from .db import Base, SessionLocal, engine


def init_db():
    # create DB tables (would be better to use Alembic)
    Base.metadata.create_all(bind=engine)

    # create super user
    db_session = SessionLocal()
    settings = get_settings()
    superuser = User.get_by_email(db_session, settings.SUPERUSER_EMAIL)
    if not superuser:
        superuser_create = UserCreate(
            email=settings.SUPERUSER_EMAIL,
            password=settings.SUPERUSER_PASSWORD,
        )
        User.create(db_session, superuser_create, is_verified=True, is_superuser=True)
