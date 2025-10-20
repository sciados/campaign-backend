# src/main.py
"""
CampaignForge AI Backend - Application Orchestration (Production-ready)
Refactored to use ASGI lifespan for safe startup under Uvicorn/Gunicorn/Railway
"""

import os
import sys
import logging
from typing import Optional
from contextlib import asynccontextmanager

# FastAPI imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Local imports (kept as they were in your original file)
from src.core.config.settings import settings
from src.core.database.session import initialize_async_session, close_async_session
from src.core.factories.service_factory import ServiceFactory
from src.core.health.metrics import initialize_health_checks
from src.core.health.health_checks import register_health_routes
from src.core.middleware.cors_middleware import setup_cors_middleware
from src.core.shared.responses import SuccessResponse
from src.core.shared.exceptions import CampaignForgeException

# Import modules registries (these modules register routers/services)
from src.campaigns.campaigns_module import CampaignsModule
from src.content.content_module import ContentModule
from src.storage.storage_module import StorageModule
from src.users.users_module import UsersModule
from src.intelligence.intelligence_module import IntelligenceModule
from src.mockups.mockup_module import MockupModule

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Module list used for initialization order
MODULE_REGISTRY = [
    ("campaigns", CampaignsModule),
    ("content", ContentModule),
    ("storage", StorageModule),
    ("users", UsersModule),
    ("intelligence", IntelligenceModule),
    ("mockups", MockupModule),
]

# Keep __version__ etc. near the top for metadata like before
__version__ = "3.3.1"
__description__ = "AI-powered marketing campaign generation and management platform with modular architecture"
__architecture__ = "modular_microservices"
__refactoring_date__ = "2025-01-17"

# Global service factory (single shared factory for services)
service_factory: Optional[ServiceFactory] = None

# Track initialized modules for later shutdown
_initialized_modules = []


async def initialize_modules(app: FastAPI):
    """
    Initialize all modules and attach their routers to the provided FastAPI app.
    This function is async and must be awaited inside the ASGI lifespan.
    """
    global service_factory, _initialized_modules

    logger.info("🚀 Initializing CampaignForge modules...")

    # Initialize the async DB session manager first
    try:
        await initialize_async_session()
        logger.info("✅ Async DB session initialized")
    except Exception as e:
        logger.error(f"Failed to initialize async DB session: {e}")
        raise

    # Initialize the service factory (registers services)
    try:
        service_factory = ServiceFactory()
        service_factory.initialize()
        logger.info("✅ ServiceFactory initialized with services")
    except Exception as e:
        logger.error(f"Failed to initialize ServiceFactory: {e}")
        raise

    # Iterate through module registry and initialize modules
    for name, ModuleClass in MODULE_REGISTRY:
        try:
            logger.info(f"🔧 Creating module: {name}")
            module_instance = ModuleClass()
            # if module exposes an async initialize() we call it
            if hasattr(module_instance, "initialize"):
                initialized = await module_instance.initialize()
                logger.info(f"✅ {name} module initialized (async)")
            else:
                # If module has get_router we include that router
                router = getattr(module_instance, "get_router", None)
                if callable(router):
                    app.include_router(router())
                    logger.info(f"✅ {name} module router included (sync)")
                else:
                    logger.info(f"ℹ️ {name} module has no initialize() or get_router()")
            # Some modules might expose router attribute
            if hasattr(module_instance, "router"):
                try:
                    app.include_router(module_instance.router)
                    logger.info(f"✅ Included router for module: {name}")
                except Exception:
                    # router may have been included already
                    pass

            _initialized_modules.append((name, module_instance))
        except Exception as e:
            logger.error(f"❌ Failed to initialize module '{name}': {e}")
            # continue initializing other modules - partial initialization is allowed
            continue

    # Setup health checks / monitoring routes if available
    try:
        initialize_health_checks(app)
        register_health_routes(app)
        logger.info("✅ Health checks and monitoring routes registered")
    except Exception as e:
        logger.warning(f"⚠️ Health checks registration failed: {e}")

    # Setup CORS (if not already set by modules)
    try:
        setup_cors_middleware(app)
        logger.info("✅ CORS middleware setup completed")
    except Exception as e:
        logger.warning(f"⚠️ CORS setup failed: {e}")

    logger.info("🎉 All modules initialization attempted (check logs for per-module errors).")


