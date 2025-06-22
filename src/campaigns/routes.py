"""
Campaign routes - Clean version with proper routing and workflow endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.models import Campaign, User, Company, CampaignType, CampaignStatus
from pydantic import BaseModel
from datetime import datetime

logger = logging.getLogger(__name__)

# ✅ FIXED: Remove duplicate prefix (main.py already adds /api/campaigns)
router = APIRouter(tags=["campaigns"])

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

# ============================================================================
# CAMPAIGN ROUTES
# ============================================================================

@router.get("", response_model=List[CampaignResponse])
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

@router.post("", response_model=CampaignResponse)
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

# ============================================================================
# WORKFLOW ENDPOINTS
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
                status_code=status.HTTP_404_NOT_FOUND,
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
                status_code=status.HTTP_404_NOT_FOUND,
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
                status_code=status.HTTP_404_NOT_FOUND,
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save progress: {str(e)}"
        )

# ============================================================================
# INTELLIGENCE ENDPOINTS
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
                status_code=status.HTTP_404_NOT_FOUND,
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign intelligence: {str(e)}"
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