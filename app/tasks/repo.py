from typing import Protocol

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.tasks.enums import TaskStatus
from app.tasks.models import Task
from app.core.logging import logging
from app.search.repo import SearchRepo

logging = logging.getLogger(__name__)


class TaskRepoProtocol(Protocol): 
    def create(self, name: str, project_id: int | None, type: str, description: str | None) -> Task: 
        ...

    def get_id(self, task_id: int)-> Task | None: 
        ...

    def get_name(self, name: str) -> Task | None: 
        ...

    def update(self, task_id: int, name: str | None, description: str | None) -> Task | None: 
        ...
    
    def delete_id(self, task_id: int) -> bool: 
        ...
    

    def list_all(self) -> list[Task]: 
        ... 

    def search_tasks(self, query: str | None, page: int, page_size: int) -> dict:
        ...

    def autocomplete_search(self, query: str, limit: int = 10) -> list[str]:
        ...

    def update_status(self, task_id: int, status: TaskStatus) -> Task | None: 
        ...

class TaskRepo: 
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.search_repo = SearchRepo(db_session)

    def create(self, name: str, project_id: int | None, type: str, description: str | None) -> Task: 
        task = Task(
            name=name,
            project_id=project_id,
            type=type,
            description=description,
            status=TaskStatus.TODO,
        )
        self.db_session.add(task)
        self.db_session.commit()
        self.db_session.refresh(task)
        return task

    def get_id(self, task_id: int) -> Task | None: 
        return self.db_session.query(Task).filter(Task.id == task_id).one_or_none()

    def get_name(self, name: str) -> Task | None:
        return self.db_session.query(Task).filter(Task.name == name).one_or_none()

    
    def update(self, task_id: int, name: str | None, description: str | None) -> Task | None: 
        statement = select(Task).where(Task.id == task_id)
        task = self.db_session.execute(statement).scalar_one_or_none()

        if task is None: 
            return None

        if name is not None: 
            task.name = name

        if description is not None: 
            task.description = description
       
       
        self.db_session.commit()
        self.db_session.refresh(task)
        return task
    
    def delete_id(self, task_id: int) -> bool: 
        task = self.db_session.query(Task).filter(Task.id == task_id).one_or_none()

        if task is None: 
            return False

        self.db_session.delete(task)
        self.db_session.commit()
        return True

    def list_all(self) -> list[Task]: 
        return self.db_session.query(Task).all()
    
    def search_tasks(self, query: str | None, page: int, page_size: int) -> dict: 
        return self.search_repo.text_search(
            Task, 
            [Task.name, Task.description], 
            query, 
            None, 
            page, 
            page_size
        )
        
    def autocomplete_search(self, query: str, limit: int = 10) -> list[str]: 
        return self.search_repo.autocomplete(
            Task, 
            [Task.name, Task.description],
            Task.name, 
            query, 
            limit
        )
    
    def update_status(self, task_id: int, status: TaskStatus) -> Task | None: 
        statement = select(Task).where(Task.id == task_id)
        task = self.db_session.execute(statement).scalar_one_or_none()

        if task is None: 
            return None
        
        task.status = status

        self.db_session.commit()
        self.db_session.refresh(task)
        return task