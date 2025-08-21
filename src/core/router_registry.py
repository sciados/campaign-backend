# src/core/router_registry.py - Router Management
"""
All router imports, registration, and availability tracking
Responsibility: Router imports with error handling, Router availability flags,
Router registration logic with prefixes, Debug route counting and logging,
Router status tracking variables, Import error debugging and fallback logic
"""

import logging
import traceback
from fastapi import FastAPI

logger = logging.getLogger(__name__)

# ============================================================================
# ✅ ROUTER AVAILABILITY FLAGS
# ============================================================================

# Core router flags
AUTH_ROUTER_AVAILABLE = False
CAMPAIGNS_ROUTER_AVAILABLE = False
DASHBOARD_ROUTER_AVAILABLE = False
ADMIN_ROUTER_AVAILABLE = False
WAITLIST_ROUTER_AVAILABLE = False
DYNAMIC_AI_PROVIDERS_ROUTER_AVAILABLE = False
AI_DISCOVERY_ROUTER_AVAILABLE = False

# Intelligence router flags
INTELLIGENCE_ROUTERS_AVAILABLE = False
INTELLIGENCE_MAIN_ROUTER_AVAILABLE = False
ANALYSIS_ROUTER_AVAILABLE = False
AFFILIATE_ROUTER_AVAILABLE = False
CONTENT_ROUTER_AVAILABLE = False
ENHANCED_EMAIL_ROUTER_AVAILABLE = False
STABILITY_ROUTER_AVAILABLE = False
STORAGE_ROUTER_AVAILABLE = False
DOCUMENT_ROUTER_AVAILABLE = False
AI_MONITORING_ROUTER_AVAILABLE = False

# System status flags
EMAIL_MODELS_AVAILABLE = False
STORAGE_SYSTEM_AVAILABLE = False
EMAIL_SYSTEM_AVAILABLE = False

# Router instances
auth_router = None
campaigns_router = None
dashboard_router = None
admin_router = None
waitlist_router = None
dynamic_ai_providers_router = None
ai_discovery_router = None
intelligence_main_router = None
content_router = None
enhanced_email_router = None
analysis_router = None
stability_router = None
storage_router = None
document_router = None
include_ai_monitoring_routes = None

# ============================================================================
# ✅ IMPORT CORE ROUTERS
# ============================================================================

def import_core_routers():
    """Import core application routers with error handling"""
    global AUTH_ROUTER_AVAILABLE, auth_router
    global CAMPAIGNS_ROUTER_AVAILABLE, campaigns_router
    global DASHBOARD_ROUTER_AVAILABLE, dashboard_router
    global ADMIN_ROUTER_AVAILABLE, admin_router
    global WAITLIST_ROUTER_AVAILABLE, waitlist_router
    global DYNAMIC_AI_PROVIDERS_ROUTER_AVAILABLE, dynamic_ai_providers_router
    global AI_DISCOVERY_ROUTER_AVAILABLE, ai_discovery_router
    
    # Import core models first
    try:
        from src.models.campaign import Campaign
        from src.models import CampaignAsset
        from src.models.intelligence import CampaignIntelligence
        from src.models.user import User
        from src.models.company import Company
        logging.info("✅ Campaign models imported successfully")
    except ImportError as e:
        logging.warning(f"⚠️ Campaign models not available: {e}")

    # Import auth router
    try:
        from src.auth.routes import router as auth_router
        logging.info("✅ Auth router imported successfully")
        AUTH_ROUTER_AVAILABLE = True
    except ImportError as e:
        logging.error(f"❌ Auth router not available: {e}")

    # Import campaigns router with detailed error handling
    try:
        from src.campaigns.routes import router as campaigns_router
        CAMPAIGNS_ROUTER_AVAILABLE = True
        logging.info("✅ Campaigns router imported successfully")
    except ImportError as e:
        logging.error(f"❌ Campaigns router not available: {e}")
        
        # Debug each component individually
        debug_campaigns_import()

    # Import dashboard router
    try:
        from src.dashboard.routes import router as dashboard_router
        logging.info("✅ Dashboard router imported successfully")
        DASHBOARD_ROUTER_AVAILABLE = True
    except ImportError as e:
        logging.warning(f"⚠️ Dashboard router not available: {e}")

    # Import admin router
    try:
        from src.admin.routes import router as admin_router
        logging.info("✅ Admin router imported successfully")
        ADMIN_ROUTER_AVAILABLE = True
    except ImportError as e:
        logging.warning(f"⚠️ Admin router not available: {e}")

    # Import waitlist router
    try:
        from src.routes.waitlist import router as waitlist_router
        logging.info("✅ Waitlist router imported successfully")
        WAITLIST_ROUTER_AVAILABLE = True
    except ImportError as e:
        logging.warning(f"⚠️ Waitlist router not available: {e}")

    # Import dynamic AI providers router
    try:
        from src.routes.dynamic_ai_providers import router as dynamic_ai_providers_router
        logging.info("✅ Dynamic AI providers router imported successfully")
        DYNAMIC_AI_PROVIDERS_ROUTER_AVAILABLE = True
    except ImportError as e:
        logging.warning(f"⚠️ Dynamic AI providers router not available: {e}")

    # Import AI Discovery router
    try:
        from src.routes.ai_platform_discovery import router as ai_discovery_router
        logging.info("✅ AI Platform Discovery System router imported successfully")
        AI_DISCOVERY_ROUTER_AVAILABLE = True
    except ImportError as e:
        logging.warning(f"⚠️ AI Platform Discovery System router not available: {e}")

