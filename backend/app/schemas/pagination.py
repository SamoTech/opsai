import math
from typing import Generic, List, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams:
    """Reusable FastAPI dependency for offset/limit pagination.

    Usage:
        @router.get("/")
        async def list_items(pagination: PaginationParams = Depends()):
            ...
    """

    def __init__(
        self,
        page: int = Query(default=1, ge=1, description="Page number (1-based)"),
        limit: int = Query(default=20, ge=1, le=100, description="Items per page (max 100)"),
    ):
        self.page = page
        self.limit = limit
        self.offset = (page - 1) * limit


class PagedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    pages: int
    limit: int

    @classmethod
    def create(cls, items: list, total: int, params: PaginationParams) -> "PagedResponse":
        return cls(
            items=items,
            total=total,
            page=params.page,
            pages=math.ceil(total / params.limit) if params.limit else 1,
            limit=params.limit,
        )
