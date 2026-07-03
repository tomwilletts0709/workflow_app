from typing import Any
from app.database.database import Base
from app.search.enums import SearchMode

#from sqlalchemy import String, Integer, DateTime
#from sqlalchemy.orm import Session, mapped_column, Mapped
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class SearchResult(BaseModel): 
    type: SearchType
    id: int
    title: str
    description: str | None = None
    created_at: datetime | None = None
    data: dict[str, Any] = Field(default_factory=dict)

class SearchResponse(BaseModel):
    result: list[SearchResult]
    page: int
    page_size: int
    total: int
    has_next: bool
    mode: SearchMode = SearchMode.KEYWORD
    query: str | None = None


