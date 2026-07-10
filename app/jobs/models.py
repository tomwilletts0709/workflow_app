from typing import Any
from datetime import datetime, timezone

from pydantic import BaseModel, Field
from sqlalchemy import String, Integer, Enum, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.jobs.enums import JobStatus
from app.database.database import Base



class Job(Base): 
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    result: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default= lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


    def __repr__(self):
        return f"Jobs(id={self.id!r}, type={self.type!r})"
    
    def __str__(self): 
        return f"{self.id}"

#pydantic models

class JobCreate(BaseModel): 
    type: str
    payload: dict[str, Any] = Field(default_factory=dict)


class JobRead(BaseModel): 
    id: int
    type: str
    status: JobStatus
    payload: dict[str, Any]
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}