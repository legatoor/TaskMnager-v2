from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import Config

# Create SQLAlchemy engine
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Database session context manager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
