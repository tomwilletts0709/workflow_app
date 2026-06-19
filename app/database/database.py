from collections.abc import Generator
import re
from typing import Annotated

from fastapi import Depends
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, declared_attr, sessionmaker

from app.core.settings import get_settings

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

def resolve_table_name(class_name: str) -> str: 
    words = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", class_name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", words).lower()


class Base(DeclarativeBase): 
    metadata = MetaData 

    @declared_attr.directive
    def __tablename__(cls) -> str: 
        return resolve_table_name(cls.__name__)
    

settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def init_db() -> None: 
    Base.metadata.create_all(bind=engine)

def check_db_connection() -> None: 
    with SessionLocal() as session:
        session.execute(text("SELECT 1"))

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try: 
        yield db
    finally: 
        db.close()


db_session = Annotated[Session, Depends(get_db)]
