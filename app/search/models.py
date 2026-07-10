from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.search.enums import SearchMode, SearchType


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
