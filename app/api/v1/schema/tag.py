from pydantic import BaseModel
from typing import Optional

class TagBase(BaseModel):
    material_id: str
    tag_type: str
    tag_value: str
    confidence: float

class TagCreate(TagBase):
    pass

class TagUpdate(TagBase):
    pass

class TagResponse(TagBase):
    tag_id: int

    class Config:
        orm_mode = True
