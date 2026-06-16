from sqlalchemy import String, Integer, Enum, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.projects.enums import ProjectStatus

from pydantic import BaseModel, Field
from datetime import datetime, timezone

class Projects(Base): 
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String)
    status: Mapped[ProjectStatus] = mapped_column(Enum, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default= lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_columnn(DateTime, default= lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now())
    

    def __repr__(self):
        return f"Tasks(id={self.id!r}, name={self.name!r}, status={self.status!r})" 
    
    def __str__(self):
        return f"{self.name} [{self.status.value}]"


#Pydantic models

class ProjectCreate(BaseModel): 
    name: str
    description: str | None = None

class ProjectRead(BaseModel): 
    id: int 
    name: str
    description: str | None = None

    model_config = {"from_attributes": True}

class ProjectUpdate(BaseModel): 
    name: str 
    description: str | None = None