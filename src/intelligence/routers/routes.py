"""
File: src/intelligence/routes.py
Main Intelligence Routes - Fixed Import Version
"""
from fastapi import APIRouter

# Import existing routers
from ..routers import (
    analysis_routes, 
    content_routes, 
    management_routes, 
    debug_routes
)

# Import the specific router objects from new files
from .universal_test_routes import universal_test_router
from .r2_debug_routes import debug_router as r2_debug_router

# Create main router
router = APIRouter(tags=["intelligence"])

# Include existing sub-routers
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

# Include new test routers
router.include_router(
    universal_test_router,
    tags=["universal-product-extraction"]
)

router.include_router(
    r2_debug_router,
    tags=["r2-debug"]
)