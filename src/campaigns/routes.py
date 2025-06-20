"""
Campaign routes - SAFE VERSION without intelligence dependencies
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID
import logging

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.models import Campaign, User, Company, CampaignType, CampaignStatus
from pydantic import BaseModel
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class CampaignCreate(BaseModel):
    title: str
    description: Optional[str] = None
    keywords: Optional[List[str]] = []
    target_audience: Optional[str] = None
    campaign_type: str = "universal"
    tone: Optional[str] = None
    style: Optional[str] = None

class CampaignUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    target_audience: Optional[str] = None
    campaign_type: Optional[str] = None
    status: Optional[str] = None
    tone: Optional[str] = None
    style: Optional[str] = None

class CampaignResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    keywords: List[str] = []
    target_audience: Optional[str] = None
    campaign_type: str
    status: str
    tone: Optional[str] = None
    style: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    workflow_state: str
    completion_percentage: float
    sources_count: int = 0
    intelligence_count: int = 0
    content_count: int = 0

    class Config:
        from_attributes = True

# ============================================================================
# CAMPAIGN ROUTES
# ============================================================================

@router.get("/", response_model=List[CampaignResponse])
async def get_campaigns(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    campaign_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all campaigns for the current user's company"""
    try:
        logger.info(f"Getting campaigns for user {current_user.id}, company {current_user.company_id}")
        
        # Build query
        query = select(Campaign).where(Campaign.company_id == current_user.company_id)
        
        # Add filters
        if status:
            query = query.where(Campaign.status == status)
        if campaign_type:
            query = query.where(Campaign.campaign_type == campaign_type)
        
        # Add pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        campaigns = result.scalars().all()
        
        logger.info(f"Found {len(campaigns)} campaigns")
        
        # Convert to response format
        campaign_responses = []
        for campaign in campaigns:
            campaign_response = CampaignResponse(
                id=str(campaign.id),
                title=campaign.title,
                description=campaign.description,
                keywords=campaign.keywords or [],
                target_audience=campaign.target_audience,
                campaign_type=campaign.campaign_type.value if campaign.campaign_type else "universal",
                status=campaign.status.value if campaign.status else "draft",
                tone=campaign.tone,
                style=campaign.style,
                created_at=campaign.created_at,
                updated_at=campaign.updated_at,
                workflow_state=campaign.workflow_state.value if campaign.workflow_state else "basic_setup",
                completion_percentage=campaign.calculate_completion_percentage(),
                sources_count=campaign.sources_count or 0,
                intelligence_count=campaign.intelligence_extracted or 0,
                content_count=campaign.content_generated or 0
            )
            campaign_responses.append(campaign_response)
        
        return campaign_responses
        
    except Exception as e:
        logger.error(f"Error getting campaigns: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve campaigns: {str(e)}"
        )

@router.post("/", response_model=CampaignResponse)
async def create_campaign(
    campaign_data: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new campaign"""
    try:
        logger.info(f"Creating campaign for user {current_user.id}")
        
        # Create new campaign
        new_campaign = Campaign(
            title=campaign_data.title,
            description=campaign_data.description,
            keywords=campaign_data.keywords or [],
            target_audience=campaign_data.target_audience,
            campaign_type=CampaignType(campaign_data.campaign_type),
            tone=campaign_data.tone,
            style=campaign_data.style,
            user_id=current_user.id,
            company_id=current_user.company_id,
            status=CampaignStatus.DRAFT
        )
        
        db.add(new_campaign)
        await db.commit()
        await db.refresh(new_campaign)
        
        logger.info(f"Created campaign {new_campaign.id}")
        
        return CampaignResponse(
            id=str(new_campaign.id),
            title=new_campaign.title,
            description=new_campaign.description,
            keywords=new_campaign.keywords or [],
            target_audience=new_campaign.target_audience,
            campaign_type=new_campaign.campaign_type.value,
            status=new_campaign.status.value,
            tone=new_campaign.tone,
            style=new_campaign.style,
            created_at=new_campaign.created_at,
            updated_at=new_campaign.updated_at,
            workflow_state=new_campaign.workflow_state.value if new_campaign.workflow_state else "basic_setup",
            completion_percentage=new_campaign.calculate_completion_percentage(),
            sources_count=0,
            intelligence_count=0,
            content_count=0
        )
        
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific campaign by ID"""
    try:
        logger.info(f"Getting campaign {campaign_id} for user {current_user.id}")
        
        # Query for the campaign
        query = select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.company_id == current_user.company_id
        )
        
        result = await db.execute(query)
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        return CampaignResponse(
            id=str(campaign.id),
            title=campaign.title,
            description=campaign.description,
            keywords=campaign.keywords or [],
            target_audience=campaign.target_audience,
            campaign_type=campaign.campaign_type.value if campaign.campaign_type else "universal",
            status=campaign.status.value if campaign.status else "draft",
            tone=campaign.tone,
            style=campaign.style,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            workflow_state=campaign.workflow_state.value if campaign.workflow_state else "basic_setup",
            completion_percentage=campaign.calculate_completion_percentage(),
            sources_count=campaign.sources_count or 0,
            intelligence_count=campaign.intelligence_extracted or 0,
            content_count=campaign.content_generated or 0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve campaign: {str(e)}"
        )

