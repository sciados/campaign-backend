# src/core/router_registry.py - FIXED VERSION with correct syntax

import logging
import traceback
from fastapi import FastAPI

logger = logging.getLogger(__name__)

# Router availability flags
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


def import_core_routers():
    """Import core application routers with error handling"""
    global AUTH_ROUTER_AVAILABLE, auth_router
    global CAMPAIGNS_ROUTER_AVAILABLE, campaigns_router
    global DASHBOARD_ROUTER_AVAILABLE, dashboard_router
    global ADMIN_ROUTER_AVAILABLE, admin_router
    global WAITLIST_ROUTER_AVAILABLE, waitlist_router
    global DYNAMIC_AI_PROVIDERS_ROUTER_AVAILABLE, dynamic_ai_providers_router
    global AI_DISCOVERY_ROUTER_AVAILABLE, ai_discovery_router
    
    print("Starting auth router import...")
    
    # Import auth router with detailed debugging
    try:
        from src.auth.routes import router as auth_router
        AUTH_ROUTER_AVAILABLE = True
        print("Auth router imported successfully")
        logging.info("Auth router imported successfully")
    except ImportError as e:
        AUTH_ROUTER_AVAILABLE = False
        auth_router = None
        print(f"Auth router import failed: {e}")
        logging.error(f"Auth router not available: {e}")
    except Exception as e:
        AUTH_ROUTER_AVAILABLE = False  
        auth_router = None
        print(f"Auth router unexpected error: {e}")
        logging.error(f"Auth router unexpected error: {e}")
    
    # Import other routers
    try:
        from src.campaigns.routes import router as campaigns_router
        CAMPAIGNS_ROUTER_AVAILABLE = True
        logging.info("Campaigns router imported successfully")
    except ImportError as e:
        logging.error(f"Campaigns router not available: {e}")

    try:
        from src.dashboard.routes import router as dashboard_router
        logging.info("Dashboard router imported successfully")
        DASHBOARD_ROUTER_AVAILABLE = True
    except ImportError as e:
        logging.warning(f"Dashboard router not available: {e}")

    try:
        from src.admin.routes import router as admin_router
        logging.info("Admin router imported successfully")
        ADMIN_ROUTER_AVAILABLE = True
    except ImportError as e:
        logging.warning(f"Admin router not available: {e}")

    try:
        from src.routes.waitlist import router as waitlist_router
        logging.info("Waitlist router imported successfully")
        WAITLIST_ROUTER_AVAILABLE = True
    except ImportError as e:
        logging.warning(f"Waitlist router not available: {e}")

    try:
        from src.routes.dynamic_ai_providers import router as dynamic_ai_providers_router
        logging.info("Dynamic AI providers router imported successfully")
        DYNAMIC_AI_PROVIDERS_ROUTER_AVAILABLE = True
    except ImportError as e:
        logging.warning(f"Dynamic AI providers router not available: {e}")

    try:
        from src.routes.ai_platform_discovery import router as ai_discovery_router
        AI_DISCOVERY_ROUTER_AVAILABLE = True
        print("AI Platform Discovery System router imported successfully")
        logging.info("AI Platform Discovery System router imported successfully")
    except ImportError as e:
        print(f"AI Discovery router import failed: {e}")
        logging.warning(f"AI Platform Discovery System router not available: {e}")


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
        logging.info("Enhanced email models imported successfully")
        EMAIL_MODELS_AVAILABLE = True
    except ImportError as e:
        logging.warning(f"Enhanced email models not available: {e}")

    # Import intelligence routers
    try:
        from src.intelligence.routes import router as intelligence_main_router
        INTELLIGENCE_MAIN_ROUTER_AVAILABLE = True
        logging.info("Intelligence main router imported successfully")
    except ImportError as e:
        logging.warning(f"Intelligence main router not available: {e}")

    try:
        from src.intelligence.routers.content_routes import router as content_router
        logging.info("Content generation router imported successfully")
        CONTENT_ROUTER_AVAILABLE = True
    except ImportError as e:
        logging.error(f"Content generation router not available: {e}")
    
    # CRITICAL: Import analysis router
    try:
        from src.intelligence.routers.analysis_routes import router as analysis_router
        ANALYSIS_ROUTER_AVAILABLE = True
        logging.info("Analysis router imported successfully")
        print("Analysis router imported successfully")
    except ImportError as e:
        logging.error(f"Analysis router not available: {e}")
        print(f"Analysis router not available: {e}")
    
    # Import user type routes
    try:
        from src.routes.user_type_routes import router as user_type_router
        print("User type routes imported successfully")
    except ImportError as e:
        print(f"User type routes not available: {e}")
        logging.warning(f"User type routes not available: {e}")

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


