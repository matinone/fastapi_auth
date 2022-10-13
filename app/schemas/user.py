from pydantic import BaseModel, EmailStr

# common properties
class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


# properties to receive when creating a user
class UserCreate(UserBase):
    password: str

# properties to use to update a user (all optional)
class UserUpdate(UserBase):
    email: EmailStr | None = None
    password: str | None = None


# properties to return from APIs
class User(UserBase):
    id: int
    is_active: bool = True

    class Config:
        orm_mode = True
