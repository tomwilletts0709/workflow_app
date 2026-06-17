

from app.database.database import Base

from sqlalchemy import String, Integer, Enum
from sqlalchemy.orm import mapped, mapped_column


class Favourites(Base): 
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String)

    