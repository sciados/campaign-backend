# File: src/intelligence/routers/__init__.py
"""
Intelligence Routers Package
"""
from .enhanced_email_routes import router as enhanced_email_router
from . import analysis_routes
from . import content_routes
from . import management_routes
from . import debug_routes

__all__ = [
    "enhanced_email_router",
    "analysis_routes",
    "content_routes",
    "management_routes", 
    "debug_routes"
]