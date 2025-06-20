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
import traceback

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
    keywords: Optional[List[str]] = []
    target_audience: Optional[str] = None
    campaign_type: str = "social_media"
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
        # Add debugging
        print(f"🔍 DEBUG: Creating campaign for user {current_user.id}")
        print(f"🔍 DEBUG: User email: {current_user.email}")
        print(f"🔍 DEBUG: Company ID: {current_user.company_id}")
        print(f"🔍 DEBUG: Company object: {current_user.company}")
        print(f"🔍 DEBUG: Request data: {request}")
        print(f"🔍 DEBUG: Keywords: {request.keywords}, type: {type(request.keywords)}")
        
        # Validate campaign type
        try:
            campaign_type_enum = CampaignType(request.campaign_type)
            print(f"🔍 DEBUG: Campaign type validated: {campaign_type_enum}")
        except ValueError as ve:
            print(f"❌ DEBUG: Invalid campaign type: {ve}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid campaign type: {request.campaign_type}. Valid options: {[e.value for e in CampaignType]}"
            )
        
        # Create campaign
        print(f"🔍 DEBUG: Creating campaign object...")
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
            company_id=current_user.company_id
        )
        
        print(f"🔍 DEBUG: Campaign object created successfully")
        print(f"🔍 DEBUG: Campaign ID: {campaign.id}")
        print(f"🔍 DEBUG: Campaign keywords: {campaign.keywords}")
        
        print(f"🔍 DEBUG: Adding to database session...")
        db.add(campaign)
        
        print(f"🔍 DEBUG: Committing to database...")
        await db.commit()
        
        print(f"🔍 DEBUG: Refreshing campaign object...")
        await db.refresh(campaign)
        
        print(f"🔍 DEBUG: Updating company campaign count...")
        # Update company campaign count
        if current_user.company:
            current_user.company.total_campaigns += 1
            print(f"🔍 DEBUG: Company total campaigns now: {current_user.company.total_campaigns}")
            await db.commit()
        else:
            print("⚠️ DEBUG: No company object found, skipping count update")
        
        print(f"🔍 DEBUG: Success! Campaign created with ID: {campaign.id}")
        
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
            updated_at=campaign.updated_at
        )
        
    except HTTPException as he:
        # Re-raise HTTP exceptions (like validation errors)
        print(f"❌ DEBUG: HTTP Exception: {he}")
        raise he
        
    except Exception as e:
        print(f"❌ DEBUG: Unexpected exception occurred!")
        print(f"❌ DEBUG: Exception type: {type(e).__name__}")
        print(f"❌ DEBUG: Exception message: '{str(e)}'")
        print(f"❌ DEBUG: Exception args: {e.args}")
        print(f"❌ DEBUG: Full traceback:")
        print(traceback.format_exc())
        
        await db.rollback()
        
        # Create detailed error message
        error_details = f"{type(e).__name__}"
        if str(e):
            error_details += f": {str(e)}"
        if e.args:
            error_details += f" | Args: {e.args}"
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {error_details}"
        )

@router.post("/test")
async def test_create(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Test campaign creation with minimal data"""
    try:
        print(f"🧪 TEST: Creating test campaign for user {current_user.id}")
        
        campaign = Campaign(
            id=uuid4(),
            title="Test Campaign",
            description="Test Description",
            keywords=["test"],
            campaign_type=CampaignType.SOCIAL_MEDIA,  # Use known working type
            user_id=current_user.id,
            company_id=current_user.company_id
        )
        
        print(f"🧪 TEST: Adding to database...")
        db.add(campaign)
        
        print(f"🧪 TEST: Committing...")
        await db.commit()
        
        print(f"🧪 TEST: Success!")
        return {"success": True, "campaign_id": str(campaign.id)}
        
    except Exception as e:
        print(f"🧪 TEST: Error - {type(e).__name__}: {str(e)}")
        print(f"🧪 TEST: Full traceback:")
        print(traceback.format_exc())
        
        return {
            "success": False, 
            "error": f"{type(e).__name__}: {str(e)}",
            "traceback": traceback.format_exc()
        }

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
            keywords=campaign.keywords or [],
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
        keywords=campaign.keywords or [],
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
        campaign.keywords = request.keywords
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
            keywords=campaign.keywords or [],
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

# ... [rest of the routes remain the same] ...

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
            keywords=original_campaign.keywords or [],
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
            keywords=duplicate.keywords or [],
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