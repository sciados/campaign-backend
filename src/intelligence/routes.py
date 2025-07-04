"""
File: src/intelligence/routes.py
Main Intelligence Routes - Updated with Stability AI Integration
"""
from fastapi import APIRouter

# Import all existing routers
from .routers import (
    analysis_routes, 
    content_routes, 
    management_routes, 
    debug_routes
)

# Import the new Stability AI routes (create this file)
try:
    from .routers import stability_routes
    STABILITY_ROUTES_AVAILABLE = True
except ImportError:
    STABILITY_ROUTES_AVAILABLE = False

# Create main router
router = APIRouter(tags=["intelligence"])

# Include existing sub-routers with proper prefixes
router.include_router(
    analysis_routes.router,
    prefix="/analysis",
    tags=["intelligence-analysis"]
)

router.include_router(
    content_routes.router,
    prefix="/content",
    tags=["intelligence-content"]
)

router.include_router(
    management_routes.router,
    prefix="/management",
    tags=["intelligence-management"]
)

router.include_router(
    debug_routes.router,
    prefix="/debug",
    tags=["intelligence-debug"]
)

# ✅ NEW: Include Stability AI routes if available
if STABILITY_ROUTES_AVAILABLE:
    router.include_router(
        stability_routes.router,
        prefix="/stability",
        tags=["stability-ai-images"]
    )