"""
File: src/intelligence/routes.py
DEBUG VERSION - Intelligence Routes with detailed logging
"""
from fastapi import APIRouter

print("🔧 DEBUG: Starting intelligence routes import...")

# Import routers conditionally with detailed logging
try:
    from .routers import analysis_routes
    ANALYSIS_ROUTES_AVAILABLE = True
    print("✅ DEBUG: Analysis routes imported successfully")
except ImportError as e:
    print(f"❌ DEBUG: Analysis routes import failed: {e}")
    ANALYSIS_ROUTES_AVAILABLE = False
    analysis_routes = None

try:
    from .routers import content_routes
    CONTENT_ROUTES_AVAILABLE = True
    print(f"✅ DEBUG: Content routes imported successfully")
    print(f"🔧 DEBUG: content_routes object: {content_routes}")
    print(f"🔧 DEBUG: content_routes.router exists: {hasattr(content_routes, 'router')}")
    if hasattr(content_routes, 'router'):
        print(f"🔧 DEBUG: content_routes.router routes: {len(content_routes.router.routes)}")
        for route in content_routes.router.routes:
            print(f"🔧 DEBUG: Content route found: {route.methods} {route.path}")
except ImportError as e:
    print(f"❌ DEBUG: Content routes import failed: {e}")
    CONTENT_ROUTES_AVAILABLE = False
    content_routes = None

try:
    from .routers import management_routes
    MANAGEMENT_ROUTES_AVAILABLE = True
    print("✅ DEBUG: Management routes imported successfully")
except ImportError as e:
    print(f"❌ DEBUG: Management routes import failed: {e}")
    MANAGEMENT_ROUTES_AVAILABLE = False
    management_routes = None

try:
    from .routers import debug_routes
    DEBUG_ROUTES_AVAILABLE = True
    print("✅ DEBUG: Debug routes imported successfully")
except ImportError as e:
    print(f"❌ DEBUG: Debug routes import failed: {e}")
    DEBUG_ROUTES_AVAILABLE = False
    debug_routes = None

# Import enhanced email routes
try:
    from .routers.enhanced_email_routes import router as enhanced_email_router
    ENHANCED_EMAIL_ROUTES_AVAILABLE = True
    print("✅ DEBUG: Enhanced email routes imported successfully")
except ImportError as e:
    print(f"❌ DEBUG: Enhanced email routes import failed: {e}")
    ENHANCED_EMAIL_ROUTES_AVAILABLE = False
    enhanced_email_router = None

# Import stability routes
try:
    from .routers import stability_routes
    STABILITY_ROUTES_AVAILABLE = True
    print("✅ DEBUG: Stability routes imported successfully")
except ImportError as e:
    print(f"❌ DEBUG: Stability routes import failed: {e}")
    STABILITY_ROUTES_AVAILABLE = False
    stability_routes = None

# Create main router
router = APIRouter(tags=["intelligence"])
print("🔧 DEBUG: Created main intelligence router")

# Include sub-routers only if they're available
if ANALYSIS_ROUTES_AVAILABLE and analysis_routes:
    router.include_router(
        analysis_routes.router,
        prefix="/analysis",
        tags=["intelligence-analysis"]
    )
    print("✅ DEBUG: Analysis routes included in main router")
else:
    print("❌ DEBUG: Analysis routes NOT included - not available or None")

if CONTENT_ROUTES_AVAILABLE and content_routes:
    print(f"🔧 DEBUG: About to include content routes...")
    print(f"🔧 DEBUG: CONTENT_ROUTES_AVAILABLE = {CONTENT_ROUTES_AVAILABLE}")
    print(f"🔧 DEBUG: content_routes = {content_routes}")
    print(f"🔧 DEBUG: content_routes is not None = {content_routes is not None}")
    
    if hasattr(content_routes, 'router'):
        print(f"🔧 DEBUG: content_routes.router = {content_routes.router}")
        print(f"🔧 DEBUG: content_routes.router routes count = {len(content_routes.router.routes)}")
        
        router.include_router(
            content_routes.router,
            prefix="/content", 
            tags=["intelligence-content"]
        )
        print("✅ DEBUG: Content routes included in main router")
    else:
        print("❌ DEBUG: content_routes has no 'router' attribute")
else:
    print(f"❌ DEBUG: Content routes NOT included")
    print(f"🔧 DEBUG: CONTENT_ROUTES_AVAILABLE = {CONTENT_ROUTES_AVAILABLE}")
    print(f"🔧 DEBUG: content_routes = {content_routes}")

if MANAGEMENT_ROUTES_AVAILABLE and management_routes:
    router.include_router(
        management_routes.router,
        prefix="/management",
        tags=["intelligence-management"]
    )
    print("✅ DEBUG: Management routes included in main router")
else:
    print("❌ DEBUG: Management routes NOT included - not available or None")

if DEBUG_ROUTES_AVAILABLE and debug_routes:
    router.include_router(
        debug_routes.router,
        prefix="/debug",
        tags=["intelligence-debug"]
    )
    print("✅ DEBUG: Debug routes included in main router")
else:
    print("❌ DEBUG: Debug routes NOT included - not available or None")

if ENHANCED_EMAIL_ROUTES_AVAILABLE and enhanced_email_router:
    router.include_router(
        enhanced_email_router, 
        prefix="/emails",
        tags=["Enhanced Email Generation"]
    )
    print("✅ DEBUG: Enhanced email routes included in main router")
else:
    print("❌ DEBUG: Enhanced email routes NOT included - not available or None")

if STABILITY_ROUTES_AVAILABLE and stability_routes:
    router.include_router(
        stability_routes.router,
        prefix="/stability",
        tags=["stability-ai-images"]
    )
    print("✅ DEBUG: Stability routes included in main router")
else:
    print("❌ DEBUG: Stability routes NOT included - not available or None")

print(f"🎯 DEBUG: Final intelligence router created with {len(router.routes)} total routes")
for route in router.routes:
    print(f"🎯 DEBUG: Final route: {route.methods} {route.path}")
print("🔧 DEBUG: Intelligence routes module completed")