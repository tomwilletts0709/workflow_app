from sqlalchemy import select
from sqlalchemy.orm import Session


from app.jobs.models import Jobs, JobStatus


class JobRepo: 
    def __init__(self, db_session: Session): 
        self.db_session = db_session

    def create(self, type: str, payload: dict) -> Job: 
        job = Job(type=type, payload=payload, status=JobStatus.Pending,)

        self.db_session.add(job)
        self.db_session.commit()
        self.db_session.refresh(job)
        return job
    
    def get(self, job_id: int) -> Job: 
        return self.db_session.query(Jobs).filter(Jobs.id == job_id).one_or_none()

    def update(self, id: int):
        job = self.db_session.query(Jobs).filter(Jobs.id == job_id).one_or_none()

        if job is None: 
            return None

        self.db_session.commit(job)
        self.db_session.refresh()

    def delete(self, id: int) -> None: 







        
    



