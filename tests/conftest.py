import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base
import app.activity.models  # noqa: F401 - registers activity tables with Base.metadata
import app.documents.models  # noqa: F401 - registers document tables with Base.metadata
import app.favourites.models  # noqa: F401 - registers favourite tables with Base.metadata
import app.jobs.models  # noqa: F401 - registers job tables with Base.metadata
import app.notifications.models  # noqa: F401 - registers notification tables with Base.metadata
import app.projects.models  # noqa: F401 - registers project tables with Base.metadata
import app.tasks.models  # noqa: F401 - registers task tables with Base.metadata


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as session:
        yield session

    Base.metadata.drop_all(bind=engine)
