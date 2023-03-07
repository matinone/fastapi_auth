from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql import func

from app.database.db import Base
from app.schemas.todo import ToDoCreate

from .base_crud_model import BaseCrudModel


class ToDo(Base, BaseCrudModel):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    done = Column(Boolean, default=False)
    time_done = Column(DateTime(timezone=True))
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
        start_datetime: datetime = None,
        end_datetime: datetime = None,
        done: bool = None,
    ):
        query = db.query(cls).filter(cls.user_id == user_id)
        if done is not None:
            query = query.filter(cls.done == done)
        if start_datetime:
            query = query.filter(cls.time_created >= start_datetime)
        if end_datetime:
            query = query.filter(cls.time_created <= end_datetime)

        return query.offset(offset).limit(limit).all()
