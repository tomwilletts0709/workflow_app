from typing import Protocol

from sqlalchemy.orm import Session
from sqlalchemy import select, or_

from app.database.service import db_session
from app.tasks.enums import TaskStatus
from app.tasks.models import Task
from app.core.logging import logging

logging = logging.getLogger(__name__)


class TasksRepoProtocol(Protocol): 
    def create(self, name: str, type: str, description: str | None) -> Tasks: 
        ...

    def get_id(self, task_id: int, name: str, description: str | None, type: str, status: TaskStatus)->Tasks: 
        ...
    
    def get_all(self, task_id: int, name: str, description: str | None, type: str, status: TaskStatus) -> Tasks: 
        ...

    def get_name(self, task_id: int, name: str) -> Tasks: 
        ...

    def update(self, name:str, description: str | None, type: str, status: TaskStatus)->Tasks:
        ...
    
    def delete_id(self, task_id: int) -> None: 
        ...
    
    def delete_name(self, name: str) -> None: 
        ...

    def list_all(self) -> list[Tasks]: 
        ... 



class TaskRepo: 
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, name: str, type: str, description: str | None) -> Tasks: 
        task = Task(
            name=name,
            type=type,
            description=description,
            status=TaskStatus.TODO,
        )
        self.db_session.add(task)
        self.db_session.commit()
        self.db_session.refresh(task)
        return task

    def get_id(self, task_id: int, name: str, description: str | None, status: TaskStatus) -> Tasks: 
        return self.db_session.query(Task).filter(Task.id == task_id).one_or_none()

    def get_all(self, task_id: int, name: str, descriptions: str | None, type: str, status: TaskStatus) -> Tasks: 
        return self.db_session.query(Task).filter(Task.id == task_ud)
    
    def get_name(self, task_id: int, name: str) -> Tasks | None:
        return self.db_session.query(Task).filter(Task.name == name).one_or_none()

    
    def update(self, name: str, description: str | None, status: TaskStatus) -> Tasks: 
        statement = select(Task).where(Task.id == task_id)
        result = self.db_session.execute(statement).scalar_one_or_none()

        if statement is None: 
            raise ValueError(f"Cannot Update Task")

        result.name = name
        result.description = description
        result.status = status

        self.db_session.commit()
        self.db_session.refresh(result)
        return result
    
    def delete_id(self, task_id: str) -> None: 
        task = self.db_session.query(Task).filter(Task.id == task_id).one()
        self.db_session.delete(task)
        self.db_session.commit()

    def delete_name(self, name: str) -> None: 
        task = self.db_session.query(Task).filter(Task.name == name).one()
        self.db_session.delete(task)
        self.db_sessionl.commit()

    def list_all(self) -> list[Tasks]: 
        return self.db_session.query(Task).all()
    
