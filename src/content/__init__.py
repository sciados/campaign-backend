"""
Initialization for the Content module.
Avoids circular imports by lazy-loading key factories and generators.
"""

def get_content_router():
    """Lazy import to avoid circular import issues."""
    from src.content.api.routes import router
    return router

__all__ = ["get_content_router"]