def register_all_routers(app: FastAPI):
    """Register all routers with the FastAPI app"""
    print("Starting router registration...")
    logging.info("Starting router registration...")
    
    # Import all routers first
    print("Importing routers...")
    import_core_routers()
    import_intelligence_routers()
    
    routes_registered = 0
    
    # Register health router first
    try:
        from src.routes.health import health_router
        app.include_router(health_router)
        print("Health router registered")
        logging.info("Health router registered")
        routes_registered += 1
    except Exception as e:
        print(f"Failed to register health router: {e}")
        logging.error(f"Failed to register health router: {e}")
    
    # Register auth router
    if AUTH_ROUTER_AVAILABLE and auth_router:
        try:
            app.include_router(auth_router, prefix="/api/auth")
            print("Auth router registered successfully")
            logging.info("Auth router registered")
            routes_registered += 1
        except Exception as e:
            print(f"Auth router registration failed: {e}")
            logging.error(f"Auth router registration failed: {e}")
    else:
        print("Auth router not available - authentication will not work")
        logging.error("Auth router not registered - authentication will not work")
    
    # Register other routers
    if CAMPAIGNS_ROUTER_AVAILABLE and campaigns_router:
        app.include_router(campaigns_router, prefix="/api/campaigns", tags=["campaigns"])
        logging.info("Campaigns router registered")
        routes_registered += 1

    if DASHBOARD_ROUTER_AVAILABLE and dashboard_router:
        app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])
        logging.info("Dashboard router registered")
        routes_registered += 1

    if ADMIN_ROUTER_AVAILABLE and admin_router:
        app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
        logging.info("Admin router registered")
        routes_registered += 1

    if WAITLIST_ROUTER_AVAILABLE and waitlist_router:
        app.include_router(waitlist_router, prefix="/api/waitlist", tags=["waitlist"])
        logging.info("Waitlist router registered")
        routes_registered += 1

    if DYNAMIC_AI_PROVIDERS_ROUTER_AVAILABLE and dynamic_ai_providers_router:
        app.include_router(dynamic_ai_providers_router, prefix="/admin", tags=["admin", "ai-providers"])
        logging.info("Dynamic AI providers router registered")
        routes_registered += 1

    if AI_DISCOVERY_ROUTER_AVAILABLE and ai_discovery_router:
        try:
            app.include_router(ai_discovery_router, prefix="/api/admin/ai-discovery", tags=["ai-discovery"])
            print("AI Discovery router registered successfully")
            logging.info("AI Discovery router registered")
            routes_registered += 1
        except Exception as e:
            print(f"AI Discovery router registration failed: {e}")
            logging.error(f"AI Discovery router registration failed: {e}")

    if INTELLIGENCE_MAIN_ROUTER_AVAILABLE and intelligence_main_router:
        app.include_router(intelligence_main_router, prefix="/api/intelligence", tags=["intelligence"])
        logging.info("Intelligence router registered")
        routes_registered += 1

    if CONTENT_ROUTER_AVAILABLE and content_router:
        app.include_router(content_router, prefix="/api/intelligence/content", tags=["content"])
        logging.info("Content router registered")
        routes_registered += 1

    # CRITICAL: Register analysis router
    if ANALYSIS_ROUTER_AVAILABLE and analysis_router:
        app.include_router(analysis_router, prefix="/api/intelligence/analysis", tags=["analysis"])
        logging.info("Analysis router registered")
        print("Analysis router registered at /api/intelligence/analysis")
        routes_registered += 1
    else:
        print("WARNING: Analysis router not available!")
        logging.error("Analysis router not available!")
    
    # Register user type routes
    try:
        from src.routes.user_type_routes import router as user_type_router
        app.include_router(user_type_router, tags=["user-types"])
        print("User type routes registered") 
        logging.info("User type routes registered")
        routes_registered += 1
    except ImportError as e:
        print(f"User type routes not available: {e}")
        logging.warning(f"User type routes not available: {e}")
    
    print(f"Router registration completed: {routes_registered} routers registered")
    logging.info(f"Router registration completed: {routes_registered} routers registered")
    
    return {
        "total_routes": routes_registered,
        "auth_registered": AUTH_ROUTER_AVAILABLE,
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


# Exports
__all__ = [
    'register_all_routers',
    'import_core_routers',
    'import_intelligence_routers',
    'get_router_status'
]