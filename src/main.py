"""
Main FastAPI application - UPDATED VERSION with Fixed CORS
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Import route modules
from src.auth.routes import router as auth_router
from src.campaigns.routes import router as campaigns_router
from src.dashboard.routes import router as dashboard_router
from src.intelligence.routes import router as intelligence_router
from src.admin.routes import router as admin_router
from src.intelligence.test_routes import router as test_router

# ✅ NEW: Import landing page and analytics routes
from src.intelligence.generators.landing_page.routes import router as landing_pages_router

# Create analytics router placeholder if it doesn't exist
try:
    from src.analytics.routes import router as analytics_router
    ANALYTICS_AVAILABLE = True
except ImportError:
    from fastapi import APIRouter
    analytics_router = APIRouter()
    ANALYTICS_AVAILABLE = False

# Import database and models for table creation
from src.core.database import engine
from src.models import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CampaignForge API",
    description="AI-powered marketing campaign intelligence platform with landing page generation",
    version="1.0.0"
)
app.include_router(test_router)

# ✅ FIXED: Better CORS configuration with multiple origins
allowed_origins = [
    "https://campaignforge-frontend.vercel.app",
    "http://localhost:3000",
    "http://localhost:3001", 
    "https://campaign-backend-production-e2db.up.railway.app"
]

# Add custom origins from environment variable if provided
custom_origins = os.getenv("ALLOWED_ORIGINS")
if custom_origins:
    additional_origins = [origin.strip() for origin in custom_origins.split(",")]
    allowed_origins.extend(additional_origins)

logger.info(f"🌐 CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Add startup event to create tables
@app.on_event("startup")
async def create_tables():
    """Create database tables on startup"""
    try:
        logger.info("Creating database tables...")
        async with engine.begin() as conn:
            # Import all models to ensure they're registered
            from src.models import (
                User, Company, Campaign, CampaignAsset, CampaignIntelligence, 
                GeneratedContent, SmartURL, CompanyMembership, CompanyInvitation
            )
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created successfully!")
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        raise

# Add a health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "CampaignForge API",
            "version": "1.0.0",
            "cors_origins": allowed_origins,
            "features": {
                "campaign_intelligence": True,
                "landing_page_generation": True,
                "real_time_analytics": ANALYTICS_AVAILABLE,
                "a_b_testing": True
            }
        }
    )

# Add root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse(
        status_code=200,
        content={
            "message": "CampaignForge API is running",
            "status": "operational",
            "docs": "/docs",
            "health": "/health",
            "features": {
                "🧠 AI Campaign Intelligence": "/api/intelligence/",
                "🚀 Landing Page Generation": "/api/landing-pages/",
                "📊 Real-time Analytics": "/api/analytics/",
                "👥 Team Collaboration": "/api/auth/",
                "📈 Campaign Management": "/api/campaigns/"
            }
        }
    )

# Include all routers with proper prefixes
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(campaigns_router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(intelligence_router, prefix="/api/intelligence", tags=["Intelligence"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])

# ✅ NEW: Include landing page and analytics routes
app.include_router(landing_pages_router, prefix="/api", tags=["Landing Pages"])
if ANALYTICS_AVAILABLE:
    app.include_router(analytics_router, prefix="/api", tags=["Analytics"])
    logger.info("✅ Analytics routes loaded")
else:
    logger.warning("⚠️ Analytics routes not available")

# Add explicit CORS preflight handler
@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """Handle CORS preflight requests"""
    return JSONResponse(
        status_code=200,
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true"
        }
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler to prevent 500 errors from crashing the app"""
    logger.error(f"Global exception handler caught: {exc}")
    logger.error(f"Request URL: {request.url}")
    logger.error(f"Request method: {request.method}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "details": str(exc) if app.debug else "Contact support for assistance"
        },
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        reload=True
    )