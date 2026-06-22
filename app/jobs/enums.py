from enum import StrEnum, auto

class JobStatus(StrEnum): 
    PENDING = auto() 
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()

class JobType(StrEnum): 
    GENERATE_PROJECT_SUMMARY = "generate_project_summary"

    