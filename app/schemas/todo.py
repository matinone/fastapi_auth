from pydantic import BaseModel


# common properties
class ToDoBase(BaseModel):
    title: str
    description: str | None = None

    class Config:
        orm_mode = True


# properties to receive when creating a todo
class ToDoCreate(ToDoBase):
    pass


# properties to receive when updating a todo
class ToDoUpdate(ToDoBase):
    title: str | None = None


# properties stored in the DB
class ToDoOut(ToDoBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
