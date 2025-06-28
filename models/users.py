from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(primary_key=True)
    username: str = Field(max_length=64, unique=True)
    password_hash: str = Field(max_length=255)
    email: Optional[str] = Field(max_length=255)
    phone: Optional[str] = Field(max_length=20)
    role: str = Field(default="user")
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime
