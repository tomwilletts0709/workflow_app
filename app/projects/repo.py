from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.logging import logging
from app.projects.models import Project


logging = logging.getLogger(__name__)


class ProjectRepoProtocol(Protocol):
    def create(self, name: str, description: str | None) -> Project:
        ...

    def update(
        self, project_id: int, name: str | None, description: str | None
    ) -> Project | None:
        ...

    def get_id(self, project_id: int) -> Project | None:
        ...

    def delete(self, project_id: int) -> bool:
        ...

    def list_all(self) -> list[Project]:
        ...


class ProjectRepo:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, name: str, description: str | None) -> Project:
        project = Project(name=name, description=description)
        self.db_session.add(project)
        self.db_session.commit()
        self.db_session.refresh(project)
        return project

    def update(
        self, project_id: int, name: str | None, description: str | None
    ) -> Project | None:
        statement = select(Project).where(Project.id == project_id)
        project = self.db_session.execute(statement).scalar_one_or_none()

        if project is None:
            return None

        if name is not None:
            project.name = name

        if description is not None:
            project.description = description

        self.db_session.commit()
        self.db_session.refresh(project)
        return project

    def delete(self, project_id: int) -> bool:
        project = self.db_session.query(Project).filter(Project.id == project_id).one_or_none()

        if project is None:
            return False

        self.db_session.delete(project)
        self.db_session.commit()
        return True

    def get_id(self, project_id: int) -> Project | None:
        return self.db_session.query(Project).filter(Project.id == project_id).one_or_none()

    def list_all(self) -> list[Project]:
        return self.db_session.query(Project).all()
