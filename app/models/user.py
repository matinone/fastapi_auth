from typing import Any

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql import func

from app.core.security import get_password_hash, verify_password
from app.database.db import Base
from app.schemas.user import UserCreate, UserUpdate

from .base_crud_model import BaseCrudModel


class User(Base, BaseCrudModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())

    todos = relationship("ToDo", back_populates="user", cascade="delete, delete-orphan")

    @classmethod
    def create(
        cls,
        db: Session,
        user_data: UserCreate,
        is_verified: bool = False,
        is_superuser: bool = False,
    ):
        new_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            is_verified=is_verified,
            is_superuser=is_superuser,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    @classmethod
    def get_multiple(cls, db: Session, offset: int = 0, limit: int = 100):
        return db.query(cls).offset(offset).limit(limit).all()

    @classmethod
    def get_by_email(cls, db: Session, email: str):
        return db.query(cls).filter(cls.email == email).first()

    @classmethod
    def update(
        cls,
        db: Session,
        current,
        new: UserUpdate | dict[str, Any],
    ):
        if isinstance(new, dict):
            update_data = new
        else:
            # exclude_unset=True to avoid updating to default values
            update_data = new.dict(exclude_unset=True)

        # store the hashed password if it is updated
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data["password"])
            update_data.pop("password")

        return BaseCrudModel.update(db, current=current, new=update_data)

    @classmethod
    def authenticate(cls, db: Session, email: str, password: str):
        user = cls.get_by_email(db, email=email)
        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user
