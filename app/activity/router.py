from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.activity.models import ActivityRead
from app.activity.repo import ActivityRepo
from app.activity.service import ActivityService
from app.database.database import get_db


activity_router = APIRouter()


def get_activity_service(db_session: Session = Depends(get_db)) -> ActivityService:
    repo = ActivityRepo(db_session)
    return ActivityService(repo)


@activity_router.get("/projects/{project_id}/activity", response_model=list[ActivityRead])
async def list_project(
    project_id: int,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: ActivityService = Depends(get_activity_service),
):
    return service.list_project(project_id, limit, offset)
