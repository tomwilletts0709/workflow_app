from app.jobs.models import Job
from app.jobs.repo import JobRepo
from app.jobs.enums import JobType


class JobError(Exception): 
    pass

class JobNotFound(Exception): 
    pass

class UnsupportedJobType(Exception): 
    pass

class InvalidJobType(Exception): 
    pass
 


class JobService:
    def __init__(self, repo: JobRepo): 
        self.repo = repo

    def create(self, type: str, payload: dict) -> Job: 

        if type == JobType.GENERATE_PROJECT_SUMMARY: 
            if "project_id" not in payload: 
                raise InvalidJobType("generate_project_summary requires project_id")

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
    
