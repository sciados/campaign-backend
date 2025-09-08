# =====================================
# File: src/core/config/__init__.py
# =====================================

"""
Configuration management for CampaignForge Core Infrastructure.

Provides centralized configuration management for Railway deployment
with comprehensive environment variable handling.
"""

from src.core.config.settings import settings #, get_settings
from src.core.config.ai_providers import ai_provider_config
from src.core.config.deployment import deployment_config
from src.core.config.storage_config import storage_config

__all__ = [
    "settings",
    "get_settings",
    "ai_provider_config",
    "deployment_config", 
    "storage_config",
]