def debug_campaigns_import():
    """Debug campaigns router import issues"""
    try:
        import src.campaigns
        logging.info("✅ src.campaigns module imports OK")
    except ImportError as campaigns_err:
        logging.error(f"❌ src.campaigns module failed: {campaigns_err}")
    
    try:
        import src.campaigns.schemas
        logging.info("✅ src.campaigns.schemas imports OK")
    except ImportError as schemas_err:
        logging.error(f"❌ src.campaigns.schemas failed: {schemas_err}")
    
    try:
        import src.campaigns.services
        logging.info("✅ src.campaigns.services imports OK")
    except ImportError as services_err:
        logging.error(f"❌ src.campaigns.services failed: {services_err}")
    
    # Test individual route files
    route_files = [
        "campaign_crud",
        "demo_management", 
        "workflow_operations",
        "dashboard_stats",
        "admin_endpoints"
    ]
    
    for route_file in route_files:
        try:
            module_path = f"src.campaigns.routes.{route_file}"
            __import__(module_path)
            logging.info(f"✅ {module_path} imports OK")
        except ImportError as route_err:
            logging.error(f"❌ {module_path} failed: {route_err}")
    
    try:
        import src.campaigns.routes
        logging.info("✅ src.campaigns.routes imports OK")
    except ImportError as routes_err:
        logging.error(f"❌ src.campaigns.routes failed: {routes_err}")
    
    logging.error(f"❌ Full traceback: {traceback.format_exc()}")

# ============================================================================
# ✅ IMPORT INTELLIGENCE ROUTERS
# ============================================================================

