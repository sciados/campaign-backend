# src/core/database/__init__.py
"""
Database package for CampaignForge Core Infrastructure

Provides database connection management, session handling, and base models.
"""

from src.core.database.connection import engine, async_engine, get_db, get_async_db, test_database_connection
from src.core.database.models import Base, TimestampMixin, UserMixin
from src.core.database.session import SessionManager, AsyncSessionManager

__all__ = [
    "engine",
    "async_engine", 
    "get_db",
    "get_async_db",
    "test_database_connection",
    "Base",
    "TimestampMixin",
    "UserMixin",
    "SessionManager",
    "AsyncSessionManager",
]