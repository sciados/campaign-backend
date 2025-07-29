# src/campaigns/__init__.py
"""
Campaigns module for marketing campaign management with streamlined 2-step workflow
Modular router architecture following intelligence/routers pattern
"""

# Try to import the main router, with detailed error handling
try:
    from .routes import router
    __all__ = ["router"]
except ImportError as e:
    import logging
    logging.error(f"❌ Failed to import campaigns router: {e}")
    # Create a fallback empty router to prevent complete failure
    from fastapi import APIRouter
    router = APIRouter(tags=["campaigns-fallback"])
    __all__ = ["router"]