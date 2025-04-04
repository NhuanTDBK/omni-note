from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class MaterialBase(BaseModel):
    type_id: int = Field()
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    tags: Optional[List[str]] = []
    metadata_data: Optional[dict] = {}



class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(MaterialBase):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)


class MaterialResponse(BaseModel):
    status: bool


class MaterialListResponse(BaseModel):
    total: int
    items: List[MaterialResponse]


class ExtractDataResponse(BaseModel):
    category: str
    summarization: str = ""
    metadata: dict = {}
    user_id: str = ""
