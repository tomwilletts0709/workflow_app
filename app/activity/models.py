from datetime import datetime, timezone
from typing import Any

from app.database.database import Base

from pydantic import BaseModel, Field
from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.activity.enums import ActivityType

class Activity(Base): 
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("project.id"), nullable=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"), nullable=False)
    type: Mapped[ActivityType] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(String)
    metadata: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

#pydantic models

class ActivityRead(BaseModel): 
    id: int
    project_id: int | None = None
    task_id: int
    type: ActivityType
    message: str
    metadata: dict[str, Any]
    created_at: datetime = Field(default=datetime.now(timezone.utc))

    model_config = {"from_attributes": True}

class ActivityCreate(BaseModel): 
    project_id: int
    task_id: int
    type: str



