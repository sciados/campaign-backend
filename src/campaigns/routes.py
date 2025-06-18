# src/campaigns/routes.py
"""
Campaign management routes - Core campaign workflow
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.models.user import User
from src.models.campaign import Campaign, CampaignStatus, CampaignType
from src.models.intelligence import CampaignIntelligence, GeneratedContent

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])

# Request/Response Models
class CampaignCreateRequest(BaseModel):
    title: str
    description: str
    target_audience: Optional[str] = None
    campaign_type: str = "social_media"
    tone: Optional[str] = "conversational"
    style: Optional[str] = "modern"
    settings: Dict[str, Any] = {}

class CampaignResponse(BaseModel):
    id: str
    title: str
    description: str
    target_audience: Optional[str]
    campaign_type: str
    status: str
    tone: Optional[str]
    style: Optional[str]
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class CampaignListResponse(BaseModel):
    campaigns: List[CampaignResponse]
    total: int
    page: int
    limit: int

class CampaignStatsResponse(BaseModel):
    credits_used_this_month: int
    credits_remaining: int
    total_campaigns: int
    active_campaigns: int

@router.post("", response_model=CampaignResponse)
async def create_campaign(
    request: CampaignCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new campaign (Step 1)"""
    
    try:
        # Validate campaign type
        try:
            campaign_type_enum = CampaignType(request.campaign_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid campaign type: {request.campaign_type}"
            )
        
        # Create campaign
        campaign = Campaign(
            id=uuid4(),
            title=request.title,
            description=request.description,
            target_audience=request.target_audience,
            campaign_type=campaign_type_enum,
            status=CampaignStatus.DRAFT,
            tone=request.tone,
            style=request.style,
            settings=request.settings,
            user_id=current_user.id,
            company_id=current_user.company_id
        )
        
        db.add(campaign)
        await db.commit()
        await db.refresh(campaign)
        
        # Update company campaign count
        current_user.company.total_campaigns += 1
        await db.commit()
        
        return CampaignResponse(
            id=str(campaign.id),
            title=campaign.title,
            description=campaign.description,
            target_audience=campaign.target_audience,
            campaign_type=campaign.campaign_type.value,
            status=campaign.status.value,
            tone=campaign.tone,
            style=campaign.style,
            settings=campaign.settings,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )

