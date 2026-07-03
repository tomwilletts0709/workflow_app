from enum import StrEnum, auto


class SearchMode(StrEnum): 
    KEYWORD = auto() 
    SEMANTIC = auto() 
    HYBRID = auto()

class SearchEvent(StrEnum): 
    EVENT = auto()

class SortOrder(StrEnum): 
    ASC = auto() 
    DESC = auto()

class SortBy(StrEnum): 
    NAME = auto()
    CREATED_AT = auto()
    UPDATED_AT = auto() 

class SearchType(StrEnum):
    TASK = auto() 
    PROJECT = auto()
    USER = auto()
    
