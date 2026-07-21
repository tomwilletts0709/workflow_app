from datetime import datetime, timezone

from sqlalchemy import select
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

    def get(self, notification_id: int) -> Notification | None:
        return self.db_session.get(Notification, notification_id)

    def list_all_by_project(
        self,
        project_id: int,
        limit: int = 10,
        offset: int = 0,
        unread_only: bool = False,
    ) -> list[Notification]:
        statement = select(Notification).where(Notification.project_id == project_id)

        if unread_only:
            statement = statement.where(Notification.is_read.is_(False))

        statement = (
            statement.order_by(Notification.created_at.desc(), Notification.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db_session.execute(statement).scalars().all())

    def mark_read(self, notification_id: int) -> Notification | None:
        notification = self.get(notification_id)
        if notification is None:
            return None

        if not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.now(timezone.utc)
            self.db_session.commit()
            self.db_session.refresh(notification)

        return notification

    def mark_all_read(self, project_id: int) -> int:
        statement = select(Notification).where(
            Notification.project_id == project_id,
            Notification.is_read.is_(False),
        )
        notifications = list(self.db_session.execute(statement).scalars().all())

        if not notifications:
            return 0

        read_at = datetime.now(timezone.utc)
        for notification in notifications:
            notification.is_read = True
            notification.read_at = read_at

        self.db_session.commit()
        return len(notifications)

    def delete(self, notification_id: int) -> bool:
        notification = self.get(notification_id)
        if notification is None:
            return False

        self.db_session.delete(notification)
        self.db_session.commit()
        return True
    
    def send(self, event: NotificationEvent) -> Notification: 
        return self.create(event)