def import_intelligence_routers():
    """Import intelligence and AI-related routers"""
    global INTELLIGENCE_MAIN_ROUTER_AVAILABLE, intelligence_main_router
    global CONTENT_ROUTER_AVAILABLE, content_router
    global ENHANCED_EMAIL_ROUTER_AVAILABLE, enhanced_email_router
    global ANALYSIS_ROUTER_AVAILABLE, analysis_router
    global STABILITY_ROUTER_AVAILABLE, stability_router
    global STORAGE_ROUTER_AVAILABLE, storage_router
    global DOCUMENT_ROUTER_AVAILABLE, document_router
    global AI_MONITORING_ROUTER_AVAILABLE, include_ai_monitoring_routes
    global EMAIL_MODELS_AVAILABLE, INTELLIGENCE_ROUTERS_AVAILABLE
    global STORAGE_SYSTEM_AVAILABLE, EMAIL_SYSTEM_AVAILABLE

    # Import enhanced email models
    try:
        from src.models.email_subject_templates import EmailSubjectTemplate, EmailSubjectPerformance
        logging.info("✅ Enhanced email models imported successfully")
        EMAIL_MODELS_AVAILABLE = True
    except ImportError as e:
        logging.warning(f"⚠️ Enhanced email models not available: {e}")

    # Import intelligence main router first
    try:
        from src.intelligence.routes import router as intelligence_main_router
        INTELLIGENCE_MAIN_ROUTER_AVAILABLE = True
        logging.info("✅ Intelligence main router imported successfully")
    except ImportError as e:
        logging.warning(f"⚠️ Intelligence main router not available: {e}")

    # Import individual content router as fallback
    try:
        from src.intelligence.routers.content_routes import router as content_router
        logging.info("✅ Content generation router imported successfully from existing content_routes.py")
        CONTENT_ROUTER_AVAILABLE = True
    except ImportError as e:
        logging.error(f"❌ Content generation router not available: {e}")

    # Import analysis router
    try:
        from src.intelligence.routers.analysis_routes import router as analysis_router
        logging.info("✅ Analysis router imported successfully")
        ANALYSIS_ROUTER_AVAILABLE = True
    except ImportError as e:
        logging.warning(f"⚠️ Analysis router not available: {e}")

    # Import enhanced email generation routes
    try:
        from src.intelligence.routers.enhanced_email_routes import router as enhanced_email_router
        logging.info("✅ Enhanced email generation routes imported successfully")
        ENHANCED_EMAIL_ROUTER_AVAILABLE = True
    except ImportError as e:
        logging.warning(f"⚠️ Enhanced email generation routes not available: {e}")

    # Import enhanced stability routes
    try:
        from src.intelligence.routers.stability_routes import router as stability_router
        logging.info("✅ Stability AI routes (with ultra-cheap generation) imported successfully")
        STABILITY_ROUTER_AVAILABLE = True
    except ImportError as e:
        logging.warning(f"⚠️ Stability AI routes not available: {e}")

    # Import universal storage routes
    try:
        from src.intelligence.routers.storage_routes import router as storage_router
        logging.info("✅ Universal storage routes imported successfully")
        STORAGE_ROUTER_AVAILABLE = True
    except ImportError as e:
        logging.warning(f"⚠️ Universal storage routes not available: {e}")

    # Import document management routes
    try:
        from src.intelligence.routers.document_routes import router as document_router
        logging.info("✅ Document management routes imported successfully")
        DOCUMENT_ROUTER_AVAILABLE = True
    except ImportError as e:
        logging.warning(f"⚠️ Document management routes not available: {e}")

    # Import AI monitoring routes
    try:
        from src.intelligence.routers.ai_monitoring_routes import include_ai_monitoring_routes
        logging.info("✅ AI monitoring routes imported successfully")
        AI_MONITORING_ROUTER_AVAILABLE = True
    except ImportError as e:
        logging.warning(f"⚠️ AI monitoring routes not available: {e}")

    # Update system status flags
    INTELLIGENCE_ROUTERS_AVAILABLE = any([
        INTELLIGENCE_MAIN_ROUTER_AVAILABLE,
        ANALYSIS_ROUTER_AVAILABLE,
        AFFILIATE_ROUTER_AVAILABLE,
        STABILITY_ROUTER_AVAILABLE,
        AI_MONITORING_ROUTER_AVAILABLE,
        ENHANCED_EMAIL_ROUTER_AVAILABLE,
        CONTENT_ROUTER_AVAILABLE
    ])

    STORAGE_SYSTEM_AVAILABLE = any([
        STORAGE_ROUTER_AVAILABLE,
        DOCUMENT_ROUTER_AVAILABLE
    ])

    EMAIL_SYSTEM_AVAILABLE = ENHANCED_EMAIL_ROUTER_AVAILABLE and EMAIL_MODELS_AVAILABLE

# ============================================================================
# ✅ ROUTER REGISTRATION FUNCTIONS
# ============================================================================

