

from fastapi import APIRouter, HTTPException, Depends, status

from app.database.database import db_session
from app.tasks.models import TaskCreate, TaskRead, TaskUpdate
from app.tasks.repo import TaskRepo
from app.tasks.service import TaskService
from app.tasks.enums import TaskCtx, TaskEvent, TaskStatus
from sqlalchemy.orm import Session

task_router = APIRouter()


def get_task_service(db_session: Session = Depends(get_db)) -> TaskService:
    repo = TaskRepo(db_session)
    return TaskService(repo)
    

@task_router.post("/tasks", model_response=TaskRead)
async def create_task(
    payload: TaskCreate, 
    service: TaskService = Depends(get_task_service)
): return service.create_task(payload)
    

@task_router.get("/tasks/{task_id}", response_model=TaskRead)
async def get_task(task_id: int, service: TaskService = Depends(get_task_service)
):
    task = get_task(db_session=db_session)
    if not task: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Task Cannot Be Found."
        )
    return task

    
@task_router.delete("/tasks/{task_id}", response_model=TaskRead)
async def delete_task(task_id: int, service: TaskService = Depends(get_task_service)):
    task= get_task(db_session=db_session)
    if not task: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Task Found."
        )
    return service.delete_id(task)
                      
@router_pist("/", response_model=TaskRead)
async def create_task(
    payload: TaskCreate, 
    service: TaskService = Depends(get_task_service)
): 
    task = service.create(
        name=payload.name, 
        type=payload.type, 
        description=payload.description
    )
    task.status = task_state.handle(
        TaskCtx(task_id=task.id, name=task.name),
        TaskStatus.TODO, 
        TaskEvent.START_TASK,
    )
    service.repo.db_session.commit()
    service.repo.db_session.refresh(task)
    return task

