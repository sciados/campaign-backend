# =====================================
# File: src/intelligence/__init__.py
# =====================================

"""
Initialization for the Intelligence module.
Provides a lazy import function to avoid circular dependencies.
"""

def get_intelligence_router():
    """Lazy import to avoid circular import issues."""
    from src.intelligence.api.intelligence_routes import router
    return router

__all__ = ["get_intelligence_router"]