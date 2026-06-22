from fastapi import APIRouter, Depends, status, HTTPException

from app.projects.service import ProjectService
from app.projects.repo import ProjectRepo
from app.projects.models import ProjectRead, ProjectCreate, ProjectUpdate
from app.projects.enums import ProjectStatus


from app.database.database import get_db
from sqlalchemy.orm import Session

project_router = APIRouter()

def get_project_service(db_session: Session=Depends(get_db)) -> ProjectService:
    repo = ProjectRepo(db_session)
    return ProjectService(repo)


@project_router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate, 
    service: ProjectService = Depends(get_project_service)
): 
    return service.create(
        project_id=payload.project_id,
        name=payload.name,
        description=payload.description,
        )

@project_router.get("/{project_id}", response_model=ProjectRead)
async def get(project_id: int, service: ProjectService = Depends(get_project_service)): 
    project = service.get(project_id)
    if project is None: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project Not Found"
        )
    return project

@project_router.patch("/{project_id}", response_model=ProjectCreate)
async def update(project_id: int, name: str, service: ProjectService = Depends(get_project_service)
): 
    project = service.update(project_id, payload.name, payload.description)
    if project is None: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {name} cannot be found."
        )
    return project

@project_router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int, service: ProjectService=Depends(get_project_service)
):
    deleted = service.delete(project_id)
    if not deleted: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )
    return None