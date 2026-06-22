from sqlalchemy import select
from sqlalchemy.orm import Session 

from app.activity.models import Activty
from app.activity.events import ActivityEvent

class ActivityRepo: 
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, event: ActivityEvent) -> Activity: 
        activity = Activity(project_id=event.project_id, 
                            task_id=event.task_id, 
                            type=event.type, 
                            message=event.message, 
                            metadata=event.metadata
                            )
        
        self.db_session.add(activity)
        self.db_session.commit()
        self.db_session.refresh(activity)
        return activity
    
    def list_project(self, project_id: int, limit: int=50, offset:int=50)->list[Activty]: 
        statement = (
            select(Activty)
            .where(Activty.project_id == project_id)
            .order_by(Activity.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db_session.execute(statement)scalars.all())
    
    