def register_core_routers(app: FastAPI):
    """Register core application routers"""
    routes_registered = 0
    
    # Register auth router
    if AUTH_ROUTER_AVAILABLE and auth_router:
        app.include_router(auth_router, prefix="/api")
        logging.info("📡 Auth router registered")
        routes_registered += 1
        
        # Debug auth routes
        print(f"🔍 Auth router has {len(auth_router.routes)} routes:")
        for route in auth_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  {list(route.methods)} /api{route.path}")
    else:
        logging.error("❌ Auth router not registered - authentication will not work")

    # Register admin router
    if ADMIN_ROUTER_AVAILABLE and admin_router:
        app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
        logging.info("📡 Admin router registered at /api/admin")
        routes_registered += 1
        
        # Debug admin routes
        print(f"🔍 Admin router has {len(admin_router.routes)} routes:")
        for route in admin_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  {list(route.methods)} /api/admin{route.path}")

    # Register admin AI optimization router
    try:
        from src.routes import admin_ai_optimization
        app.include_router(admin_ai_optimization.router, prefix="/api/admin/ai-optimization", tags=["admin", "ai-optimization"])
        logging.info("📡 Admin AI optimization router registered at /api/admin/ai-optimization")
        routes_registered += 1
        
        # Debug AI optimization routes
        print(f"🔍 Admin AI optimization router has {len(admin_ai_optimization.router.routes)} routes:")
        for route in admin_ai_optimization.router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  {list(route.methods)} /api/admin/ai-optimization{route.path}")
    except Exception as e:
        logging.error(f"❌ Failed to register admin AI optimization router: {e}")

    # Register waitlist router
    if WAITLIST_ROUTER_AVAILABLE and waitlist_router:
        app.include_router(waitlist_router, prefix="/api/waitlist", tags=["waitlist"])
        logging.info("📡 Waitlist router registered at /api/waitlist")
        routes_registered += 1
        
        # Debug waitlist routes
        print(f"🔍 Waitlist router has {len(waitlist_router.routes)} routes:")
        for route in waitlist_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  {list(route.methods)} /api/waitlist{route.path}")

    # Register dynamic AI providers router
    if DYNAMIC_AI_PROVIDERS_ROUTER_AVAILABLE and dynamic_ai_providers_router:
        app.include_router(dynamic_ai_providers_router, prefix="/admin", tags=["admin", "ai-providers"])
        logging.info("📡 Dynamic AI providers router registered at /admin")
        routes_registered += 1
        
        # Debug dynamic AI provider routes
        print(f"🔍 Dynamic AI providers router has {len(dynamic_ai_providers_router.routes)} routes:")
        for route in dynamic_ai_providers_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  {list(route.methods)} /admin{route.path}")
    else:
        logging.error("❌ Dynamic AI providers router not registered")

    # Register AI Platform Discovery System router
    if AI_DISCOVERY_ROUTER_AVAILABLE and ai_discovery_router:
        app.include_router(ai_discovery_router, prefix="/api/admin/ai-discovery", tags=["ai-discovery"])
        logging.info("📡 AI Platform Discovery System router registered at /api/admin/ai-discovery")
        routes_registered += 1
        
        # Debug AI discovery routes
        print(f"🔍 AI Discovery router has {len(ai_discovery_router.routes)} routes:")
        for route in ai_discovery_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  {list(route.methods)} /api/admin/ai-discovery{route.path}")
        
        print("✅ AI Discovery endpoints now available at:")
        print("  GET /api/admin/ai-discovery/health")
        print("  GET /api/admin/ai-discovery/active-providers")
        print("  GET /api/admin/ai-discovery/discovered-suggestions")
        print("  GET /api/admin/ai-discovery/category-rankings")
        print("  GET /api/admin/ai-discovery/dashboard")
    else:
        logging.error("❌ AI Platform Discovery System router not registered")

    return routes_registered

