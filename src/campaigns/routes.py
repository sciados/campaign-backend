"""
Campaign routes - ENHANCED VERSION with Content Management - FIXED
"""
# from fastapi import APIRouter, Depends, HTTPException
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, update
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging
import json
from datetime import datetime

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.models import Campaign, User, Company, CampaignStatus
from src.models.intelligence import GeneratedContent, CampaignIntelligence
from pydantic import BaseModel
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(tags=["campaigns"])

# ============================================================================
# PYDANTIC SCHEMAS - ENHANCED WITH CONTENT MANAGEMENT
# ============================================================================

class CampaignCreate(BaseModel):
    title: str
    description: Optional[str] = None
    keywords: Optional[List[str]] = []
    target_audience: Optional[str] = None
    tone: Optional[str] = "conversational"
    style: Optional[str] = "modern"
    settings: Optional[Dict[str, Any]] = {}

class CampaignUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    target_audience: Optional[str] = None
    status: Optional[str] = None
    tone: Optional[str] = None
    style: Optional[str] = None

class CampaignResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = ""
    keywords: List[str] = []
    target_audience: Optional[str] = None
    campaign_type: str = "universal"
    status: str = "draft"
    tone: Optional[str] = "conversational"
    style: Optional[str] = "modern"
    created_at: datetime
    updated_at: datetime
    workflow_state: str = "basic_setup"
    completion_percentage: float = 25.0
    sources_count: int = 0
    intelligence_count: int = 0
    content_count: int = 0

    class Config:
        from_attributes = True
        use_enum_values = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class WorkflowPreferences(BaseModel):
    workflow_preference: Optional[str] = "flexible"
    quick_mode: Optional[bool] = False
    auto_advance: Optional[bool] = False
    detailed_guidance: Optional[bool] = False

class ProgressData(BaseModel):
    current_step: Optional[int] = None
    session_data: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None

class WorkflowStateResponse(BaseModel):
    campaign_id: str
    suggested_step: int
    workflow_preference: str
    progress_summary: Dict[str, Any]
    progress: Dict[str, Any]
    available_actions: List[Dict[str, Any]]
    primary_suggestion: str

# ✅ NEW: Content Management Schemas
class ContentUpdateRequest(BaseModel):
    content_title: Optional[str] = None
    content_body: Optional[str] = None
    content_metadata: Optional[Dict[str, Any]] = None
    user_rating: Optional[int] = None
    is_published: Optional[bool] = None
    published_at: Optional[str] = None
    performance_data: Optional[Dict[str, Any]] = None

class ContentRatingRequest(BaseModel):
    rating: int

class ContentPublishRequest(BaseModel):
    published_at: Optional[str] = "Manual"

class BulkContentActionRequest(BaseModel):
    content_ids: List[str]
    action: str  # "delete", "publish", "rate"
    params: Optional[Dict[str, Any]] = {}

class ContentDuplicateRequest(BaseModel):
    title: Optional[str] = None

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def normalize_campaign_status(status_str: str) -> CampaignStatus:
    """Normalize campaign status string to enum value"""
    try:
        return CampaignStatus(status_str.upper())
    except ValueError:
        logger.warning(f"Unknown campaign status '{status_str}', defaulting to DRAFT")
        return CampaignStatus.DRAFT

async def update_campaign_counters(campaign_id: str, db: AsyncSession):
    """Update campaign counter fields based on actual data"""
    try:
        # Count intelligence sources
        intelligence_count = await db.execute(
            select(func.count(CampaignIntelligence.id)).where(
                CampaignIntelligence.campaign_id == campaign_id
            )
        )
        sources_count = intelligence_count.scalar() or 0
        
        # Count generated content
        content_count = await db.execute(
            select(func.count(GeneratedContent.id)).where(
                GeneratedContent.campaign_id == campaign_id
            )
        )
        generated_content_count = content_count.scalar() or 0
        
        # Update campaign record
        await db.execute(
            update(Campaign).where(Campaign.id == campaign_id).values(
                sources_count=sources_count,
                intelligence_extracted=sources_count,
                intelligence_count=sources_count,
                content_generated=generated_content_count,
                generated_content_count=generated_content_count,
                updated_at=datetime.utcnow()
            )
        )
        
        logger.info(f"📊 Updated campaign counters: {sources_count} sources, {generated_content_count} content")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error updating campaign counters: {str(e)}")
        return False

# ============================================================================
# CAMPAIGN ROUTES - FIXED
# ============================================================================

