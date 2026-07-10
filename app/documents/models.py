from datetime import datetime, timezone

from pydantic import BaseModel, Field
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.documents.enums import DocumentType


class Document(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    type: Mapped[DocumentType] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class DocumentRead(BaseModel):
    id: int
    type: DocumentType
    title: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentCreate(BaseModel):
    type: DocumentType
    title: str = Field(min_length=1, max_length=256)
