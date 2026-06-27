from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.projects.models import ProjectCreate, ProjectRead, ProjectUpdate
from app.projects.repo import ProjectRepo
from app.projects.service import ProjectService


project_router = APIRouter()


def get_project_service(db_session: Session = Depends(get_db)) -> ProjectService:
    repo = ProjectRepo(db_session)
    return ProjectService(repo)


@project_router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
):
    return service.create(
        name=payload.name,
        description=payload.description,
    )


@project_router.get("", response_model=list[ProjectRead])
async def list_projects(service: ProjectService = Depends(get_project_service)):
    return service.list_all()


@project_router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
):
    project = service.get_id(project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project Not Found",
        )
    return project


@project_router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int,
    payload: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
):
    project = service.update(project_id, payload.name, payload.description)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} cannot be found.",
        )
    return project


@project_router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
):
    deleted = service.delete(project_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return None
