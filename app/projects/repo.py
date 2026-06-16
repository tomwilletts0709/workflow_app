from typing import Protocol

from app.projects.models import Projects

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.logging import logging


logging = logging.getLogger(__name__)

class ProjectRepoProtocol(Protocol): 
    
    def create(self, project_id: int, name: str, description: str | None) -> Projects: 
        ... 

    def update(self, project_id: int, name: str) -> Projects | None:
        ...

    def get_id(self, project_id: int) -> Projects | None: 
        ... 

    def delete(self, project_id: int) -> bool: 
        ...
    
    def list_all(self) -> list[Projects]: 
        ...


class ProjectRepo: 
    def __init__(self, db_session: Session): 
        self.db_session = db_session

    def create(self, project_id: int, name: str, description: str | None) -> Projects: 
        project = Project(
            project_id = project_id, 
            name = name,
            description = description,
        )
        self.db_session.add(project)
        self.db_session.commit()
        self.db_session.refresh(project)
    
    def update(self, project_id: int, name: str) -> Projects | None:
        statement = select(Project).where(projects.id == project_id)
        result = self.db_session.execute(statement).scalar_one_or_none()

        if result is None: 
            return None
        
        if name is not None: 
            project.name = name

        self.db_session.commit(result) 
        self.db_session.refresh()
    
    def delete(self, project_id: int) -> bool: 
        project = self.db_session.query(Project).filter(Projects.id == project_id).one_or_none()

        if project is None: 
            return False
        
        self.db_session.delete(project)
        self.db_session.refresh()
        return True


    def get_id(self, project_id: int) -> Projects | None: 
        return self.db_session.query(Project).filter(projects.id == project_id).one_or_none()
    
    def list_all(self) -> list[Projects]: 
        return self.db_session.query(Projects).all()

    



