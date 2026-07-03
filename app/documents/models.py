from datetime import datetime, timezone

from sqlalchemy import String, Integer, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship 
from pydantic import BaseModel, Field
from app.documents.enums import DocuementType
from app.database.database import Base



class Document(Base): 
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    
    type: Mapped[DocumentType] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default = lambda: datetime.now(timezone.utc), nullable=False)


class DocumentRead(BaseModel): 
    id: int
    type: DocumentType
    title: str
    created_at: datetime

    model_config = {"from_attributes": True}

class NotificationCreate(BaseModel): 
    title: str
