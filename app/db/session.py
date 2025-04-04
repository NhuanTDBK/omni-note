from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.configs import get_config

config = get_config()
engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
