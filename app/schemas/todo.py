from pydantic import BaseModel, EmailStr


# common properties
class ToDoBase(BaseModel):
    title: str
    description: str | None = None


# properties to receive when creating a todo
class ToDoCreate(ToDoBase):
    pass


# properties stored in the DB
class ToDoInDB(ToDoBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
