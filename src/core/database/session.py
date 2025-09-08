# src/core/database/session.py - Enhanced Session Management for Session 5

import logging
from typing import AsyncGenerator, Optional, Generator
from contextlib import asynccontextmanager, contextmanager
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from src.core.config.settings import get_database_url

logger = logging.getLogger(__name__)

class AsyncSessionManager:
    """Enhanced async session manager with proper lifecycle management"""
    
    _engine = None
    _session_factory = None
    _initialized = False
    
    @classmethod
    async def initialize(cls):
        """Initialize the session manager"""
        if cls._initialized:
            return
        
        try:
            database_url = get_database_url(async_mode=True)
            logger.info("Initializing async database session manager...")
            
            # Create async engine with optimized settings
            cls._engine = create_async_engine(
                database_url,
                poolclass=NullPool,  # Railway-friendly
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False,  # Set to True for SQL debugging
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
            logger.info("Async database session manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize async session manager: {e}")
            cls._initialized = False
            raise
    
    @classmethod
    @asynccontextmanager
    async def get_session(cls) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session with proper cleanup"""
        if not cls._initialized:
            await cls.initialize()
        
        if cls._session_factory is None:
            raise RuntimeError("Async session manager not properly initialized")
        
        async with cls._session_factory() as session:
            try:
                logger.debug("Created new async database session")
                yield session
            except Exception as e:
                logger.error(f"Async session error: {e}")
                await session.rollback()
                raise
            finally:
                await session.close()
                logger.debug("Closed async database session")
    
    @classmethod
    @asynccontextmanager
    async def get_transaction(cls) -> AsyncGenerator[AsyncSession, None]:
        """Get a transactional session with automatic commit/rollback"""
        async with cls.get_session() as session:
            try:
                yield session
                await session.commit()
                logger.debug("Async transaction committed")
            except Exception as e:
                await session.rollback()
                logger.error(f"Async transaction rolled back due to error: {e}")
                raise
    
    @classmethod
    async def close(cls):
        """Close the async session manager and engine"""
        if cls._engine:
            await cls._engine.dispose()
            cls._engine = None
            cls._session_factory = None
            cls._initialized = False
            logger.info("Async session manager closed")


class SessionManager:
    """Synchronous session manager for sync operations"""
    
    _engine = None
    _session_factory = None
    _initialized = False
    
    @classmethod
    def initialize(cls):
        """Initialize the sync session manager"""
        if cls._initialized:
            return
        
        try:
            # Get sync database URL (without asyncpg)
            database_url = get_database_url(async_mode=False)
            
            logger.info("Initializing sync database session manager...")
            
            # Create sync engine
            cls._engine = create_engine(
                database_url,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False,
                future=True
            )
            
            # Create session factory
            cls._session_factory = sessionmaker(
                bind=cls._engine,
                autoflush=True,
                autocommit=False
            )
            
            cls._initialized = True
            logger.info("Sync database session manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize sync session manager: {e}")
            cls._initialized = False
            raise
    
    @classmethod
    @contextmanager
    def get_session(cls) -> Generator[Session, None, None]:
        """Get a sync database session with proper cleanup"""
        if not cls._initialized:
            cls.initialize()
        
        if cls._session_factory is None:
            raise RuntimeError("Sync session manager not properly initialized")
        
        session = cls._session_factory()
        try:
            logger.debug("Created new sync database session")
            yield session
        except Exception as e:
            logger.error(f"Sync session error: {e}")
            session.rollback()
            raise
        finally:
            session.close()
            logger.debug("Closed sync database session")
    
    @classmethod
    def close(cls):
        """Close the sync session manager and engine"""
        if cls._engine:
            cls._engine.dispose()
            cls._engine = None
            cls._session_factory = None
            cls._initialized = False
            logger.info("Sync session manager closed")


# Legacy compatibility function
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Legacy function for backward compatibility"""
    async with AsyncSessionManager.get_session() as session:
        yield session


# FastAPI dependency functions
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for sync database sessions"""
    with SessionManager.get_session() as session:
        yield session


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for async database sessions"""
    async with AsyncSessionManager.get_session() as session:
        yield session


# Engine access functions
def get_engine():
    """Get the sync database engine"""
    if not SessionManager._initialized:
        SessionManager.initialize()
    return SessionManager._engine


async def get_async_engine():
    """Get the async database engine"""
    if not AsyncSessionManager._initialized:
        await AsyncSessionManager.initialize()
    return AsyncSessionManager._engine