def register_campaigns_router(app: FastAPI):
    """Register campaigns router with fallback endpoints"""
    from fastapi import Depends, BackgroundTasks
    from src.core.database import get_async_db
    from src.auth.dependencies import get_current_user
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.models.user import User
    
    if CAMPAIGNS_ROUTER_AVAILABLE and campaigns_router:
        app.include_router(campaigns_router, prefix="/api/campaigns", tags=["campaigns"])
        logging.info("📡 Campaigns router registered with prefix /api/campaigns")
        
        # Debug campaigns routes
        print(f"🔍 Campaigns router has {len(campaigns_router.routes)} routes:")
        for route in campaigns_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  {list(route.methods)} /api/campaigns{route.path}")
        
        # Add direct routes to prevent redirects
        @app.get("/api/campaigns")
        async def campaigns_direct_route(
            skip: int = 0,
            limit: int = 100,
            db: AsyncSession = Depends(get_async_db),
            current_user: User = Depends(get_current_user)
        ):
            """Direct route to prevent redirects"""
            from src.campaigns.routes.campaign_crud import get_campaigns
            return await get_campaigns(skip, limit, None, db, current_user)
        
        @app.post("/api/campaigns")
        async def campaigns_create_direct_route(
            campaign_data: dict,
            background_tasks: BackgroundTasks,
            db: AsyncSession = Depends(get_async_db),
            current_user: User = Depends(get_current_user)
        ):
            """Direct create route to prevent redirects"""
            from src.campaigns.routes.campaign_crud import create_campaign
            from src.campaigns.schemas import CampaignCreate
            campaign_obj = CampaignCreate(**campaign_data)
            return await create_campaign(campaign_obj, background_tasks, db, current_user)
        
        return 1
    else:
        logging.error("❌ Campaigns router not registered - Adding emergency CRUD endpoints")
        
        # Emergency CRUD endpoints
        import uuid
        
        @app.get("/api/campaigns", tags=["emergency-campaigns"])
        async def emergency_get_campaigns():
            """Emergency endpoint for getting campaigns"""
            return [
                {
                    "id": "emergency-campaign-1",
                    "name": "Emergency Campaign Response",
                    "description": "CRUD router failed to load. This is an emergency response.",
                    "status": "fallback",
                    "is_demo": True,
                    "created_at": "2025-01-17T12:00:00Z",
                    "updated_at": "2025-01-17T12:00:00Z",
                    "error_context": "campaigns router import failed",
                    "debug_url": "/api/debug/campaigns-status"
                }
            ]
        
        @app.post("/api/campaigns", tags=["emergency-campaigns"]) 
        async def emergency_create_campaign():
            """Emergency endpoint for creating campaigns"""
            return {
                "id": str(uuid.uuid4()),
                "name": "Emergency Campaign Creation",
                "description": "CRUD router failed. Campaign creation in emergency mode.",
                "status": "emergency",
                "created_at": "2025-01-17T12:00:00Z",
                "message": "CRUD router import failed - check logs",
                "debug_url": "/api/debug/campaigns-status"
            }
        
        @app.get("/api/campaigns/{campaign_id}", tags=["emergency-campaigns"])
        async def emergency_get_campaign(campaign_id: str):
            """Emergency endpoint for getting single campaign"""
            return {
                "id": campaign_id,
                "name": f"Emergency Campaign {campaign_id}",
                "description": "CRUD router failed. Single campaign in emergency mode.",
                "status": "emergency",
                "created_at": "2025-01-17T12:00:00Z",
                "debug_url": "/api/debug/campaigns-status"
            }
        
        return 0

def register_dashboard_router(app: FastAPI):
    """Register dashboard router with fallback endpoints"""
    if DASHBOARD_ROUTER_AVAILABLE and dashboard_router:
        app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])
        logging.info("📡 Dashboard router registered at /api/dashboard")
        
        # Debug dashboard routes
        print(f"🔍 Dashboard router has {len(dashboard_router.routes)} routes:")
        for route in dashboard_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  {list(route.methods)} /api/dashboard{route.path}")
        
        return 1
    else:
        logging.error("❌ Dashboard router not registered - dashboard stats will not work")
        
        # Emergency dashboard endpoints
        @app.get("/api/dashboard/stats", tags=["emergency-dashboard"])
        async def emergency_dashboard_stats():
            """Emergency dashboard stats endpoint"""
            return {
                "company_name": "CampaignForge",
                "subscription_tier": "free",
                "monthly_credits_used": 0,
                "monthly_credits_limit": 5000,
                "credits_remaining": 5000,
                "total_campaigns_created": 0,
                "active_campaigns": 0,
                "team_members": 1,
                "campaigns_this_month": 0,
                "usage_percentage": 0.0,
                "emergency_mode": True,
                "debug_message": "Dashboard router failed to import - using fallback data"
            }
        
        @app.get("/api/dashboard/company", tags=["emergency-dashboard"])
        async def emergency_company_details():
            """Emergency company details endpoint"""
            return {
                "id": "emergency-company-id",
                "company_name": "CampaignForge",
                "company_slug": "campaignforge",
                "industry": "Technology",
                "company_size": "small",
                "website_url": "",
                "subscription_tier": "free",
                "subscription_status": "active",
                "monthly_credits_used": 0,
                "monthly_credits_limit": 5000,
                "created_at": "2025-01-17T12:00:00Z",
                "emergency_mode": True
            }
        
        return 0

