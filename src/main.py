# src/main.py - FIXED VERSION with proper import order and error handling
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
import sys
import os

# ============================================================================
# ✅ FIXED: Ensure proper Python path setup
# ============================================================================

# Add src to Python path if not already there
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir)
app_path = os.path.dirname(current_dir)

if src_path not in sys.path:
    sys.path.insert(0, src_path)
if app_path not in sys.path:
    sys.path.insert(0, app_path)

# ============================================================================
# ✅ FIXED: Import database and models BEFORE routers to prevent conflicts
# ============================================================================

# Import database setup first
try:
    from src.core.database import engine, Base, get_db
    logging.info("✅ Database core imported successfully")
except ImportError as e:
    logging.error(f"❌ Failed to import database core: {e}")
    raise

# Import models in dependency order to prevent table conflicts
try:
    # Import base models first
    from src.models.user import User
    from src.models.company import Company
    
    # Import campaign models
    try:
        from src.models.campaign import Campaign
        logging.info("✅ Campaign models imported successfully")
    except ImportError as e:
        logging.warning(f"⚠️ Campaign models not available: {e}")
    
    # Import ClickBank models LAST to prevent conflicts
    try:
        from src.models.clickbank import (
            ClickBankProduct,
            ClickBankCategoryURL,
            UserAffiliatePreferences,
            AffiliateLinkClick,
            ScrapingSchedule,
            ScrapingLog,
            ProductPerformance
        )
        logging.info("✅ ClickBank models imported successfully")
        CLICKBANK_MODELS_AVAILABLE = True
    except ImportError as e:
        logging.warning(f"⚠️ ClickBank models not available: {e}")
        CLICKBANK_MODELS_AVAILABLE = False
    
    # Create all tables after models are imported
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("✅ Database tables created/verified successfully")
    except Exception as e:
        logging.error(f"❌ Database table creation failed: {e}")
        # Try to handle table conflicts
        try:
            logging.info("🔄 Attempting to resolve table conflicts...")
            # Drop and recreate metadata if there are conflicts
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
            logging.info("✅ Database tables recreated successfully")
        except Exception as recreate_error:
            logging.error(f"❌ Failed to recreate tables: {recreate_error}")
            # Continue anyway, tables might already exist
            pass
    
except ImportError as e:
    logging.error(f"❌ Failed to import models: {e}")
    CLICKBANK_MODELS_AVAILABLE = False

# ============================================================================
# ✅ FIXED: Import routers AFTER models are properly set up
# ============================================================================

# Import core routers (always required)
try:
    from src.auth.routes import router as auth_router
    logging.info("✅ Auth router imported successfully")
    AUTH_ROUTER_AVAILABLE = True
except ImportError as e:
    logging.error(f"❌ Auth router not available: {e}")
    AUTH_ROUTER_AVAILABLE = False

try:
    from src.campaigns.routes import router as campaigns_router
    logging.info("✅ Campaigns router imported successfully")
    CAMPAIGNS_ROUTER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ Campaigns router not available: {e}")
    CAMPAIGNS_ROUTER_AVAILABLE = False

try:
    from src.dashboard.routes import router as dashboard_router
    logging.info("✅ Dashboard router imported successfully")
    DASHBOARD_ROUTER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ Dashboard router not available: {e}")
    DASHBOARD_ROUTER_AVAILABLE = False

# Import intelligence routers with proper error handling
INTELLIGENCE_ROUTERS_AVAILABLE = False
ANALYSIS_ROUTER_AVAILABLE = False
CLICKBANK_ROUTER_AVAILABLE = False
AFFILIATE_ROUTER_AVAILABLE = False
CLICKBANK_ADMIN_ROUTER_AVAILABLE = False

try:
    from src.intelligence.routers.analysis_routes import router as analysis_router
    logging.info("✅ Analysis router imported successfully")
    ANALYSIS_ROUTER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ Analysis router not available: {e}")
    analysis_router = None

try:
    from src.intelligence.routers.clickbank_routes import router as clickbank_router
    logging.info("✅ ClickBank routes imported successfully")
    CLICKBANK_ROUTER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ ClickBank routes not available: {e}")
    clickbank_router = None

try:
    from src.intelligence.routers.affiliate_links import router as affiliate_router
    logging.info("✅ Affiliate links router imported successfully")
    AFFILIATE_ROUTER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ Affiliate links router not available: {e}")
    affiliate_router = None

try:
    from src.intelligence.routers.clickbank_admin import router as clickbank_admin_router
    logging.info("✅ ClickBank admin router imported successfully")
    CLICKBANK_ADMIN_ROUTER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ ClickBank admin router not available: {e}")
    clickbank_admin_router = None

# Update intelligence routers status
INTELLIGENCE_ROUTERS_AVAILABLE = any([
    ANALYSIS_ROUTER_AVAILABLE,
    CLICKBANK_ROUTER_AVAILABLE, 
    AFFILIATE_ROUTER_AVAILABLE,
    CLICKBANK_ADMIN_ROUTER_AVAILABLE
])

