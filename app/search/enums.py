from enum import StrEnum, auto


class SearchMode(): 
    KEYWORD = auto() 
    SEMANTIC = auto() 
    HYBRID = auto()

class SearchEvent(): 
    EVENT = auto()

class SortOrder(): 
    ASC = auto() 
    DESC = auto()

class SortBy(): 
    NAME = auto()
    CREATED_AT = auto()
    UPDATED_AT = auto() 

class SearchType():
    TASK = auto() 
    PROJECT = auto()
    USER = auto()
    
