

from app.projects.repo import ProjectRepo


class ProjectService: 
    def __init__(self, repo: ProjectRepo): 
        self.repo = repo

    def create(self, project_id: int, name: str, description: str | None) -> Projects: 
        return self.repo.create(project_id, name, description)
    
    def get(self, project_id: int) -> Projects | None:
        return self.repo.get(project_id)

    def update(self, project_id: int, name: str) -> Projects: 
        return self.repo.update(project_id, name)
    
    def delete(self, project_id: int) -> bool: 
        return self.repo.delete(project_id)
    
    def list_all(self, project_id:int) -> list[Projects]: 
        return self.repo.list_all(project_id)
    
    