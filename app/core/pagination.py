from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel, Field, model_validator


class CommonParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    query: str | None = None


def common_params(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    query: str | None = Query(default=None),
) -> CommonParams:
    return CommonParams(
        page=page,
        page_size=page_size,
        query=query,
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
