"""
File: src/intelligence/routes.py
Main Intelligence Routes - Updated with Ultra-Cheap AI and Storage Integration
"""
from fastapi import APIRouter
from .routers.enhanced_email_routes import router as enhanced_email_router
from .routers import enhanced_intelligence_routes

# Import all existing routers
from .routers import (
    analysis_routes, 
    content_routes, 
    management_routes, 
    debug_routes
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

# ✅ ADD THE NEW ENHANCED EMAIL ROUTES
router.include_router(
    enhanced_email_router, 
    prefix="/emails",  # This makes endpoints like /emails/enhanced-emails/generate
    tags=["Enhanced Email Generation"]
)

router.include_router(
    enhanced_intelligence_routes.router,
    prefix="/campaigns",
    tags=["intelligence-campaigns"]
)

# ✅ EXISTING: Include Stability AI routes if available
if STABILITY_ROUTES_AVAILABLE:
    router.include_router(
        stability_routes.router,
        prefix="/stability",
        tags=["stability-ai-images"]
    )