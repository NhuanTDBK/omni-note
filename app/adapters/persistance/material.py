from datetime import datetime, timezone
import uuid

from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    JSON,
    Integer,
    LargeBinary,
    SmallInteger,
)

from .base import Base
from .template import Template
from .user import User


class MaterialContent(Base):
    __tablename__ = "contents"
    __table_args__ = {'schema': 'app'}
    id = Column(String, primary_key=True, default=uuid.uuid4)
    type_id = Column(Integer, ForeignKey(Template.id))
    user_id = Column(String, ForeignKey(User.user_id))
    title = Column(String(255))
    file_path = Column(String(1024))
    metadata_data = Column(JSON, nullable=True)
    embedding = Column(LargeBinary, nullable=True)
    content = Column(LargeBinary, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime, default=datetime.now(timezone.utc), onupdate=timezone.utc
    )
