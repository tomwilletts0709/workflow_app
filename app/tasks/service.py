from app.tasks.repo import TaskRepo
from app.tasks.models import Task
from app.tasks.enums import TaskCtx, TaskEvent, task_state




class TaskService: 
    def __init__(self, repo:TaskRepo): 
        self.repo = repo

    def create(self, name: str, project_id: int | None,  type: str, description: str | None) -> Task: 
        return self.repo.create(name, project_id, type, description)

    def get_id(self, task_id: int)->Task | None: 
        return self.repo.get_id(task_id)
    
    def get_name(self, name: str) -> Task | None: 
        return self.repo.get_name(name)

    def update(self, task_id: int, name: str | None, description: str | None)->Task | None:
        return self.repo.update(task_id, name, description)

    def delete_id(self, task_id: int) -> bool: 
        return self.repo.delete_id(task_id)
 
    def list_all(self) -> list[Task]: 
        return self.repo.list_all()
    

    def task_search(self, query: str | None, page: int, page_size: int) -> dict: 
        return self.repo.search_tasks(query, page, page_size)
    
    def autocomplete_search(self, query: str | None, limit: int = 10) -> list[str]: 
        return self.repo.autocomplete_search(query, limit)
    
    def transition(self, task_id: int, event: TaskEvent) -> Task | None: 
        task = self.repo.get_id(task_id)

        if task is None: 
            return None 

        ctx = TaskCtx(task_id=task.id, name=task.name)
        next_status = task_state.handle(ctx, task.status, event)

        return self.repo.update_status(task_id, next_status)
