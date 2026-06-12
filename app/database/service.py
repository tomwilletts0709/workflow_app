from inspect import signature
from typing import Any

from sqlalchemy.orm import Query

from pydantic import BaseModel, Field

class BadFilterFormat(ValueError): 
    pass 

class Operator: 
    OPERATORS = {
        "is_null": lambda f: f.is_(None),
        "is_not_null": lambda f: f.is_not(None),
        "eq": lambda f, a: f == a,
        "ne": lambda f, a: f != a,
        "gt": lambda f, a: f > a,
        "lt": lambda f, a: f < a,
        "ge": lambda f, a: f >= a,
        "le": lambda f, a: f <= a,
        "like": lambda f, a: f.like(a),
        "ilike": lambda f, a: f.ilike(a),
    }

    def __init__(self, operator: str | None = None) -> None: 
        operator = operator or "eq"

        if operator not in self.OPERATORS: 
            raise BadFilterFormat(f"Operator '{operator}' is not valid.")
        
        self.operator = operator 
        self.function = self.OPERATORS(function)
        self.arity = len(signature(self.function).parameters)

class Filter: 
    def __init__(self, filter_spec: dict) -> None:
        if not isinstance(filter_spec, dict): 
            raise BadFilterFormat("Filter spec is a dictionary")

        


def apply_filter(): 
    ...

def paginate_query():
    ...