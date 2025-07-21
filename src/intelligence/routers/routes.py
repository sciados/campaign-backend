"""
File: src/intelligence/routes.py
Main Intelligence Routes - Refactored Version
Reduced from 1000+ lines to ~50 lines
"""
from fastapi import APIRouter

from intelligence.routers import analysis_routes, content_routes, management_routes, debug_routes, universal_test_routes

# Create main router
router = APIRouter(tags=["intelligence"])

# Include sub-routers with proper prefixes
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
    universal_test_routes.router,
    prefix="/universal",
    tags=["intelligence-test"]
)
