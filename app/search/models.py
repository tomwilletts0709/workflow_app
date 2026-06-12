from typing import Any
from typing import datetime, timezone
from app.database.database import Base

from app.search.enums import SearchMode

from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Session

from pydantic import BaseModel, Field


class Search(Base): 
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)

class SearchEvent(Base): 
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    query: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default= lambda: datetine.now(timezone.utc))



#pydantic models

class SearchRequest(BaseModel): 
    id: int
    query: str | None = None

class SearchResult(BaseModel): 
    type: SearchType
    query: str | None = None
    mode: SearchMode = SearchMode.KEYWORD
    filters: dict[str, Any] | None = None
    page: int
    page_size: int


class SearchResponse(BaseModel):
    result: list[SearchResult]
    page: int
    page_size: int
    total: int
    mode: SearchMode = SearchMode.KEYWORD
    query: str | None = None


