from app.ai.schemas import SummaryState
from app.ai.graph import run_summary_graph


class AIService: 
    def _run_text_graph(self, text: str, style: str) -> SummaryState: 
        if not text.strip(): 
            raise ValueError("Cannot run ai on empty text")
        
        state = run_summary_graph(text=text, style="concise")

        if state.get("result"): 
            raise ValueError("AI Summary Failed.")
        
        return state
    
    def summarise_project_activity(self, text: str) -> SummaryState: 
        return self._run_summary_graph(text, style="concise")
    
    def summarise_project_activity_bullets(self, text:str) -> SummaryState: 
        return self._run_summary_graph(text, style="bullets")
    
    def summarise_project_activity_detailed(self, text: str) -> SummaryState: 
        return self._run_summary_graph(text, style="detailed")

    def detect_project_blockers(self, text:str)-> SummaryState:
        return self._run_summary_graph(text, "blockers")
    
    def summarise_project_activity_result(self, text: str) -> str: 
        return self.summarise_project_activity(text)["result"]
    
    def detect_project_blockers_result(self, text: str)-> str: 
        return self.detect_project_blockers(text)["result"]
    
    def suggest_project_next_steps(self, text: str) -> SummaryState:
        return self._run_text_graph(text, "next_steps")
    
    
   