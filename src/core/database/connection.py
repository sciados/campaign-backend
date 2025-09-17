# =====================================
# File: src/core/database/connection.py
# =====================================

"""
Database connection management for CampaignForge

Handles both synchronous and asynchronous database connections
for Railway PostgreSQL deployment.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging
from sqlalchemy import text
from typing import Generator, AsyncGenerator

from src.core.config import settings

logger = logging.getLogger(__name__)

# Synchronous engine for standard operations
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=StaticPool,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG if hasattr(settings, 'DEBUG') else False,
)

# Asynchronous engine for high-performance operations
async_engine = create_async_engine(
    settings.DATABASE_URL_ASYNC,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10,
    echo=settings.DEBUG if hasattr(settings, 'DEBUG') else False,
    # Use READ_COMMITTED to prevent transaction conflicts
    isolation_level="READ_COMMITTED",
    connect_args={
        "server_settings": {
            "application_name": "campaignforge_backend",
        }
    }
)

# Session factories
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,  # Enable autoflush for immediate writes
    autocommit=False  # Explicit transaction control
)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session for synchronous operations.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get async database session for asynchronous operations.

    Yields:
        AsyncSession: SQLAlchemy async database session with proper transaction handling
    """
    session = AsyncSessionLocal()
    try:
        yield session
        # Commit any pending transactions
        await session.commit()
    except Exception as e:
        logger.error(f"Async database session error: {e}")
        await session.rollback()
        raise
    finally:
        await session.close()

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set database connection parameters for optimal performance."""
    if "postgresql" in settings.DATABASE_URL:
        # PostgreSQL-specific optimizations for Railway
        cursor = dbapi_connection.cursor()
        cursor.execute("SET timezone = 'UTC'")
        cursor.execute("SET statement_timeout = '30s'")
        cursor.close()


async def test_database_connection() -> bool:
    """
    Test database connectivity for health checks.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        # Test sync connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        # Test async connection with autocommit
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))

        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False