from langgraph.graph import END, START, StateGraph
from langchain_openai import ChatOpenAI

from app.ai.prompts import build_prompt
from app.ai.schemas import SummaryState
from app.core.settings import get_settings

def get_llm() -> ChatOpenAI: 
    settings = get_settings() 
    return ChatOpenAI(
        model=settings.ai_model, 
        api_key=settings.open_api_key,
    )

def build_prompt_node(state: SummaryState) -> SummaryState: 
    prompt = build_prompt(state["style"], state["text"])
    return {
        **state, 
        "prompt": prompt,
    }

def llm_node(state: SummaryState)-> SummaryState: 
    return {
        **state, 
        "result": f"ai result for prompt: {state['prompt']}"
    }

def build_summary_graph(): 
    graph = StateGraph(SummaryState)

    graph.add_node("build_prompt", build_prompt_node)
    graph.add_node("llm_node", fake_llm_node)

    graph.add_edge(START, "build_prompt")
    graph.add_edge("build_prompt", "llm_node")
    graph.add_edge("llm_node", END)

    return graph.compile()

summary_graph = build_summary_graph()

def run_summary_graph(text: str, style: str = "concise") -> SummaryState: 
    return summary_graph.invoke(
        {
            "text": text, 
            "style": style,
        }
    )