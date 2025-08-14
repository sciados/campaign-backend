# src/intelligence/routers/__init__.py
"""
Intelligence Routers Package - CORRECTED IMPORTS
"""

# Import the actual router modules that exist according to the sitemap
try:
    from . import analysis_routes
    ANALYSIS_ROUTES_AVAILABLE = True
except ImportError:
    ANALYSIS_ROUTES_AVAILABLE = False
    analysis_routes = None

try:
    from . import content_routes  
    CONTENT_ROUTES_AVAILABLE = True
except ImportError:
    CONTENT_ROUTES_AVAILABLE = False
    content_routes = None

try:
    from . import management_routes
    MANAGEMENT_ROUTES_AVAILABLE = True
except ImportError:
    MANAGEMENT_ROUTES_AVAILABLE = False
    management_routes = None

try:
    from . import debug_routes
    DEBUG_ROUTES_AVAILABLE = True
except ImportError:
    DEBUG_ROUTES_AVAILABLE = False
    debug_routes = None

# Enhanced email routes (if it exists)
try:
    from .enhanced_email_routes import router as enhanced_email_router
    ENHANCED_EMAIL_ROUTER_AVAILABLE = True
except ImportError:
    ENHANCED_EMAIL_ROUTER_AVAILABLE = False
    enhanced_email_router = None

__all__ = []

if ANALYSIS_ROUTES_AVAILABLE:
    __all__.append("analysis_routes")
if CONTENT_ROUTES_AVAILABLE:
    __all__.append("content_routes")
if MANAGEMENT_ROUTES_AVAILABLE:
    __all__.append("management_routes")
if DEBUG_ROUTES_AVAILABLE:
    __all__.append("debug_routes")
if ENHANCED_EMAIL_ROUTER_AVAILABLE:
    __all__.append("enhanced_email_router")