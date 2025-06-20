# src/campaigns/routes.py
"""
Campaign management routes - Enhanced with flexible workflow support
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
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
    CampaignWorkflowState,
    calculate_completion_percentage,
    suggest_session_length,
    can_quick_complete_campaign,
    calculate_time_spent_today
)
from src.models.intelligence import CampaignIntelligence, GeneratedContent

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
    sources_count: Optional[int] = None
    intelligence_count: Optional[int] = None
    generated_content_count: Optional[int] = None

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
        
        # Create campaign with enhanced workflow support
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
        
        # Update company campaign count
        if current_user.company:
            current_user.company.total_campaigns += 1
            await db.commit()
        
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
            completion_percentage=campaign.calculate_completion_percentage(),
            sources_count=campaign.sources_count,
            intelligence_count=campaign.intelligence_extracted,
            generated_content_count=campaign.content_generated
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
    """Get user's campaigns with filtering"""
    
    # Build query with relationships
    query = select(Campaign).options(
        selectinload(Campaign.intelligence_sources),
        selectinload(Campaign.generated_content)
    ).where(Campaign.company_id == current_user.company_id)
    
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
    
    # Convert to response format with enhanced data
    campaign_list = []
    for campaign in campaigns:
        # Update workflow progress before returning
        campaign.update_workflow_progress()
        
        # Safe handling of campaign_type
        campaign_type_value = campaign.campaign_type.value if campaign.campaign_type else "universal"
        
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
            settings=campaign.settings,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            workflow_state=campaign.workflow_state.value if campaign.workflow_state else None,
            workflow_preference=campaign.workflow_preference.value if campaign.workflow_preference else None,
            completion_percentage=campaign.calculate_completion_percentage(),
            sources_count=len(campaign.intelligence_sources) if campaign.intelligence_sources else 0,
            intelligence_count=campaign.intelligence_extracted,
            generated_content_count=len(campaign.generated_content) if campaign.generated_content else 0
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
    
    # Get campaign with relationships
    result = await db.execute(
        select(Campaign).options(
            selectinload(Campaign.intelligence_sources),
            selectinload(Campaign.generated_content)
        ).where(
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
    
    # Update workflow progress
    campaign.update_workflow_progress()
    await db.commit()
    
    # Safe handling of campaign_type
    campaign_type_value = campaign.campaign_type.value if campaign.campaign_type else "universal"
    
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
        settings=campaign.settings,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
        workflow_state=campaign.workflow_state.value if campaign.workflow_state else None,
        workflow_preference=campaign.workflow_preference.value if campaign.workflow_preference else None,
        completion_percentage=campaign.calculate_completion_percentage(),
        sources_count=len(campaign.intelligence_sources) if campaign.intelligence_sources else 0,
        intelligence_count=campaign.intelligence_extracted,
        generated_content_count=len(campaign.generated_content) if campaign.generated_content else 0
    )

# ============================================================================
# FLEXIBLE WORKFLOW API ENDPOINTS
# ============================================================================

@router.get("/{campaign_id}/workflow-state")
async def get_flexible_workflow_state(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current workflow state with flexible navigation options"""
    
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
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Calculate what's available to the user right now
    input_sources = campaign.intelligence_sources or []
    generated_content = campaign.generated_content or []
    
    # Determine available actions based on current state
    available_actions = []
    
    # Step 1: Always available for editing
    available_actions.append({
        "step": 1,
        "action": "edit_campaign",
        "title": "Edit Campaign Details",
        "description": "Update title, description, target audience, etc.",
        "can_access": True,
        "is_complete": True
    })
    
    # Step 2: Always available for adding more sources
    available_actions.append({
        "step": 2,
        "action": "add_sources", 
        "title": "Add More Sources",
        "description": f"Currently have {len(input_sources)} sources",
        "can_access": True,
        "is_complete": len(input_sources) > 0,
        "suggested": len(input_sources) == 0
    })
    
    # Step 3: Available if has sources OR in quick mode
    can_analyze = len(input_sources) > 0 or campaign.quick_mode_enabled
    available_actions.append({
        "step": 3,
        "action": "run_analysis",
        "title": "Analyze Sources",
        "description": f"Extract intelligence from {len(input_sources)} sources" if input_sources else "Run analysis (some sources recommended)",
        "can_access": can_analyze,
        "is_complete": campaign.intelligence_extracted > 0,
        "prerequisites": [] if can_analyze else ["Add at least one source"],
        "suggested": len(input_sources) > 0 and campaign.intelligence_extracted == 0
    })
    
    # Step 4: Available if has intelligence OR in quick mode with sources
    can_generate = campaign.intelligence_extracted > 0 or (campaign.quick_mode_enabled and len(input_sources) > 0)
    available_actions.append({
        "step": 4,
        "action": "generate_content",
        "title": "Generate Content",
        "description": f"Create content from {campaign.intelligence_extracted} intelligence sources" if campaign.intelligence_extracted > 0 else "Generate content (analysis recommended)",
        "can_access": can_generate,
        "is_complete": len(generated_content) > 0,
        "prerequisites": [] if can_generate else ["Complete source analysis"],
        "suggested": campaign.intelligence_extracted > 0 and len(generated_content) == 0
    })
    
    # Determine user's current focus and suggested next steps
    if len(input_sources) == 0:
        primary_suggestion = "Start by adding some sources to analyze"
        suggested_step = 2
    elif campaign.intelligence_extracted == 0:
        primary_suggestion = "Analyze your sources to extract intelligence"
        suggested_step = 3
    elif len(generated_content) == 0:
        primary_suggestion = "Generate marketing content from your intelligence"
        suggested_step = 4
    else:
        primary_suggestion = "Your campaign is ready! Add more sources or generate more content"
        suggested_step = 2  # Encourage expansion
    
    # Quick actions for power users
    quick_actions = []
    if campaign.quick_mode_enabled or campaign.workflow_preference == WorkflowPreference.QUICK:
        if len(input_sources) > 0 and campaign.intelligence_extracted == 0:
            quick_actions.append({
                "action": "analyze_all_sources",
                "title": "Analyze All Sources",
                "description": "Run AI analysis on all uploaded sources"
            })
        
        if campaign.intelligence_extracted > 0 and len(generated_content) == 0:
            quick_actions.append({
                "action": "generate_content_suite", 
                "title": "Generate Content Suite",
                "description": "Create multiple types of content at once"
            })
    
    return {
        "campaign_id": campaign_id,
        "workflow_state": campaign.workflow_state.value if campaign.workflow_state else "basic_setup",
        "workflow_preference": campaign.workflow_preference.value if campaign.workflow_preference else "flexible",
        "current_session": campaign.current_session or {},
        
        # What user can do right now
        "available_actions": available_actions,
        "quick_actions": quick_actions,
        "primary_suggestion": primary_suggestion,
        "suggested_step": suggested_step,
        
        # Progress overview
        "progress_summary": {
            "sources_added": len(input_sources),
            "sources_analyzed": campaign.intelligence_extracted, 
            "content_generated": len(generated_content),
            "completion_percentage": campaign.calculate_completion_percentage()
        },
        
        # Progress breakdown by step
        "progress": {
            "steps": {
                "step_1": 100,  # Always complete
                "step_2": 100 if len(input_sources) > 0 else 0,
                "step_3": 100 if campaign.intelligence_extracted > 0 else 0,
                "step_4": 100 if len(generated_content) > 0 else 0
            }
        },
        
        # User preferences
        "user_settings": {
            "quick_mode": campaign.quick_mode_enabled,
            "auto_advance": campaign.auto_advance_steps,
            "detailed_guidance": campaign.show_detailed_guidance,
            "save_frequently": campaign.save_frequently
        },
        
        # Session info for resuming work
        "resume_info": {
            "last_action": campaign.current_session.get("last_action"),
            "time_spent_today": calculate_time_spent_today(campaign.session_history),
            "suggested_session_length": suggest_session_length(campaign.workflow_preference),
            "can_quick_complete": campaign.can_quick_complete()
        }
    }

@router.post("/{campaign_id}/workflow/set-preference")
async def set_workflow_preference(
    campaign_id: str,
    preference_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Set user's workflow preference and mode"""
    
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
    
    # Update workflow preferences
    if "workflow_preference" in preference_data:
        campaign.workflow_preference = WorkflowPreference(preference_data["workflow_preference"])
    
    if "quick_mode" in preference_data:
        campaign.quick_mode_enabled = preference_data["quick_mode"]
        
    if "auto_advance" in preference_data:
        campaign.auto_advance_steps = preference_data["auto_advance"]
        
    if "detailed_guidance" in preference_data:
        campaign.show_detailed_guidance = preference_data["detailed_guidance"]
    
    # Quick mode adjustments
    if campaign.quick_mode_enabled:
        campaign.auto_advance_steps = True
        campaign.skip_confirmations = True
        campaign.show_detailed_guidance = False
        # Unlock all steps for quick access
        campaign.available_steps = [1, 2, 3, 4]
    
    # Methodical mode adjustments  
    if campaign.workflow_preference == WorkflowPreference.METHODICAL:
        campaign.show_detailed_guidance = True
        campaign.save_frequently = True
        campaign.auto_advance_steps = False
    
    campaign.updated_at = datetime.utcnow()
    await db.commit()
    
    return {
        "campaign_id": campaign_id,
        "workflow_preference": campaign.workflow_preference.value,
        "settings_updated": preference_data,
        "message": f"Switched to {campaign.workflow_preference.value} mode"
    }

@router.post("/{campaign_id}/workflow/advance-step")
async def advance_campaign_step(
    campaign_id: str,
    step_data: Dict[str, Any] = {},
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Advance campaign to next workflow step"""
    
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
    
    # Update workflow status based on current step
    current_step = campaign.last_active_step or 1
    
    if current_step == 1:
        campaign.workflow_state = CampaignWorkflowState.COLLECTING_SOURCES
        campaign.last_active_step = 2
    elif current_step == 2:
        campaign.workflow_state = CampaignWorkflowState.ANALYZING_SOURCES
        campaign.last_active_step = 3
    elif current_step == 3:
        campaign.workflow_state = CampaignWorkflowState.GENERATING_CONTENT
        campaign.last_active_step = 4
    
    # Store step-specific data
    if current_step == 2:
        campaign.step_2_data = {**campaign.step_2_data, **step_data}
    elif current_step == 3:
        campaign.step_3_data = {**campaign.step_3_data, **step_data}
    elif current_step == 4:
        campaign.step_4_data = {**campaign.step_4_data, **step_data}
    
    campaign.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "campaign_id": campaign_id,
        "previous_step": current_step,
        "current_step": campaign.last_active_step,
        "workflow_state": campaign.workflow_state.value,
        "message": f"Advanced to step {campaign.last_active_step}"
    }

@router.post("/{campaign_id}/workflow/save-progress")
async def save_campaign_progress(
    campaign_id: str,
    progress_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Save progress at any step without advancing"""
    
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
    
    # Update resume data for later continuation
    campaign.resume_data = {
        **campaign.resume_data,
        "saved_at": datetime.utcnow().isoformat(),
        "step_data": progress_data,
        "user_notes": progress_data.get("notes", "")
    }
    
    # Update session history
    if not campaign.session_history:
        campaign.session_history = []
    
    campaign.session_history.append({
        "date": datetime.utcnow().date().isoformat(),
        "action": "progress_saved",
        "data": progress_data,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    campaign.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "campaign_id": campaign_id,
        "message": "Progress saved successfully",
        "saved_at": campaign.resume_data["saved_at"]
    }

@router.post("/{campaign_id}/workflow/quick-complete")
async def quick_complete_campaign(
    campaign_id: str,
    quick_options: Dict[str, Any] = {},
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Quickly complete remaining campaign steps with sensible defaults"""
    
    campaign_result = await db.execute(
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
    campaign = campaign_result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    completion_plan = []
    
    # Quick complete sources (if none exist)
    if not campaign.intelligence_sources:
        completion_plan.append({
            "step": 2,
            "action": "add_sample_sources",
            "description": "Add example sources to get started quickly"
        })
    
    # Quick complete analysis (if not done)
    if not campaign.intelligence_extracted and campaign.intelligence_sources:
        completion_plan.append({
            "step": 3, 
            "action": "run_basic_analysis",
            "description": "Run basic AI analysis on all sources"
        })
    
    # Quick complete content generation (if not done)
    if not campaign.generated_content and campaign.intelligence_extracted:
        completion_plan.append({
            "step": 4,
            "action": "generate_starter_content",
            "description": "Generate essential marketing content"
        })
    
    return {
        "campaign_id": campaign_id,
        "completion_plan": completion_plan,
        "estimated_time": f"{len(completion_plan) * 2}-{len(completion_plan) * 5} minutes",
        "can_execute": len(completion_plan) > 0,
        "message": f"Can quick-complete {len(completion_plan)} remaining steps"
    }

# ============================================================================
# EXISTING ROUTES (Enhanced)
# ============================================================================

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
            completion_percentage=campaign.calculate_completion_percentage()
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
        if current_user.company:
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
        # Use default campaign type if original doesn't have one
        campaign_type = original_campaign.campaign_type if original_campaign.campaign_type else CampaignType.UNIVERSAL
        
        # Create duplicate campaign
        duplicate = Campaign(
            id=uuid4(),
            title=f"{original_campaign.title} (Copy)",
            description=original_campaign.description,
            keywords=original_campaign.keywords or [],
            target_audience=original_campaign.target_audience,
            campaign_type=campaign_type,
            status=CampaignStatus.DRAFT,
            tone=original_campaign.tone,
            style=original_campaign.style,
            settings=original_campaign.settings.copy() if original_campaign.settings else {},
            user_id=current_user.id,
            company_id=current_user.company_id,
            # Reset workflow for new campaign
            workflow_state=CampaignWorkflowState.BASIC_SETUP,
            workflow_preference=original_campaign.workflow_preference or WorkflowPreference.FLEXIBLE
        )
        
        db.add(duplicate)
        await db.commit()
        await db.refresh(duplicate)
        
        # Update company campaign count
        if current_user.company:
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
            updated_at=duplicate.updated_at,
            workflow_state=duplicate.workflow_state.value if duplicate.workflow_state else None,
            workflow_preference=duplicate.workflow_preference.value if duplicate.workflow_preference else None,
            completion_percentage=duplicate.calculate_completion_percentage()
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to duplicate campaign: {str(e)}"
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
        
        # Get credits info from company
        credits_used = current_user.company.monthly_credits_used if current_user.company else 0
        credits_limit = current_user.company.monthly_credits_limit if current_user.company else 1000
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