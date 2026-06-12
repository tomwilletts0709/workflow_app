from app.tasks.repo import TaskRepo
from app.tasks.models import Task



class TaskService: 
    def __init__(self, repo:TaskRepo): 
        self.repo = repo

    def create(self, name: str, type: str, description: str | None) -> Task: 
        return self.repo.create(name, type, description)

    def get_id(self, task_id: int, name: str, description: str | None, type: str, status: TaskStatus)->Tasks: 
        return self.repo.get_id(task_id)
    
    def get_all(self, task_id: int, name: str, description: str | None, type: str, status: TaskStatus) -> Tasks: 
        return self.repo.get_all()

    def get_name(self, task_id: int, name: str) -> Tasks: 
        return self.repo.get_name(name)

    def update(self, name:str, description: str | None, type: str, status: TaskStatus)->Tasks:
        return self.repo.update(name)

    def delete_id(self, task_id: int) -> None: 
        task = self.repo.get_id(task_id)

        if task is None: 
            raise ValueError("No Task Found.")
        
        if task.status == "deleted": 
            return False

        return self.repo.delete_id(task_id, "deleted")
    
    def delete_name(self, name: str) -> None: 
        task = self.repo.get_name(name)
         
        if task is None: 
            raise ValueError("No Task Found.")
        
        if task.status == "deleted":
            return False
        
        return self.repo.delete_name(name, "deleted")

    def list_all(self) -> list[Tasks]: 
        return self.repo.list_all()
    

