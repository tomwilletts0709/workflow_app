from celery import Celery

from app.core.settings import get_settings
from app.database.database import SessionLocal
from app.jobs.repo import JobRepo

settings = get_settings()

celery_app = Celery(
    "workflow",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)


@celery_app.task(name="jobs.process")
def process_job(job_id: int) -> dict:
    with SessionLocal() as db_session:
        repo = JobRepo(db_session)

        job = repo.running(job_id)
        if job is None:
            return {"status": "missing", "job_id": job_id}

        try:
            result = {
                "message": "job processed successfully",
                "job_id": job_id,
                "type": job.type,
            }
            repo.completed(job_id, result)
            return result
        except Exception as exc:
            repo.failed(job_id, str(exc))
            raise
