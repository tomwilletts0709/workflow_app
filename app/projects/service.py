from app.projects.models import Project
from app.projects.repo import ProjectRepo


class ProjectService:
    def __init__(self, repo: ProjectRepo):
        self.repo = repo

    def create(self, name: str, description: str | None) -> Project:
        return self.repo.create(name, description)

    def get_id(self, project_id: int) -> Project | None:
        return self.repo.get_id(project_id)

    def update(
        self, project_id: int, name: str | None, description: str | None
    ) -> Project | None:
        return self.repo.update(project_id, name, description)

    def delete(self, project_id: int) -> bool:
        return self.repo.delete(project_id)

    def list_all(self) -> list[Project]:
        return self.repo.list_all()
