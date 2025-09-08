# =====================================
# File: src/core/__init__.py
# =====================================

"""
Core Infrastructure Module

This module provides the foundational infrastructure for CampaignForge,
including database connections, configuration management, shared utilities,
and module interfaces.
"""

from src.core.database import get_db, get_async_db, engine, async_engine
from src.core.config import settings, get_settings
from src.core.interfaces import ModuleInterface, ServiceInterface, RepositoryInterface
from src.core.shared import (
    CampaignForgeException,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    StandardResponse,
    SuccessResponse,
    ErrorResponse
)

__version__ = "1.0.0"
__all__ = [
    # Database
    "get_db",
    "get_async_db", 
    "engine",
    "async_engine",
    
    # Configuration
    "settings",
    "get_settings",
    
    # Interfaces
    "ModuleInterface",
    "ServiceInterface", 
    "RepositoryInterface",
    
    # Exceptions
    "CampaignForgeException",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError", 
    "NotFoundError",
    
    # Responses
    "StandardResponse",
    "SuccessResponse",
    "ErrorResponse",
]