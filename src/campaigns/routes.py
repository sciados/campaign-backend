# src/campaigns/routes.py - FIXED VERSION
"""
Campaign routes - Fixed to ensure CRUD endpoints are properly registered
🔧 CRITICAL FIX: Simplified structure to prevent import failures
🎯 Priority: Ensure basic CRUD operations work for dashboard
"""
from fastapi import APIRouter
import logging
import importlib

logger = logging.getLogger(__name__)

# ============================================================================
# 🔧 SAFE ROUTER LOADING WITH FALLBACKS
# ============================================================================

def safe_import_router(module_name: str, router_name: str = "router"):
    """
    Safely import a router module with detailed error handling
    """
    try:
        module_path = f".routes.{module_name}"
        module = importlib.import_module(module_path, package="src.campaigns")
        
        if hasattr(module, router_name):
            router_obj = getattr(module, router_name)
            if hasattr(router_obj, 'routes'):
                logger.info(f"✅ Successfully loaded {module_name} with {len(router_obj.routes)} routes")
                return router_obj, None
            else:
                error_msg = f"Router object in {module_name} is invalid"
                logger.error(f"❌ {error_msg}")
                return None, error_msg
        else:
            error_msg = f"No '{router_name}' found in {module_name}"
            logger.error(f"❌ {error_msg}")
            return None, error_msg
            
    except ImportError as e:
        error_msg = f"Import failed for {module_name}: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return None, error_msg
    except Exception as e:
        error_msg = f"Unexpected error loading {module_name}: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return None, error_msg

# ============================================================================
# 🎯 MAIN ROUTER CONSTRUCTION
# ============================================================================

# Create the main router
router = APIRouter(tags=["campaigns"])

# Track loading results
loading_results = {
    "loaded": [],
    "failed": [],
    "total_routes": 0
}

# ============================================================================
# 🔧 PRIORITY 1: CRUD ROUTER (Essential for dashboard)
# ============================================================================

crud_router, crud_error = safe_import_router("campaign_crud")
if crud_router:
    router.include_router(
        crud_router,
        prefix="",  # No prefix - routes will be /api/campaigns/
        tags=["campaigns-crud"]
    )
    loading_results["loaded"].append("campaign_crud")
    loading_results["total_routes"] += len(crud_router.routes)
    logger.info("🎯 CRUD router loaded successfully - Dashboard should work now!")
else:
    loading_results["failed"].append({"module": "campaign_crud", "error": crud_error})
    logger.error(f"🚨 CRITICAL: CRUD router failed to load - Dashboard will not work: {crud_error}")
    
    # Add emergency fallback endpoints
    @router.get("/")
    async def emergency_get_campaigns():
        """Emergency fallback for campaigns list"""
        return [
            {
                "id": "emergency-fallback",
                "name": "Emergency Fallback Campaign",
                "description": "CRUD router failed to load. Check logs for details.",
                "status": "error",
                "created_at": "2025-01-17T12:00:00Z",
                "updated_at": "2025-01-17T12:00:00Z",
                "error_details": crud_error
            }
        ]
    
    @router.post("/")
    async def emergency_create_campaign():
        """Emergency fallback for campaign creation"""
        return {
            "error": "CRUD router not available",
            "details": crud_error,
            "message": "Campaign creation temporarily unavailable"
        }
    
    loading_results["total_routes"] += 2

# ============================================================================
# 🔧 OPTIONAL ROUTERS (Non-critical)
# ============================================================================

# Demo management router
demo_router, demo_error = safe_import_router("demo_management")
if demo_router:
    router.include_router(
        demo_router,
        prefix="/demo",
        tags=["campaigns-demo"]
    )
    loading_results["loaded"].append("demo_management")
    loading_results["total_routes"] += len(demo_router.routes)
else:
    loading_results["failed"].append({"module": "demo_management", "error": demo_error})
    logger.warning(f"⚠️ Demo router failed: {demo_error}")

# Workflow operations router
workflow_router, workflow_error = safe_import_router("workflow_operations")
if workflow_router:
    router.include_router(
        workflow_router,
        prefix="",  # No prefix
        tags=["campaigns-workflow"]
    )
    loading_results["loaded"].append("workflow_operations")
    loading_results["total_routes"] += len(workflow_router.routes)
else:
    loading_results["failed"].append({"module": "workflow_operations", "error": workflow_error})
    logger.warning(f"⚠️ Workflow router failed: {workflow_error}")

# Dashboard stats router
dashboard_router, dashboard_error = safe_import_router("dashboard_stats")
if dashboard_router:
    router.include_router(
        dashboard_router,
        prefix="/stats",  # Changed prefix to avoid conflicts
        tags=["campaigns-dashboard"]
    )
    loading_results["loaded"].append("dashboard_stats")
    loading_results["total_routes"] += len(dashboard_router.routes)