# ============================================================================
# ✅ FIXED: Application lifespan with proper initialization
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager with proper startup/shutdown handling
    """
    # Startup
    logging.info("🚀 Starting CampaignForge AI Backend...")
    
    # Verify database connection
    try:
        from src.core.database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logging.info("✅ Database connection verified")
    except Exception as e:
        logging.error(f"❌ Database connection failed: {e}")
    
    # Log available features
    features = []
    if AUTH_ROUTER_AVAILABLE:
        features.append("Authentication")
    if CAMPAIGNS_ROUTER_AVAILABLE:
        features.append("Campaigns")
    if DASHBOARD_ROUTER_AVAILABLE:
        features.append("Dashboard")
    if INTELLIGENCE_ROUTERS_AVAILABLE:
        features.append("Intelligence")
    if CLICKBANK_MODELS_AVAILABLE:
        features.append("ClickBank Models")
    
    logging.info(f"🎯 Available features: {', '.join(features)}")
    
    yield
    
    # Shutdown
    logging.info("🛑 Shutting down CampaignForge AI Backend...")

# ============================================================================
# ✅ FIXED: FastAPI app creation with conditional router inclusion
# ============================================================================

app = FastAPI(
    title="CampaignForge AI Backend",
    description="AI-powered marketing campaign generation and management platform",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# ============================================================================
# ✅ FIXED: Middleware configuration
# ============================================================================

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "https://campaignforge.vercel.app",
        "https://campaignforge-frontend.vercel.app",
        "https://*.vercel.app",
        "https://campaign-frontend-production-e2db.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Trusted host middleware for security
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

# ============================================================================
# ✅ FIXED: Router registration with availability checks
# ============================================================================

# Core routers (always included if available)
if AUTH_ROUTER_AVAILABLE:
    app.include_router(auth_router, prefix="/api")
    logging.info("📡 Auth router registered")
else:
    logging.error("❌ Auth router not registered - authentication will not work")

if CAMPAIGNS_ROUTER_AVAILABLE:
    app.include_router(campaigns_router, prefix="/api")
    logging.info("📡 Campaigns router registered")

if DASHBOARD_ROUTER_AVAILABLE:
    app.include_router(dashboard_router, prefix="/api")
    logging.info("📡 Dashboard router registered")

# Intelligence routers (optional, with fallbacks)
intelligence_routes_registered = 0

if ANALYSIS_ROUTER_AVAILABLE and analysis_router:
    app.include_router(analysis_router, prefix="/api")
    logging.info("📡 Analysis router registered")
    intelligence_routes_registered += 1

if CLICKBANK_ROUTER_AVAILABLE and clickbank_router:
    app.include_router(clickbank_router, prefix="/api")
    logging.info("📡 ClickBank routes registered")
    intelligence_routes_registered += 1

if AFFILIATE_ROUTER_AVAILABLE and affiliate_router:
    app.include_router(affiliate_router, prefix="/api")
    logging.info("📡 Affiliate links router registered")
    intelligence_routes_registered += 1

if CLICKBANK_ADMIN_ROUTER_AVAILABLE and clickbank_admin_router:
    app.include_router(clickbank_admin_router, prefix="/api")
    logging.info("📡 ClickBank admin router registered")
    intelligence_routes_registered += 1

if intelligence_routes_registered > 0:
    logging.info(f"✅ Intelligence system: {intelligence_routes_registered} routers registered")
else:
    logging.warning("⚠️ Intelligence system: No routers available")

# ============================================================================
# ✅ FIXED: Health check and status endpoints
# ============================================================================

@app.get("/api/health")
async def health_check():
    """
    Enhanced health check with feature availability
    """
    return {
        "status": "healthy",
        "version": "2.0.0",
        "features": {
            "authentication": AUTH_ROUTER_AVAILABLE,
            "campaigns": CAMPAIGNS_ROUTER_AVAILABLE,
            "dashboard": DASHBOARD_ROUTER_AVAILABLE,
            "intelligence": INTELLIGENCE_ROUTERS_AVAILABLE,
            "clickbank_models": CLICKBANK_MODELS_AVAILABLE,
            "analysis": ANALYSIS_ROUTER_AVAILABLE,
            "clickbank_routes": CLICKBANK_ROUTER_AVAILABLE,
            "affiliate_links": AFFILIATE_ROUTER_AVAILABLE,
            "clickbank_admin": CLICKBANK_ADMIN_ROUTER_AVAILABLE
        },
        "intelligence_routes_count": intelligence_routes_registered,
        "database_status": "connected" if CLICKBANK_MODELS_AVAILABLE else "limited"
    }

@app.get("/api/status")
async def system_status():
    """
    Detailed system status for debugging
    """
    try:
        # Test database connection
        from src.core.database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "application": "CampaignForge AI Backend",
        "version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "database": db_status,
        "routers": {
            "auth": AUTH_ROUTER_AVAILABLE,
            "campaigns": CAMPAIGNS_ROUTER_AVAILABLE,
            "dashboard": DASHBOARD_ROUTER_AVAILABLE,
            "analysis": ANALYSIS_ROUTER_AVAILABLE,
            "clickbank": CLICKBANK_ROUTER_AVAILABLE,
            "affiliate": AFFILIATE_ROUTER_AVAILABLE,
            "clickbank_admin": CLICKBANK_ADMIN_ROUTER_AVAILABLE
        },
        "models": {
            "clickbank_available": CLICKBANK_MODELS_AVAILABLE
        },
        "python_path": sys.path[:3],  # Show first 3 paths for debugging
        "working_directory": os.getcwd()
    }

@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "CampaignForge AI Backend API",
        "version": "2.0.0",
        "docs": "/api/docs",
        "health": "/api/health",
        "status": "/api/status",
        "features_available": intelligence_routes_registered > 0
    }

# ============================================================================
# ✅ FIXED: Global exception handler
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for better error reporting
    """
    logging.error(f"❌ Unhandled exception: {str(exc)}")
    logging.error(f"Request: {request.method} {request.url}")
    
    return {
        "error": "Internal server error",
        "detail": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else "An unexpected error occurred",
        "type": type(exc).__name__
    }