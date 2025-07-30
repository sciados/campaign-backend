"""
Campaign Routes Package - Production Ready Architecture
Clean, maintainable, and properly structured for long-term use
"""

from fastapi import APIRouter
from typing import Dict, List, Optional
import logging
import importlib

logger = logging.getLogger(__name__)

class CampaignRouterRegistry:
    """
    Router Registry Pattern for Campaign Routes
    Manages route module loading with proper error handling and monitoring
    """
    
    def __init__(self):
        self.modules: Dict[str, dict] = {}
        self.main_router = APIRouter()
        self.loaded_count = 0
        self.failed_count = 0
    
    def register_module(self, name: str, module_name: str, required: bool = False, prefix: str = ""):
        """Register a route module for loading"""
        self.modules[name] = {
            "module_name": module_name,
            "required": required,
            "prefix": prefix,
            "loaded": False,
            "router": None,
            "error": None,
            "route_count": 0
        }
    
    def _load_single_module(self, name: str) -> bool:
        """Load and validate a single route module"""
        module_info = self.modules[name]
        
        try:
            # Import the module
            module = importlib.import_module(f".{module_info['module_name']}", package="src.campaigns.routes")
            
            # Validate it has a router
            if not hasattr(module, 'router'):
                raise ImportError(f"Module {module_info['module_name']} missing 'router' attribute")
            
            if not hasattr(module.router, 'routes'):
                raise ImportError(f"Module {module_info['module_name']} router is invalid")
            
            # Store the router and metadata
            module_info['router'] = module.router
            module_info['loaded'] = True
            module_info['error'] = None
            module_info['route_count'] = len(module.router.routes)
            
            logger.info(f"✅ Loaded {name}: {module_info['route_count']} routes")
            return True
            
        except Exception as e:
            module_info['error'] = str(e)
            module_info['loaded'] = False
            
            if module_info['required']:
                logger.error(f"❌ CRITICAL: Required module '{name}' failed: {e}")
                raise RuntimeError(f"Critical module {name} failed to load: {e}")
            else:
                logger.warning(f"⚠️ Optional module '{name}' failed: {e}")
                return False
    
    def build_router(self) -> APIRouter:
        """Build the main router with all registered modules"""
        
        for name, module_info in self.modules.items():
            try:
                if self._load_single_module(name):
                    # Include the router in main router
                    self.main_router.include_router(
                        module_info['router'],
                        prefix=module_info['prefix'],
                        tags=[f"campaigns-{name}"]
                    )
                    self.loaded_count += 1
                    logger.info(f"✅ Included {name} router with {module_info['route_count']} routes")
                else:
                    self.failed_count += 1
                    
            except Exception as e:
                self.failed_count += 1
                logger.error(f"❌ Failed to include {name}: {e}")
                
                # For critical modules, this will have already raised an exception
                # For optional modules, we continue
        
        # Add registry status endpoints
        self._add_registry_endpoints()
        
        total_routes = len(self.main_router.routes)
        logger.info(f"📦 Router registry complete: {self.loaded_count} loaded, {self.failed_count} failed, {total_routes} total routes")
        
        return self.main_router
    
    def _add_registry_endpoints(self):
        """Add endpoints for monitoring the registry status"""
        
        @self.main_router.get("/registry/status")
        async def registry_status():
            """Get detailed status of all registered modules"""
            return {
                "registry_status": "healthy",
                "total_modules": len(self.modules),
                "loaded_modules": self.loaded_count,
                "failed_modules": self.failed_count,
                "total_routes": len(self.main_router.routes),
                "modules": {
                    name: {
                        "loaded": info['loaded'],
                        "required": info['required'],
                        "route_count": info['route_count'],
                        "error": info['error'] if info['error'] else None
                    }
                    for name, info in self.modules.items()
                }
            }
        
        @self.main_router.get("/registry/routes")
        async def registry_routes():
            """Get detailed information about all registered routes"""
            route_details = []
            
            for route in self.main_router.routes:
                if hasattr(route, 'path') and hasattr(route, 'methods'):
                    route_details.append({
                        "path": route.path,
                        "methods": list(route.methods),
                        "name": getattr(route, 'name', 'unnamed'),
                        "tags": getattr(route, 'tags', [])
                    })
            
            return {
                "total_routes": len(route_details),
                "routes": route_details
            }

# ============================================================================
# ✅ INITIALIZE REGISTRY AND REGISTER MODULES
# ============================================================================

# Create the registry
registry = CampaignRouterRegistry()

# Register all campaign route modules
# CRUD is marked as required since dashboard depends on it
registry.register_module("crud", "campaign_crud", required=True)
registry.register_module("workflow", "workflow_operations", required=False)
registry.register_module("dashboard", "dashboard_stats", required=False)
registry.register_module("admin", "admin_endpoints", required=False)
registry.register_module("demo", "demo_management", required=False)

# Build the main router
try:
    router = registry.build_router()
    logger.info("🎉 Campaign routes successfully initialized")
except Exception as e:
    logger.error(f"💥 FATAL: Campaign routes initialization failed: {e}")
    # Create a minimal fallback router
    router = APIRouter()
    
    @router.get("/error")
    async def initialization_error():
        return {
            "error": "Campaign routes failed to initialize",
            "details": str(e),
            "status": "failed"
        }

# ============================================================================
# ✅ BACKWARDS COMPATIBILITY AND UTILITIES
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

# Make analysis task available for backwards compatibility
trigger_auto_analysis_task_fixed = get_safe_analysis_task()

# ============================================================================
# ✅ MODULE EXPORTS
# ============================================================================

__all__ = [
    "router",
    "registry", 
    "trigger_auto_analysis_task_fixed"
]

# Module metadata
__version__ = "2.0.0"
__description__ = "Campaign routes with production-ready registry pattern"

# Import modules for backwards compatibility (safe imports)
campaign_crud = None
workflow_operations = None
dashboard_stats = None
admin_endpoints = None
demo_management = None

for module_name in ["campaign_crud", "workflow_operations", "dashboard_stats", "admin_endpoints", "demo_management"]:
    try:
        imported_module = importlib.import_module(f".{module_name}", package="src.campaigns.routes")
        globals()[module_name] = imported_module
    except ImportError as e:
        logger.warning(f"⚠️ Could not import {module_name} for backwards compatibility: {e}")

logger.info(f"📦 Campaign routes package loaded (v{__version__})")