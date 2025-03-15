from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Integer, SmallInteger

from .base import Base


class Template(Base):
    __tablename__ = "templates"
    __table_args__ = {'schema': 'app'}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True)
    description = Column(String(255), nullable=True)
    level = Column(SmallInteger, default=0)
    schema = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    parent_id = Column(Integer, nullable=True)
