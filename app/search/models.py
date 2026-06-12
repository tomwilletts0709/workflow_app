from typing import Optional
from typing import datetime, timezone
from app.database.database import Base

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

class SearchRead(BaseModel): 
    id: int


