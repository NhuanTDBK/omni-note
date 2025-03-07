from datetime import datetime, timezone
import uuid

from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    JSON,
    Integer,
    BLOB,
    SmallInteger,
)

from .base import Base


class MaterialType(Base):
    __tablename__ = "material_types"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True)
    description = Column(String(255), nullable=True)
    schema = Column(JSON, nullable=True)
    level = Column(SmallInteger, default=0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    parent_id = Column(Integer, nullable=True)


class MaterialContent(Base):
    __tablename__ = "material_contents"
    id = Column(String, primary_key=True, default=uuid.uuid4)
    type_id = Column(Integer, ForeignKey("material_types.id"))
    user_id = Column(String, ForeignKey("users.user_id"))
    title = Column(String(255))
    file_path = Column(String(1024))
    metadata_data = Column(JSON, nullable=True)
    embedding = Column(BLOB, nullable=True)
    content = Column(BLOB, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime, default=datetime.now(timezone.utc), onupdate=timezone.utc
    )
