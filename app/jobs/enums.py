from enum import StrEnum, auto

class JobStatus(StrEnum): 
    PENDING = auto() 
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()


