# =====================================
# File: src/core/database/__init__.py
# =====================================

"""
Database package for CampaignForge Core Infrastructure

Provides database connection management, session handling, and base models.
"""

from .connection import engine, async_engine, get_db, get_async_db
from .models import Base, TimestampMixin, UserMixin
from .session import SessionManager, AsyncSessionManager

__all__ = [
    "engine",
    "async_engine", 
    "get_db",
    "get_async_db",
    "Base",
    "TimestampMixin",
    "UserMixin",
    "SessionManager",
    "AsyncSessionManager",
]