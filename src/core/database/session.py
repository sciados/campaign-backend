
# =====================================
# File: src/core/database/session.py
# =====================================

"""
Advanced session management for CampaignForge database operations.

Provides transaction management, connection pooling, and error handling.
Enhanced for Session 5 with Railway optimizations.
"""

from contextlib import contextmanager, asynccontextmanager
from typing import Optional, Any, Dict, AsyncGenerator
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
import logging

from src.core.database.connection import SessionLocal, AsyncSessionLocal
from src.core.config.settings import get_database_url

logger = logging.getLogger(__name__)


class SessionManager:
    """Synchronous database session manager with transaction support."""
    
    @staticmethod
    @contextmanager
    def get_session():
        """Get a database session with automatic cleanup."""
        session = SessionLocal()
        try:
            yield session
        except Exception as e:
            logger.error(f"Session error: {e}")
            session.rollback()
            raise
        finally:
            session.close()
    
    @staticmethod
    @contextmanager
    def get_transaction():
        """Get a database session with automatic transaction management."""
        session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            logger.error(f"Transaction error: {e}")
            session.rollback()
            raise
        finally:
            session.close()


class AsyncSessionManager:
    """Asynchronous database session manager with transaction support."""
    
    # Enhanced class variables for Session 5
    _engine = None
    _session_factory = None
    _initialized = False
    
    @staticmethod
    @asynccontextmanager
    async def get_session():
        """Get an async database session with automatic cleanup."""
        async with AsyncSessionLocal() as session:
            try:
                yield session
            except Exception as e:
                logger.error(f"Async session error: {e}")
                await session.rollback()
                raise
    
    @staticmethod
    @asynccontextmanager
    async def get_transaction():
        """Get an async database session with automatic transaction management."""
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                logger.error(f"Async transaction error: {e}")
                await session.rollback()
                raise
    
    # Session 5 Enhancements
    @classmethod
    async def initialize(cls):
        """Initialize the session manager for Railway deployment"""
        if cls._initialized:
            return
        
        try:
            database_url = get_database_url()
            logger.info("Initializing enhanced database session manager...")
            
            # Create async engine with Railway-optimized settings
            cls._engine = create_async_engine(
                database_url,
                poolclass=NullPool,  # Railway-friendly
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False,
                future=True
            )
            
            # Create session factory
            cls._session_factory = async_sessionmaker(
                bind=cls._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=True,
                autocommit=False
            )
            
            cls._initialized = True
            logger.info("Enhanced database session manager initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize session manager: {e}")
            cls._initialized = False
            raise
    
    @classmethod
    async def close(cls):
        """Close the session manager and engine"""
        if cls._engine:
            await cls._engine.dispose()
            cls._engine = None
            cls._session_factory = None
            cls._initialized = False
            logger.info("Session manager closed")


# Legacy compatibility function and Service Factory support
async def get_enhanced_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Enhanced session getter for service factory"""
    if not AsyncSessionManager._initialized:
        await AsyncSessionManager.initialize()
    
    async with AsyncSessionManager.get_session() as session:
        yield session