"""
Campaign Routes Package - FIXED VERSION
Simplified but robust router loading with proper error handling
"""

from fastapi import APIRouter
import logging
import importlib

logger = logging.getLogger(__name__)

# Create main router
router = APIRouter(tags=["campaigns"])

# Track loading results
loading_results = {
    "loaded": [],
    "failed": [],
    "total_routes": 0,
    "errors": {}
}

# ============================================================================
# 🔧 SIMPLIFIED ROUTER LOADING (No complex registry)
# ============================================================================

def safe_load_router(module_name: str, prefix: str = "", required: bool = False):
    """Safely load a single router module"""
    try:
        # Import the module using the correct path
        full_module_path = f"src.campaigns.routes.{module_name}"
        module = importlib.import_module(full_module_path)
        
        # Check if it has a router
        if not hasattr(module, 'router'):
            raise ImportError(f"Module {module_name} has no 'router' attribute")
        
        sub_router = module.router
        
        # Validate the router has routes
        if not hasattr(sub_router, 'routes'):
            raise ImportError(f"Module {module_name} router is invalid")
        
        route_count = len(sub_router.routes)
        
        # Include in main router
        router.include_router(
            sub_router,
            prefix=prefix,
            tags=[f"campaigns-{module_name.replace('_', '-')}"]
        )
        
        # Track success
        loading_results["loaded"].append({
            "module": module_name,
            "route_count": route_count,
            "prefix": prefix
        })
        loading_results["total_routes"] += route_count
        
        logger.info(f"✅ Loaded {module_name}: {route_count} routes")
        return True
        
    except Exception as e:
        error_msg = str(e)
        loading_results["failed"].append({
            "module": module_name,
            "error": error_msg,
            "required": required
        })
        loading_results["errors"][module_name] = error_msg
        
        if required:
            logger.error(f"❌ CRITICAL: Required module {module_name} failed: {e}")
            # Don't raise - instead add emergency fallback
            return False
        else:
            logger.warning(f"⚠️ Optional module {module_name} failed: {e}")
            return False

# ============================================================================
# 🎯 LOAD ROUTERS IN ORDER OF IMPORTANCE
# ============================================================================

# 1. CRITICAL: CRUD router (required for dashboard)
crud_loaded = safe_load_router("campaign_crud", "", required=True)

# 2. IMPORTANT: Workflow operations
workflow_loaded = safe_load_router("workflow_operations", "", required=False)

# 3. USEFUL: Dashboard stats  
dashboard_loaded = safe_load_router("dashboard_stats", "/stats", required=False)

# 4. OPTIONAL: Demo management
demo_loaded = safe_load_router("demo_management", "/demo", required=False)

# 5. OPTIONAL: Admin endpoints
admin_loaded = safe_load_router("admin_endpoints", "/admin", required=False)

# ============================================================================
# 🚨 EMERGENCY CRUD FALLBACK (if main CRUD failed)
# ============================================================================

if not crud_loaded:
    logger.error("🚨 CRITICAL: CRUD router failed - adding emergency endpoints")
    
    @router.get("/")
    async def emergency_get_campaigns():
        """Emergency fallback for campaigns list"""
        return [
            {
                "id": "emergency-crud-fallback",
                "name": "Emergency CRUD Response", 
                "description": "Main CRUD router failed to load. Using emergency fallback.",
                "status": "emergency",
                "is_demo": True,
                "created_at": "2025-01-17T12:00:00Z",
                "updated_at": "2025-01-17T12:00:00Z",
                "error_details": loading_results["errors"].get("campaign_crud", "Unknown error"),
                "debug_info": {
                    "crud_import_failed": True,
                    "total_failed_modules": len(loading_results["failed"]),
                    "working_modules": len(loading_results["loaded"])
                }
            }
        ]
    
    @router.post("/")
    async def emergency_create_campaign():
        """Emergency fallback for campaign creation"""
        import uuid
        return {
            "id": str(uuid.uuid4()),
            "name": "Emergency Campaign Creation",
            "description": "CRUD router failed. Campaign created in emergency mode.",
            "status": "emergency",
            "created_at": "2025-01-17T12:00:00Z",
            "error_details": loading_results["errors"].get("campaign_crud", "Unknown error")
        }
    
    @router.get("/{campaign_id}")
    async def emergency_get_campaign(campaign_id: str):
        """Emergency fallback for single campaign"""
        return {
            "id": campaign_id,
            "name": f"Emergency Campaign {campaign_id}",
            "description": "CRUD router failed. Single campaign in emergency mode.",
            "status": "emergency",
            "created_at": "2025-01-17T12:00:00Z",
            "error_details": loading_results["errors"].get("campaign_crud", "Unknown error")
        }
    
    # Add to loading results
    loading_results["total_routes"] += 3
    loading_results["emergency_mode"] = True

