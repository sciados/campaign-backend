"""
Main FastAPI application - Clean best practice implementation
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

from src.core.database import engine, Base
from src.auth.routes import router as auth_router
from src.admin.routes import router as admin_router

# Lifespan event handler (modern approach)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✓ Database tables created successfully")
    except Exception as e:
        print(f"✗ Database startup error: {str(e)}")
    
    yield
    
    # Shutdown (add cleanup code here if needed)
    print("🔄 Application shutting down")

# Create FastAPI app with lifespan
app = FastAPI(
    title="CampaignForge AI",
    description="Multimedia Campaign Creation Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://campaignforge-frontend.vercel.app",  # Production frontend
        "https://campaignforge-frontend-git-main-yourusername.vercel.app",  # Git branch deployments
        "*"  # Temporary fix - replace with specific domains in production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors gracefully"""
    print(f"Global exception: {type(exc).__name__}: {str(exc)}")  # Add logging
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc),
            "path": str(request.url)
        }
    )

# Include routers
app.include_router(auth_router)
app.include_router(admin_router)

# Note: Add dashboard router when src/dashboard/routes.py is created
# from src.dashboard.routes import router as dashboard_router  
# app.include_router(dashboard_router)

# Basic routes
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "CampaignForge AI",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected" if os.getenv("DATABASE_URL") else "not configured"
    }

# Handle preflight requests
@app.options("/{full_path:path}")
async def options_handler():
    """Handle CORS preflight requests"""
    return JSONResponse(content={})