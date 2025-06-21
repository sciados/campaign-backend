"""
Main FastAPI application - FIXED VERSION with proper CORS and table creation
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

# Import database and models for table creation
from src.core.database import engine
from src.models import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CampaignForge API",
    description="AI-powered marketing campaign intelligence platform",
    version="1.0.0"
)

# ✅ FIXED: Simple CORS configuration
allowed_origins = [os.getenv("ALLOWED_ORIGINS", "https://campaignforge-frontend.vercel.app")]

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
        logger.info("Database tables created successfully!")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
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
            "version": "1.0.0"
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
            "health": "/health"
        }
    )

# Include all routers with proper prefixes
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(campaigns_router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(intelligence_router, prefix="/api/intelligence", tags=["Intelligence"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])

# ✅ REMOVED: Duplicate auth router that was causing conflicts
# app.include_router(auth_router, prefix="/auth", tags=["Authentication - Legacy"])

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
        }
    )

# ✅ REMOVED: Conflicting OPTIONS handler - let CORS middleware handle this
# @app.options("/{full_path:path}")
# async def options_handler(full_path: str):
#     ...

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        reload=True
    )