def register_intelligence_routers(app: FastAPI):
    """Register intelligence and AI-related routers"""
    intelligence_routes_registered = 0
    
    # Try intelligence main router first (includes content routes)
    if INTELLIGENCE_MAIN_ROUTER_AVAILABLE and intelligence_main_router:
        app.include_router(
            intelligence_main_router,
            prefix="/api/intelligence",
            tags=["intelligence"]
        )
        logging.info("📡 Intelligence main router registered at /api/intelligence")
        logging.info("✅ This includes content routes at /api/intelligence/content/*")
        intelligence_routes_registered += 1
        
        # Update content router status since it's included in main router
        global CONTENT_ROUTER_AVAILABLE
        CONTENT_ROUTER_AVAILABLE = True
        
        # Debug intelligence main router routes
        print(f"🔍 Intelligence main router has {len(intelligence_main_router.routes)} routes:")
        for route in intelligence_main_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  {list(route.methods)} /api/intelligence{route.path}")

    elif CONTENT_ROUTER_AVAILABLE and content_router:
        # Fallback: Register content router directly if main router is not available
        app.include_router(
            content_router, 
            prefix="/api/intelligence/content", 
            tags=["intelligence", "content", "generation"]
        )
        logging.info("📡 Content generation router registered directly at /api/intelligence/content")
        intelligence_routes_registered += 1
        
        # Debug content routes
        print(f"🔍 Content generation router has {len(content_router.routes)} routes:")
        for route in content_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  {list(route.methods)} /api/intelligence/content{route.path}")

    else:
        # Only add emergency endpoints if no content router is available
        logging.error("❌ Neither intelligence main router nor content router available - Adding emergency content endpoints")
        
        @app.post("/api/intelligence/content/generate", tags=["emergency-content"])
        async def emergency_generate_content():
            """Emergency content generation endpoint"""
            return {
                "content_id": "emergency-content-123",
                "content_type": "emergency",
                "campaign_id": "unknown",
                "generated_content": {
                    "title": "Emergency Content Response",
                    "content": {"message": "Content router failed to load. Emergency response active."},
                    "metadata": {"emergency_mode": True}
                },
                "success": False,
                "error": "Content router not available",
                "debug_url": "/api/debug/content-status"
            }
        
        @app.get("/api/intelligence/content/{campaign_id}", tags=["emergency-content"])
        async def emergency_get_content(campaign_id: str):
            """Emergency get content endpoint"""
            return []

    # Register enhanced email generation routes
    if ENHANCED_EMAIL_ROUTER_AVAILABLE and enhanced_email_router:
        app.include_router(
            enhanced_email_router, 
            prefix="/api/intelligence/emails", 
            tags=["intelligence", "enhanced-email-generation", "learning"]
        )
        logging.info("📡 Enhanced email generation routes registered at /api/intelligence/emails")
        intelligence_routes_registered += 1
        
        # Debug enhanced email routes
        print(f"🔍 Enhanced email router has {len(enhanced_email_router.routes)} routes:")
        for route in enhanced_email_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  {list(route.methods)} /api/intelligence/emails{route.path}")

    # Register enhanced stability routes
    if STABILITY_ROUTER_AVAILABLE and stability_router:
        app.include_router(stability_router, prefix="/api/intelligence/stability", tags=["intelligence", "stability", "ultra-cheap-ai"])
        logging.info("📡 Stability AI routes (with ultra-cheap generation) registered at /api/intelligence/stability")
        intelligence_routes_registered += 1
        
        # Debug stability routes
        print(f"🔍 Stability AI router has {len(stability_router.routes)} routes:")
        for route in stability_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  {list(route.methods)} /api/intelligence/stability{route.path}")

    # Register universal storage routes
    if STORAGE_ROUTER_AVAILABLE and storage_router:
        app.include_router(storage_router, prefix="/api/storage", tags=["storage", "dual-storage", "universal"])
        logging.info("📡 Universal storage routes registered at /api/storage")
        intelligence_routes_registered += 1
        
        # Debug storage routes
        print(f"🔍 Storage router has {len(storage_router.routes)} routes:")
        for route in storage_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  {list(route.methods)} /api/storage{route.path}")

    # Register document management routes
    if DOCUMENT_ROUTER_AVAILABLE and document_router:
        app.include_router(document_router, prefix="/api/documents", tags=["documents", "file-management"])
        logging.info("📡 Document management routes registered at /api/documents")
        intelligence_routes_registered += 1
        
        # Debug document routes
        print(f"🔍 Document router has {len(document_router.routes)} routes:")
        for route in document_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  {list(route.methods)} /api/documents{route.path}")

    # Register AI monitoring routes
    if AI_MONITORING_ROUTER_AVAILABLE and include_ai_monitoring_routes:
        include_ai_monitoring_routes(app)
        logging.info("📡 AI monitoring routes registered at /api/ai-monitoring")
        intelligence_routes_registered += 1
        
        # Debug monitoring routes
        print("🔍 AI monitoring routes registered:")
        print("  GET /api/ai-monitoring/status")
        print("  GET /api/ai-monitoring/analytics")
        print("  GET /api/ai-monitoring/providers")
        print("  GET /api/ai-monitoring/dashboard")
        print("  POST /api/ai-monitoring/optimization/recalculate")

    return intelligence_routes_registered

