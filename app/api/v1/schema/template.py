from typing import Optional
from pydantic import BaseModel


class TemplateBase(BaseModel):
    name: str
    level: int
    content: str
    parent_id: Optional[int] = None


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(TemplateBase):
    name: Optional[str] = None
    level: Optional[int] = None
    content: Optional[str] = None


class TemplateResponse(TemplateBase):
    id: int

    class Config:
        from_attributes = True
