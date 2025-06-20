# src/campaigns/routes.py
"""
Campaign management routes - Safe version without intelligence dependencies
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.models.user import User
from src.models.campaign import (
    Campaign, 
    CampaignStatus, 
    CampaignType, 
    WorkflowPreference,
    CampaignWorkflowState
)

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])

# Request/Response Models
class CampaignCreateRequest(BaseModel):
    title: str
    description: str
    keywords: Optional[List[str]] = []
    target_audience: Optional[str] = None
    campaign_type: str = Field(default="universal", description="Campaign type is required")
    tone: Optional[str] = "conversational"
    style: Optional[str] = "modern"
    settings: Dict[str, Any] = {}

class CampaignResponse(BaseModel):
    id: str
    title: str
    description: str
    keywords: Optional[List[str]] = []
    target_audience: Optional[str]
    campaign_type: str
    status: str
    tone: Optional[str]
    style: Optional[str]
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    # Workflow fields
    workflow_state: Optional[str] = None
    workflow_preference: Optional[str] = None
    completion_percentage: Optional[float] = None
    sources_count: Optional[int] = 0
    intelligence_count: Optional[int] = 0
    generated_content_count: Optional[int] = 0

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
        # Validate campaign type is provided and valid
        if not request.campaign_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campaign type is required"
            )
        
        try:
            campaign_type_enum = CampaignType(request.campaign_type)
        except ValueError:
            valid_types = [e.value for e in CampaignType]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid campaign type: {request.campaign_type}. Valid options: {valid_types}"
            )
        
        # Create campaign with basic workflow support
        campaign = Campaign(
            id=uuid4(),
            title=request.title,
            description=request.description,
            keywords=request.keywords or [],
            target_audience=request.target_audience,
            campaign_type=campaign_type_enum,
            status=CampaignStatus.DRAFT,
            tone=request.tone,
            style=request.style,
            settings=request.settings,
            user_id=current_user.id,
            company_id=current_user.company_id,
            # Initialize workflow state
            workflow_state=CampaignWorkflowState.BASIC_SETUP,
            workflow_preference=WorkflowPreference.FLEXIBLE,
            last_active_step=1,
            current_session={
                "started_at": datetime.utcnow().isoformat(),
                "initial_setup": True
            }
        )
        
        db.add(campaign)
        await db.commit()
        await db.refresh(campaign)
        
        # Update company campaign count (safely)
        try:
            if current_user.company:
                current_user.company.total_campaigns += 1
                await db.commit()
        except Exception as e:
            print(f"Warning: Could not update company campaign count: {e}")
        
        return CampaignResponse(
            id=str(campaign.id),
            title=campaign.title,
            description=campaign.description,
            keywords=campaign.keywords or [],
            target_audience=campaign.target_audience,
            campaign_type=campaign.campaign_type.value,
            status=campaign.status.value,
            tone=campaign.tone,
            style=campaign.style,
            settings=campaign.settings,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            workflow_state=campaign.workflow_state.value if campaign.workflow_state else None,
            workflow_preference=campaign.workflow_preference.value if campaign.workflow_preference else None,
            completion_percentage=campaign.calculate_completion_percentage() if hasattr(campaign, 'calculate_completion_percentage') else 25.0,
            sources_count=campaign.sources_count or 0,
            intelligence_count=campaign.intelligence_extracted or 0,
            generated_content_count=campaign.content_generated or 0
        )
        
    except HTTPException:
        raise
        
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
    """Get user's campaigns with filtering - SAFE VERSION"""
    
    # Build basic query without relationships that might fail
    query = select(Campaign).where(Campaign.company_id == current_user.company_id)
    
    # Apply filters
    conditions = []
    if status_filter:
        try:
            status_enum = CampaignStatus(status_filter)
            conditions.append(Campaign.status == status_enum)
        except ValueError:
            pass  # Ignore invalid status filter
    
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
    
    # Convert to response format safely
    campaign_list = []
    for campaign in campaigns:
        try:
            # Update workflow progress safely
            if hasattr(campaign, 'update_workflow_progress'):
                campaign.update_workflow_progress()
        except Exception as e:
            print(f"Warning: Could not update workflow progress: {e}")
        
        # Safe handling of campaign_type
        campaign_type_value = campaign.campaign_type.value if campaign.campaign_type else "universal"
        
        # Safe completion percentage calculation
        try:
            completion_percentage = campaign.calculate_completion_percentage() if hasattr(campaign, 'calculate_completion_percentage') else 25.0
        except Exception:
            completion_percentage = 25.0
        
        campaign_response = CampaignResponse(
            id=str(campaign.id),
            title=campaign.title,
            description=campaign.description,
            keywords=campaign.keywords or [],
            target_audience=campaign.target_audience,
            campaign_type=campaign_type_value,
            status=campaign.status.value,
            tone=campaign.tone,
            style=campaign.style,
            settings=campaign.settings or {},
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            workflow_state=campaign.workflow_state.value if campaign.workflow_state else None,
            workflow_preference=campaign.workflow_preference.value if campaign.workflow_preference else None,
            completion_percentage=completion_percentage,
            sources_count=getattr(campaign, 'sources_count', 0) or 0,
            intelligence_count=getattr(campaign, 'intelligence_extracted', 0) or 0,
            generated_content_count=getattr(campaign, 'content_generated', 0) or 0
        )
        campaign_list.append(campaign_response)
    
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
    
    # Get campaign without potentially problematic relationships
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
    
    # Update workflow progress safely
    try:
        if hasattr(campaign, 'update_workflow_progress'):
            campaign.update_workflow_progress()
            await db.commit()
    except Exception as e:
        print(f"Warning: Could not update workflow progress: {e}")
    
    # Safe handling of campaign_type
    campaign_type_value = campaign.campaign_type.value if campaign.campaign_type else "universal"
    
    # Safe completion percentage calculation
    try:
        completion_percentage = campaign.calculate_completion_percentage() if hasattr(campaign, 'calculate_completion_percentage') else 25.0
    except Exception:
        completion_percentage = 25.0
    
    return CampaignResponse(
        id=str(campaign.id),
        title=campaign.title,
        description=campaign.description,
        keywords=campaign.keywords or [],
        target_audience=campaign.target_audience,
        campaign_type=campaign_type_value,
        status=campaign.status.value,
        tone=campaign.tone,
        style=campaign.style,
        settings=campaign.settings or {},
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
        workflow_state=campaign.workflow_state.value if campaign.workflow_state else None,
        workflow_preference=campaign.workflow_preference.value if campaign.workflow_preference else None,
        completion_percentage=completion_percentage,
        sources_count=getattr(campaign, 'sources_count', 0) or 0,
        intelligence_count=getattr(campaign, 'intelligence_extracted', 0) or 0,
        generated_content_count=getattr(campaign, 'content_generated', 0) or 0
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
        # Validate campaign type is provided and valid
        if not request.campaign_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campaign type is required"
            )
        
        # Update campaign fields
        campaign.title = request.title
        campaign.description = request.description
        campaign.keywords = request.keywords
        campaign.target_audience = request.target_audience
        campaign.tone = request.tone
        campaign.style = request.style
        campaign.settings = request.settings
        campaign.updated_at = datetime.utcnow()
        
        # Update campaign type
        try:
            campaign.campaign_type = CampaignType(request.campaign_type)
        except ValueError:
            valid_types = [e.value for e in CampaignType]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid campaign type: {request.campaign_type}. Valid options: {valid_types}"
            )
        
        await db.commit()
        await db.refresh(campaign)
        
        # Safe completion percentage calculation
        try:
            completion_percentage = campaign.calculate_completion_percentage() if hasattr(campaign, 'calculate_completion_percentage') else 25.0
        except Exception:
            completion_percentage = 25.0
        
        return CampaignResponse(
            id=str(campaign.id),
            title=campaign.title,
            description=campaign.description,
            keywords=campaign.keywords or [],
            target_audience=campaign.target_audience,
            campaign_type=campaign.campaign_type.value,
            status=campaign.status.value,
            tone=campaign.tone,
            style=campaign.style,
            settings=campaign.settings or {},
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            workflow_state=campaign.workflow_state.value if campaign.workflow_state else None,
            workflow_preference=campaign.workflow_preference.value if campaign.workflow_preference else None,
            completion_percentage=completion_percentage
        )
        
    except HTTPException:
        raise
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
        
        # Update company campaign count safely
        try:
            if current_user.company:
                current_user.company.total_campaigns = max(0, current_user.company.total_campaigns - 1)
        except Exception as e:
            print(f"Warning: Could not update company campaign count: {e}")
        
        await db.commit()
        
        return {"message": "Campaign deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete campaign: {str(e)}"
        )

# Get campaign stats for dashboard
@router.get("/dashboard/stats", response_model=CampaignStatsResponse)
async def get_campaign_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get campaign statistics for dashboard"""
    
    try:
        # Get total campaigns count
        total_campaigns_result = await db.execute(
            select(func.count(Campaign.id)).where(Campaign.company_id == current_user.company_id)
        )
        total_campaigns = total_campaigns_result.scalar() or 0
        
        # Get active campaigns count (non-draft, non-completed)
        active_campaigns_result = await db.execute(
            select(func.count(Campaign.id)).where(
                and_(
                    Campaign.company_id == current_user.company_id,
                    Campaign.status.notin_([CampaignStatus.DRAFT, CampaignStatus.COMPLETED])
                )
            )
        )
        active_campaigns = active_campaigns_result.scalar() or 0
        
        # Get credits info from company safely
        credits_used = 0
        credits_limit = 1000
        try:
            if current_user.company:
                credits_used = getattr(current_user.company, 'monthly_credits_used', 0) or 0
                credits_limit = getattr(current_user.company, 'monthly_credits_limit', 1000) or 1000
        except Exception as e:
            print(f"Warning: Could not get company credit info: {e}")
        
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
            detail=f"Failed to get campaign stats: {str(e)}"
        )