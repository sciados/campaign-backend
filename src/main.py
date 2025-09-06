# src/main.py - Clean Modular Architecture for CampaignForge

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

# Core Infrastructure (Session 1)
from src.core.config import deployment_config
from src.core.middleware import setup_cors, ErrorHandlingMiddleware, RateLimitMiddleware
from src.core.database import test_database_connection
from src.core.health import get_health_status

# Intelligence Engine (Session 2)
from src.intelligence.intelligence_module import intelligence_module

# Authentication Routes (NEW)
from src.api.routes.auth import get_auth_router


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
    Create CampaignForge application with modular architecture.
    
    Returns:
        FastAPI: Configured FastAPI application
    """
    logger.info("Starting CampaignForge Modular Backend...")
    
    # Create FastAPI application
    app = FastAPI(
        title="CampaignForge AI Backend",
        description="Modular AI-powered marketing campaign platform",
        version="2.0.0",
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
    
    # Phase 3: Initialize modules
    logger.info("Phase 3: Initializing modules...")
    
    # Initialize Intelligence Engine module
    intelligence_initialized = await intelligence_module.initialize()
    if intelligence_initialized:
        logger.info("Intelligence Engine module initialized successfully")
        # Register Intelligence Engine routes
        intelligence_router = intelligence_module.get_api_router()
        if intelligence_router:
            app.include_router(intelligence_router, prefix="/api")
    else:
        logger.error("Intelligence Engine module initialization failed")
    
    # Initialize Authentication module (NEW)
    logger.info("Phase 3.1: Initializing Authentication...")
    try:
        auth_router = get_auth_router()
        app.include_router(auth_router)
        logger.info("Authentication routes registered successfully")
    except Exception as e:
        logger.error(f"Failed to register authentication routes: {e}")
    
    # Phase 4: Add core health endpoints
    logger.info("Phase 4: Adding core endpoints...")
    
    @app.get("/health")
    async def health_check():
        """System health check endpoint."""
        try:
            health_status = await get_health_status()
            return {
                "status": health_status["status"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "modules": {
                    "intelligence": "healthy" if intelligence_initialized else "unhealthy",
                    "authentication": "healthy"  # Auth doesn't need async init
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
        """Root endpoint."""
        return {
            "message": "CampaignForge AI Backend",
            "version": "2.0.0",
            "architecture": "modular",
            "modules": {
                "core": "active",
                "intelligence": "active" if intelligence_initialized else "inactive",
                "authentication": "active"
            },
            "docs": "/docs",
            "health": "/health",
            "auth_endpoints": [
                "/api/auth/login",
                "/api/auth/register", 
                "/api/auth/profile",
                "/api/auth/dashboard-route",
                "/api/auth/logout",
                "/api/auth/me"
            ]
        }
    
    @app.get("/api/modules/status")
    async def module_status():
        """Module status endpoint."""
        try:
            intelligence_health = await intelligence_module.health_check()
            intelligence_metrics = await intelligence_module.get_metrics()
            
            return {
                "modules": {
                    "intelligence": {
                        "status": intelligence_health["status"],
                        "version": intelligence_module.version,
                        "metrics": intelligence_metrics
                    },
                    "authentication": {
                        "status": "healthy",
                        "version": "1.0.0",
                        "endpoints": [
                            "/api/auth/login",
                            "/api/auth/register", 
                            "/api/auth/profile",
                            "/api/auth/dashboard-route",
                            "/api/auth/logout",
                            "/api/auth/me"
                        ]
                    }
                },
                "total_modules": 2,
                "healthy_modules": 2 if intelligence_health["status"] == "healthy" else 1
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
    logger.info("CampaignForge Modular Backend initialization complete!")
    logger.info(f"Database: {'Connected' if db_connected else 'Issues detected'}")
    logger.info(f"Intelligence Engine: {'Active' if intelligence_initialized else 'Failed'}")
    logger.info(f"Authentication: Active")
    logger.info(f"Total routes: {len(app.routes)}")
    
    return app

# ============================================================================
# APPLICATION INSTANCE
# ============================================================================

# Global app instance
app = None

async def get_app() -> FastAPI:
    """Get or create the application instance."""
    global app
    if app is None:
        app = await create_campaignforge_app()
    return app

# ============================================================================
# MODULE SHUTDOWN HANDLER
# ============================================================================

async def shutdown_modules():
    """Gracefully shutdown all modules."""
    logger.info("Shutting down modules...")
    try:
        await intelligence_module.shutdown()
        logger.info("Intelligence Engine module shutdown complete")
    except Exception as e:
        logger.error(f"Module shutdown error: {e}")

# ============================================================================
# RAILWAY DEPLOYMENT COMPATIBILITY
# ============================================================================

async def initialize_for_railway():
    """Initialize application for Railway deployment."""
    global app
    try:
        app = await create_campaignforge_app()
        logger.info("Railway deployment initialization complete")
        return app
    except Exception as e:
        logger.error(f"Railway initialization failed: {e}")
        
        # Create fallback app
        fallback_app = FastAPI(
            title="CampaignForge AI Backend - Initialization Failed",
            version="2.0.0-fallback"
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
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        @fallback_app.get("/")
        async def fallback_root():
            return {
                "message": "CampaignForge AI Backend - Fallback Mode",
                "status": "initialization_error",
                "docs": "/docs"
            }
        
        return fallback_app

# ============================================================================
# PRODUCTION DEPLOYMENT
# ============================================================================

# Create app synchronously for Railway
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
    logger.info(f"Production app created with {len(app.routes)} routes")
except Exception as e:
    logger.error(f"Failed to create production app: {e}")
    
    # Minimal fallback for Railway
    app = FastAPI(title="CampaignForge AI Backend - Error", version="2.0.0-error")
    
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
            "timestamp": datetime.now(timezone.utc).isoformat()
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
    'get_app',
    'initialize_for_railway',
    'shutdown_modules'
]

__version__ = "2.0.0"
__architecture__ = "modular"