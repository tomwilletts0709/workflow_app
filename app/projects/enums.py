

from enum import StrEnum, auto

class ProjectStatus(StrEnum): 
    IN_PROGRESS = auto()
    BLOCKED = auto() 
    COMPLETED = auto()
    CANCELLED = auto()

class ProjectType(StrEnum):
    pass