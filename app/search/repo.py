from typing import Any, Protocol, TypeVar

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

T = TypeVar("T")


class SearchRepoProtocol(Protocol):
    def autocomplete(self, model: type[T], search_columns: list[Any], label_column: Any, query: str, limit: int = 10) -> list[str]:
        ...

    def text_search(self, model: type[T], search_columns: list[Any], query: str | None, filters: dict | None, page: int, page_size: int) -> dict[str, Any]:
        ...


class SearchRepo:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def text_search(self, model: type[T], search_columns: list[Any], query: str | None, filters: dict | None, page: int, page_size: int) -> dict[str, Any]:
        statement = select(model)
        cleaned_query = query.strip() if query else None

        if cleaned_query:
            pattern = f"%{cleaned_query}%"
            statement = statement.where(
                or_(*(column.ilike(pattern) for column in search_columns))
            )

        total_statement = select(func.count()).select_from(statement.subquery())
        total = self.db_session.execute(total_statement).scalar_one()

        offset = (page - 1) * page_size
        rows = (
            self.db_session.execute(statement.offset(offset).limit(page_size))
            .scalars()
            .all()
        )

        return {
            "items": rows,
            "page": page,
            "page_size": page_size,
            "total": total,
            "has_next": offset + page_size < total,
        }

    def autocomplete(self, model: type[T], search_columns: list[Any], label_column: Any, query: str, limit: int = 10) -> list[str]:
        cleaned_query = query.strip()

        if not cleaned_query:
            return []

        pattern = f"%{cleaned_query}%"
        statement = (
            select(label_column)
            .select_from(model)
            .where(or_(*(column.ilike(pattern) for column in search_columns)))
            .limit(limit)
        )

        return list(self.db_session.execute(statement).scalars().all())
