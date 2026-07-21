from app.notifications.events import NotificationEvent
from app.notifications.models import Notification
from app.notifications.repo import NotificationRepo


class NotificationService:
    def __init__(self, repo: NotificationRepo):
        self.repo = repo

    def create(self, event: NotificationEvent) -> Notification:
        return self.repo.create(event)

    def get(self, notification_id: int) -> Notification | None:
        return self.repo.get(notification_id)

    def list_project(
        self,
        project_id: int,
        limit: int = 10,
        offset: int = 0,
        unread_only: bool = False,
    ) -> list[Notification]:
        return self.repo.list_all_by_project(
            project_id=project_id,
            limit=limit,
            offset=offset,
            unread_only=unread_only,
        )

    def mark_read(self, notification_id: int) -> Notification | None:
        return self.repo.mark_read(notification_id)

    def mark_project_read(self, project_id: int) -> int:
        return self.repo.mark_all_read(project_id)

    def delete(self, notification_id: int) -> bool:
        return self.repo.delete(notification_id)
