from pydantic import BaseModel
from typing import List


class SearchResponse(BaseModel):
    """
    Response model for search results.
    """

    id: str
    score: float
    payload: dict


class ListSearchResponse(BaseModel):
    """
    Response model for a list of search results.
    """

    results: List[SearchResponse]
    total: int
    page: int
    page_size: int

    class Config:
        orm_mode = True
