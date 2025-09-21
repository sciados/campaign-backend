# src/core/database/__init__.py
"""
Database package for CampaignForge Core Infrastructure

Provides database connection management, session handling, and base models.
"""

from src.core.database.session import engine, async_engine, get_db, get_async_db, test_database_connection
from src.core.database.models import Base, TimestampMixin, UserMixin
from src.core.database.session import SessionManager, AsyncSessionManager

# ClickBank integration
try:
    from src.core.database.clickbank_repo import save_clickbank_creds, get_clickbank_creds
    CLICKBANK_DB_AVAILABLE = True
except ImportError:
    CLICKBANK_DB_AVAILABLE = False

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

if CLICKBANK_DB_AVAILABLE:
    __all__.extend(["save_clickbank_creds", "get_clickbank_creds"])