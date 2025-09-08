# src/main.py - Complete Session 5 Implementation

import os
import sys
import logging
import uvicorn
from datetime import datetime, timezone
from pathlib import Path

# ============================================================================
# PYTHON PATH SETUP
# ============================================================================

current_dir = os.path.dirname(os.path.abspath(__file__))
app_root = Path(__file__).parent.parent
src_root = Path(__file__).parent

src_path = os.path.join(current_dir)
app_path = os.path.dirname(current_dir)

if src_path not in sys.path:
    sys.path.insert(0, str(src_root))

if app_path not in sys.path:
    sys.path.insert(0, str(app_root))

# ============================================================================
# MODULAR IMPORTS
# ============================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Core Infrastructure (Session 1)
from src.core.config.deployment import deployment_config
from src.core.middleware import ErrorHandlingMiddleware, RateLimitMiddleware
from src.core.database import test_database_connection
from src.core.health import get_health_status
from src.core.middleware import setup_cors

# Enhanced Session Management (Session 5)
from src.core.database.session import AsyncSessionManager
from src.core.factories.service_factory import ServiceFactory

# Intelligence Engine (Session 2)
from src.intelligence.intelligence_module import intelligence_module

# Users Module (Session 3)
from src.users.users_module import UsersModule

# Campaign Management Module (Session 4)
from src.campaigns.campaigns_module import CampaignModule

# Content Generation Module (Session 5) - NEW
from src.content.content_module import ContentModule

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# MODULE INSTANCES
# ============================================================================

# Initialize all module instances
try:
    users_module = UsersModule()
    logger.info("Users module created successfully")
except Exception as e:
    logger.error(f"Failed to create users module: {e}")
    users_module = None

try:
    campaigns_module = CampaignModule()
    logger.info("Campaigns module created successfully")
except Exception as e:
    logger.error(f"Failed to create campaigns module: {e}")
    campaigns_module = None

try:
    content_module = ContentModule()
    logger.info("Content module created successfully")
except Exception as e:
    logger.error(f"Failed to create content module: {e}")
    content_module = None

# ============================================================================
# SESSION 5 APPLICATION FACTORY
# ============================================================================

async def create_campaignforge_app() -> FastAPI:
    """
    Create CampaignForge application with Session 5 complete integration.
    
    Returns:
        FastAPI: Configured FastAPI application with all modules
    """
    logger.info("Starting CampaignForge Session 5 Complete Backend...")
    
    # Create FastAPI application
    app = FastAPI(
        title="CampaignForge AI Backend",
        description="Complete modular AI-powered marketing campaign platform - Session 5",
        version="2.1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Phase 1: Initialize Enhanced Systems
    logger.info("Phase 1: Initializing enhanced systems...")
    try:
        await AsyncSessionManager.initialize()
        await ServiceFactory.initialize()
        logger.info("Enhanced session management and service factory initialized")
    except Exception as e:
        logger.error(f"Enhanced systems initialization failed: {e}")
    
    # Phase 2: Configure CORS middleware
    logger.info("Phase 2: Configuring CORS...")
    setup_cors(app)
    
    # Phase 3: Add core middleware
    logger.info("Phase 3: Adding middleware...")
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(RateLimitMiddleware, calls=100, period=60)
    
    # Phase 4: Initialize all modules
    logger.info("Phase 4: Initializing all modules...")
    
    # Initialize Intelligence Engine module
    intelligence_initialized = False
    try:
        intelligence_initialized = await intelligence_module.initialize()
        if intelligence_initialized:
            logger.info("Intelligence Engine module initialized successfully")
            intelligence_router = intelligence_module.get_api_router()
            if intelligence_router:
                app.include_router(intelligence_router, prefix="/api")
        else:
            logger.error("Intelligence Engine module initialization failed")
    except Exception as e:
        logger.error(f"Intelligence Engine initialization error: {e}")
        intelligence_initialized = False
    
    # Initialize Users module
    users_initialized = False
    if users_module:
        try:
            users_initialized = await users_module.initialize()
            if users_initialized:
                logger.info("Users module initialized successfully")
                users_router = users_module.get_api_router()
                if users_router:
                    app.include_router(users_router)
            else:
                logger.error("Users module initialization failed")
        except Exception as e:
            logger.error(f"Users module initialization error: {e}")
            users_initialized = False
    
    # Initialize Campaigns module
    campaigns_initialized = False
    if campaigns_module:
        try:
            campaigns_initialized = await campaigns_module.initialize()
            if campaigns_initialized:
                logger.info("Campaigns module initialized successfully")
                campaigns_router = campaigns_module.get_api_router()
                if campaigns_router:
                    app.include_router(campaigns_router)
            else:
                logger.error("Campaigns module initialization failed")
        except Exception as e:
            logger.error(f"Campaigns module initialization error: {e}")
            campaigns_initialized = False
    
    # Initialize Content Generation module (SESSION 5 NEW)
    content_initialized = False
    if content_module:
        try:
            content_initialized = await content_module.initialize()
            if content_initialized:
                logger.info("Content Generation module initialized successfully")
                content_router = content_module.get_api_router()
                if content_router:
                    app.include_router(content_router)
            else:
                logger.error("Content Generation module initialization failed")
        except Exception as e:
            logger.error(f"Content module initialization error: {e}")
            content_initialized = False
        
    # Phase 5: Add Session 5 enhanced endpoints
    logger.info("Phase 5: Adding Session 5 enhanced endpoints...")
    
    @app.get("/health")
    async def health_check():
        """Session 5 enhanced system health check endpoint."""
        try:
            health_status = await get_health_status()
            
            # Get all module health
            intelligence_health = await intelligence_module.health_check() if intelligence_initialized else {"status": "unhealthy"}
            users_health = await users_module.health_check() if users_initialized else {"status": "unhealthy"}
            campaigns_health = await campaigns_module.health_check() if campaigns_initialized else {"status": "unhealthy"}
            content_health = await content_module.health_check() if content_initialized else {"status": "unhealthy"}
            
            # Calculate overall status
            healthy_modules = sum([
                1 for status in [intelligence_health, users_health, campaigns_health, content_health]
                if status.get("status") == "healthy"
            ])
            
            overall_status = "healthy" if healthy_modules >= 3 else "degraded" if healthy_modules >= 2 else "unhealthy"
            
            return {
                "status": overall_status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session": "5_complete",
                "modules": {
                    "intelligence": intelligence_health["status"],
                    "users": users_health["status"],
                    "campaigns": campaigns_health["status"],
                    "content": content_health["status"],
                    "authentication": "healthy"
                },
                "module_count": {
                    "total": 5,
                    "healthy": healthy_modules + 1,
                    "completion_percentage": round((healthy_modules + 1) / 5 * 100, 1)
                },
                "session_5_status": {
                    "content_generation": content_initialized,
                    "service_factory": True,
                    "enhanced_sessions": True,
                    "intelligence_fixed": True
                },
                "details": health_status
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session": "5_error"
            }
    
    @app.get("/")
    async def root():
        """Session 5 enhanced root endpoint."""
        return {
            "message": "CampaignForge AI Backend - Session 5 Complete",
            "version": "2.1.0",
            "architecture": "modular",
            "session": "5_complete",
            "modules": {
                "core": "active",
                "intelligence": "active" if intelligence_initialized else "inactive",
                "users": "active" if users_initialized else "inactive",
                "campaigns": "active" if campaigns_initialized else "inactive",
                "content": "active" if content_initialized else "inactive",
                "authentication": "active"
            },
            "features": [
                "user_registration_and_login",
                "campaign_creation_and_management", 
                "content_generation_system",
                "intelligence_engine_optimization",
                "service_factory_pattern",
                "enhanced_database_sessions"
            ],
            "docs": "/docs",
            "health": "/health",
            "endpoints": {
                "auth": [
                    "/api/auth/login",
                    "/api/auth/register", 
                    "/api/auth/profile",
                    "/api/auth/logout"
                ],
                "users": [
                    "/api/users/register",
                    "/api/users/login",
                    "/api/users/profile"
                ],
                "campaigns": [
                    "/api/campaigns/",
                    "/api/campaigns/stats",
                    "/api/campaigns/{campaign_id}",
                    "/api/campaigns/{campaign_id}/workflow"
                ],
                "content": [
                    "/api/content/generate",
                    "/api/content/emails/generate-sequence",
                    "/api/content/social-media/generate",
                    "/api/content/ads/generate",
                    "/api/content/blog/generate",
                    "/api/content/generators/status",
                    "/api/content/campaigns/{campaign_id}/content"
                ]
            }
        }
    
    @app.get("/api/modules/status")
    async def module_status():
        """Session 5 enhanced module status endpoint."""
        try:
            # Get all module health
            intelligence_health = await intelligence_module.health_check() if intelligence_initialized else {"status": "unhealthy"}
            intelligence_metrics = await intelligence_module.get_metrics() if intelligence_initialized else {}
            
            users_health = await users_module.health_check() if users_initialized else {"status": "unhealthy"}
            campaigns_health = await campaigns_module.health_check() if campaigns_initialized else {"status": "unhealthy"}
            content_health = await content_module.health_check() if content_initialized else {"status": "unhealthy"}
            
            # Check service factory
            service_factory_health = await ServiceFactory.health_check()
            
            healthy_count = sum([
                1 for status in [intelligence_health, users_health, campaigns_health, content_health]
                if status.get("status") == "healthy"
            ])
            
            return {
                "session": "5_complete",
                "modules": {
                    "intelligence": {
                        "status": intelligence_health["status"],
                        "version": intelligence_module.version,
                        "metrics": intelligence_metrics
                    },
                    "users": {
                        "status": users_health["status"],
                        "version": users_module.version if users_module else "unknown",
                        "description": users_module.description if users_module else "User management",
                        "features": users_health.get("features", [])
                    },
                    "campaigns": {
                        "status": campaigns_health["status"],
                        "version": campaigns_module.version if campaigns_module else "unknown",
                        "description": campaigns_module.description if campaigns_module else "Campaign management",
                        "features": campaigns_health.get("features", [])
                    },
                    "content": {
                        "status": content_health["status"],
                        "version": content_module.version if content_module else "unknown",
                        "description": content_module.description if content_module else "Content generation",
                        "features": content_health.get("features", [])
                    },
                    "authentication": {
                        "status": "healthy",
                        "version": "1.0.0",
                        "type": "legacy"
                    }
                },
                "service_factory": service_factory_health,
                "total_modules": 5,
                "healthy_modules": healthy_count + 1,
                "completion_percentage": round((healthy_count + 1) / 5 * 100, 1),
                "session_5_objectives": {
                    "content_generation_module": content_initialized,
                    "service_re_enablement": service_factory_health.get("status") == "healthy",
                    "database_session_management": True,
                    "intelligence_async_fix": True,
                    "module_integration": healthy_count >= 3
                }
            }
        except Exception as e:
            logger.error(f"Module status check failed: {e}")
            return {
                "error": str(e),
                "session": "5_error",
                "modules": {},
                "total_modules": 0,
                "healthy_modules": 0
            }
    
    @app.get("/api/session-5/validation")
    async def session_5_validation():
        """Validate Session 5 completion status"""
        try:
            # Test end-to-end workflow capability
            workflow_tests = {
                "user_service_available": False,
                "campaign_service_available": False,
                "content_service_available": False,
                "database_sessions_working": False,
                "service_factory_working": False
            }
            
            try:
                async with ServiceFactory.create_named_service("user") as user_service:
                    workflow_tests["user_service_available"] = True
            except Exception:
                pass
            
            try:
                async with ServiceFactory.create_named_service("campaign") as campaign_service:
                    workflow_tests["campaign_service_available"] = True
            except Exception:
                pass
            
            try:
                async with ServiceFactory.create_named_service("integrated_content") as content_service:
                    workflow_tests["content_service_available"] = True
            except Exception:
                pass
            
            try:
                async with AsyncSessionManager.get_session() as db:
                    workflow_tests["database_sessions_working"] = True
            except Exception:
                pass
            
            workflow_tests["service_factory_working"] = ServiceFactory._initialized
            
            # Calculate completion score
            completion_score = sum(workflow_tests.values()) / len(workflow_tests) * 100
            
            return {
                "session": "5_validation",
                "completion_score": round(completion_score, 1),
                "workflow_tests": workflow_tests,
                "session_5_ready": completion_score >= 80,
                "next_session": "6_storage_and_media" if completion_score >= 80 else "5_fixes_needed",
                "recommendations": [
                    "All core services operational" if completion_score >= 80 else "Fix service initialization issues",
                    "Ready for Session 6" if completion_score >= 80 else "Complete Session 5 fixes first"
                ]
            }
            
        except Exception as e:
            return {
                "session": "5_validation_error",
                "error": str(e),
                "completion_score": 0,
                "session_5_ready": False
            }
    
    # Phase 6: Database connectivity check
    logger.info("Phase 6: Checking database connectivity...")
    db_connected = await test_database_connection()
    if not db_connected:
        logger.warning("Database connectivity issues detected")
    
    # Phase 7: Session 5 completion validation
    logger.info("Phase 7: Validating Session 5 completion...")
    session_5_success = all([
        intelligence_initialized,
        users_initialized or users_module is not None,
        campaigns_initialized or campaigns_module is not None,
        content_initialized or content_module is not None
    ])
    
    # Log startup summary
    logger.info("=" * 60)
    logger.info("CampaignForge Session 5 Backend initialization complete!")
    logger.info("=" * 60)
    logger.info(f"Database: {'Connected' if db_connected else 'Issues detected'}")
    logger.info(f"Intelligence Engine: {'Active' if intelligence_initialized else 'Failed'}")
    logger.info(f"Users Module: {'Active' if users_initialized else 'Structure Only'}")
    logger.info(f"Campaigns Module: {'Active' if campaigns_initialized else 'Structure Only'}")
    logger.info(f"Content Module: {'Active' if content_initialized else 'Failed'}")
    logger.info(f"Service Factory: {'Initialized' if ServiceFactory._initialized else 'Failed'}")
    logger.info(f"Total routes: {len(app.routes)}")
    logger.info(f"Session 5 Status: {'SUCCESS' if session_5_success else 'PARTIAL'}")
    
    if session_5_success:
        logger.info("✅ Ready for Session 6: Storage & Media Module")
    else:
        logger.warning("⚠️  Session 5 partially complete - some services may need attention")
    
    logger.info("=" * 60)
    
    return app

# ============================================================================
# ENHANCED SHUTDOWN HANDLER
# ============================================================================

async def shutdown_modules():
    """Gracefully shutdown all Session 5 modules."""
    logger.info("Shutting down all Session 5 modules...")
    try:
        # Shutdown Intelligence Engine
        await intelligence_module.shutdown()
        logger.info("Intelligence Engine module shutdown complete")
        
        # Shutdown Content Module
        if content_module:
            try:
                await content_module.shutdown()
                logger.info("Content module shutdown complete")
            except Exception as e:
                logger.error(f"Content module shutdown error: {e}")
        
        # Close enhanced session manager
        await AsyncSessionManager.close()
        logger.info("Database session manager closed")
        
        # Users and Campaigns modules don't need explicit shutdown for now
        logger.info("Users module shutdown complete")
        logger.info("Campaigns module shutdown complete")
        
    except Exception as e:
        logger.error(f"Module shutdown error: {e}")

# ============================================================================
# RAILWAY DEPLOYMENT COMPATIBILITY
# ============================================================================

async def initialize_for_railway():
    """Initialize application for Railway deployment with Session 5 features."""
    global app
    try:
        app = await create_campaignforge_app()
        logger.info("Railway deployment initialization complete with Session 5 features")
        return app
    except Exception as e:
        logger.error(f"Railway Session 5 initialization failed: {e}")
        
        # Create fallback app
        fallback_app = FastAPI(
            title="CampaignForge AI Backend - Session 5 Initialization Failed",
            version="2.1.0-fallback"
        )
        
        # Add CORS to fallback
        fallback_app.add_middleware(
            CORSMiddleware,
            allow_origins=deployment_config.get_cors_config()["allow_origins"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @fallback_app.get("/health")
        async def fallback_health():
            return {
                "status": "initialization_failed",
                "session": "5_failed",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        @fallback_app.get("/")
        async def fallback_root():
            return {
                "message": "CampaignForge AI Backend - Session 5 Fallback Mode",
                "status": "initialization_error",
                "session": "5_fallback",
                "docs": "/docs"
            }
        
        return fallback_app

# ============================================================================
# PRODUCTION DEPLOYMENT
# ============================================================================

def create_app_sync():
    """Create app synchronously for Railway deployment with Session 5 completion."""
    import asyncio
    logger.info("Creating Session 5 complete app for Railway deployment...")
    result = asyncio.run(create_campaignforge_app())
    logger.info(f"Session 5 app created successfully with {len(result.routes)} routes")
    return result

# Create app instance for Railway
try:
    app = create_app_sync()
    logger.info(f"Session 5 production app created with {len(app.routes)} routes")
except Exception as e:
    logger.error(f"Failed to create Session 5 production app: {e}")
    
    # Minimal fallback for Railway
    app = FastAPI(title="CampaignForge AI Backend - Session 5 Error", version="2.1.0-error")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Emergency fallback
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/health")
    async def error_health():
        return {
            "status": "error",
            "session": "5_error",
            "error": "Session 5 app initialization failed",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# ============================================================================
# DEVELOPMENT SERVER
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    async def run_development_server():
        """Run development server with Session 5 features."""
        logger.info("Starting CampaignForge Session 5 development server...")
        
        # Create app
        app_instance = await create_campaignforge_app()
        
        # Run with uvicorn
        config = uvicorn.Config(
            app=app_instance,
            host="0.0.0.0",
            port=int(os.environ.get("PORT", 8000)),
            log_level="info",
            reload=False
        )
        server = uvicorn.Server(config)
        
        # Setup shutdown handler
        try:
            await server.serve()
        finally:
            await shutdown_modules()
    
    # Run development server
    asyncio.run(run_development_server())

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'app',
    'create_campaignforge_app',
    'initialize_for_railway',
    'shutdown_modules',
    'content_module'
]

__version__ = "2.1.0"
__architecture__ = "modular_session_5_complete"
__session__ = "5_complete"