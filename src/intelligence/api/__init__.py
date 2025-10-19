# =====================================
# File: src/intelligence/api/__init__.py
# =====================================

"""
API layer for Intelligence Engine.

Provides FastAPI route handlers for intelligence operations.
"""

from src.intelligence.api.intelligence_routes import router

__all__ = ["router"]