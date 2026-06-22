

from typing import Callable


PromptBuilder = Callable[[str], str]

def concise_prompt(text: str)->str: 
    return f"summarise this into one concise paragraph:\n\{text}"

def bullet_point_prompt(text: str)-> str: 
    return f"list out this prompt in succinct bullet points:\n\n{text}"

def blocker_prompt(text: str) -> str: 
    return f"Identity blockers, risks, and next steps from this project activity: \n\n{text}"


PROMPTS: dict[str, PromptBuilder] = {
    "concise": concise_prompt, 
    "bullets": bullet_point_prompt,
    "blockers": blockers,
}

def build_prompt(style: str, text: str)-> str: 
    try: 
        builder = PROMPTS[style]
    except KeyError: 
        raise ValueError(f"Unknown prompt style: {style}") from None
    return builder(text)

