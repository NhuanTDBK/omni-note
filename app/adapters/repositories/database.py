from qdrant_client import AsyncQdrantClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.configs import get_config

settings = get_config()

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    return db


def get_qdrant_client() -> AsyncQdrantClient:
    qdrant_client = AsyncQdrantClient()
    return qdrant_client
