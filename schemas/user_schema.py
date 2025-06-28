from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlmodel import Field


class UserRegister(BaseModel):
    username: str = Field(max_length=64, unique=True)
    password: str = Field(max_length=255)


class UserLogin(BaseModel):
    username: str = Field(max_length=64, unique=True)
    password: str = Field(max_length=255)


class UserAdd(BaseModel):
    username: str = Field(max_length=64, unique=True)
    password: str = Field(max_length=255)
    email: Optional[str] = Field(max_length=255)
    phone: Optional[str] = Field(max_length=20)
    role: str = Field(max_length=6)


class UserUpdate(BaseModel):
    id: int
    username: str = Field(max_length=64)
    email: Optional[str] = Field(max_length=255,default=None)
    phone: Optional[str] = Field(max_length=20,default=None)
    role: str = Field(max_length=6)


class UserList(BaseModel):
    id: int
    username: str = Field(max_length=64)
    email: Optional[str] = Field(max_length=255)
    phone: Optional[str] = Field(max_length=20)
    role: str = Field(max_length=6)
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class UserSearch(BaseModel):
    username: Optional[str] = Field(max_length=64, default=None)
    role: Optional[str] = Field(max_length=6, default=None)


class UserInfo(BaseModel):
    username: str = Field(max_length=64, unique=True)
    email: Optional[str] = Field(max_length=255)
    phone: Optional[str] = Field(max_length=20)
    role: str = Field(max_length=6)


class UserPasswordUpdate(BaseModel):
    password: str = Field(max_length=255)
    new_password: str = Field(max_length=255)
    re_password: str = Field(max_length=255)
