from sqlalchemy.dialects.postgresql.base import PGDialect
PGDialect._get_server_version_info = lambda *args: (9, 2)
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from settings or environment variable
SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


