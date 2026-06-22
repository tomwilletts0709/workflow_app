from enum import StrEnum, auto

class Activity(StrEnum):
    PROJECT_CREATED = auto()
    TASK_CREATED = auto()
    TASK_STATUS = auto()
    AI_RUN_REQUESTED = auto()
    AI_RUN_COMPLETED = auto()
    AI_RUN_FAILED = auto()