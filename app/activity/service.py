from app.activity.enums import ActivityType                                                                                                                                             
from app.activity.events import ActivityEvent                                                                                                                                           
from app.activity.models import Activity                                                                                                                                                
from app.activity.repo import ActivityRepo                                                                                                                                              
from app.tasks.enums import TaskStatus                                                                                                                                                  
from app.tasks.models import Task                                                                                                                                                       
                                             
                                             
class ActivityService: 
    def __init__(self, repo: ActivityRepo): 
        self.repo = repo

    def create(self, event: ActivityEvent)-> Activity: 
        return self.repo.create(event)
    
    def list_project(self, project_id: int, limit: int=50, offset: int=0)-> list[Activity]: 
        return self.repo.list_project(project_id, limit, offset)
    
    def task_created(self, task: Task) -> Activity: 
        event = ActivityEvent(
            project_id=task.project_id 
            task_id=event.task_id, 
            type = ActivityType.TASK_CREATED, 
            message=f"Task '{task.name} was created", 
            metadata={
                "task_id": task.id, 
                "task_name": task.name, 
                "task_status": task.status,
            },
        )
        return self.create(event)
    
    def task_status_changed(self, task: Task, old_status: TaskStatus, new_status: TaskStatus) -> Activity: 
        event= ActivityEvent(
            project_id=task.project_id 
            task_id=task.id, 
             type = ActivityType.TASK_CREATED, 
            message=f"Task '{task.name} was created", 
            metadata={
                "task_id": task.id, 
                "task_name": task.name, 
                "task_status": task.status,
            },
        )
        return self.create(event)
    
