from typing import Any

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session


class BaseCrudModel:
    @classmethod
    def get_by_id(cls, db: Session, id: int):
        return db.query(cls).filter(cls.id == id).first()

    @classmethod
    def update(cls, db: Session, current, new: BaseModel | dict[str, Any]):
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
    def delete(cls, db: Session, db_obj):
        db.delete(db_obj)
        db.commit()

        return db_obj

    @classmethod
    def delete_by_id(cls, db: Session, id: int):
        db_obj = cls.get_by_id(db, id)
        db.delete(db_obj)
        db.commit()

        return db_obj
