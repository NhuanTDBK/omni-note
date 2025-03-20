from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class MaterialBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    tags: Optional[List[str]] = []


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(MaterialBase):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)


class MaterialResponse(MaterialBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class MaterialListResponse(BaseModel):
    total: int
    items: List[MaterialResponse]


class ExtractDataResponse(BaseModel):
    summary: str
    keywords: List[str]
    hyperlinks: Optional[List[str]] = []
    content: dict
