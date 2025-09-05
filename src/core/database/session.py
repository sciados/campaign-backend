# =====================================
# File: src/core/database/session.py
# =====================================

"""
Advanced session management for CampaignForge database operations.

Provides transaction management, connection pooling, and error handling.
"""

from contextlib import contextmanager, asynccontextmanager
from typing import Optional, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from .connection import SessionLocal, AsyncSessionLocal

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