

from app.database.database import Base

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel


class Favourites(Base): 
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String)
    

class FavouritesRead(BaseModel):
    id: int
    

class FavouritesCreate(BaseModel): 
    name: str
    
    