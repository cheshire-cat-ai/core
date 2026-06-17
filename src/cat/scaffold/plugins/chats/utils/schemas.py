from uuid import UUID
from datetime import datetime
from typing import List, TypeVar, Generic

from pydantic import BaseModel


T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: List[T]
    cursor: str | None = None


class CRUDSelect(BaseModel):
    id: UUID
    name: str
    updated_at: datetime


class CRUDUpdate(BaseModel):
    name: str = "No name"