@router.get("", response_model=List[CampaignResponse])
async def get_campaigns(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all campaigns for the current user's company - MINIMAL DEBUG VERSION"""
    try:
        logger.info(f"🔍 DEBUG: Starting get_campaigns for user {current_user.id}")
        
        # Test 1: Check if we can connect to database
        try:
            test_query = select(func.count(Campaign.id))
            test_result = await db.execute(test_query)
            total_campaigns = test_result.scalar()
            logger.info(f"✅ DEBUG: Database connection OK, total campaigns in system: {total_campaigns}")
        except Exception as db_error:
            logger.error(f"❌ DEBUG: Database connection failed: {str(db_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Database connection failed: {str(db_error)}"
            )
        
        # Test 2: Check if we can query campaigns for this company
        try:
            count_query = select(func.count(Campaign.id)).where(Campaign.company_id == current_user.company_id)
            count_result = await db.execute(count_query)
            company_campaigns = count_result.scalar()
            logger.info(f"✅ DEBUG: Found {company_campaigns} campaigns for company {current_user.company_id}")
        except Exception as company_error:
            logger.error(f"❌ DEBUG: Company campaign query failed: {str(company_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Company campaign query failed: {str(company_error)}"
            )
        
        # Test 3: Try to get one campaign to examine its structure
        try:
            single_query = select(Campaign).where(Campaign.company_id == current_user.company_id).limit(1)
            single_result = await db.execute(single_query)
            sample_campaign = single_result.scalar_one_or_none()
            
            if sample_campaign:
                logger.info(f"✅ DEBUG: Sample campaign found: ID={sample_campaign.id}, Title={sample_campaign.title}")
                logger.info(f"✅ DEBUG: Sample campaign status type: {type(sample_campaign.status)}")
                logger.info(f"✅ DEBUG: Sample campaign status value: {sample_campaign.status}")
            else:
                logger.info("ℹ️ DEBUG: No campaigns found for this company")
                # Return empty list if no campaigns
                return []
                
        except Exception as sample_error:
            logger.error(f"❌ DEBUG: Sample campaign query failed: {str(sample_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Sample campaign query failed: {str(sample_error)}"
            )
        
        # Test 4: Try to create a minimal response
        try:
            if sample_campaign:
                # Try to create one campaign response
                test_response = CampaignResponse(
                    id=str(sample_campaign.id),
                    title=sample_campaign.title or "Untitled",
                    description=sample_campaign.description or "",
                    keywords=[],
                    target_audience=sample_campaign.target_audience,
                    campaign_type="universal",
                    status="draft",  # Hard-coded for now
                    tone=sample_campaign.tone or "conversational",
                    style=sample_campaign.style or "modern",
                    created_at=sample_campaign.created_at,
                    updated_at=sample_campaign.updated_at,
                    workflow_state="basic_setup",  # Hard-coded for now
                    completion_percentage=25.0,  # Hard-coded for now
                    sources_count=0,
                    intelligence_count=0,
                    content_count=0
                )
                logger.info(f"✅ DEBUG: Successfully created test CampaignResponse")
                return [test_response]
            else:
                return []
                
        except Exception as response_error:
            logger.error(f"❌ DEBUG: CampaignResponse creation failed: {str(response_error)}")
            logger.error(f"❌ DEBUG: Error type: {type(response_error)}")
            import traceback
            logger.error(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500,
                detail=f"Response creation failed: {str(response_error)}"
            )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ DEBUG: Unexpected error in get_campaigns: {str(e)}")
        logger.error(f"❌ DEBUG: Error type: {type(e)}")
        import traceback
        logger.error(f"❌ DEBUG: Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

@router.get("/debug/campaigns")
async def debug_campaigns(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Debug endpoint to check campaign data structure"""
    try:
        # Get one campaign to examine its structure
        query = select(Campaign).where(Campaign.company_id == current_user.company_id).limit(1)
        result = await db.execute(query)
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            return {"message": "No campaigns found", "user_id": str(current_user.id), "company_id": str(current_user.company_id)}
        
        # Examine the campaign object
        campaign_dict = {}
        for attr in dir(campaign):
            if not attr.startswith('_') and not callable(getattr(campaign, attr)):
                try:
                    value = getattr(campaign, attr)
                    if hasattr(value, 'value'):  # Enum
                        campaign_dict[attr] = f"{value} (enum: {value.value})"
                    else:
                        campaign_dict[attr] = str(value)
                except Exception as e:
                    campaign_dict[attr] = f"Error: {str(e)}"
        
        return {
            "campaign_id": str(campaign.id),
            "campaign_attributes": campaign_dict,
            "campaign_type": type(campaign).__name__,
            "has_calculate_method": hasattr(campaign, 'calculate_completion_percentage'),
            "status_type": type(campaign.status).__name__ if campaign.status else "None"
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@router.post("", response_model=CampaignResponse)
async def create_campaign(
    campaign_data: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new universal campaign"""
    try:
        logger.info(f"Creating universal campaign for user {current_user.id}")
        logger.info(f"Campaign data received: {campaign_data.dict()}")
        
        new_campaign = Campaign(
            title=campaign_data.title,
            description=campaign_data.description,
            keywords=campaign_data.keywords or [],
            target_audience=campaign_data.target_audience,
            tone=campaign_data.tone or "conversational",
            style=campaign_data.style or "modern",
            user_id=current_user.id,
            company_id=current_user.company_id,
            status=CampaignStatus.DRAFT,
            settings=campaign_data.settings or {}
        )
        
        db.add(new_campaign)
        await db.commit()
        await db.refresh(new_campaign)
        
        logger.info(f"Created universal campaign {new_campaign.id}")
        
        return CampaignResponse(
            id=str(new_campaign.id),
            title=new_campaign.title,
            description=new_campaign.description,
            keywords=new_campaign.keywords or [],
            target_audience=new_campaign.target_audience,
            campaign_type="universal",
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
        logger.error(f"Campaign data was: {campaign_data.dict()}")
        await db.rollback()
        
        error_detail = f"Failed to create campaign: {str(e)}"
        
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
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
        
        query = select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.company_id == current_user.company_id
        )
        
        result = await db.execute(query)
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        return CampaignResponse(
            id=str(campaign.id),
            title=campaign.title,
            description=campaign.description,
            keywords=campaign.keywords or [],
            target_audience=campaign.target_audience,
            campaign_type="universal",
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
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
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
        
        query = select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.company_id == current_user.company_id
        )
        
        result = await db.execute(query)
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Update fields
        update_data = campaign_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "status" and value:
                setattr(campaign, field, normalize_campaign_status(value))
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
            campaign_type="universal",
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
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
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
        
        query = select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.company_id == current_user.company_id
        )
        
        result = await db.execute(query)
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
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
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete campaign: {str(e)}"
        )

# ============================================================================
# ✅ NEW: CONTENT MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/{campaign_id}/content")
async def get_campaign_content_list(
    campaign_id: UUID,
    include_body: bool = False,
    content_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of generated content for a campaign"""
    try:
        logger.info(f"Getting content list for campaign {campaign_id}")
        
        # Verify campaign ownership
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
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Build query for generated content
        query = select(GeneratedContent).where(
            GeneratedContent.campaign_id == campaign_id
        ).order_by(GeneratedContent.created_at.desc())
        
        # Add content type filter if specified
        if content_type:
            query = query.where(GeneratedContent.content_type == content_type)
        
        result = await db.execute(query)
        content_items = result.scalars().all()
        
        # Format response
        content_list = []
        for item in content_items:
            content_data = {
                "id": str(item.id),
                "content_type": item.content_type,
                "content_title": item.content_title,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
                "user_rating": item.user_rating,
                "is_published": item.is_published,
                "published_at": item.published_at,
                "performance_data": item.performance_data or {},
                "content_metadata": item.content_metadata or {},
                "generation_settings": item.generation_settings or {},
                "intelligence_used": item.intelligence_used or {}
            }
            
            # Include full content body if requested
            if include_body:
                content_data["content_body"] = item.content_body
            else:
                # Just include a preview
                try:
                    parsed_body = json.loads(item.content_body) if item.content_body else {}
                    if isinstance(parsed_body, dict):
                        # Extract preview from different content types
                        preview = ""
                        if "emails" in parsed_body and parsed_body["emails"]:
                            preview = f"{len(parsed_body['emails'])} emails"
                        elif "posts" in parsed_body and parsed_body["posts"]:
                            preview = f"{len(parsed_body['posts'])} posts"
                        elif "ads" in parsed_body and parsed_body["ads"]:
                            preview = f"{len(parsed_body['ads'])} ads"
                        elif "title" in parsed_body:
                            preview = parsed_body["title"][:100] + "..."
                        else:
                            preview = "Generated content"
                        content_data["content_preview"] = preview
                    else:
                        content_data["content_preview"] = str(parsed_body)[:100] + "..."
                except:
                    content_data["content_preview"] = "Content available"
            
            content_list.append(content_data)
        
        return {
            "campaign_id": str(campaign_id),
            "total_content": len(content_list),
            "content_items": content_list
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign content: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign content: {str(e)}"
        )

@router.get("/{campaign_id}/content/{content_id}")
async def get_content_detail(
    campaign_id: UUID,
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed content including full body"""
    try:
        logger.info(f"Getting content detail for {content_id} in campaign {campaign_id}")
        
        # Get the content item with campaign verification
        content_result = await db.execute(
            select(GeneratedContent).where(
                and_(
                    GeneratedContent.id == content_id,
                    GeneratedContent.campaign_id == campaign_id,
                    GeneratedContent.company_id == current_user.company_id
                )
            )
        )
        content_item = content_result.scalar_one_or_none()
        
        if not content_item:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Parse content body
        parsed_content = {}
        try:
            if content_item.content_body:
                parsed_content = json.loads(content_item.content_body)
        except json.JSONDecodeError:
            parsed_content = {"raw_content": content_item.content_body}
        
        # Get intelligence source info if available
        intelligence_info = None
        if content_item.intelligence_source_id:
            intel_result = await db.execute(
                select(CampaignIntelligence).where(
                    CampaignIntelligence.id == content_item.intelligence_source_id
                )
            )
            intelligence_source = intel_result.scalar_one_or_none()
            if intelligence_source:
                intelligence_info = {
                    "id": str(intelligence_source.id),
                    "source_title": intelligence_source.source_title,
                    "source_url": intelligence_source.source_url,
                    "confidence_score": intelligence_source.confidence_score,
                    "source_type": intelligence_source.source_type.value if intelligence_source.source_type else None
                }
        
        return {
            "id": str(content_item.id),
            "campaign_id": str(campaign_id),
            "content_type": content_item.content_type,
            "content_title": content_item.content_title,
            "content_body": content_item.content_body,
            "parsed_content": parsed_content,
            "content_metadata": content_item.content_metadata or {},
            "generation_settings": content_item.generation_settings or {},
            "intelligence_used": content_item.intelligence_used or {},
            "performance_data": content_item.performance_data or {},
            "user_rating": content_item.user_rating,
            "is_published": content_item.is_published,
            "published_at": content_item.published_at,
            "created_at": content_item.created_at.isoformat() if content_item.created_at else None,
            "updated_at": content_item.updated_at.isoformat() if content_item.updated_at else None,
            "intelligence_source": intelligence_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting content detail: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content detail: {str(e)}"
        )

@router.put("/{campaign_id}/content/{content_id}")
async def update_content(
    campaign_id: UUID,
    content_id: UUID,
    update_data: ContentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update generated content"""
    try:
        logger.info(f"Updating content {content_id} in campaign {campaign_id}")
        
        # Get the content item with verification
        content_result = await db.execute(
            select(GeneratedContent).where(
                and_(
                    GeneratedContent.id == content_id,
                    GeneratedContent.campaign_id == campaign_id,
                    GeneratedContent.company_id == current_user.company_id
                )
            )
        )
        content_item = content_result.scalar_one_or_none()
        
        if not content_item:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Update allowed fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(content_item, field):
                setattr(content_item, field, value)
        
        # Update timestamp
        content_item.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(content_item)
        
        logger.info(f"Content {content_id} updated successfully")
        
        return {
            "id": str(content_item.id),
            "message": "Content updated successfully",
            "updated_at": content_item.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating content: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update content: {str(e)}"
        )

@router.delete("/{campaign_id}/content/{content_id}")
async def delete_content(
    campaign_id: UUID,
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete generated content"""
    try:
        logger.info(f"Deleting content {content_id} from campaign {campaign_id}")
        
        # Get the content item with verification
        content_result = await db.execute(
            select(GeneratedContent).where(
                and_(
                    GeneratedContent.id == content_id,
                    GeneratedContent.campaign_id == campaign_id,
                    GeneratedContent.company_id == current_user.company_id
                )
            )
        )
        content_item = content_result.scalar_one_or_none()
        
        if not content_item:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Delete the content
        await db.delete(content_item)
        await db.commit()
        
        # Update campaign counters
        try:
            await update_campaign_counters(str(campaign_id), db)
            await db.commit()
        except Exception as counter_error:
            logger.warning(f"Failed to update campaign counters: {str(counter_error)}")
        
        logger.info(f"Content {content_id} deleted successfully")
        
        return {"message": "Content deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting content: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete content: {str(e)}"
        )

@router.post("/{campaign_id}/content/{content_id}/rate")
async def rate_content(
    campaign_id: UUID,
    content_id: UUID,
    rating_data: ContentRatingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Rate generated content (1-5 stars)"""
    try:
        rating = rating_data.rating
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            raise HTTPException(status_code=400, detail="Rating must be an integer between 1 and 5")
        
        # Get the content item with verification
        content_result = await db.execute(
            select(GeneratedContent).where(
                and_(
                    GeneratedContent.id == content_id,
                    GeneratedContent.campaign_id == campaign_id,
                    GeneratedContent.company_id == current_user.company_id
                )
            )
        )
        content_item = content_result.scalar_one_or_none()
        
        if not content_item:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Update rating
        content_item.user_rating = rating
        content_item.updated_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "id": str(content_item.id),
            "rating": rating,
            "message": "Content rated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rating content: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rate content: {str(e)}"
        )

@router.post("/{campaign_id}/content/{content_id}/publish")
async def publish_content(
    campaign_id: UUID,
    content_id: UUID,
    publish_data: ContentPublishRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark content as published"""
    try:
        published_at = publish_data.published_at or "Manual"
        
        # Get the content item with verification
        content_result = await db.execute(
            select(GeneratedContent).where(
                and_(
                    GeneratedContent.id == content_id,
                    GeneratedContent.campaign_id == campaign_id,
                    GeneratedContent.company_id == current_user.company_id
                )
            )
        )
        content_item = content_result.scalar_one_or_none()
        
        if not content_item:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Mark as published
        content_item.is_published = True
        content_item.published_at = published_at
        content_item.updated_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "id": str(content_item.id),
            "is_published": True,
            "published_at": published_at,
            "message": "Content marked as published"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing content: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to publish content: {str(e)}"
        )

@router.post("/{campaign_id}/content/bulk-action")
async def bulk_content_action(
    campaign_id: UUID,
    action_data: BulkContentActionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Perform bulk actions on content (delete, publish, rate)"""
    try:
        content_ids = action_data.content_ids
        action = action_data.action
        action_params = action_data.params or {}
        
        if not content_ids or not action:
            raise HTTPException(status_code=400, detail="Missing content_ids or action")
        
        # Verify campaign ownership
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
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Get content items
        content_result = await db.execute(
            select(GeneratedContent).where(
                and_(
                    GeneratedContent.id.in_(content_ids),
                    GeneratedContent.campaign_id == campaign_id,
                    GeneratedContent.company_id == current_user.company_id
                )
            )
        )
        content_items = content_result.scalars().all()
        
        if not content_items:
            raise HTTPException(status_code=404, detail="No content found")
        
        results = []
        
        for content_item in content_items:
            try:
                if action == "delete":
                    await db.delete(content_item)
                    results.append({"id": str(content_item.id), "action": "deleted", "success": True})
                    
                elif action == "publish":
                    content_item.is_published = True
                    content_item.published_at = action_params.get("published_at", "Bulk Action")
                    content_item.updated_at = datetime.utcnow()
                    results.append({"id": str(content_item.id), "action": "published", "success": True})
                    
                elif action == "rate":
                    rating = action_params.get("rating")
                    if rating and 1 <= rating <= 5:
                        content_item.user_rating = rating
                        content_item.updated_at = datetime.utcnow()
                        results.append({"id": str(content_item.id), "action": "rated", "rating": rating, "success": True})
                    else:
                        results.append({"id": str(content_item.id), "action": "rate", "success": False, "error": "Invalid rating"})
                        
                else:
                    results.append({"id": str(content_item.id), "action": action, "success": False, "error": "Unknown action"})
                    
            except Exception as item_error:
                results.append({"id": str(content_item.id), "action": action, "success": False, "error": str(item_error)})
        
        await db.commit()
        
        # Update campaign counters if any deletions
        if action == "delete":
            try:
                await update_campaign_counters(str(campaign_id), db)
                await db.commit()
            except Exception as counter_error:
                logger.warning(f"Failed to update campaign counters: {str(counter_error)}")
        
        successful_count = sum(1 for r in results if r["success"])
        
        return {
            "campaign_id": str(campaign_id),
            "action": action,
            "total_items": len(content_ids),
            "successful": successful_count,
            "failed": len(content_ids) - successful_count,
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing bulk action: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform bulk action: {str(e)}"
        )

@router.get("/{campaign_id}/content/stats")
async def get_content_stats(
    campaign_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get content statistics for a campaign"""
    try:
        # Verify campaign ownership
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
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Get content statistics
        content_result = await db.execute(
            select(GeneratedContent).where(
                GeneratedContent.campaign_id == campaign_id
            )
        )
        content_items = content_result.scalars().all()
        
        # Calculate stats
        total_content = len(content_items)
        published_content = sum(1 for item in content_items if item.is_published)
        rated_content = sum(1 for item in content_items if item.user_rating)
        avg_rating = 0.0
        
        if rated_content > 0:
            total_rating = sum(item.user_rating for item in content_items if item.user_rating)
            avg_rating = total_rating / rated_content
        
        # Content by type
        content_by_type = {}
        amplified_content = 0
        
        for item in content_items:
            content_type = item.content_type
            if content_type not in content_by_type:
                content_by_type[content_type] = 0
            content_by_type[content_type] += 1
            
            # Check if generated from amplified intelligence
            intelligence_used = item.intelligence_used or {}
            if intelligence_used.get("amplified", False):
                amplified_content += 1
        
        # Recent content (last 7 days)
        from datetime import timedelta
        recent_cutoff = datetime.utcnow() - timedelta(days=7)
        recent_content = sum(1 for item in content_items if item.created_at and item.created_at >= recent_cutoff)
        
        return {
            "campaign_id": str(campaign_id),
            "total_content": total_content,
            "published_content": published_content,
            "unpublished_content": total_content - published_content,
            "rated_content": rated_content,
            "average_rating": round(avg_rating, 2),
            "amplified_content": amplified_content,
            "recent_content": recent_content,
            "content_by_type": content_by_type,
            "performance_metrics": {
                "publication_rate": round((published_content / max(total_content, 1)) * 100, 1),
                "rating_rate": round((rated_content / max(total_content, 1)) * 100, 1),
                "amplification_rate": round((amplified_content / max(total_content, 1)) * 100, 1)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting content stats: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content stats: {str(e)}"
        )

@router.post("/{campaign_id}/content/{content_id}/duplicate")
async def duplicate_content(
    campaign_id: UUID,
    content_id: UUID,
    duplicate_data: ContentDuplicateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Duplicate content item"""
    try:
        # Get the original content item
        content_result = await db.execute(
            select(GeneratedContent).where(
                and_(
                    GeneratedContent.id == content_id,
                    GeneratedContent.campaign_id == campaign_id,
                    GeneratedContent.company_id == current_user.company_id
                )
            )
        )
        original_content = content_result.scalar_one_or_none()
        
        if not original_content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Create duplicate
        new_title = duplicate_data.title or f"{original_content.content_title} (Copy)"
        
        duplicate_content_item = GeneratedContent(
            content_type=original_content.content_type,
            content_title=new_title,
            content_body=original_content.content_body,
            content_metadata=original_content.content_metadata,
            generation_settings=original_content.generation_settings,
            intelligence_used=original_content.intelligence_used,
            campaign_id=original_content.campaign_id,
            intelligence_source_id=original_content.intelligence_source_id,
            user_id=current_user.id,
            company_id=current_user.company_id,
            # Reset status fields
            user_rating=None,
            is_published=False,
            published_at=None,
            performance_data={}
        )
        
        db.add(duplicate_content_item)
        await db.commit()
        await db.refresh(duplicate_content_item)
        
        # Update campaign counters
        try:
            await update_campaign_counters(str(campaign_id), db)
            await db.commit()
        except Exception as counter_error:
            logger.warning(f"Failed to update campaign counters: {str(counter_error)}")
        
        return {
            "id": str(duplicate_content_item.id),
            "original_id": str(content_id),
            "title": new_title,
            "message": "Content duplicated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error duplicating content: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to duplicate content: {str(e)}"
        )

# ============================================================================
# DASHBOARD STATS ENDPOINT
# ============================================================================

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics"""
    try:
        logger.info(f"Getting dashboard stats for user {current_user.id}, company {current_user.company_id}")
        
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
        completed_query = select(func.count(Campaign.id)).where(
            Campaign.company_id == current_user.company_id,
            Campaign.status == CampaignStatus.COMPLETED
        )
        
        # Execute queries
        total_result = await db.execute(total_query)
        active_result = await db.execute(active_query)
        draft_result = await db.execute(draft_query)
        completed_result = await db.execute(completed_query)
        
        total_campaigns_created = total_result.scalar() or 0
        active_campaigns = active_result.scalar() or 0
        draft_campaigns = draft_result.scalar() or 0
        completed_campaigns = completed_result.scalar() or 0
        
        # Get content and intelligence counts
        intelligence_query = select(func.count(CampaignIntelligence.id)).join(Campaign).where(
            Campaign.company_id == current_user.company_id
        )
        content_query = select(func.count(GeneratedContent.id)).join(Campaign).where(
            Campaign.company_id == current_user.company_id
        )
        
        intelligence_result = await db.execute(intelligence_query)
        content_result = await db.execute(content_query)
        
        total_sources = intelligence_result.scalar() or 0
        total_content = content_result.scalar() or 0
        
        # Calculate average completion
        avg_completion = 25.0 if total_campaigns_created > 0 else 0.0
        
        # Get recent campaigns for activity feed
        recent_query = select(Campaign).where(
            Campaign.company_id == current_user.company_id
        ).order_by(Campaign.updated_at.desc()).limit(5)
        
        recent_result = await db.execute(recent_query)
        recent_campaigns = recent_result.scalars().all()
        
        recent_activity = []
        for campaign in recent_campaigns:
            recent_activity.append({
                "id": str(campaign.id),
                "title": campaign.title,
                "type": "campaign",
                "action": "updated",
                "timestamp": campaign.updated_at.isoformat() if campaign.updated_at else None,
                "status": campaign.status.value if campaign.status else "draft"
            })
        
        return {
            "total_campaigns_created": total_campaigns_created,
            "active_campaigns": active_campaigns,
            "draft_campaigns": draft_campaigns,
            "completed_campaigns": completed_campaigns,
            "total_sources": total_sources,
            "total_content": total_content,
            "avg_completion": avg_completion,
            "recent_activity": recent_activity,
            "user_id": str(current_user.id),
            "company_id": str(current_user.company_id),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard stats: {str(e)}"
        )

# ============================================================================
# WORKFLOW ENDPOINTS (EXISTING - KEEPING FOR COMPATIBILITY)
# ============================================================================

@router.get("/{campaign_id}/workflow-state", response_model=WorkflowStateResponse)
async def get_campaign_workflow_state(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current workflow state for a campaign"""
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
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Calculate progress based on actual data
        sources_count = getattr(campaign, 'sources_count', 0) or 0
        intelligence_count = getattr(campaign, 'intelligence_extracted', 0) or 0
        content_count = getattr(campaign, 'content_generated', 0) or 0
        
        # Determine current step based on progress
        if content_count > 0:
            current_step = 4
        elif intelligence_count > 0:
            current_step = 3
        elif sources_count > 0:
            current_step = 2
        else:
            current_step = 1
        
        # Calculate completion percentage
        completion_percentage = campaign.calculate_completion_percentage()
        
        # Define available actions
        available_actions = [
            {"step": 1, "can_access": True},
            {"step": 2, "can_access": True},
            {"step": 3, "can_access": sources_count > 0},
            {"step": 4, "can_access": intelligence_count > 0}
        ]
        
        # Get workflow preference from campaign or default
        workflow_preference = getattr(campaign, 'workflow_preference', None)
        if workflow_preference:
            workflow_preference = workflow_preference.value if hasattr(workflow_preference, 'value') else workflow_preference
        else:
            workflow_preference = 'flexible'
        
        # Generate suggestion based on current state
        suggestions = {
            1: "Complete campaign setup and move to add sources",
            2: "Add input sources (URLs, documents) for analysis",
            3: "Run AI analysis on your sources",
            4: "Generate content based on your intelligence"
        }
        
        return WorkflowStateResponse(
            campaign_id=str(campaign_id),
            suggested_step=current_step,
            workflow_preference=workflow_preference,
            progress_summary={
                "completion_percentage": completion_percentage,
                "sources_added": sources_count,
                "sources_analyzed": intelligence_count,
                "content_generated": content_count
            },
            progress={
                "steps": {
                    "step_1": 100 if campaign.title else 0,
                    "step_2": min(100, sources_count * 25) if sources_count > 0 else 0,
                    "step_3": min(100, intelligence_count * 25) if intelligence_count > 0 else 0,
                    "step_4": min(100, content_count * 25) if content_count > 0 else 0
                }
            },
            available_actions=available_actions,
            primary_suggestion=suggestions.get(current_step, "Continue with your campaign")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow state: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow state: {str(e)}"
        )

@router.post("/{campaign_id}/workflow/set-preference")
async def set_workflow_preference(
    campaign_id: UUID,
    preferences: WorkflowPreferences,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Set workflow preferences for a campaign"""
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
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Update workflow preference (if the field exists)
        if hasattr(campaign, 'workflow_preference') and preferences.workflow_preference:
            from src.models.campaign import WorkflowPreference
            campaign.workflow_preference = WorkflowPreference(preferences.workflow_preference)
        
        # Update other workflow settings if they exist
        if hasattr(campaign, 'quick_mode_enabled'):
            campaign.quick_mode_enabled = preferences.quick_mode or False
        if hasattr(campaign, 'auto_advance_steps'):
            campaign.auto_advance_steps = preferences.auto_advance or False
        if hasattr(campaign, 'show_detailed_guidance'):
            campaign.show_detailed_guidance = preferences.detailed_guidance or True
        
        await db.commit()
        
        return {
            "campaign_id": str(campaign_id),
            "workflow_preference": preferences.workflow_preference,
            "settings_updated": preferences.dict(exclude_unset=True),
            "message": "Workflow preferences updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting workflow preference: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set workflow preference: {str(e)}"
        )

@router.post("/{campaign_id}/workflow/save-progress")
async def save_campaign_progress(
    campaign_id: UUID,
    progress_data: ProgressData,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save campaign progress (auto-save functionality)"""
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
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Update progress fields if they exist
        if hasattr(campaign, 'last_active_step') and progress_data.current_step:
            campaign.last_active_step = progress_data.current_step
        
        if hasattr(campaign, 'current_session') and progress_data.session_data:
            campaign.current_session = progress_data.session_data
        
        # Update timestamp
        campaign.updated_at = datetime.utcnow()
        if hasattr(campaign, 'last_activity'):
            campaign.last_activity = datetime.utcnow()
        
        await db.commit()
        
        return {
            "campaign_id": str(campaign_id),
            "message": "Progress saved successfully",
            "saved_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving progress: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save progress: {str(e)}"
        )

# ============================================================================
# INTELLIGENCE ENDPOINTS (EXISTING - KEEPING FOR COMPATIBILITY)
# ============================================================================

@router.get("/{campaign_id}/intelligence")
async def get_campaign_intelligence(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get intelligence sources for a campaign"""
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
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Get intelligence sources from relationships if they exist
        intelligence_sources = []
        if hasattr(campaign, 'intelligence_sources') and campaign.intelligence_sources:
            for source in campaign.intelligence_sources:
                intelligence_sources.append({
                    "id": str(source.id),
                    "source_title": source.source_title or "Untitled Source",
                    "source_url": source.source_url,
                    "source_type": source.source_type.value if hasattr(source.source_type, 'value') else str(source.source_type),
                    "confidence_score": source.confidence_score or 0.0,
                    "usage_count": getattr(source, 'usage_count', 0),
                    "analysis_status": source.analysis_status.value if hasattr(source.analysis_status, 'value') else str(source.analysis_status),
                    "created_at": source.created_at.isoformat() if source.created_at else None,
                    "updated_at": source.updated_at.isoformat() if source.updated_at else None
                })
        
        # Get generated content if exists
        generated_content = []
        if hasattr(campaign, 'generated_content') and campaign.generated_content:
            for content in campaign.generated_content:
                generated_content.append({
                    "id": str(content.id),
                    "content_type": content.content_type,
                    "content_title": content.content_title,
                    "created_at": content.created_at.isoformat() if content.created_at else None
                })
        
        return {
            "campaign_id": str(campaign_id),
            "intelligence_sources": intelligence_sources,
            "generated_content": generated_content,
            "summary": {
                "total_intelligence_sources": len(intelligence_sources),
                "total_generated_content": len(generated_content),
                "avg_confidence_score": sum(s.get("confidence_score", 0) for s in intelligence_sources) / len(intelligence_sources) if intelligence_sources else 0.0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign intelligence: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign intelligence: {str(e)}"
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
        
        total_campaigns_created = total_result.scalar()
        active_campaigns = active_result.scalar()
        draft_campaigns = draft_result.scalar()
        
        return {
            "total_campaigns_created": total_campaigns_created,
            "active_campaigns": active_campaigns,
            "draft_campaigns": draft_campaigns,
            "completed_campaigns": total_campaigns_created - active_campaigns - draft_campaigns,
            "total_sources": 0,  # Will be populated when intelligence is added back
            "total_content": 0,  # Will be populated when intelligence is added back
            "avg_completion": 25.0  # Basic completion for existing campaigns
        }
        
    except Exception as e:
        logger.error(f"Error getting campaign stats: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign stats: {str(e)}"
        )