from typing import TypeVar, Any
from app.search.repo import SearchRepo

T = TypeVar("T")

class SearchService: 
    def __init__(self, repo:SearchRepo): 
        self.repo = repo

    def text_search(self, model: type[T], search_columns: list[Any], query: str | None, filters: dict | None, page: int, page_size: int) -> dict[str, Any]:
        return self.repo.text_search(model, search_columns, query, filters, page, page_size)
    
    def autocomplete(self, model: type[T], search_columns: list[Any], label_column: Any, query: str, limit: int = 10) -> list[str]:
        return self.repo.autocomplete(model, search_columns, label_column, query, limit)
    
    def global_autocomplete(self, model: type[T], search_columns: list[Any], label_column: Any, query: str, limit: int = 10) -> list[str]:
        pass

        