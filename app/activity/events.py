from typing import Any
from dataclasses import dataclass, field
from app.activity.enums import ActivityType

@dataclass(frozen=True)
class ActivityEvent: 
    project_id: int
    type: ActivityType
    message: str
    task_id: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

