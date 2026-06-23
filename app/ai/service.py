from app.ai.schemas import SummaryState
from app.ai.graph import run_summary_graph


def summarise_text(text: str, style: str = "concise") -> SummaryState: 
    return run_summary_graph(text=text, style=style)

def summarise_bullets(text:str, style: str="bullets") -> SummaryState: 
    return run_summary_graph(text=text, style=style)

def detailed_text(text: str, style: str="detailed")->SummaryState: 
    return run_summary_graph(text=text, style=style)

def summarise_text_result(text: str, style: str ="consice") -> SummaryState: 
    state = summarise_text(text=text, style=style)
    return state["result"]

def summarise_bullet_result(text: str, style: str="bullett")-> SummaryState: 
    state = summarise_bullets(text=text, style=style)
    return state["result"]
