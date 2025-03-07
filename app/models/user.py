from datetime import datetime
import uuid

from sqlalchemy import Column, String, DateTime


from .base import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