@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: UUID,
    campaign_data: CampaignUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a campaign"""
    try:
        logger.info(f"Updating campaign {campaign_id} for user {current_user.id}")
        
        # Get the campaign
        query = select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.company_id == current_user.company_id
        )
        
        result = await db.execute(query)
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Update fields
        update_data = campaign_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "campaign_type" and value:
                setattr(campaign, field, CampaignType(value))
            elif field == "status" and value:
                setattr(campaign, field, CampaignStatus(value))
            else:
                setattr(campaign, field, value)
        
        await db.commit()
        await db.refresh(campaign)
        
        logger.info(f"Updated campaign {campaign_id}")
        
        return CampaignResponse(
            id=str(campaign.id),
            title=campaign.title,
            description=campaign.description,
            keywords=campaign.keywords or [],
            target_audience=campaign.target_audience,
            campaign_type=campaign.campaign_type.value if campaign.campaign_type else "universal",
            status=campaign.status.value if campaign.status else "draft",
            tone=campaign.tone,
            style=campaign.style,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            workflow_state=campaign.workflow_state.value if campaign.workflow_state else "basic_setup",
            completion_percentage=campaign.calculate_completion_percentage(),
            sources_count=campaign.sources_count or 0,
            intelligence_count=campaign.intelligence_extracted or 0,
            content_count=campaign.content_generated or 0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating campaign: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign: {str(e)}"
        )

@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a campaign"""
    try:
        logger.info(f"Deleting campaign {campaign_id} for user {current_user.id}")
        
        # Get the campaign
        query = select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.company_id == current_user.company_id
        )
        
        result = await db.execute(query)
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        await db.delete(campaign)
        await db.commit()
        
        logger.info(f"Deleted campaign {campaign_id}")
        
        return {"message": "Campaign deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting campaign: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete campaign: {str(e)}"
        )

@router.get("/{campaign_id}/workflow")
async def get_campaign_workflow(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get campaign workflow status"""
    try:
        # Get the campaign
        query = select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.company_id == current_user.company_id
        )
        
        result = await db.execute(query)
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        return campaign.get_workflow_summary()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign workflow: {str(e)}"
        )

# ============================================================================
# STATS AND ANALYTICS ROUTES
# ============================================================================

@router.get("/stats/overview")
async def get_campaign_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get campaign statistics overview"""
    try:
        # Get basic campaign counts
        total_query = select(func.count(Campaign.id)).where(Campaign.company_id == current_user.company_id)
        active_query = select(func.count(Campaign.id)).where(
            Campaign.company_id == current_user.company_id,
            Campaign.status == CampaignStatus.ACTIVE
        )
        draft_query = select(func.count(Campaign.id)).where(
            Campaign.company_id == current_user.company_id,
            Campaign.status == CampaignStatus.DRAFT
        )
        
        total_result = await db.execute(total_query)
        active_result = await db.execute(active_query)
        draft_result = await db.execute(draft_query)
        
        total_campaigns = total_result.scalar()
        active_campaigns = active_result.scalar()
        draft_campaigns = draft_result.scalar()
        
        return {
            "total_campaigns": total_campaigns,
            "active_campaigns": active_campaigns,
            "draft_campaigns": draft_campaigns,
            "completed_campaigns": total_campaigns - active_campaigns - draft_campaigns,
            "total_sources": 0,  # Will be populated when intelligence is added back
            "total_content": 0,  # Will be populated when intelligence is added back
            "avg_completion": 25.0  # Basic completion for existing campaigns
        }
        
    except Exception as e:
        logger.error(f"Error getting campaign stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign stats: {str(e)}"
        )