from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.jobs.models import JobCreate, JobRead
from app.jobs.service import JobService
from app.jobs.repo import JobRepo

job_router = APIRouter()

def get_job_service(db_session: Session = Depends(get_db)) -> JobService: 
    repo = JobRepo(db_session)
    return JobService(repo)


@job_router.post("", response_model=JobRead)
async def create(
    payload: JobCreate,
    service: JobService = Depends(get_job_service)
):
    return service.create(payload.type, payload.payload)

@job_router.get("/{job_id}", response_model=JobRead)
async def get_job(
    job_id: int, 
    service: JobService = Depends(get_job_service)
): 
    job = service.get(job_id)
    if job is None: 
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Job Not Found."
        )
    return job



