from sqlalchemy import Column, String, Float, ForeignKey, Integer

from .base import Base


class Tag(Base):
    __tablename__ = "material_tags"

    tag_id = Column(Integer, primary_key=True, autoincrement=True)
    material_id = Column(String, ForeignKey("material_contents.id"))
    tag_type = Column(String(50))
    tag_value = Column(String(255))
    confidence = Column(Float)
