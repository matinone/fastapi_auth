from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql import func

from app.database.db import Base
from app.schemas.todo import ToDoCreate, ToDoUpdate


class ToDo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="todos")

    @classmethod
    def create(cls, db: Session, todo_data: ToDoCreate, user_id: int):
        new_todo = ToDo(
            title=todo_data.title,
            description=todo_data.description,
            user_id=user_id,
        )
        db.add(new_todo)
        db.commit()
        db.refresh(new_todo)

        return new_todo

    @classmethod
    def get_multiple(
        cls,
        db: Session,
        user_id: int,
        offset: int = 0,
        limit: int = 100,
        start_datetime=None,
        end_datetime=None,
    ):
        query = db.query(cls).filter(cls.user_id == user_id)
        if start_datetime:
            query = query.filter(cls.time_created >= start_datetime)
        if end_datetime:
            query = query.filter(cls.time_created <= end_datetime)

        return query.offset(offset).limit(limit).all()

    @classmethod
    def get_by_id(cls, db: Session, id: int):
        return db.query(cls).filter(cls.id == id).first()

    @classmethod
    def update(cls, db: Session, current, new: ToDoUpdate | dict[str, Any]):
        if isinstance(new, dict):
            update_data = new
        else:
            # exclude_unset=True to avoid updating to default values
            update_data = new.dict(exclude_unset=True)

        current_data = jsonable_encoder(current)
        for field in current_data:
            if field in update_data:
                setattr(current, field, update_data[field])

        db.add(current)
        db.commit()
        db.refresh(current)

        return current

    @classmethod
    def delete(cls, db: Session, todo):
        db.delete(todo)
        db.commit()

        return todo

    @classmethod
    def delete_by_id(cls, db: Session, id: int):
        todo = cls.get_by_id(db, id)
        db.delete(todo)
        db.commit()

        return todo