async def shutdown_modules():
    """
    Best-effort module shutdown / cleanup for graceful termination.
    Called during lifespan cleanup (when ASGI server is stopping app).
    """
    global _initialized_modules

    logger.info("🛑 Shutting down CampaignForge modules...")

    # reverse-order shutdown
    for name, module_instance in reversed(_initialized_modules):
        try:
            if hasattr(module_instance, "shutdown"):
                await module_instance.shutdown()
                logger.info(f"✅ {name} module shutdown (async)")
            elif hasattr(module_instance, "close"):
                maybe = module_instance.close()
                if hasattr(maybe, "__await__"):
                    await maybe
                logger.info(f"✅ {name} module closed (sync/awaited)")
            else:
                logger.debug(f"ℹ️ {name} module had no shutdown/close method")
        except Exception as e:
            logger.warning(f"⚠️ Error shutting down module '{name}': {e}")

    # Close DB session manager
    try:
        await close_async_session()
        logger.info("✅ Async DB session closed")
    except Exception as e:
        logger.warning(f"⚠️ Error closing async DB session: {e}")

    _initialized_modules = []


# ---------------------------------------------------------
# The main app creation function
# - Now accepts an optional FastAPI `app` argument.
# - If an `app` is provided, routers and middleware are registered into it.
# - If None, a new FastAPI app is created and returned (backwards-compatible).
# ---------------------------------------------------------
async def create_campaignforge_app(app: Optional[FastAPI] = None) -> FastAPI:
    """
    Create and/or initialize the CampaignForge FastAPI app with modular routers.

    If a FastAPI `app` instance is provided, this function will attach routers
    and middleware to that instance in-place and return it. This allows using
    the same app instance for ASGI lifespan initialization without recreating
    another FastAPI object.
    """
    # If an app is not provided, create one (backwards compatibility)
    create_new_app = app is None
    if create_new_app:
        app = FastAPI(
            title=f"CampaignForge AI Backend v{__version__}",
            version=__version__,
            description=__description__,
            docs_url="/docs",
        )

        # Standard CORS policies (modules may augment/override later)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Attach a simple root endpoint if not present
    try:
        @app.get("/", include_in_schema=False)
        async def root():
            return {"status": "ok", "version": __version__}
    except Exception:
        # may already be attached
        pass

    # Initialize modules and attach routers into the given app
    await initialize_modules(app)

    return app


# ============================================================================
# Lifespan-based ASGI app initialization (compatible with Railway/Uvicorn)
# ============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan handler initializes modules at startup without running an event loop
    during import time. This avoids asyncio.run() errors when running under an
    ASGI server that already has an event loop (e.g., Uvicorn/Gunicorn).
    """
    try:
        # Initialize modules into the provided `app` instance (this will
        # include routers, middleware and register services).
        await create_campaignforge_app(app)
        yield
    finally:
        # Clean shutdown of background tasks and modules (best-effort)
        try:
            await shutdown_modules()
        except Exception as e:
            logger.warning(f"Error during shutdown_modules in lifespan: {e}")


# Create the FastAPI app instance used by the ASGI server
app = FastAPI(
    title=f"CampaignForge AI Backend v{__version__}",
    version=__version__,
    description=__description__,
    lifespan=lifespan,
    docs_url="/docs",
)

# If someone runs this file directly, start uvicorn (development)
if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload_flag = os.getenv("DEV_RELOAD", "false").lower() in ("1", "true", "yes")

    logger.info(f"Starting uvicorn on {host}:{port} (reload={reload_flag})")
    uvicorn.run("src.main:app", host=host, port=port, reload=reload_flag)
