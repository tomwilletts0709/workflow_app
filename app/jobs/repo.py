from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.jobs.enums import JobStatus
from app.jobs.models import Job


class JobRepo:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, type: str, payload: dict) -> Job:
        job = Job(type=type, payload=payload, status=JobStatus.PENDING)

        self.db_session.add(job)
        self.db_session.commit()
        self.db_session.refresh(job)
        return job

    def get(self, job_id: int) -> Job | None:
        return self.db_session.query(Job).filter(Job.id == job_id).one_or_none()

    def get_next_pending(self) -> Job | None:
        return (
            self.db_session.query(Job)
            .filter(Job.status == JobStatus.PENDING)
            .order_by(Job.created_at)
            .first()
        )

    def running(self, job_id: int) -> Job | None:
        job = self.get(job_id)

        if job is None:
            return None

        job.status = JobStatus.RUNNING
        self.db_session.commit()
        self.db_session.refresh(job)
        return job

    def completed(self, job_id: int, result: dict) -> Job | None:
        job = self.get(job_id)

        if job is None:
            return None

        job.status = JobStatus.COMPLETED
        job.result = result
        job.completed_at = datetime.now(timezone.utc)
        self.db_session.commit()
        self.db_session.refresh(job)
        return job

    def failed(self, job_id: int, error: str) -> Job | None:
        job = self.get(job_id)
        if job is None:
            return None

        job.status = JobStatus.FAILED
        job.error = error
        job.completed_at = datetime.now(timezone.utc)
        self.db_session.commit()
        self.db_session.refresh(job)
        return job
