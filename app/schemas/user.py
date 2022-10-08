from pydantic import BaseModel, EmailStr

# common properties
class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    is_active: bool = True


# properties to receive when creating a user
class UserCreate(UserBase):
    password: str


# properties stored in the DB
class UserInDB(UserBase):
    id: int
    hashed_password: str

    class Config:
        orm_mode = True
