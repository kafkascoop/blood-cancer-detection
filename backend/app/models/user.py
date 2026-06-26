from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6)
    full_name: str = Field(min_length=1, max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserInDB(BaseModel):
    id: str
    email: str
    username: str
    hashed_password: str
    full_name: str
    created_at: datetime
    updated_at: datetime