def register_storage_endpoints(app: FastAPI):
    """Register enhanced cloudflare storage endpoints"""
    try:
        from src.routes.user_storage import router as user_storage_router
        from src.routes.admin_storage import router as admin_storage_router
        
        app.include_router(user_storage_router)
        app.include_router(admin_storage_router)
        
        logging.info("📡 Enhanced Cloudflare storage endpoints registered")
        return 2
    except Exception as e:
        logging.error(f"❌ Failed to register storage endpoints: {e}")
        return 0

# ============================================================================
# ✅ MAIN ROUTER REGISTRATION FUNCTION
# ============================================================================

def register_all_routers(app: FastAPI):
    """Register all routers with the FastAPI app"""
    logging.info("🔄 Starting router registration...")
    
    # Import all routers first
    import_core_routers()
    import_intelligence_routers()
    
    # Register health router first
    try:
        from src.routes.health import health_router
        app.include_router(health_router)
        logging.info("📡 Health router registered")
    except Exception as e:
        logging.error(f"❌ Failed to register health router: {e}")
    
    # Register core routers
    core_routes = register_core_routers(app)
    
    # Register campaigns router
    campaigns_routes = register_campaigns_router(app)
    
    # Register dashboard router
    dashboard_routes = register_dashboard_router(app)
    
    # Register intelligence routers
    intelligence_routes = register_intelligence_routers(app)
    
    # Register storage endpoints
    storage_routes = register_storage_endpoints(app)
    
    # Log system capabilities
    total_routes = core_routes + campaigns_routes + dashboard_routes + intelligence_routes + storage_routes
    
    logging.info(f"✅ Router registration completed: {total_routes} router groups registered")
    
    if intelligence_routes > 0:
        logging.info(f"✅ Intelligence system: {intelligence_routes} routers registered")
    else:
        logging.warning("⚠️ Intelligence system: No routers available")

    if ENHANCED_EMAIL_ROUTER_AVAILABLE:
        logging.info("🎯 Enhanced email features: AI subject lines + Learning system")
    else:
        logging.warning("⚠️ Enhanced email system: No router available")

    if CONTENT_ROUTER_AVAILABLE:
        logging.info("🎯 Content generation features: Intelligence-based content creation")
    else:
        logging.warning("⚠️ Content generation system: No router available")

    if STORAGE_SYSTEM_AVAILABLE:
        logging.info("🎯 Complete storage system: Universal storage + Document management")
    else:
        logging.warning("⚠️ Storage system: No routers available")

    if AI_MONITORING_ROUTER_AVAILABLE:
        logging.info("🎯 Complete AI monitoring: Real-time optimization + Cost tracking")
    else:
        logging.warning("⚠️ AI monitoring system: No routers available")

    if AI_DISCOVERY_ROUTER_AVAILABLE:
        logging.info("🎯 Complete AI Discovery: Two-table architecture + Automated discovery")
    else:
        logging.warning("⚠️ AI Discovery system: No routers available")
    
    return {
        "total_routes": total_routes,
        "core_routes": core_routes,
        "campaigns_routes": campaigns_routes,
        "dashboard_routes": dashboard_routes,
        "intelligence_routes": intelligence_routes,
        "storage_routes": storage_routes,
        "router_status": get_router_status()
    }

