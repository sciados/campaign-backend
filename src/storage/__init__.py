# ============================================================================
# src/storage/__init__.py
# ============================================================================

"""
Storage Module

File storage, media generation, and Cloudflare R2 integration module.
Provides file upload/download, quota management, and media generation capabilities.
"""

from src.storage.storage_module import StorageModule

__all__ = [
    "StorageModule"
]

__version__ = "1.0.0"
__module_name__ = "storage"
__description__ = "File storage and media generation module"