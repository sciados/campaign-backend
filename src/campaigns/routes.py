# src/campaigns/routes.py
"""
Campaign routes for CRUD operations and dashboard stats
"""
import logging
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from src.core.database import get_db
from src.auth.routes import get_current_user  # Import your auth dependency
from src.models.user import User
from src.models.company import Company
from src.models.campaign import Campaign, CampaignType, CampaignStatus

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/campaigns",
    tags=["Campaigns"],
    responses={404: {"description": "Not found"}},
)

# --- Pydantic Models ---

class CampaignCreate(BaseModel):
    """Schema for creating a new campaign."""
    title: str
    description: Optional[str] = ""
    campaign_type: str
    target_audience: Optional[str] = ""
    tone: Optional[str] = "professional"
    style: Optional[str] = "modern"
    brand_voice: Optional[str] = ""

class CampaignUpdate(BaseModel):
    """Schema for updating an existing campaign."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    target_audience: Optional[str] = None
    tone: Optional[str] = None
    style: Optional[str] = None
    brand_voice: Optional[str] = None

class CampaignResponse(BaseModel):
    """Schema for campaign response."""
    id: UUID
    title: str
    description: Optional[str]
    campaign_type: str
    status: str
    created_at: datetime
    user_id: UUID
    company_id: UUID
    tone: Optional[str]
    style: Optional[str]
    target_audience: Optional[str]
    intelligence_count: int = 0
    generated_content_count: int = 0
    confidence_score: Optional[float] = None
    last_activity: Optional[datetime] = None

class CampaignListResponse(BaseModel):
    """Schema for campaign list with pagination."""
    campaigns: List[CampaignResponse]
    total: int
    page: int
    limit: int
    pages: int

class DashboardStatsResponse(BaseModel):
    """Schema for dashboard statistics."""
    total_campaigns: int
    active_campaigns: int
    draft_campaigns: int
    completed_campaigns: int
    total_intelligence_sources: int
    total_generated_content: int
    credits_used_this_month: int
    credits_remaining: int
    avg_confidence_score: float

# --- Helper Functions ---

async def get_campaign_intelligence_count(campaign_id: UUID, db: AsyncSession) -> int:
    """Get count of intelligence sources for a campaign."""
    try:
        # This assumes you have a CampaignIntelligence model
        # from src.models.intelligence import CampaignIntelligence
        # count = await db.scalar(
        #     select(func.count(CampaignIntelligence.id))
        #     .where(CampaignIntelligence.campaign_id == campaign_id)
        # )
        # return count or 0
        
        # For now, return mock data until intelligence model is integrated
        import random
        return random.randint(0, 5)
    except Exception:
        return 0

async def get_campaign_content_count(campaign_id: UUID, db: AsyncSession) -> int:
    """Get count of generated content for a campaign."""
    try:
        # This assumes you have a GeneratedContent model
        # from src.models.intelligence import GeneratedContent
        # count = await db.scalar(
        #     select(func.count(GeneratedContent.id))
        #     .where(GeneratedContent.campaign_id == campaign_id)
        # )
        # return count or 0
        
        # For now, return mock data until content model is integrated
        import random
        return random.randint(5, 30)
    except Exception:
        return 0

# --- API Endpoints ---

@router.get("/", response_model=CampaignListResponse, summary="Get user's campaigns")
async def get_campaigns(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    campaign_type: Optional[str] = Query(None)
):
    """Get paginated list of campaigns for the current user's company."""
    
    try:
        # Build query
        query = select(Campaign).where(Campaign.company_id == current_user.company_id)
        
        # Apply filters
        conditions = []
        if search:
            conditions.append(
                or_(
                    Campaign.title.ilike(f"%{search}%"),
                    Campaign.description.ilike(f"%{search}%")
                )
            )
        
        if status:
            conditions.append(Campaign.status == status)
            
        if campaign_type:
            conditions.append(Campaign.campaign_type == campaign_type)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count
        total_query = select(func.count(Campaign.id)).where(Campaign.company_id == current_user.company_id)
        if conditions:
            total_query = total_query.where(and_(*conditions))
        
        total = await db.scalar(total_query) or 0
        
        # Apply pagination and ordering
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit).order_by(Campaign.created_at.desc())
        
        result = await db.execute(query)
        campaigns = result.scalars().all()
        
        # Build response with additional counts
        campaign_responses = []
        for campaign in campaigns:
            intelligence_count = await get_campaign_intelligence_count(campaign.id, db)
            content_count = await get_campaign_content_count(campaign.id, db)
            
            campaign_responses.append(CampaignResponse(
                id=campaign.id,
                title=campaign.title,
                description=campaign.description,
                campaign_type=campaign.campaign_type,
                status=campaign.status,
                created_at=campaign.created_at,
                user_id=campaign.user_id,
                company_id=campaign.company_id,
                tone=campaign.tone,
                style=campaign.style,
                target_audience=campaign.target_audience,
                intelligence_count=intelligence_count,
                generated_content_count=content_count,
                confidence_score=0.85,  # Mock data for now
                last_activity=campaign.updated_at if hasattr(campaign, 'updated_at') else campaign.created_at
            ))
        
        return CampaignListResponse(
            campaigns=campaign_responses,
            total=total,
            page=page,
            limit=limit,
            pages=((total - 1) // limit + 1) if total > 0 else 0
        )
        
    except Exception as e:
        logger.exception(f"Error fetching campaigns for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch campaigns: {str(e)}"
        )

@router.post("/", response_model=CampaignResponse, summary="Create new campaign")
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new campaign for the current user's company."""
    
    try:
        # Validate campaign type
        valid_types = [t.value for t in CampaignType]
        if campaign_data.campaign_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid campaign type. Must be one of: {valid_types}"
            )
        
        # Create new campaign
        new_campaign = Campaign(
            id=uuid4(),
            title=campaign_data.title,
            description=campaign_data.description,
            campaign_type=campaign_data.campaign_type,
            status=CampaignStatus.DRAFT.value,
            target_audience=campaign_data.target_audience,
            tone=campaign_data.tone,
            style=campaign_data.style,
            brand_voice=campaign_data.brand_voice,
            user_id=current_user.id,
            company_id=current_user.company_id,
            content={},
            settings={},
            campaign_metadata={}
        )
        
        db.add(new_campaign)
        await db.commit()
        await db.refresh(new_campaign)
        
        # Update company's total campaigns count
        company = await db.scalar(select(Company).where(Company.id == current_user.company_id))
        if company:
            company.total_campaigns += 1
            await db.commit()
        
        logger.info(f"Campaign '{new_campaign.title}' created by user {current_user.id}")
        
        return CampaignResponse(
            id=new_campaign.id,
            title=new_campaign.title,
            description=new_campaign.description,
            campaign_type=new_campaign.campaign_type,
            status=new_campaign.status,
            created_at=new_campaign.created_at,
            user_id=new_campaign.user_id,
            company_id=new_campaign.company_id,
            tone=new_campaign.tone,
            style=new_campaign.style,
            target_audience=new_campaign.target_audience,
            intelligence_count=0,
            generated_content_count=0,
            confidence_score=0.0,
            last_activity=new_campaign.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.exception(f"Error creating campaign for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )

@router.get("/{campaign_id}", response_model=CampaignResponse, summary="Get campaign by ID")
async def get_campaign(
    campaign_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific campaign by ID."""
    
    try:
        campaign = await db.scalar(
            select(Campaign).where(
                and_(
                    Campaign.id == campaign_id,
                    Campaign.company_id == current_user.company_id
                )
            )
        )
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        intelligence_count = await get_campaign_intelligence_count(campaign.id, db)
        content_count = await get_campaign_content_count(campaign.id, db)
        
        return CampaignResponse(
            id=campaign.id,
            title=campaign.title,
            description=campaign.description,
            campaign_type=campaign.campaign_type,
            status=campaign.status,
            created_at=campaign.created_at,
            user_id=campaign.user_id,
            company_id=campaign.company_id,
            tone=campaign.tone,
            style=campaign.style,
            target_audience=campaign.target_audience,
            intelligence_count=intelligence_count,
            generated_content_count=content_count,
            confidence_score=0.85,
            last_activity=campaign.updated_at if hasattr(campaign, 'updated_at') else campaign.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error fetching campaign {campaign_id} for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch campaign: {str(e)}"
        )

@router.put("/{campaign_id}", response_model=CampaignResponse, summary="Update campaign")
async def update_campaign(
    campaign_id: UUID,
    campaign_update: CampaignUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing campaign."""
    
    try:
        campaign = await db.scalar(
            select(Campaign).where(
                and_(
                    Campaign.id == campaign_id,
                    Campaign.company_id == current_user.company_id
                )
            )
        )
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Update fields if provided
        if campaign_update.title is not None:
            campaign.title = campaign_update.title
        if campaign_update.description is not None:
            campaign.description = campaign_update.description
        if campaign_update.status is not None:
            valid_statuses = [s.value for s in CampaignStatus]
            if campaign_update.status not in valid_statuses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status. Must be one of: {valid_statuses}"
                )
            campaign.status = campaign_update.status
        if campaign_update.target_audience is not None:
            campaign.target_audience = campaign_update.target_audience
        if campaign_update.tone is not None:
            campaign.tone = campaign_update.tone
        if campaign_update.style is not None:
            campaign.style = campaign_update.style
        if campaign_update.brand_voice is not None:
            campaign.brand_voice = campaign_update.brand_voice
        
        await db.commit()
        await db.refresh(campaign)
        
        logger.info(f"Campaign {campaign_id} updated by user {current_user.id}")
        
        intelligence_count = await get_campaign_intelligence_count(campaign.id, db)
        content_count = await get_campaign_content_count(campaign.id, db)
        
        return CampaignResponse(
            id=campaign.id,
            title=campaign.title,
            description=campaign.description,
            campaign_type=campaign.campaign_type,
            status=campaign.status,
            created_at=campaign.created_at,
            user_id=campaign.user_id,
            company_id=campaign.company_id,
            tone=campaign.tone,
            style=campaign.style,
            target_audience=campaign.target_audience,
            intelligence_count=intelligence_count,
            generated_content_count=content_count,
            confidence_score=0.85,
            last_activity=campaign.updated_at if hasattr(campaign, 'updated_at') else campaign.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.exception(f"Error updating campaign {campaign_id} for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign: {str(e)}"
        )

@router.delete("/{campaign_id}", summary="Delete campaign")
async def delete_campaign(
    campaign_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a campaign."""
    
    try:
        campaign = await db.scalar(
            select(Campaign).where(
                and_(
                    Campaign.id == campaign_id,
                    Campaign.company_id == current_user.company_id
                )
            )
        )
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        await db.delete(campaign)
        
        # Update company's total campaigns count
        company = await db.scalar(select(Company).where(Company.id == current_user.company_id))
        if company and company.total_campaigns > 0:
            company.total_campaigns -= 1
            await db.commit()
        else:
            await db.commit()
        
        logger.info(f"Campaign {campaign_id} deleted by user {current_user.id}")
        
        return {"message": "Campaign deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.exception(f"Error deleting campaign {campaign_id} for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete campaign: {str(e)}"
        )

@router.get("/dashboard/stats", response_model=DashboardStatsResponse, summary="Get dashboard statistics")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard statistics for the current user's company."""
    
    try:
        # Get current date ranges
        now = datetime.utcnow()
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Campaign statistics
        total_campaigns = await db.scalar(
            select(func.count(Campaign.id)).where(Campaign.company_id == current_user.company_id)
        ) or 0
        
        active_campaigns = await db.scalar(
            select(func.count(Campaign.id)).where(
                and_(
                    Campaign.company_id == current_user.company_id,
                    Campaign.status == CampaignStatus.ACTIVE.value
                )
            )
        ) or 0
        
        draft_campaigns = await db.scalar(
            select(func.count(Campaign.id)).where(
                and_(
                    Campaign.company_id == current_user.company_id,
                    Campaign.status == CampaignStatus.DRAFT.value
                )
            )
        ) or 0
        
        completed_campaigns = await db.scalar(
            select(func.count(Campaign.id)).where(
                and_(
                    Campaign.company_id == current_user.company_id,
                    Campaign.status == CampaignStatus.COMPLETED.value
                )
            )
        ) or 0
        
        # Get company data for credits
        company = await db.scalar(select(Company).where(Company.id == current_user.company_id))
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        credits_used = company.monthly_credits_used
        credits_limit = company.monthly_credits_limit
        credits_remaining = max(0, credits_limit - credits_used)
        
        # Mock intelligence and content data until those models are integrated
        total_intelligence_sources = total_campaigns * 2  # Mock: 2 intelligence sources per campaign
        total_generated_content = total_campaigns * 8     # Mock: 8 content pieces per campaign
        avg_confidence_score = 0.85
        
        return DashboardStatsResponse(
            total_campaigns=total_campaigns,
            active_campaigns=active_campaigns,
            draft_campaigns=draft_campaigns,
            completed_campaigns=completed_campaigns,
            total_intelligence_sources=total_intelligence_sources,
            total_generated_content=total_generated_content,
            credits_used_this_month=credits_used,
            credits_remaining=credits_remaining,
            avg_confidence_score=avg_confidence_score
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error fetching dashboard stats for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard statistics: {str(e)}"
        )