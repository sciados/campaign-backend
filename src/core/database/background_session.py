# src/core/database/background_session.py

"""
Background task session management for long-running operations.

Provides proper database session handling for background tasks that run
outside of the FastAPI dependency injection system.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.connection import AsyncSessionLocal

logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_background_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session for background tasks with proper error handling.

    This provides the same transaction management as the FastAPI dependency
    but can be used in background tasks and asyncio.create_task() contexts.

    Yields:
        AsyncSession: SQLAlchemy async database session
    """
    session = AsyncSessionLocal()
    try:
        logger.debug("Background session created")
        yield session
        await session.commit()
        logger.debug("Background session committed")
    except Exception as e:
        logger.error(f"Background session error: {e}")
        await session.rollback()
        raise
    finally:
        await session.close()
        logger.debug("Background session closed")


class BackgroundSessionManager:
    """
    Session manager for background tasks with connection pooling awareness.

    Future enhancement: Could include metrics, connection pooling optimization,
    and retry logic for background operations.
    """

    @staticmethod
    async def execute_with_session(task_func, *args, **kwargs):
        """
        Execute a function with a background session.

        Args:
            task_func: Async function that takes session as first parameter
            *args: Additional arguments for task_func
            **kwargs: Additional keyword arguments for task_func
        """
        async with get_background_session() as session:
            return await task_func(session, *args, **kwargs)