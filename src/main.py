from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from uuid import UUID
from typing import Optional
import os

from src.core.database import get_db, engine
from src.models import Campaign, CampaignType, CampaignStatus, User

# Pydantic schemas
class CampaignCreate(BaseModel):
    title: str
    description: Optional[str] = None
    target_audience: Optional[str] = None
    campaign_type: CampaignType
    tone: Optional[str] = None
    style: Optional[str] = None
    brand_voice: Optional[str] = None

class CampaignResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    target_audience: Optional[str]
    campaign_type: CampaignType
    status: CampaignStatus
    tone: Optional[str]
    style: Optional[str]
    brand_voice: Optional[str]
    created_at: str
    updated_at: Optional[str]
    
    class Config:
        from_attributes = True

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

@app.on_event("startup")
async def startup_event():
    # Create database tables
    from src.core.database import Base
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

@app.get("/campaigns", response_model=list[CampaignResponse])
async def get_campaigns(db: AsyncSession = Depends(get_db)):
    """Get all campaigns"""
    result = await db.execute(select(Campaign))
    campaigns = result.scalars().all()
    return campaigns

@app.post("/campaigns", response_model=CampaignResponse)
async def create_campaign(
    campaign_data: CampaignCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new campaign"""
    # For now, create with a dummy user_id (you'll add auth later)
    campaign = Campaign(
        title=campaign_data.title,
        description=campaign_data.description,
        target_audience=campaign_data.target_audience,
        campaign_type=campaign_data.campaign_type,
        tone=campaign_data.tone,
        style=campaign_data.style,
        brand_voice=campaign_data.brand_voice,
        user_id="00000000-0000-0000-0000-000000000000"  # Placeholder until auth is added
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign

@app.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific campaign"""
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign