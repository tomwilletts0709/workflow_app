from dataclasses import dataclass, field
from typing import Any


from app.notifications.enums import NotificationType

@dataclass(frozen=True)
class NotificationEvent: 
    title: str
    message: str
    type: NotificationType = NotificationType.INFO
    project_id: int | None = None
    task_id: int | None = None
    data: dict[str, Any] = field(default_factory=dict)

