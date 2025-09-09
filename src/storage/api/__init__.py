# ============================================================================
# src/storage/api/__init__.py
# ============================================================================

"""
Storage API

REST API endpoints for file operations, uploads, downloads, and media generation.
"""

from src.storage.api.routes import router

__all__ = [
    "router"
]