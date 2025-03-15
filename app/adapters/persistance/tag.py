from sqlalchemy import Column, String, Float, ForeignKey, Integer

from .base import Base
from .material import MaterialContent


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = {'schema': 'app'}

    tag_id = Column(Integer, primary_key=True, autoincrement=True)
    material_id = Column(String, ForeignKey(MaterialContent.id))
    tag_type = Column(String(50))
    tag_value = Column(String(255))
    confidence = Column(Float)
