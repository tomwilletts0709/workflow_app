from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.pagination import CommonParamsDependency
from app.database.database import get_db
from app.search.models import SearchResponse
from app.search.repo import SearchRepo
from app.search.service import SearchService

search_router = APIRouter()


def get_search_service(db_session: Session = Depends(get_db)) -> SearchService:
    return SearchService(SearchRepo(db_session))


@search_router.get("", response_model=SearchResponse)
async def search(
    params: CommonParamsDependency,
    service: SearchService = Depends(get_search_service),
):
    return service.global_search(
        query=params.query,
        page=params.page,
        page_size=params.page_size,
    )