def get_router_status():
    """Get current router availability status"""
    return {
        "auth": AUTH_ROUTER_AVAILABLE,
        "campaigns": CAMPAIGNS_ROUTER_AVAILABLE,
        "dashboard": DASHBOARD_ROUTER_AVAILABLE,
        "admin": ADMIN_ROUTER_AVAILABLE,
        "waitlist": WAITLIST_ROUTER_AVAILABLE,
        "dynamic_ai_providers": DYNAMIC_AI_PROVIDERS_ROUTER_AVAILABLE,
        "ai_discovery": AI_DISCOVERY_ROUTER_AVAILABLE,
        "intelligence_main": INTELLIGENCE_MAIN_ROUTER_AVAILABLE,
        "content": CONTENT_ROUTER_AVAILABLE,
        "enhanced_email": ENHANCED_EMAIL_ROUTER_AVAILABLE,
        "analysis": ANALYSIS_ROUTER_AVAILABLE,
        "stability": STABILITY_ROUTER_AVAILABLE,
        "storage": STORAGE_ROUTER_AVAILABLE,
        "document": DOCUMENT_ROUTER_AVAILABLE,
        "ai_monitoring": AI_MONITORING_ROUTER_AVAILABLE,
        "email_models": EMAIL_MODELS_AVAILABLE,
        "storage_system": STORAGE_SYSTEM_AVAILABLE,
        "email_system": EMAIL_SYSTEM_AVAILABLE,
        "intelligence_system": INTELLIGENCE_ROUTERS_AVAILABLE
    }

# ============================================================================
# ✅ EXPORTS
# ============================================================================

__all__ = [
    'register_all_routers',
    'register_core_routers',
    'register_campaigns_router',
    'register_dashboard_router',
    'register_intelligence_routers',
    'register_storage_endpoints',
    'import_core_routers',
    'import_intelligence_routers',
    'get_router_status',
    # Router availability flags
    'AUTH_ROUTER_AVAILABLE',
    'CAMPAIGNS_ROUTER_AVAILABLE',
    'DASHBOARD_ROUTER_AVAILABLE',
    'ADMIN_ROUTER_AVAILABLE',
    'WAITLIST_ROUTER_AVAILABLE',
    'DYNAMIC_AI_PROVIDERS_ROUTER_AVAILABLE',
    'AI_DISCOVERY_ROUTER_AVAILABLE',
    'INTELLIGENCE_ROUTERS_AVAILABLE',
    'INTELLIGENCE_MAIN_ROUTER_AVAILABLE',
    'ANALYSIS_ROUTER_AVAILABLE',
    'AFFILIATE_ROUTER_AVAILABLE',
    'CONTENT_ROUTER_AVAILABLE',
    'ENHANCED_EMAIL_ROUTER_AVAILABLE',
    'STABILITY_ROUTER_AVAILABLE',
    'STORAGE_ROUTER_AVAILABLE',
    'DOCUMENT_ROUTER_AVAILABLE',
    'AI_MONITORING_ROUTER_AVAILABLE',
    'EMAIL_MODELS_AVAILABLE',
    'STORAGE_SYSTEM_AVAILABLE',
    'EMAIL_SYSTEM_AVAILABLE'
]