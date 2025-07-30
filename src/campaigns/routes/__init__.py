"""
Campaign Routes Package
Following intelligence/routers pattern for modular organization
FIXED VERSION - Resolves circular import and missing router export
"""

from fastapi import APIRouter
import logging

# Create main campaigns router
router = APIRouter()

# ============================================================================
# ✅ SAFE MODULE IMPORTS (Prevent Circular Import)
# ============================================================================

def safe_import_route_module(module_name: str, router_instance: APIRouter):
    """
    Safely import and include a route module
    If import fails, log error but continue with other modules
    """
    try:
        if module_name == "campaign_crud":
            from . import campaign_crud
            if hasattr(campaign_crud, 'router'):
                router_instance.include_router(campaign_crud.router, tags=[f"campaigns-{module_name}"])
                logging.info(f"✅ {module_name} router included successfully")
                return True
            else:
                logging.warning(f"⚠️ {module_name} has no router attribute")
                return False
                
        elif module_name == "demo_management":
            from . import demo_management
            if hasattr(demo_management, 'router'):
                router_instance.include_router(demo_management.router, tags=[f"campaigns-{module_name}"])
                logging.info(f"✅ {module_name} router included successfully")
                return True
            else:
                logging.warning(f"⚠️ {module_name} has no router attribute")
                return False
                
        elif module_name == "workflow_operations":
            from . import workflow_operations
            if hasattr(workflow_operations, 'router'):
                router_instance.include_router(workflow_operations.router, tags=[f"campaigns-{module_name}"])
                logging.info(f"✅ {module_name} router included successfully")
                return True
            else:
                logging.warning(f"⚠️ {module_name} has no router attribute")
                return False
                
        elif module_name == "dashboard_stats":
            from . import dashboard_stats
            if hasattr(dashboard_stats, 'router'):
                router_instance.include_router(dashboard_stats.router, tags=[f"campaigns-{module_name}"])
                logging.info(f"✅ {module_name} router included successfully")
                return True
            else:
                logging.warning(f"⚠️ {module_name} has no router attribute")
                return False
                
        elif module_name == "admin_endpoints":
            from . import admin_endpoints
            if hasattr(admin_endpoints, 'router'):
                router_instance.include_router(admin_endpoints.router, tags=[f"campaigns-{module_name}"])
                logging.info(f"✅ {module_name} router included successfully")
                return True
            else:
                logging.warning(f"⚠️ {module_name} has no router attribute")
                return False
                
    except ImportError as e:
        logging.error(f"❌ Failed to import {module_name}: {e}")
        return False
    except Exception as e:
        logging.error(f"❌ Unexpected error with {module_name}: {e}")
        return False

# ============================================================================
# ✅ BUILD MAIN ROUTER
# ============================================================================

# List of route modules to include
route_modules = [
    "campaign_crud",
    "demo_management", 
    "workflow_operations",
    "dashboard_stats",
    "admin_endpoints"
]

# Track successful imports
successful_imports = 0
failed_imports = []

# Import each module safely
for module_name in route_modules:
    if safe_import_route_module(module_name, router):
        successful_imports += 1
    else:
        failed_imports.append(module_name)

# ============================================================================
# ✅ FALLBACK ROUTES (Always Available)
# ============================================================================

@router.get("/health")
async def campaigns_health():
    """Health check for campaigns router"""
    return {
        "status": "healthy",
        "module": "campaigns.routes",
        "successful_imports": successful_imports,
        "failed_imports": failed_imports,
        "total_routes": len(router.routes),
        "message": "Campaigns routes operational"
    }

@router.get("/import-status")
async def campaigns_import_status():
    """Detailed import status for debugging"""
    return {
        "campaigns_routes_status": "operational",
        "successful_modules": successful_imports,
        "failed_modules": failed_imports,
        "total_modules": len(route_modules),
        "success_rate": f"{(successful_imports/len(route_modules)*100):.1f}%",
        "router_info": {
            "total_routes": len(router.routes),
            "router_type": str(type(router)),
            "available": True
        }
    }

# ============================================================================
# ✅ PROVIDE MISSING FUNCTION (Prevent Import Errors)
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
        async def fallback_analysis_task(campaign_id: int, **kwargs):
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
# ✅ EXPORT EVERYTHING
# ============================================================================

# Export the main router (this is what src/campaigns/__init__.py needs)
__all__ = [
    "router",  # Main export - this was missing!
    "campaign_crud",
    "demo_management",
    "workflow_operations", 
    "dashboard_stats",
    "admin_endpoints",
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
logging.info(f"📦 Campaigns routes package loaded: {successful_imports}/{len(route_modules)} modules successful")
logging.info(f"🔗 Main campaigns router created with {len(router.routes)} routes")

if failed_imports:
    logging.warning(f"⚠️ Failed to import: {', '.join(failed_imports)}")