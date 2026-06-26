from enum import StrEnum, auto

class ActivityType(StrEnum):
    PROJECT_CREATED = auto()
    TASK_CREATED = auto()
    TASK_STATUS_CHANGED = auto()
    AI_RUN_REQUESTED = auto()
    AI_RUN_COMPLETED = auto()
    AI_RUN_FAILED = auto()