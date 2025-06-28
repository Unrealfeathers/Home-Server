from typing import TypeVar, Generic, List

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedRequest(BaseModel):
    page: int
    size: int


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    page: int
    size: int
    total: int
    total_pages: int
