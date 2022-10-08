from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Session

from app.database.db import Base
from app.core.security import verify_password


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    todos = relationship("ToDo", back_populates="user")


    @classmethod
    def get_by_id(cls, db, id):
        return db.query(cls).filter(cls.id == id).first()

    @classmethod
    def get_by_email(cls, db, email):
        return db.query(cls).filter(cls.email == email).first()

    @classmethod
    def authenticate_user(cls, db: Session, email: str, password: str):
        user = cls.get_by_email(db, email=email)
        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user
