"""
Database configuration and connection management
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import structlog

from src.core.config import settings

logger = structlog.get_logger()

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# Create session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Create base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()

async def get_db() -> AsyncSession:
    """Dependency for getting database session"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initialize database"""
    logger.info("Initializing database connection")
    try:
        async with engine.begin() as conn:
            # Import all models to ensure they are registered
            from src.models import campaign, user, content, analytics
ECHO is off.
            # Create tables
            await conn.run_sync(Base.metadata.create_all)
ECHO is off.
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise
