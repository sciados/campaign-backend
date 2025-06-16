from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from uuid import UUID, uuid4
from typing import Optional
import os

from src.core.database import get_db, engine, Base

# Import routes
from src.auth.routes import router as auth_router

app = FastAPI(
    title="CampaignForge AI",
    description="Multimedia Campaign Creation Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://campaignforge-frontend.vercel.app",  # Your Vercel frontend
        "https://*.vercel.app"  # Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth_router)

@app.on_event("startup")
async def startup_event():
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {
        "message": "CampaignForge AI Backend",
        "version": "1.0.0",
        "status": "running",
        "database": "connected" if os.getenv("DATABASE_URL") else "not configured"
    }

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    # Test database connection
    try:
        await db.execute(select(1))
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status
    }

# Simple test endpoint without models first
@app.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint working"}

@app.get("/campaigns")
async def get_campaigns(db: AsyncSession = Depends(get_db)):
    """Get all campaigns - simplified version"""
    try:
        # Import here to avoid circular import issues
        from src.models.campaign import Campaign
        
        result = await db.execute(select(Campaign))
        campaigns = result.scalars().all()
        
        # Convert to simple dict to avoid serialization issues
        campaign_list = []
        for campaign in campaigns:
            campaign_list.append({
                "id": str(campaign.id),
                "title": campaign.title,
                "description": campaign.description,
                "campaign_type": campaign.campaign_type.value if campaign.campaign_type else None,
                "status": campaign.status.value if campaign.status else None,
                "created_at": campaign.created_at.isoformat() if campaign.created_at else None
            })
        
        return {"campaigns": campaign_list}
    except Exception as e:
        # Log the actual error for debugging
        print(f"Error in get_campaigns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Pydantic schemas for campaign creation
class CampaignCreate(BaseModel):
    title: str
    description: Optional[str] = None
    target_audience: Optional[str] = None
    campaign_type: str = "social_media"  # Use string instead of enum for now
    tone: Optional[str] = None
    style: Optional[str] = None
    brand_voice: Optional[str] = None

@app.post("/campaigns")
async def create_campaign(
    campaign_data: CampaignCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new campaign - simplified version"""
    try:
        from src.models.campaign import Campaign, CampaignType, CampaignStatus
        
        # Convert string to enum
        try:
            campaign_type_enum = CampaignType(campaign_data.campaign_type)
        except ValueError:
            campaign_type_enum = CampaignType.SOCIAL_MEDIA  # default
        
        campaign = Campaign(
            title=campaign_data.title,
            description=campaign_data.description,
            target_audience=campaign_data.target_audience,
            campaign_type=campaign_type_enum,
            tone=campaign_data.tone,
            style=campaign_data.style,
            brand_voice=campaign_data.brand_voice,
            user_id=uuid4()  # Generate a random UUID for now
        )
        
        db.add(campaign)
        await db.commit()
        await db.refresh(campaign)
        
        return {
            "message": "Campaign created successfully",
            "campaign": {
                "id": str(campaign.id),
                "title": campaign.title,
                "status": campaign.status.value
            }
        }
    except Exception as e:
        await db.rollback()
        print(f"Error creating campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create campaign: {str(e)}")