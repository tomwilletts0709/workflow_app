from app.jobs.models import Job
from app.jobs.repo import JobRepo


class JobService:
    def __init__(self, repo: JobRepo): 
        self.repo = repo

    def create(self, type: str, payload: dict) -> Job: 
        return self.repo.create(type, payload)
    
    def get(self, job_id: int)-> Job | None: 
        return self.repo.get(job_id)
    
    def get_next_pending(self) -> Job | None: 
        return self.repo.get_next_pending()
    
    def running(self, job_id: int) -> Job | None: 
        return self.repo.running(job_id)
    
    def completed(self, job_id: int, result: dict) -> Job | None: 
        return self.repo.completed(job_id, result)
    
    def failed(self, job_id: int, error: str) -> Job | None: 
        return self.repo.failed(job_id, error)
    
    