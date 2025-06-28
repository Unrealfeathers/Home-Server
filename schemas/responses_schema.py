from datetime import datetime
from typing import Optional, TypeVar, Generic

from pydantic import BaseModel
from sqlmodel import Field

T = TypeVar("T")


class Responses(BaseModel, Generic[T]):
    status_code: int = 0
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Optional[T] = None


class Token(BaseModel):
    access_token: str
    token_type: str
