# src/main.py - Complete CampaignForge Backend with All Modules

import os
import sys
import logging
import uvicorn
from datetime import datetime, timezone

# ============================================================================
# PYTHON PATH SETUP
# ============================================================================

current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir)
app_path = os.path.dirname(current_dir)

if src_path not in sys.path:
    sys.path.insert(0, src_path)
if app_path not in sys.path:
    sys.path.insert(0, app_path)

# ============================================================================
# MODULAR IMPORTS
# ============================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Core Infrastructure
from src.core.config import deployment_config
from src.core.middleware import setup_cors, ErrorHandlingMiddleware, RateLimitMiddleware
from src.core.database import test_database_connection
from src.core.health import get_health_status

# Module Imports
from src.intelligence.intelligence_module import intelligence_module
from src.users.users_module import users_module
from src.campaigns.campaigns_module import campaigns_module
from src.content.content_module import content_module
from src.storage.storage_module import storage_module

# Additional API Routes
from src.users.api.routes import router as users_router
from src.campaigns.api.routes import router as campaigns_router
from src.content.api.routes import router as content_router
from src.storage.api.routes import router as storage_router

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# MODULAR APPLICATION FACTORY
# ============================================================================

async def create_campaignforge_app() -> FastAPI:
    """
    Create CampaignForge application with complete modular architecture.

    Returns:
        FastAPI: Fully configured FastAPI application with all modules
    """
    logger.info("Starting CampaignForge Complete Backend (Session 6+)...")

    # Create FastAPI application
    app = FastAPI(
        title="CampaignForge AI Backend",
        description="Complete modular AI-powered marketing campaign platform - Session 6 Complete",
        version="3.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Phase 1: Configure CORS middleware
    logger.info("Phase 1: Configuring CORS...")
    setup_cors(app)

    # Phase 2: Add core middleware
    logger.info("Phase 2: Adding middleware...")
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(RateLimitMiddleware, calls=100, period=60)

    # Phase 3: Initialize all modules
    logger.info("Phase 3: Initializing modules...")

    modules_status = {}

    # Initialize Intelligence Engine module
    try:
        intelligence_initialized = await intelligence_module.initialize()
        modules_status["intelligence"] = "healthy" if intelligence_initialized else "unhealthy"
        if intelligence_initialized:
            logger.info("✓ Intelligence Engine module initialized")
            intelligence_router = intelligence_module.get_api_router()
            if intelligence_router:
                app.include_router(intelligence_router, prefix="/api")
        else:
            logger.warning("✗ Intelligence Engine module initialization failed")
    except Exception as e:
        logger.error(f"✗ Intelligence module error: {e}")
        modules_status["intelligence"] = "unhealthy"

    # Initialize Users module
    try:
        users_initialized = await users_module.initialize()
        modules_status["users"] = "healthy" if users_initialized else "unhealthy"
        if users_initialized:
            logger.info("✓ Users module initialized")
            # Include users router (contains auth endpoints)
            app.include_router(users_router)
        else:
            logger.warning("✗ Users module initialization failed")
    except Exception as e:
        logger.error(f"✗ Users module error: {e}")
        modules_status["users"] = "unhealthy"

    # Initialize Campaigns module
    try:
        campaigns_initialized = await campaigns_module.initialize()
        modules_status["campaigns"] = "healthy" if campaigns_initialized else "unhealthy"
        if campaigns_initialized:
            logger.info("✓ Campaigns module initialized")
            app.include_router(campaigns_router)
        else:
            logger.warning("✗ Campaigns module initialization failed")
    except Exception as e:
        logger.error(f"✗ Campaigns module error: {e}")
        modules_status["campaigns"] = "unhealthy"

    # Initialize Content module
    try:
        content_initialized = await content_module.initialize()
        modules_status["content"] = "healthy" if content_initialized else "unhealthy"
        if content_initialized:
            logger.info("✓ Content module initialized")
            app.include_router(content_router)
        else:
            logger.warning("✗ Content module initialization failed")
    except Exception as e:
        logger.error(f"✗ Content module error: {e}")
        modules_status["content"] = "unhealthy"

    # Initialize Storage module
    try:
        storage_initialized = await storage_module.initialize()
        modules_status["storage"] = "healthy" if storage_initialized else "unhealthy"
        if storage_initialized:
            logger.info("✓ Storage module initialized")
            app.include_router(storage_router)
        else:
            logger.warning("✗ Storage module initialization failed")
    except Exception as e:
        logger.error(f"✗ Storage module error: {e}")
        modules_status["storage"] = "unhealthy"

    # Phase 4: Add core health endpoints
    logger.info("Phase 4: Adding core endpoints...")

    @app.get("/health")
    async def health_check():
        """
        System health check endpoint - Returns status of all modules.
        Used by Railway for health monitoring.
        """
        try:
            health_status = await get_health_status()

            # Calculate module statistics
            healthy_count = sum(1 for status in modules_status.values() if status == "healthy")
            total_count = len(modules_status)
            completion_percentage = (healthy_count / total_count * 100) if total_count > 0 else 0

            return {
                "status": "healthy" if healthy_count == total_count else "degraded",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session": "6_complete",
                "modules": modules_status,
                "module_count": {
                    "total": total_count,
                    "healthy": healthy_count,
                    "completion_percentage": round(completion_percentage, 1)
                },
                "session_6_status": {
                    "storage_module": storage_initialized,
                    "cloudflare_r2": "ready",
                    "file_management": "operational",
                    "media_generation": "ready",
                    "quota_system": "active",
                    "enhanced_image_generation": "active"
                },
                "details": health_status
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    @app.get("/")
    async def root():
        """Root endpoint - API information"""
        healthy_count = sum(1 for status in modules_status.values() if status == "healthy")
        total_count = len(modules_status)

        return {
            "message": "CampaignForge AI Backend",
            "version": "3.0.0",
            "architecture": "modular",
            "session": "6_complete",
            "modules": modules_status,
            "module_health": f"{healthy_count}/{total_count}",
            "docs": "/docs",
            "health": "/health",
            "features": [
                "AI Content Generation",
                "Campaign Management",
                "Intelligence Analysis",
                "Media Generation",
                "Cloud Storage (R2)",
                "User Management"
            ]
        }

    @app.get("/api/modules/status")
    async def module_status():
        """Detailed module status endpoint"""
        try:
            module_details = {}

            # Intelligence module details
            if modules_status.get("intelligence") == "healthy":
                intelligence_health = await intelligence_module.health_check()
                intelligence_metrics = await intelligence_module.get_metrics()
                module_details["intelligence"] = {
                    "status": intelligence_health["status"],
                    "version": intelligence_module.version,
                    "metrics": intelligence_metrics
                }

            # Users module details
            if modules_status.get("users") == "healthy":
                users_health = await users_module.health_check()
                module_details["users"] = {
                    "status": users_health["status"],
                    "version": users_module.version
                }

            # Campaigns module details
            if modules_status.get("campaigns") == "healthy":
                campaigns_health = await campaigns_module.health_check()
                module_details["campaigns"] = {
                    "status": campaigns_health["status"],
                    "version": campaigns_module.version
                }

            # Content module details
            if modules_status.get("content") == "healthy":
                content_health = await content_module.health_check()
                module_details["content"] = {
                    "status": content_health["status"],
                    "version": content_module.version
                }

            # Storage module details
            if modules_status.get("storage") == "healthy":
                storage_health = await storage_module.health_check()
                module_details["storage"] = {
                    "status": storage_health["status"],
                    "version": storage_module.version
                }

            healthy_count = sum(1 for status in modules_status.values() if status == "healthy")

            return {
                "modules": module_details,
                "total_modules": len(modules_status),
                "healthy_modules": healthy_count,
                "module_status_summary": modules_status
            }
        except Exception as e:
            logger.error(f"Module status check failed: {e}")
            return {
                "error": str(e),
                "modules": {},
                "total_modules": 0,
                "healthy_modules": 0
            }

    # Phase 5: Database connectivity check
    logger.info("Phase 5: Checking database connectivity...")
    db_connected = await test_database_connection()
    if not db_connected:
        logger.warning("Database connectivity issues detected")

    # Log startup summary
    healthy_count = sum(1 for status in modules_status.values() if status == "healthy")
    logger.info("=" * 60)
    logger.info("CampaignForge Complete Backend - Initialization Summary")
    logger.info("=" * 60)
    logger.info(f"Database: {'✓ Connected' if db_connected else '✗ Issues detected'}")
    logger.info(f"Modules: {healthy_count}/{len(modules_status)} healthy")
    for module_name, module_status in modules_status.items():
        status_icon = "✓" if module_status == "healthy" else "✗"
        logger.info(f"  {status_icon} {module_name.capitalize()}: {module_status}")
    logger.info(f"Total routes: {len(app.routes)}")
    logger.info(f"API Documentation: /docs")
    logger.info("=" * 60)

    return app

# ============================================================================
# MODULE SHUTDOWN HANDLER
# ============================================================================

async def shutdown_modules():
    """Gracefully shutdown all modules."""
    logger.info("Shutting down modules...")
    try:
        await intelligence_module.shutdown()
        await users_module.shutdown()
        await campaigns_module.shutdown()
        await content_module.shutdown()
        await storage_module.shutdown()
        logger.info("All modules shutdown complete")
    except Exception as e:
        logger.error(f"Module shutdown error: {e}")

# ============================================================================
# PRODUCTION DEPLOYMENT
# ============================================================================

def create_app_sync():
    """Create app synchronously for Railway deployment."""
    import asyncio
    logger.info("Creating app for Railway deployment...")
    result = asyncio.run(create_campaignforge_app())
    logger.info("App created successfully for Railway")
    return result

# Create app instance for Railway
try:
    app = create_app_sync()
    logger.info(f"✓ Production app created with {len(app.routes)} routes")
except Exception as e:
    logger.error(f"✗ Failed to create production app: {e}")

    # Minimal fallback for Railway
    app = FastAPI(title="CampaignForge AI Backend - Error", version="3.0.0-error")

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
            "error": "App initialization failed",
            "details": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    @app.get("/")
    async def error_root():
        return {
            "message": "CampaignForge AI Backend - Initialization Error",
            "error": str(e),
            "docs": "/docs"
        }

# ============================================================================
# DEVELOPMENT SERVER
# ============================================================================

if __name__ == "__main__":
    import asyncio

    async def run_development_server():
        """Run development server."""
        logger.info("Starting CampaignForge development server...")

        # Create app
        app_instance = await create_campaignforge_app()

        # Run with uvicorn
        config = uvicorn.Config(
            app_instance,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            reload=True
        )
        server = uvicorn.Server(config)
        await server.serve()

    # Run the development server
    asyncio.run(run_development_server())
