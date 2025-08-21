# src/core/app_factory.py - App Creation & Configuration (FIXED - NO AI DISCOVERY INTERFERENCE)
"""
FastAPI app creation, middleware, basic configuration, and lifespan management
Responsibility: FastAPI app instantiation, CORS middleware, TrustedHost middleware,
Global exception handlers, Basic app metadata, Lifespan management
"""

import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import Response
from sqlalchemy import text

logger = logging.getLogger(__name__)

# ============================================================================
# 🔧 CRITICAL FIX: ASYNC SESSION MANAGER FOR CONTEXT MANAGER PROTOCOL
# ============================================================================

class AsyncSessionManager:
    """Async session manager that supports context manager protocol"""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        """Enter async context manager"""
        from src.core.database import AsyncSessionLocal
        self.session = AsyncSessionLocal()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager"""
        if self.session:
            await self.session.close()

def get_async_session_manager():
    """Get async session manager for context manager usage"""
    return AsyncSessionManager()

# ============================================================================
# ✅ APPLICATION LIFESPAN - FIXED VERSION (NO AI DISCOVERY INTERFERENCE)
# ============================================================================

@asynccontextmanager
async def create_lifespan(app: FastAPI):
    """Application lifespan manager - FIXED VERSION"""
    # Startup
    logging.info("🚀 Starting CampaignForge AI Backend with Ultra-Cheap AI + Dual Storage + AI Monitoring + Enhanced Email Generation + AI Discovery System + FIXED Content Routes...")
    
    # ✅ FIX: Test database connection with proper text import
    try:
        from src.core.database import engine
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logging.info("✅ Database connection verified")
    except Exception as e:
        logging.error(f"❌ Database connection failed: {e}")

    # 🔧 CRITICAL FIX: Enhanced email system health check with proper session management
    try:
        from src.models.email_subject_templates import EmailSubjectTemplate
        EMAIL_MODELS_AVAILABLE = True
        logging.info("✅ Enhanced email models available")
    except ImportError:
        EMAIL_MODELS_AVAILABLE = False
        logging.warning("⚠️ Enhanced email models not available")

    if EMAIL_MODELS_AVAILABLE:
        try:
            from src.intelligence.generators.database_seeder import seed_subject_line_templates
            from sqlalchemy import select, func
            
            # 🔧 FIX: Use proper async context manager
            async with get_async_session_manager() as db:
                # Check if templates exist
                result = await db.execute(select(func.count(EmailSubjectTemplate.id)))
                template_count = result.scalar()
                
                if template_count == 0:
                    logging.info("🔥 Seeding email templates on startup...")
                    await seed_subject_line_templates()
                    logging.info("✅ Email templates seeded successfully")
                else:
                    logging.info(f"✅ Enhanced email system ready with {template_count} templates")
                    
        except Exception as e:
            logging.warning(f"⚠️ Enhanced email system startup check failed: {str(e)}")

    # ✅ NEW: Test storage system health
    try:
        from src.storage.universal_dual_storage import get_storage_manager
        storage_manager = get_storage_manager()
        health = await storage_manager.get_storage_health()
        logging.info(f"✅ Storage system health: {health['overall_status']}")
    except Exception as e:
        logging.warning(f"⚠️ Storage system health check failed: {e}")
    
    # ✅ NEW: Initialize AI monitoring system
    try:
        from src.intelligence.utils.smart_router import get_smart_router
        from src.intelligence.generators.factory import get_global_factory
        
        smart_router = get_smart_router()
        enhanced_factory = get_global_factory()
        
        logging.info("✅ AI monitoring system initialized")
    except Exception as e:
        logging.warning(f"⚠️ AI monitoring system initialization failed: {e}")
    
    # ✅ REMOVED: AI Discovery initialization that was causing interference
    # Let AI Discovery work as it did before refactoring - no interference!
    
    logging.info("🎯 CampaignForge AI Backend startup completed")
    
    yield
    
    # Shutdown
    logging.info("🛑 Shutting down CampaignForge AI Backend...")

# ============================================================================
# ✅ MIDDLEWARE CONFIGURATION
# ============================================================================

def configure_cors_middleware(app: FastAPI):
    """Configure CORS middleware"""
    print("🔧 Configuring CORS middleware...")
    
    # Add CORS middleware with explicit configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:3001", 
            "https://campaignforge.vercel.app",
            "https://campaignforge-frontend.vercel.app",
            "https://rodgersdigital.com",
            "https://www.rodgersdigital.com",
            "https://rodgersdigital.vercel.app",
            "https://www.rodgersdigital.vercel.app",
            "https://*.vercel.app"  # This might not work, so let's be explicit
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
    
    print("✅ CORS middleware configured")
    print("🌐 Allowed origins include:")
    print("  - https://www.rodgersdigital.com")
    print("  - https://rodgersdigital.com") 
    print("  - https://rodgersdigital.vercel.app")
    print("  - https://www.rodgersdigital.vercel.app")

def configure_trusted_host_middleware(app: FastAPI):
    """Configure TrustedHost middleware"""
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[
            "localhost",
            "127.0.0.1",
            "*.railway.app",
            "*.vercel.app",
            "campaign-backend-production-e2db.up.railway.app"
        ]
    )

def configure_custom_middleware(app: FastAPI):
    """Configure custom middleware"""
    
    @app.middleware("http")
    async def cors_fix_middleware(request: Request, call_next):
        """
        Simplified middleware that doesn't interfere with CORS
        """
        # Skip all middleware processing for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            response = await call_next(request)
            return response
        
        # For all other requests, just pass through
        response = await call_next(request)
        
        # Only add security headers in production, and only for non-OPTIONS
        if os.getenv("RAILWAY_ENVIRONMENT_NAME") == "production":
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
        
        return response

# ============================================================================
# ✅ GLOBAL EXCEPTION HANDLER
# ============================================================================

def configure_exception_handlers(app: FastAPI):
    """Configure global exception handlers"""
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Global exception handler"""
        logging.error(f"❌ Unhandled exception: {str(exc)}")
        logging.error(f"Request: {request.method} {request.url}")
        
        return {
            "error": "Internal server error",
            "detail": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else "An unexpected error occurred",
            "type": type(exc).__name__
        }

# ============================================================================
# ✅ FASTAPI APP CREATION - FIXED
# ============================================================================

async def create_app() -> FastAPI:
    """
    Create and configure FastAPI application - FIXED
    """
    # 🔧 FIX: Don't await the lifespan function, just pass the function reference
    lifespan = create_lifespan  # ✅ FIXED: No await here!
    
    # Create FastAPI app
    app = FastAPI(
        title="CampaignForge AI Backend",
        description="AI-powered marketing campaign generation with enhanced email generation, ultra-cheap image generation, dual storage, AI monitoring, AI platform discovery system, and FIXED intelligence-based content generation",
        version="3.3.1",  # 🆕 NEW: Updated version for refactoring
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan
    )
    
    # Configure middleware
    configure_cors_middleware(app)
    configure_trusted_host_middleware(app)
    configure_custom_middleware(app)
    
    # Configure exception handlers
    configure_exception_handlers(app)
    
    logging.info("✅ FastAPI app created and configured")
    return app

# ============================================================================
# ✅ EXPORTS
# ============================================================================

__all__ = [
    'create_app',
    'AsyncSessionManager',
    'get_async_session_manager',
    'configure_cors_middleware',
    'configure_trusted_host_middleware',
    'configure_custom_middleware',
    'configure_exception_handlers'
]