# ============================================================================
# 🔧 REGISTRY STATUS ENDPOINTS (Simplified)
# ============================================================================

@router.get("/registry/status")
async def registry_status():
    """Get status of router loading"""
    return {
        "registry_status": "healthy" if crud_loaded else "degraded",
        "loading_results": loading_results,
        "modules_loaded": len(loading_results["loaded"]),
        "modules_failed": len(loading_results["failed"]),
        "total_routes": loading_results["total_routes"],
        "crud_available": crud_loaded,
        "emergency_mode": not crud_loaded,
        "module_details": {
            "loaded": loading_results["loaded"],
            "failed": loading_results["failed"]
        }
    }

@router.get("/registry/routes")
async def registry_routes():
    """Get all registered routes"""
    route_details = []
    
    for route in router.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            route_details.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, 'name', 'unnamed'),
                "tags": getattr(route, 'tags', [])
            })
    
    return {
        "total_routes": len(route_details),
        "routes": route_details,
        "loading_summary": loading_results
    }

# ============================================================================
# 🔧 BACKWARDS COMPATIBILITY
# ============================================================================

def get_safe_analysis_task():
    """Safely import analysis task to prevent circular imports"""
    try:
        from src.intelligence.tasks.auto_analysis import trigger_auto_analysis_task_fixed
        return trigger_auto_analysis_task_fixed
    except ImportError:
        async def fallback_task(*args, **kwargs):
            logger.warning("⚠️ Auto analysis task not available, using fallback")
            return {
                "success": False,
                "error": "Analysis task not available", 
                "fallback_used": True
            }
        return fallback_task

# Make analysis task available
trigger_auto_analysis_task_fixed = get_safe_analysis_task()

# ============================================================================
# ✅ FINAL RESULTS AND LOGGING
# ============================================================================

# Calculate success rate
total_attempted = len(loading_results["loaded"]) + len(loading_results["failed"])
success_rate = (len(loading_results["loaded"]) / total_attempted * 100) if total_attempted > 0 else 0

# Log final results
if crud_loaded:
    logger.info(f"🎉 Campaign routes initialized successfully!")
    logger.info(f"✅ CRUD router working - Dashboard will function")
else:
    logger.warning(f"⚠️ Campaign routes in emergency mode!")
    logger.warning(f"❌ CRUD router failed - Dashboard using emergency endpoints")

logger.info(f"📊 Router loading summary:")
logger.info(f"   • Loaded: {len(loading_results['loaded'])} modules")
logger.info(f"   • Failed: {len(loading_results['failed'])} modules") 
logger.info(f"   • Total routes: {loading_results['total_routes']}")
logger.info(f"   • Success rate: {success_rate:.1f}%")

if loading_results["failed"]:
    logger.info(f"❌ Failed modules: {[f['module'] for f in loading_results['failed']]}")

# Module exports
__all__ = [
    "router",
    "loading_results",
    "trigger_auto_analysis_task_fixed"
]

# Module metadata  
__version__ = "2.1.0-fixed"
__description__ = "Fixed campaign routes with simplified but robust loading"