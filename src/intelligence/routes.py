"""
File: src/intelligence/routes.py
Main Intelligence Routes - Updated with Ultra-Cheap AI and Storage Integration
"""
from fastapi import APIRouter

# Import all existing routers
from .routers import (
    analysis_routes, 
    content_routes, 
    management_routes, 
    debug_routes,
    clickbank_routes
)

# Import the Stability AI routes (already exists)
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

router.include_router(
    clickbank_routes.router,
    prefix="/clickbank",
    tags=["clickbank"]
)

# ✅ EXISTING: Include Stability AI routes if available
if STABILITY_ROUTES_AVAILABLE:
    router.include_router(
        stability_routes.router,
        prefix="/stability",
        tags=["stability-ai-images"]
    )