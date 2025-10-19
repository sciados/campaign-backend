# =====================================
# File: src/intelligence/api/__init__.py
# =====================================

from fastapi import APIRouter

def get_intelligence_router() -> APIRouter:
    """Lazy import to avoid circular dependency"""
    from src.intelligence.api.intelligence_routes import router
    return router


__all__ = ["get_intelligence_router"]
