from sqlalchemy.orm import Session

from app.notifications.events import NotificationEvent
from app.notifications.models import Notification


class NotificationRepo:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, event: NotificationEvent) -> Notification:
        notification = Notification(
            title=event.title,
            message=event.message,
            project_id=event.project_id,
            task_id=event.task_id,
            type=event.type,
            data=event.data,
        )

        self.db_session.add(notification)
        self.db_session.commit()
        self.db_session.refresh(notification)
        return notification

    def list_all_by_project(
        self,
        project_id: int,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Notification]:
        return (
            self.db_session.query(Notification)
            .filter(Notification.project_id == project_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def delete(self, notification_id: int) -> bool:
        notification = (
            self.db_session.query(Notification)
            .filter(Notification.id == notification_id)
            .one_or_none()
        )

        if notification is None:
            return False

        self.db_session.delete(notification)
        self.db_session.commit()
        return True
