# =====================================
# File: src/intelligence/api/__init__.py
# =====================================

"""
API layer for Intelligence Engine.

Provides FastAPI route handlers for intelligence operations.
"""

from .intelligence_routes import router

__all__ = ["router"]