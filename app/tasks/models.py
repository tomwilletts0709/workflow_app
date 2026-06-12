
from datetime import datetime, timezone

from app.database.database import Base
from app.tasks.enums import TaskStatus

from pydantic import BaseModel, Field
from sqlalchemy import String, Integer, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

class Task(Base): 
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    project_id:[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[TaskStatus] = mapped_column(Enum, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"Tasks(id={self.id!r}, name={self.name!r}, status={self.status!r})" 
     
    def __str__(self):
        return f"{self.name} [{self.status.value}]"

#pydantic models

class TaskRead(BaseModel): 
    id: int
    name: str
    description: str | None = Field(min_length=1, max_length=256)
    search_columns: list[str, Any]
    label_column: str 
    type: str
    query: str 
    status: TaskStatus
    created_at: datetime = Field(default=datetime.now(timezone.utc))

class TaskCreate(BaseModel): 
    name: str = Field(min_length=1, max_length=256)
    description: str | None = Field(min_length=1, max_length=256)
    type: str 

class TaskUpdate(BaseModel): 
    name: str | None 
    description: str | None
    status: TaskStatus | None
    


