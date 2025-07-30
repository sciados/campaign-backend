"""
Campaign Routes Package - FINAL FIX
Following intelligence/routers pattern for modular organization
Ensures CRUD routes are properly included and exported
"""

from fastapi import APIRouter
import logging

# Create main campaigns router
router = APIRouter()

# ============================================================================
# ✅ SAFE IMPORT AND INCLUDE CRUD ROUTES (Priority #1)
# ============================================================================

def include_crud_routes():
    """Include CRUD routes with proper error handling"""
    try:
        from .campaign_crud import router as crud_router
        # Include CRUD routes at the ROOT level (no prefix)
        # This makes /api/campaigns/ work directly
        router.include_router(crud_router, tags=["campaigns-crud"])
        logging.info("✅ CRUD router included successfully")
        return True
    except ImportError as e:
        logging.error(f"❌ CRUD router import failed: {e}")
        return False
    except Exception as e:
        logging.error(f"❌ CRUD router inclusion failed: {e}")
        return False

# ============================================================================
# ✅ INCLUDE OTHER ROUTE MODULES
# ============================================================================

def include_other_routes():
    """Include other route modules safely"""
    included_count = 0
    
    # Include workflow operations
    try:
        from .workflow_operations import router as workflow_router
        router.include_router(workflow_router, tags=["campaigns-workflow"])
        logging.info("✅ Workflow operations router included")
        included_count += 1
    except ImportError as e:
        logging.warning(f"⚠️ Workflow operations router not available: {e}")
    
    # Include dashboard stats
    try:
        from .dashboard_stats import router as dashboard_router
        router.include_router(dashboard_router, tags=["campaigns-dashboard"])
        logging.info("✅ Dashboard stats router included")
        included_count += 1
    except ImportError as e:
        logging.warning(f"⚠️ Dashboard stats router not available: {e}")
    
    # Include admin endpoints
    try:
        from .admin_endpoints import router as admin_router
        router.include_router(admin_router, tags=["campaigns-admin"])
        logging.info("✅ Admin endpoints router included")
        included_count += 1
    except ImportError as e:
        logging.warning(f"⚠️ Admin endpoints router not available: {e}")
    
    # Include demo management
    try:
        from .demo_management import router as demo_router
        router.include_router(demo_router, tags=["campaigns-demo"])
        logging.info("✅ Demo management router included")
        included_count += 1
    except ImportError as e:
        logging.warning(f"⚠️ Demo management router not available: {e}")
    
    return included_count

# ============================================================================
# ✅ EXECUTE ROUTER SETUP
# ============================================================================

# Include CRUD routes first (highest priority)
crud_included = include_crud_routes()

# Include other routes
other_routes_count = include_other_routes()

# ============================================================================
# ✅ FALLBACK HEALTH ENDPOINTS
# ============================================================================

@router.get("/health")
async def campaigns_health():
    """Health check for campaigns router"""
    return {
        "status": "healthy",
        "module": "campaigns.routes",
        "crud_included": crud_included,
        "other_routes_count": other_routes_count,
        "total_routes": len(router.routes),
        "message": "Campaigns routes operational"
    }

@router.get("/import-status")
async def campaigns_import_status():
    """Detailed import status for debugging"""
    return {
        "campaigns_routes_status": "operational",
        "crud_router_included": crud_included,
        "other_routes_included": other_routes_count,
        "total_routes": len(router.routes),
        "expected_endpoints": [
            "GET /api/campaigns/ (list campaigns)",
            "POST /api/campaigns/ (create campaign)",
            "GET /api/campaigns/{id} (get campaign)",
            "PUT /api/campaigns/{id} (update campaign)",
            "DELETE /api/campaigns/{id} (delete campaign)"
        ] if crud_included else ["CRUD endpoints missing - check campaign_crud.py import"],
        "router_info": {
            "total_routes": len(router.routes),
            "router_type": str(type(router)),
            "available": True
        }
    }

# ============================================================================
# ✅ ADD MISSING FUNCTION FOR BACKWARDS COMPATIBILITY
# ============================================================================

def get_trigger_auto_analysis_task_fixed():
    """
    Safely get the auto analysis task function
    This prevents the circular import that was causing issues
    """
    try:
        # Try to import from the intelligence module
        from src.intelligence.tasks.auto_analysis import trigger_auto_analysis_task_fixed
        return trigger_auto_analysis_task_fixed
    except ImportError:
        # If not available, return a safe fallback function
        async def fallback_analysis_task(campaign_id: str, **kwargs):
            logging.warning(f"⚠️ Auto analysis task not available for campaign {campaign_id}")
            return {
                "success": False,
                "error": "Auto analysis task not available",
                "campaign_id": campaign_id,
                "fallback_used": True
            }
        return fallback_analysis_task

# Make the function available at module level for backwards compatibility
trigger_auto_analysis_task_fixed = get_trigger_auto_analysis_task_fixed()

# ============================================================================
# ✅ EXPORT EVERYTHING FOR BACKWARDS COMPATIBILITY
# ============================================================================

# Export the main router (this is what src/campaigns/__init__.py needs)
__all__ = [
    "router",  # Main export - this is critical!
    "trigger_auto_analysis_task_fixed",  # Prevent import errors
    "get_trigger_auto_analysis_task_fixed"
]

# Import modules for backwards compatibility (but safely)
try:
    from . import campaign_crud
except ImportError as e:
    logging.error(f"❌ campaign_crud import failed: {e}")

try:
    from . import demo_management
except ImportError as e:
    logging.error(f"❌ demo_management import failed: {e}")

try:
    from . import workflow_operations
except ImportError as e:
    logging.error(f"❌ workflow_operations import failed: {e}")

try:
    from . import dashboard_stats
except ImportError as e:
    logging.error(f"❌ dashboard_stats import failed: {e}")

try:
    from . import admin_endpoints
except ImportError as e:
    logging.error(f"❌ admin_endpoints import failed: {e}")

# Log final status
total_routes_registered = len(router.routes)
logging.info(f"📦 Campaigns routes package loaded successfully")
logging.info(f"🔗 Main campaigns router created with {total_routes_registered} routes")
logging.info(f"✅ CRUD router included: {crud_included}")
logging.info(f"📊 Other routes included: {other_routes_count}")

if not crud_included:
    logging.error("🚨 CRITICAL: CRUD router not included - dashboard will fail!")
    logging.error("🔧 Check campaign_crud.py import and dependencies")

if total_routes_registered < 5:
    logging.warning(f"⚠️ Low route count ({total_routes_registered}) - expected 10+ routes")
else:
    logging.info(f"🎯 Good route count: {total_routes_registered} routes registered")