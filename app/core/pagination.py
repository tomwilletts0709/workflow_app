from typing import Annotated, Generic, TypeVar

from fastapi import Depends, Query
from pydantic import BaseModel, Field, model_validator

from app.search.enums import SortOrder

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]): 
    items: list[T]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
    has_next= bool

class CommonParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    query: str | None = None
    sort_by: str | None = None
    sort_order: SortOrder | None = None


def common_params(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    query: str | None = Query(default=None),
    sort_by: str | None = Query(default=None),
    sort_order: SortOrder | None = Query(default=None),
) -> CommonParams:
    return CommonParams(
        page=page,
        page_size=page_size,
        query=query,
        sort_by=sort_by,
        sort_order=sort_order,
    )


CommonParamsDependency = Annotated[CommonParams, Depends(common_params)]


class Pagination(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    total: int = Field(default=0, ge=0)

    @model_validator(mode="before")
    @classmethod
    def validate_pagination(cls, values):
        page = values.get("page", 1)
        page_size = values.get("page_size", 10)

        if page < 1:
            raise ValueError("Page cannot be less than 1.")

        if page_size < 1:
            raise ValueError("Page size cannot be less than 1.")

        return values
