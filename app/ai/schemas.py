from typing_extensions import TypedDict
from pydantic import BaseModel

class SummaryState(TypedDict): 
    text: str
    style: str
    prompt: str
    result: str


class ProjectSummaryModel(BaseModel): 
    summary: str
    blockers: str
    suggest_next_steps: list[str]
