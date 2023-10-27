from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    email: str
    password: str


class UserCreate(UserBase):
    is_admin: bool


class UserUpdateIn(BaseModel):
    email: str
    is_admin: bool


class UserUpdate(UserUpdateIn):
    model_config = ConfigDict(from_attributes=True)

    id: int


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