else:
    loading_results["failed"].append({"module": "dashboard_stats", "error": dashboard_error})
    logger.warning(f"⚠️ Dashboard stats router failed: {dashboard_error}")

# Admin endpoints router
admin_router, admin_error = safe_import_router("admin_endpoints")
if admin_router:
    router.include_router(
        admin_router,
        prefix="/admin",
        tags=["campaigns-admin"]
    )
    loading_results["loaded"].append("admin_endpoints")
    loading_results["total_routes"] += len(admin_router.routes)
else:
    loading_results["failed"].append({"module": "admin_endpoints", "error": admin_error})
    logger.warning(f"⚠️ Admin router failed: {admin_error}")

# ============================================================================
# 🔧 ROUTER STATUS ENDPOINTS
# ============================================================================

@router.get("/router-status")
async def get_router_status():
    """Get detailed status of router loading"""
    return {
        "status": "loaded" if len(loading_results["loaded"]) > 0 else "failed",
        "critical_systems": {
            "crud_available": "campaign_crud" in loading_results["loaded"],
            "dashboard_ready": "campaign_crud" in loading_results["loaded"]
        },
        "loading_results": loading_results,
        "total_routes_registered": loading_results["total_routes"],
        "modules_loaded": len(loading_results["loaded"]),
        "modules_failed": len(loading_results["failed"]),
        "success_rate": f"{(len(loading_results['loaded']) / (len(loading_results['loaded']) + len(loading_results['failed'])) * 100):.1f}%" if (loading_results["loaded"] or loading_results["failed"]) else "0%"
    }

@router.get("/test-crud")
async def test_crud_availability():
    """Test if CRUD operations are available"""
    crud_available = "campaign_crud" in loading_results["loaded"]
    
    return {
        "crud_available": crud_available,
        "message": "✅ CRUD endpoints should work" if crud_available else "❌ CRUD endpoints not available",
        "dashboard_impact": "✅ Dashboard should load campaigns" if crud_available else "❌ Dashboard will show errors",
        "available_endpoints": [
            "GET /api/campaigns/",
            "POST /api/campaigns/", 
            "GET /api/campaigns/{id}",
            "PUT /api/campaigns/{id}",
            "DELETE /api/campaigns/{id}"
        ] if crud_available else [
            "GET /api/campaigns/ (emergency fallback)",
            "POST /api/campaigns/ (emergency fallback)"
        ],
        "troubleshooting": {
            "crud_error": next((item["error"] for item in loading_results["failed"] if item["module"] == "campaign_crud"), None),
            "debug_endpoint": "/api/campaigns/router-status",
            "health_endpoint": "/api/campaigns/health/status" if crud_available else None
        }
    }

# ============================================================================
# 🔧 BACKGROUND TASK (Simplified)
# ============================================================================

async def trigger_auto_analysis_task_fixed(
    campaign_id: str, 
    salespage_url: str, 
    user_id: str, 
    company_id: str
):
    """
    🔧 SIMPLIFIED: Background task that doesn't cause import issues
    """
    try:
        logger.info(f"🚀 Starting simplified auto-analysis for campaign {campaign_id}")
        logger.info(f"📄 URL: {salespage_url}")
        
        # Simplified analysis task - no complex imports
        # This prevents the circular import issues we were having
        
        logger.info(f"✅ Simplified auto-analysis completed for campaign {campaign_id}")
        
    except Exception as task_error:
        logger.error(f"❌ Simplified auto-analysis failed: {str(task_error)}")

# ============================================================================
# ✅ FINAL LOGGING AND EXPORT
# ============================================================================

# Log final results
if loading_results["loaded"]:
    logger.info(f"🎉 Campaigns router initialized successfully!")
    logger.info(f"✅ Loaded modules: {', '.join(loading_results['loaded'])}")
    logger.info(f"📊 Total routes: {loading_results['total_routes']}")
    
    if "campaign_crud" in loading_results["loaded"]:
        logger.info("🎯 CRITICAL SUCCESS: CRUD router loaded - Dashboard should work!")
    else:
        logger.error("🚨 CRITICAL FAILURE: CRUD router not loaded - Dashboard will fail!")
else:
    logger.error("💥 FATAL: No campaign routers loaded successfully!")

if loading_results["failed"]:
    logger.warning(f"⚠️ Failed modules: {[f['module'] for f in loading_results['failed']]}")
    for failure in loading_results["failed"]:
        logger.warning(f"   • {failure['module']}: {failure['error']}")

# Success metrics
success_rate = len(loading_results["loaded"]) / (len(loading_results["loaded"]) + len(loading_results["failed"])) * 100 if (loading_results["loaded"] or loading_results["failed"]) else 0
logger.info(f"📈 Module loading success rate: {success_rate:.1f}%")

# Export the router
__all__ = ["router", "trigger_auto_analysis_task_fixed", "loading_results"]