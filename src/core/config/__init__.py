# =====================================
# File: src/core/config/__init__.py
# =====================================

"""
Configuration management for CampaignForge Core Infrastructure.

Provides centralized configuration management for Railway deployment
with comprehensive environment variable handling.
"""

from .settings import settings, get_settings
from .ai_providers import ai_provider_config
from .deployment import deployment_config
from .storage_config import storage_config

__all__ = [
    "settings",
    "get_settings",
    "ai_provider_config",
    "deployment_config", 
    "storage_config",
]