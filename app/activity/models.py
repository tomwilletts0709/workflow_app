from datetime import datetime, timezone
from typing import Any

from app.database.database import Base

from pydantic import BaseModel, Field
from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.activity.enums import ActivityType

class Activity(Base): 
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("project.id"), nullable=True)
    task_id: Mapped[int | None] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    type: Mapped[ActivityType] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(String)
    data: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

#pydantic models

class ActivityRead(BaseModel): 
    id: int
    project_id: int | None = None
    task_id: int | None = None
    type: ActivityType
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"from_attributes": True}

class ActivityCreate(BaseModel): 
    project_id: int
    task_id: int
    type: str



