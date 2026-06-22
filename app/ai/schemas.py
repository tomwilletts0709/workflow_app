from typing_extensions import TypedDict


class SummaryState(TypedDict): 
    text: str
    style: str
    prompt: str
    result: str

