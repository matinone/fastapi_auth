from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Session

from app.database.db import Base
from app.core.security import verify_password, get_password_hash
from app.schemas.user import UserCreate, UserUpdate


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    todos = relationship("ToDo", back_populates="user")


    @classmethod
    def create(cls, db: Session, user_data: UserCreate):
        new_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    @classmethod
    def get_multiple(cls, db: Session, offset: int = 0, limit: int = 100):
        return db.query(cls).offset(offset).limit(limit).all()

    @classmethod
    def get_by_id(cls, db: Session, id: int):
        return db.query(cls).filter(cls.id == id).first()

    @classmethod
    def get_by_email(cls, db: Session, email: str):
        return db.query(cls).filter(cls.email == email).first()

    @classmethod
    def update(cls, db: Session,
        current, new: UserUpdate | dict[str, Any],
    ):
        if isinstance(new, dict):
            update_data = new
        else:
            # exclude_unset=True to avoid updating to default values
            update_data = new.dict(exclude_unset=True)

        # store the hashed password if it is updated
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(
                update_data["password"]
            )
            update_data.pop("password")

        current_data = jsonable_encoder(current)
        for field in current_data:
            if field in update_data:
                setattr(current, field, update_data[field])

        db.add(current)
        db.commit()
        db.refresh(current)

        return current

    @classmethod
    def delete(cls, db: Session, user):
        db.delete(user)
        db.commit()

        return user

    @classmethod
    def delete_by_id(cls, db: Session, id: int):
        user = cls.get_by_id(db, id)
        db.delete(user)
        db.commit()

        return user

    @classmethod
    def authenticate(cls, db: Session, email: str, password: str):
        user = cls.get_by_email(db, email=email)
        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user
