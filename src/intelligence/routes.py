"""
File: src/intelligence/routes.py
Main Intelligence Routes - FIXED conditional imports to match routers/__init__.py
"""
from fastapi import APIRouter

# Import routers conditionally to match the routers/__init__.py pattern
try:
    from .routers import analysis_routes
    ANALYSIS_ROUTES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Analysis routes not available: {e}")
    ANALYSIS_ROUTES_AVAILABLE = False
    analysis_routes = None

try:
    from .routers import content_routes
    CONTENT_ROUTES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Content routes not available: {e}")
    CONTENT_ROUTES_AVAILABLE = False
    content_routes = None

try:
    from .routers import management_routes
    MANAGEMENT_ROUTES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Management routes not available: {e}")
    MANAGEMENT_ROUTES_AVAILABLE = False
    management_routes = None

try:
    from .routers import debug_routes
    DEBUG_ROUTES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Debug routes not available: {e}")
    DEBUG_ROUTES_AVAILABLE = False
    debug_routes = None

# Import enhanced email routes
try:
    from .routers.enhanced_email_routes import router as enhanced_email_router
    ENHANCED_EMAIL_ROUTES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Enhanced email routes not available: {e}")
    ENHANCED_EMAIL_ROUTES_AVAILABLE = False
    enhanced_email_router = None

# Import stability routes
try:
    from .routers import stability_routes
    STABILITY_ROUTES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Stability routes not available: {e}")
    STABILITY_ROUTES_AVAILABLE = False
    stability_routes = None

# Create main router
router = APIRouter(tags=["intelligence"])

# Include sub-routers only if they're available
if ANALYSIS_ROUTES_AVAILABLE and analysis_routes:
    router.include_router(
        analysis_routes.router,
        prefix="/analysis",
        tags=["intelligence-analysis"]
    )
    print("✅ Analysis routes included")

if CONTENT_ROUTES_AVAILABLE and content_routes:
    router.include_router(
        content_routes.router,
        prefix="/content", 
        tags=["intelligence-content"]
    )
    print("✅ Content routes included")

if MANAGEMENT_ROUTES_AVAILABLE and management_routes:
    router.include_router(
        management_routes.router,
        prefix="/management",
        tags=["intelligence-management"]
    )
    print("✅ Management routes included")

if DEBUG_ROUTES_AVAILABLE and debug_routes:
    router.include_router(
        debug_routes.router,
        prefix="/debug",
        tags=["intelligence-debug"]
    )
    print("✅ Debug routes included")

if ENHANCED_EMAIL_ROUTES_AVAILABLE and enhanced_email_router:
    router.include_router(
        enhanced_email_router, 
        prefix="/emails",
        tags=["Enhanced Email Generation"]
    )
    print("✅ Enhanced email routes included")

if STABILITY_ROUTES_AVAILABLE and stability_routes:
    router.include_router(
        stability_routes.router,
        prefix="/stability",
        tags=["stability-ai-images"]
    )
    print("✅ Stability routes included")

print(f"🎯 Intelligence main router created with {len(router.routes)} total routes")