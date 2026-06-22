

from fastapi import APIRouter, HTTPException, Depends, status

from app.core.pagination import CommonParamsDependency 
from app.database.database import get_db
from app.tasks.models import TaskCreate, TaskRead, TaskUpdate
from app.tasks.repo import TaskRepo
from app.tasks.flows import InvalidTransition
from app.tasks.service import TaskService
from app.tasks.models import TaskCreate, TaskRead, TaskUpdate, TaskTransitionRequest
from sqlalchemy.orm import Session


task_router = APIRouter()


def get_task_service(db_session: Session = Depends(get_db)) -> TaskService:
    repo = TaskRepo(db_session)
    return TaskService(repo)
    

@task_router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate, 
    service: TaskService = Depends(get_task_service)
): return service.create(
    name=payload.name,
    project_id=payload.project_id,
    type=payload.type,
    description=payload.description,
)
    

@task_router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: int, service: TaskService = Depends(get_task_service)
):
    task = service.get_id(task_id)
    if task is None: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Task not found."
        )
    return task

@task_router.get("")
async def list_tasks(params: CommonParamsDependency, service: TaskService = Depends(get_task_service)): 
    return service.task_search(params.query, params.page, params.page_size)

@task_router.patch("/{task_id}", response_model=TaskRead) 
async def update_task(task_id: int, payload: TaskUpdate, service: TaskService = Depends(get_task_service)): 
    task = service.update(task_id, payload.name, payload.description)
    if task is None: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task Not Found.")
    return task
        
    
@task_router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, service: TaskService = Depends(get_task_service)):
    deleted = service.delete_id(task_id)
    if not deleted: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Task Found."
        )
    return None      

@task_router.post("/{task_id}/transition", response_model=TaskRead)
async def transition_task(
    task_id: int, 
    payload: TaskTransitionRequest, 
    service: TaskService = Depends(get_task_service),
):
    try: 
        task = service.transition(task_id, payload.event)
    except InvalidTransition: 
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    if task is None: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Task Not Found.")
    return task