@router.get("", response_model=CampaignListResponse)
async def list_campaigns(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """Get user's campaigns with filtering"""
    
    # Build query
    query = select(Campaign).where(Campaign.company_id == current_user.company_id)
    
    # Apply filters
    conditions = []
    if status_filter:
        conditions.append(Campaign.status == status_filter)
    
    if search:
        conditions.append(
            or_(
                Campaign.title.ilike(f"%{search}%"),
                Campaign.description.ilike(f"%{search}%")
            )
        )
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Get total count
    total_query = select(func.count(Campaign.id)).where(Campaign.company_id == current_user.company_id)
    if conditions:
        total_query = total_query.where(and_(*conditions))
    
    total = await db.scalar(total_query) or 0
    
    # Apply pagination and ordering
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Campaign.updated_at.desc())
    
    result = await db.execute(query)
    campaigns = result.scalars().all()
    
    # Convert to response format
    campaign_list = [
        CampaignResponse(
            id=str(campaign.id),
            title=campaign.title,
            description=campaign.description,
            target_audience=campaign.target_audience,
            campaign_type=campaign.campaign_type.value,
            status=campaign.status.value,
            tone=campaign.tone,
            style=campaign.style,
            settings=campaign.settings,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at
        )
        for campaign in campaigns
    ]
    
    return CampaignListResponse(
        campaigns=campaign_list,
        total=total,
        page=page,
        limit=limit
    )

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific campaign by ID"""
    
    # Get campaign with access check
    result = await db.execute(
        select(Campaign).where(
            and_(
                Campaign.id == campaign_id,
                Campaign.company_id == current_user.company_id
            )
        )
    )
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
        target_audience=campaign.target_audience,
        campaign_type=campaign.campaign_type.value,
        status=campaign.status.value,
        tone=campaign.tone,
        style=campaign.style,
        settings=campaign.settings,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at
    )

@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    request: CampaignCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update campaign details"""
    
    # Get campaign with access check
    result = await db.execute(
        select(Campaign).where(
            and_(
                Campaign.id == campaign_id,
                Campaign.company_id == current_user.company_id
            )
        )
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    try:
        # Update campaign fields
        campaign.title = request.title
        campaign.description = request.description
        campaign.target_audience = request.target_audience
        campaign.tone = request.tone
        campaign.style = request.style
        campaign.settings = request.settings
        campaign.updated_at = datetime.utcnow()
        
        # Update campaign type if provided
        if request.campaign_type:
            try:
                campaign.campaign_type = CampaignType(request.campaign_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid campaign type: {request.campaign_type}"
                )
        
        await db.commit()
        await db.refresh(campaign)
        
        return CampaignResponse(
            id=str(campaign.id),
            title=campaign.title,
            description=campaign.description,
            target_audience=campaign.target_audience,
            campaign_type=campaign.campaign_type.value,
            status=campaign.status.value,
            tone=campaign.tone,
            style=campaign.style,
            settings=campaign.settings,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign: {str(e)}"
        )

@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete campaign"""
    
    # Get campaign with access check
    result = await db.execute(
        select(Campaign).where(
            and_(
                Campaign.id == campaign_id,
                Campaign.company_id == current_user.company_id
            )
        )
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    try:
        await db.delete(campaign)
        
        # Update company campaign count
        current_user.company.total_campaigns = max(0, current_user.company.total_campaigns - 1)
        
        await db.commit()
        
        return {"message": "Campaign deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete campaign: {str(e)}"
        )

@router.post("/{campaign_id}/advance-step")
async def advance_campaign_step(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Advance campaign to next step"""
    
    # Get campaign with access check
    result = await db.execute(
        select(Campaign).where(
            and_(
                Campaign.id == campaign_id,
                Campaign.company_id == current_user.company_id
            )
        )
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    try:
        # Advance status based on current state
        if campaign.status == CampaignStatus.DRAFT:
            campaign.status = CampaignStatus.IN_PROGRESS
        elif campaign.status == CampaignStatus.IN_PROGRESS:
            campaign.status = CampaignStatus.REVIEW
        elif campaign.status == CampaignStatus.REVIEW:
            campaign.status = CampaignStatus.ACTIVE
        
        campaign.updated_at = datetime.utcnow()
        await db.commit()
        
        return {"status": campaign.status.value}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to advance campaign: {str(e)}"
        )

@router.get("/dashboard/stats", response_model=CampaignStatsResponse)
async def get_campaign_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard statistics for campaigns"""
    
    try:
        # Get current month's date range
        now = datetime.utcnow()
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Total campaigns for this company
        total_campaigns = await db.scalar(
            select(func.count(Campaign.id)).where(Campaign.company_id == current_user.company_id)
        ) or 0
        
        # Active campaigns (not archived/completed)
        active_campaigns = await db.scalar(
            select(func.count(Campaign.id)).where(
                and_(
                    Campaign.company_id == current_user.company_id,
                    Campaign.status.in_([CampaignStatus.DRAFT, CampaignStatus.IN_PROGRESS, CampaignStatus.ACTIVE])
                )
            )
        ) or 0
        
        # Credits info from company
        credits_used = current_user.company.monthly_credits_used
        credits_limit = current_user.company.monthly_credits_limit
        credits_remaining = max(0, credits_limit - credits_used)
        
        return CampaignStatsResponse(
            credits_used_this_month=credits_used,
            credits_remaining=credits_remaining,
            total_campaigns=total_campaigns,
            active_campaigns=active_campaigns
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch campaign stats: {str(e)}"
        )

@router.get("/{campaign_id}/intelligence-summary")
async def get_campaign_intelligence_summary(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get intelligence and content summary for campaign"""
    
    # Verify campaign access
    campaign_result = await db.execute(
        select(Campaign).where(
            and_(
                Campaign.id == campaign_id,
                Campaign.company_id == current_user.company_id
            )
        )
    )
    campaign = campaign_result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    try:
        # Get intelligence sources count
        intelligence_count = await db.scalar(
            select(func.count(CampaignIntelligence.id)).where(
                CampaignIntelligence.campaign_id == campaign_id
            )
        ) or 0
        
        # Get generated content count
        content_count = await db.scalar(
            select(func.count(GeneratedContent.id)).where(
                GeneratedContent.campaign_id == campaign_id
            )
        ) or 0
        
        # Get recent intelligence sources
        recent_intelligence = await db.execute(
            select(CampaignIntelligence).where(
                CampaignIntelligence.campaign_id == campaign_id
            ).order_by(CampaignIntelligence.created_at.desc()).limit(5)
        )
        intelligence_sources = recent_intelligence.scalars().all()
        
        # Get recent generated content
        recent_content = await db.execute(
            select(GeneratedContent).where(
                GeneratedContent.campaign_id == campaign_id
            ).order_by(GeneratedContent.created_at.desc()).limit(5)
        )
        generated_content = recent_content.scalars().all()
        
        return {
            "campaign_id": campaign_id,
            "campaign_title": campaign.title,
            "campaign_status": campaign.status.value,
            "intelligence_summary": {
                "total_sources": intelligence_count,
                "recent_sources": [
                    {
                        "id": str(intel.id),
                        "source_title": intel.source_title,
                        "source_type": intel.source_type.value,
                        "confidence_score": intel.confidence_score,
                        "created_at": intel.created_at
                    }
                    for intel in intelligence_sources
                ]
            },
            "content_summary": {
                "total_generated": content_count,
                "recent_content": [
                    {
                        "id": str(content.id),
                        "content_type": content.content_type,
                        "content_title": content.content_title,
                        "user_rating": content.user_rating,
                        "is_published": content.is_published,
                        "created_at": content.created_at
                    }
                    for content in generated_content
                ]
            },
            "next_steps": _get_campaign_next_steps(campaign, intelligence_count, content_count)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch campaign summary: {str(e)}"
        )

def _get_campaign_next_steps(campaign: Campaign, intelligence_count: int, content_count: int) -> List[str]:
    """Generate next steps recommendations based on campaign state"""
    
    next_steps = []
    
    if campaign.status == CampaignStatus.DRAFT:
        if intelligence_count == 0:
            next_steps.append("Add intelligence sources (URLs, documents, videos)")
        else:
            next_steps.append("Generate content using your intelligence sources")
    
    elif campaign.status == CampaignStatus.IN_PROGRESS:
        if content_count == 0:
            next_steps.append("Generate your first piece of content")
        else:
            next_steps.append("Review and refine generated content")
            next_steps.append("Generate additional content variations")
    
    elif campaign.status == CampaignStatus.REVIEW:
        next_steps.append("Review all generated content")
        next_steps.append("Download and deploy content to platforms")
        next_steps.append("Activate campaign when ready")
    
    elif campaign.status == CampaignStatus.ACTIVE:
        next_steps.append("Monitor campaign performance")
        next_steps.append("Generate additional content as needed")
    
    # Always available options
    if intelligence_count > 0:
        next_steps.append("Add more intelligence sources for variety")
    
    if content_count > 0:
        next_steps.append("Generate variations of existing content")
    
    return next_steps

@router.post("/{campaign_id}/duplicate")
async def duplicate_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Duplicate an existing campaign"""
    
    # Get original campaign
    result = await db.execute(
        select(Campaign).where(
            and_(
                Campaign.id == campaign_id,
                Campaign.company_id == current_user.company_id
            )
        )
    )
    original_campaign = result.scalar_one_or_none()
    
    if not original_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    try:
        # Create duplicate campaign
        duplicate = Campaign(
            id=uuid4(),
            title=f"{original_campaign.title} (Copy)",
            description=original_campaign.description,
            target_audience=original_campaign.target_audience,
            campaign_type=original_campaign.campaign_type,
            status=CampaignStatus.DRAFT,
            tone=original_campaign.tone,
            style=original_campaign.style,
            settings=original_campaign.settings.copy() if original_campaign.settings else {},
            user_id=current_user.id,
            company_id=current_user.company_id
        )
        
        db.add(duplicate)
        await db.commit()
        await db.refresh(duplicate)
        
        # Update company campaign count
        current_user.company.total_campaigns += 1
        await db.commit()
        
        return CampaignResponse(
            id=str(duplicate.id),
            title=duplicate.title,
            description=duplicate.description,
            target_audience=duplicate.target_audience,
            campaign_type=duplicate.campaign_type.value,
            status=duplicate.status.value,
            tone=duplicate.tone,
            style=duplicate.style,
            settings=duplicate.settings,
            created_at=duplicate.created_at,
            updated_at=duplicate.updated_at
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to duplicate campaign: {str(e)}"
        )

@router.get("/{campaign_id}/export")
async def export_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export campaign data for backup or migration"""
    
    # Get campaign with all related data
    result = await db.execute(
        select(Campaign)
        .options(
            selectinload(Campaign.intelligence_sources),
            selectinload(Campaign.generated_content)
        )
        .where(
            and_(
                Campaign.id == campaign_id,
                Campaign.company_id == current_user.company_id
            )
        )
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    try:
        export_data = {
            "campaign": {
                "title": campaign.title,
                "description": campaign.description,
                "target_audience": campaign.target_audience,
                "campaign_type": campaign.campaign_type.value,
                "status": campaign.status.value,
                "tone": campaign.tone,
                "style": campaign.style,
                "settings": campaign.settings,
                "created_at": campaign.created_at.isoformat(),
                "updated_at": campaign.updated_at.isoformat()
            },
            "intelligence_sources": [
                {
                    "source_title": intel.source_title,
                    "source_type": intel.source_type.value,
                    "source_url": intel.source_url,
                    "confidence_score": intel.confidence_score,
                    "offer_intelligence": intel.offer_intelligence,
                    "psychology_intelligence": intel.psychology_intelligence,
                    "created_at": intel.created_at.isoformat()
                }
                for intel in campaign.intelligence_sources
            ],
            "generated_content": [
                {
                    "content_type": content.content_type,
                    "content_title": content.content_title,
                    "content_body": content.content_body,
                    "content_metadata": content.content_metadata,
                    "user_rating": content.user_rating,
                    "is_published": content.is_published,
                    "created_at": content.created_at.isoformat()
                }
                for content in campaign.generated_content
            ],
            "export_metadata": {
                "exported_at": datetime.utcnow().isoformat(),
                "exported_by": current_user.email,
                "export_version": "1.0"
            }
        }
        
        return export_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export campaign: {str(e)}"
        )