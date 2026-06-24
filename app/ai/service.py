from app.ai.schemas import SummaryState
from app.ai.graph import run_summary_graph


class AIService: 
    def __init__(self, graph=summary_graph):
        self.graph = graph

def summarise_text(self, text: str, style: str = "concise") -> SummaryState: 
    return run_summary_graph(text=text, style=style)

def summarise_bullets(self, text:str, style: str="bullets") -> SummaryState: 
    return run_summary_graph(text=text, style=style)

def detailed_text(self, text: str, style: str="detailed")->SummaryState: 
    return run_summary_graph(text=text, style=style)

def summarise_text_result(self, text: str, style: str ="concise") -> SummaryState: 
    state = summarise_text(text=text, style=style)
    return state["result"]

def summarise_bullet_result(self, text: str, style: str="bullett")-> SummaryState: 
    state = summarise_bullets(text=text, style=style)
    return state["result"]

