from sqlalchemy import select
from sqlalchemy.orm import Session

from app.notifications.models import Notification
from app.notifications.events import NotificationEvent

class NotificationRepo: 
    def __init__(self, db_session: Session): 
        self.db_session = db_session

    
    def create(self, event: NotificationEvent) -> Notification:
        notofication = Notification(
            title = event.title,
            message=event.message,
            project_id = event.project_id,
            task_id=event.task_id,
            type=event.type,
            data=event.data,
        )

        self.db_session.add(notification)
        self.db_session.commit()
        self.db_session.refresh(notification)
        return Notification
    
    def list_all_by_project(self, project_id: int, limit: int = 10, offset: int = 10) -> Notification | None: 
        return self.db_session.query(Notification).filter(Notification.id == project_id).one_or_none()
    

    def delete(self, notification_id: int)-> bool: 
        notification = self.db_session.query(Notification).filter(Notification.id == notification_id)

        if notification is None: 
            return False

        self.db_session.delete(notification)
        self.db_session.commit()
        return True
