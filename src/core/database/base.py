# File: backend/src/core/database/base.py
# SQLAlchemy base class and database setup

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/campaignforge")

# Create engine with NullPool for Railway compatibility
# This prevents connection pool exhaustion on Railway's managed Postgres
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # No connection pooling - prevents Railway connection limit issues
    pool_pre_ping=True,
    pool_recycle=300
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()