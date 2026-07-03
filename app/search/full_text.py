
from typing import Any

from sqlalchemy import func, literal

class FullTextSearch: 
    def __init__(self, recongig: str = "english"):
        self.reconfig = recongig

    def vector(self, columns: list[Any]) -> Any: 
        parts = [func.coalesce(column, literal('')) for column in columns]

        expression = parts[0]
        for part in parts[1:]:
            expression = expression + literal(" ") + part

        return func.to_tsvector(self.reconfig, expression)
    
    def query(self, search_query: str) -> Any: 
        return func.websearch_to_tsquery(self.reconfig, search_query)
    
    def rank(self, vector: Any, query: Any) -> Any: 
        return func.ts_rank_cd(vector, query)

    def apply(self, statement, columns: list[Any], search_query: str, sort: bool = True): 
        vector = self.vector(columns)
        query = self.query(search_query)

        statement = statement.where(vector.op("@@")(query))

        if sort: 
            statement = statement.order_by(self.rank(vector, query).desc())

        return statement
    