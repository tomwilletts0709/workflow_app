from inspect import signature
from typing import Any

from sqlalchemy import Select, func, select


class BadFilterFormat(ValueError):
    pass


class Operator:
    OPERATORS = {
        "is_null": lambda field: field.is_(None),
        "is_not_null": lambda field: field.is_not(None),
        "eq": lambda field, value: field == value,
        "ne": lambda field, value: field != value,
        "gt": lambda field, value: field > value,
        "lt": lambda field, value: field < value,
        "ge": lambda field, value: field >= value,
        "le": lambda field, value: field <= value,
        "like": lambda field, value: field.like(value),
        "ilike": lambda field, value: field.ilike(value),
    }

    def __init__(self, operator: str | None = None) -> None:
        operator = operator or "eq"

        if operator not in self.OPERATORS:
            raise BadFilterFormat(f"Operator '{operator}' is not valid.")

        self.operator = operator
        self.function = self.OPERATORS[operator]
        self.arity = len(signature(self.function).parameters)

    def apply(self, field: Any, value: Any = None) -> Any:
        if self.arity == 1:
            return self.function(field)
        return self.function(field, value)


class Filter:
    def __init__(self, filter_spec: dict[str, Any]) -> None:
        if not isinstance(filter_spec, dict):
            raise BadFilterFormat("Filter spec must be a dictionary.")

        self.field = filter_spec.get("field")
        self.value = filter_spec.get("value")
        self.operator = Operator(filter_spec.get("operator"))

        if not self.field:
            raise BadFilterFormat("Filter spec must contain a 'field' key.")

        if self.operator.arity != 1 and "value" not in filter_spec:
            raise BadFilterFormat(
                f"Filter spec must contain a value key for operator "
                f"'{self.operator.operator}'."
            )

    def apply(self, allowed_fields: dict[str, Any]) -> Any:
        column = allowed_fields.get(self.field)
        if column is None:
            raise BadFilterFormat(f"Field '{self.field}' is not filterable.")
        return self.operator.apply(column, self.value)


def apply_filter(
    statement: Select,
    filters: list[dict[str, Any]] | None,
    allowed_fields: dict[str, Any],
) -> Select:
    if not filters:
        return statement

    for filter_spec in filters:
        statement = statement.where(Filter(filter_spec).apply(allowed_fields))

    return statement


def apply_sort(
    statement: Select,
    sort_by: str | None,
    sort_order: str | None,
    allowed_sort_fields: dict[str, Any],
    default_sort: Any | None = None,
) -> Select:
    column = allowed_sort_fields.get(sort_by) if sort_by else default_sort

    if column is None:
        return statement

    if sort_order == "asc":
        return statement.order_by(column.asc())

    return statement.order_by(column.desc())


def paginate_statement(statement: Select, page: int, page_size: int) -> Select:
    offset = (page - 1) * page_size
    return statement.offset(offset).limit(page_size)


def count_statement(statement: Select) -> Select:
    return select(func.count()).select_from(statement.order_by(None).subquery())
