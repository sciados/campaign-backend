"""
Campaign routes - STREAMLINED WORKFLOW with Auto-Analysis
🎯 NEW: Campaign Creation → Auto-Analysis → Content Generation
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, update
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging
import json
from datetime import datetime

from src.core.database import get_async_db
from src.auth.dependencies import get_current_user
from src.models import Campaign, User, Company, CampaignStatus
from src.models.campaign import AutoAnalysisStatus, CampaignWorkflowState  # 🆕 NEW imports
from src.models.intelligence import GeneratedContent, CampaignIntelligence
from pydantic import BaseModel
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(tags=["campaigns"])

# ============================================================================
# 🆕 UPDATED PYDANTIC SCHEMAS - Streamlined Workflow
# ============================================================================

class CampaignCreate(BaseModel):
    title: str
    description: Optional[str] = None
    keywords: Optional[List[str]] = []
    target_audience: Optional[str] = None
    tone: Optional[str] = "conversational"
    style: Optional[str] = "modern"
    
    # 🆕 NEW: Auto-Analysis Fields
    competitor_url: Optional[str] = None
    auto_analysis_enabled: Optional[bool] = True
    content_types: Optional[List[str]] = ["email", "social_post", "ad_copy"]
    content_tone: Optional[str] = "conversational"
    content_style: Optional[str] = "modern"
    generate_content_after_analysis: Optional[bool] = False
    
    settings: Optional[Dict[str, Any]] = {}

class CampaignUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    target_audience: Optional[str] = None
    status: Optional[str] = None
    tone: Optional[str] = None
    style: Optional[str] = None
    
    # 🆕 NEW: Auto-Analysis Updates
    competitor_url: Optional[str] = None
    auto_analysis_enabled: Optional[bool] = None
    content_types: Optional[List[str]] = None

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
    
    # 🆕 NEW: Auto-Analysis Response Fields
    competitor_url: Optional[str] = None
    auto_analysis_enabled: bool = True
    auto_analysis_status: str = "pending"
    analysis_confidence_score: float = 0.0
    
    # Workflow fields
    workflow_state: str = "basic_setup"
    completion_percentage: float = 0.0
    sources_count: int = 0
    intelligence_count: int = 0
    content_count: int = 0
    total_steps: int = 2  # 🆕 NEW: Streamlined to 2 steps

    class Config:
        from_attributes = True
        use_enum_values = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

# 🆕 NEW: Auto-Analysis Specific Schemas
class AutoAnalysisStatusResponse(BaseModel):
    campaign_id: str
    status: str
    competitor_url: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    confidence_score: float = 0.0
    intelligence_id: Optional[str] = None
    error_message: Optional[str] = None
    summary: Dict[str, Any] = {}
    can_generate_content: bool = False
    progress_percentage: float = 0.0

class TriggerAnalysisRequest(BaseModel):
    competitor_url: str
    analysis_type: Optional[str] = "sales_page"
    auto_generate_content: Optional[bool] = False

# Existing schemas (keeping for compatibility)
class WorkflowPreferences(BaseModel):
    workflow_preference: Optional[str] = "flexible"
    quick_mode: Optional[bool] = False
    auto_advance: Optional[bool] = True  # 🆕 DEFAULT: Auto-advance enabled
    detailed_guidance: Optional[bool] = False

class WorkflowStateResponse(BaseModel):
    campaign_id: str
    suggested_step: int
    workflow_preference: str
    progress_summary: Dict[str, Any]
    progress: Dict[str, Any]
    available_actions: List[Dict[str, Any]]
    primary_suggestion: str
    auto_analysis_status: str = "pending"  # 🆕 NEW field

# ============================================================================
# 🆕 NEW: Auto-Analysis Background Task
# ============================================================================

async def trigger_auto_analysis_task(
    campaign_id: str, 
    competitor_url: str, 
    user_id: str, 
    company_id: str,
    db_connection_params: dict
):
    """Background task to trigger auto-analysis"""
    try:
        logger.info(f"🚀 Starting auto-analysis background task for campaign {campaign_id}")
        
        # Import analysis handler
        from src.intelligence.handlers.analysis_handler import AnalysisHandler
        
        # Create new DB session for background task
        from src.core.database import get_async_db_session
        async with get_async_db_session() as db:
            
            # Get user for analysis handler
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            
            if not user:
                logger.error(f"❌ User {user_id} not found for auto-analysis")
                return
            
            # Get campaign
            campaign_result = await db.execute(
                select(Campaign).where(
                    and_(Campaign.id == campaign_id, Campaign.company_id == company_id)
                )
            )
            campaign = campaign_result.scalar_one_or_none()
            
            if not campaign:
                logger.error(f"❌ Campaign {campaign_id} not found for auto-analysis")
                return
            
            # Start analysis
            campaign.start_auto_analysis()
            await db.commit()
            
            # Create analysis handler and run analysis
            handler = AnalysisHandler(db, user)
            
            analysis_request = {
                "url": competitor_url,
                "campaign_id": str(campaign_id),
                "analysis_type": "sales_page"
            }
            
            try:
                analysis_result = await handler.analyze_url(analysis_request)
                
                # Update campaign with results
                if analysis_result.get("intelligence_id"):
                    intelligence_id = analysis_result["intelligence_id"]
                    confidence_score = analysis_result.get("confidence_score", 0.0)
                    
                    # Create analysis summary for content generation
                    analysis_summary = {
                        "offer_intelligence": analysis_result.get("offer_intelligence", {}),
                        "psychology_intelligence": analysis_result.get("psychology_intelligence", {}),
                        "competitive_opportunities": analysis_result.get("competitive_opportunities", []),
                        "campaign_suggestions": analysis_result.get("campaign_suggestions", []),
                        "amplification_applied": analysis_result.get("amplification_metadata", {}).get("amplification_applied", False)
                    }
                    
                    campaign.complete_auto_analysis(intelligence_id, confidence_score, analysis_summary)
                    logger.info(f"✅ Auto-analysis completed for campaign {campaign_id}")
                    
                else:
                    raise Exception("Analysis failed - no intelligence ID returned")
                    
            except Exception as analysis_error:
                logger.error(f"❌ Auto-analysis failed: {str(analysis_error)}")
                campaign.fail_auto_analysis(str(analysis_error))
            
            await db.commit()
            
    except Exception as task_error:
        logger.error(f"❌ Auto-analysis background task failed: {str(task_error)}")
        
        # Try to update campaign status to failed
        try:
            async with get_async_db_session() as db:
                campaign_result = await db.execute(
                    select(Campaign).where(Campaign.id == campaign_id)
                )
                campaign = campaign_result.scalar_one_or_none()
                if campaign:
                    campaign.fail_auto_analysis(f"Background task failed: {str(task_error)}")
                    await db.commit()
        except Exception as update_error:
            logger.error(f"❌ Failed to update campaign status: {str(update_error)}")

# ============================================================================
# UTILITY FUNCTIONS (Updated)
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
# 🆕 UPDATED CAMPAIGN ROUTES - Auto-Analysis Support
# ============================================================================

@router.post("", response_model=CampaignResponse)
async def create_campaign(
    campaign_data: CampaignCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """🆕 ENHANCED: Create campaign with optional auto-analysis trigger"""
    try:
        logger.info(f"🎯 Creating streamlined campaign for user {current_user.id}")
        logger.info(f"Auto-analysis enabled: {campaign_data.auto_analysis_enabled}")
        logger.info(f"Competitor URL: {campaign_data.competitor_url}")
        
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
            settings=campaign_data.settings or {},
            
            # 🆕 NEW: Auto-analysis fields
            competitor_url=campaign_data.competitor_url,
            auto_analysis_enabled=campaign_data.auto_analysis_enabled,
            content_types=campaign_data.content_types or ["email", "social_post", "ad_copy"],
            content_tone=campaign_data.content_tone or "conversational",
            content_style=campaign_data.content_style or "modern",
            generate_content_after_analysis=campaign_data.generate_content_after_analysis or False
        )
        
        db.add(new_campaign)
        await db.commit()
        await db.refresh(new_campaign)
        
        logger.info(f"✅ Created campaign {new_campaign.id}")
        
        # 🆕 NEW: Trigger auto-analysis if enabled and URL provided
        if (campaign_data.auto_analysis_enabled and 
            campaign_data.competitor_url and 
            campaign_data.competitor_url.strip()):
            
            logger.info(f"🚀 Triggering auto-analysis for {campaign_data.competitor_url}")
            
            # Add background task for auto-analysis
            background_tasks.add_task(
                trigger_auto_analysis_task,
                str(new_campaign.id),
                campaign_data.competitor_url.strip(),
                str(current_user.id),
                str(current_user.company_id),
                {}  # DB connection params
            )
            
            logger.info(f"✅ Auto-analysis background task scheduled")
        
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
            
            # 🆕 NEW: Auto-analysis response fields
            competitor_url=new_campaign.competitor_url,
            auto_analysis_enabled=new_campaign.auto_analysis_enabled,
            auto_analysis_status=new_campaign.auto_analysis_status.value if new_campaign.auto_analysis_status else "pending",
            analysis_confidence_score=new_campaign.analysis_confidence_score or 0.0,
            
            workflow_state=new_campaign.workflow_state.value if new_campaign.workflow_state else "basic_setup",
            completion_percentage=new_campaign.calculate_completion_percentage(),
            sources_count=0,
            intelligence_count=0,
            content_count=0,
            total_steps=2
        )
        
    except Exception as e:
        logger.error(f"❌ Error creating campaign: {e}")
        logger.error(f"Campaign data was: {campaign_data.dict()}")
        await db.rollback()
        
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )

# ============================================================================
# 🆕 NEW: Auto-Analysis Endpoints
# ============================================================================

@router.get("/{campaign_id}/auto-analysis-status", response_model=AutoAnalysisStatusResponse)
async def get_auto_analysis_status(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """🆕 NEW: Get auto-analysis status for a campaign"""
    try:
        logger.info(f"📊 Getting auto-analysis status for campaign {campaign_id}")
        
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
        
        # Get detailed auto-analysis status
        analysis_status = campaign.get_auto_analysis_status()
        
        # Calculate progress percentage
        progress_percentage = 0.0
        if campaign.auto_analysis_status == AutoAnalysisStatus.PENDING:
            progress_percentage = 0.0
        elif campaign.auto_analysis_status == AutoAnalysisStatus.IN_PROGRESS:
            progress_percentage = 50.0
        elif campaign.auto_analysis_status == AutoAnalysisStatus.COMPLETED:
            progress_percentage = 100.0
        elif campaign.auto_analysis_status == AutoAnalysisStatus.FAILED:
            progress_percentage = 25.0  # Partial progress before failure
        
        return AutoAnalysisStatusResponse(
            campaign_id=str(campaign_id),
            status=analysis_status["status"],
            competitor_url=analysis_status["competitor_url"],
            started_at=analysis_status["started_at"],
            completed_at=analysis_status["completed_at"],
            confidence_score=analysis_status["confidence_score"],
            intelligence_id=analysis_status["intelligence_id"],
            error_message=analysis_status["error_message"],
            summary=analysis_status["summary"],
            can_generate_content=analysis_status["can_generate_content"],
            progress_percentage=progress_percentage
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting auto-analysis status: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get auto-analysis status: {str(e)}"
        )

@router.post("/{campaign_id}/trigger-analysis")
async def trigger_manual_analysis(
    campaign_id: UUID,
    analysis_request: TriggerAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """🆕 NEW: Manually trigger analysis for a campaign"""
    try:
        logger.info(f"🎯 Manually triggering analysis for campaign {campaign_id}")
        
        # Get campaign
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
        
        # Update campaign with new URL if provided
        if analysis_request.competitor_url != campaign.competitor_url:
            campaign.competitor_url = analysis_request.competitor_url
            await db.commit()
        
        # Reset analysis status for retry
        campaign.auto_analysis_status = AutoAnalysisStatus.PENDING
        campaign.auto_analysis_error = None
        await db.commit()
        
        # Trigger background analysis
        background_tasks.add_task(
            trigger_auto_analysis_task,
            str(campaign_id),
            analysis_request.competitor_url,
            str(current_user.id),
            str(current_user.company_id),
            {}
        )
        
        logger.info(f"✅ Manual analysis triggered for campaign {campaign_id}")
        
        return {
            "campaign_id": str(campaign_id),
            "message": "Analysis triggered successfully",
            "competitor_url": analysis_request.competitor_url,
            "status": "in_progress"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error triggering analysis: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger analysis: {str(e)}"
        )

@router.post("/{campaign_id}/retry-analysis")
async def retry_failed_analysis(
    campaign_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """🆕 NEW: Retry failed auto-analysis"""
    try:
        logger.info(f"🔄 Retrying failed analysis for campaign {campaign_id}")
        
        # Get campaign
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
        
        if not campaign.competitor_url:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="No competitor URL available for analysis"
            )
        
        # Reset analysis status
        campaign.auto_analysis_status = AutoAnalysisStatus.PENDING
        campaign.auto_analysis_error = None
        await db.commit()
        
        # Trigger background analysis
        background_tasks.add_task(
            trigger_auto_analysis_task,
            str(campaign_id),
            campaign.competitor_url,
            str(current_user.id),
            str(current_user.company_id),
            {}
        )
        
        logger.info(f"✅ Analysis retry triggered for campaign {campaign_id}")
        
        return {
            "campaign_id": str(campaign_id),
            "message": "Analysis retry triggered successfully",
            "competitor_url": campaign.competitor_url,
            "status": "retrying"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrying analysis: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retry analysis: {str(e)}"
        )

# ============================================================================
# EXISTING ROUTES (Updated for 2-step workflow)
# ============================================================================

@router.get("", response_model=List[CampaignResponse])
async def get_campaigns(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get all campaigns for the current user's company"""
    try:
        logger.info(f"Getting campaigns for user {current_user.id}, company {current_user.company_id}")
        
        # Build query for FULL Campaign objects
        query = select(Campaign).where(Campaign.company_id == current_user.company_id)
        
        # Add status filter if provided
        if status:
            try:
                status_enum = normalize_campaign_status(status)
                query = query.where(Campaign.status == status_enum)
                logger.info(f"Applied status filter: {status}")
            except Exception as status_error:
                logger.warning(f"Invalid status filter '{status}': {status_error}")
        
        # Add pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        campaigns = result.scalars().all()
        
        logger.info(f"Found {len(campaigns)} campaigns")
        
        # Convert to response format with proper error handling
        campaign_responses = []
        for campaign in campaigns:
            try:
                # Safely handle status enum
                try:
                    if hasattr(campaign.status, 'value'):
                        status_value = campaign.status.value
                    else:
                        status_value = str(campaign.status)
                except (AttributeError, TypeError):
                    status_value = "draft"
                
                # Safely calculate completion percentage
                try:
                    completion_percentage = campaign.calculate_completion_percentage()
                except (AttributeError, TypeError, Exception):
                    completion_percentage = 0.0
                
                # Safely get workflow state
                try:
                    if hasattr(campaign.workflow_state, 'value'):
                        workflow_state = campaign.workflow_state.value
                    else:
                        workflow_state = str(campaign.workflow_state) if campaign.workflow_state else "basic_setup"
                except (AttributeError, TypeError):
                    workflow_state = "basic_setup"
                
                # Safely get auto-analysis status
                try:
                    if hasattr(campaign.auto_analysis_status, 'value'):
                        auto_analysis_status = campaign.auto_analysis_status.value
                    else:
                        auto_analysis_status = str(campaign.auto_analysis_status) if campaign.auto_analysis_status else "pending"
                except (AttributeError, TypeError):
                    auto_analysis_status = "pending"
                
                # Create response object
                campaign_response = CampaignResponse(
                    id=str(campaign.id),
                    title=campaign.title or "Untitled Campaign",
                    description=campaign.description or "",
                    keywords=campaign.keywords if isinstance(campaign.keywords, list) else [],
                    target_audience=campaign.target_audience,
                    campaign_type="universal",
                    status=status_value,
                    tone=campaign.tone or "conversational",
                    style=campaign.style or "modern",
                    created_at=campaign.created_at,
                    updated_at=campaign.updated_at,
                    
                    # 🆕 NEW: Auto-analysis fields
                    competitor_url=getattr(campaign, 'competitor_url', None),
                    auto_analysis_enabled=getattr(campaign, 'auto_analysis_enabled', True),
                    auto_analysis_status=auto_analysis_status,
                    analysis_confidence_score=getattr(campaign, 'analysis_confidence_score', 0.0) or 0.0,
                    
                    workflow_state=workflow_state,
                    completion_percentage=completion_percentage,
                    sources_count=getattr(campaign, 'sources_count', 0) or 0,
                    intelligence_count=getattr(campaign, 'intelligence_extracted', 0) or 0,
                    content_count=getattr(campaign, 'content_generated', 0) or 0,
                    total_steps=2
                )
                campaign_responses.append(campaign_response)
                
            except Exception as campaign_error:
                logger.error(f"Error processing campaign {campaign.id}: {campaign_error}")
                continue
        
        logger.info(f"Successfully processed {len(campaign_responses)} campaigns")
        return campaign_responses
        
    except Exception as e:
        logger.error(f"Error getting campaigns: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve campaigns: {str(e)}"
        )

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_async_db),
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
            
            # 🆕 NEW: Auto-analysis fields
            competitor_url=campaign.competitor_url,
            auto_analysis_enabled=campaign.auto_analysis_enabled,
            auto_analysis_status=campaign.auto_analysis_status.value if campaign.auto_analysis_status else "pending",
            analysis_confidence_score=campaign.analysis_confidence_score or 0.0,
            
            workflow_state=campaign.workflow_state.value if campaign.workflow_state else "basic_setup",
            completion_percentage=campaign.calculate_completion_percentage(),
            sources_count=campaign.sources_count or 0,
            intelligence_count=campaign.intelligence_extracted or 0,
            content_count=campaign.content_generated or 0,
            total_steps=2
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve campaign: {str(e)}"
        )

@router.get("/{campaign_id}/workflow-state", response_model=WorkflowStateResponse)
async def get_campaign_workflow_state(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """🆕 UPDATED: Get current workflow state for 2-step campaign"""
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
        
        # Get workflow summary
        workflow_summary = campaign.get_workflow_summary()
        
        # Define available actions for 2-step workflow
        available_actions = [
            {
                "step": 1, 
                "can_access": True,
                "description": "Campaign Setup & Analysis",
                "completed": campaign.auto_analysis_status == AutoAnalysisStatus.COMPLETED
            },
            {
                "step": 2, 
                "can_access": campaign.auto_analysis_status == AutoAnalysisStatus.COMPLETED,
                "description": "Content Generation",
                "completed": campaign.content_generated > 0
            }
        ]
        
        # Generate contextual suggestions
        auto_analysis_status = campaign.auto_analysis_status.value if campaign.auto_analysis_status else "pending"
        
        if auto_analysis_status == "pending":
            primary_suggestion = "Complete campaign setup to trigger auto-analysis"
        elif auto_analysis_status == "in_progress":
            primary_suggestion = "Auto-analysis in progress - please wait"
        elif auto_analysis_status == "failed":
            primary_suggestion = "Fix analysis errors and retry analysis"
        elif auto_analysis_status == "completed" and campaign.content_generated == 0:
            primary_suggestion = "Generate content using your analysis insights"
        else:
            primary_suggestion = "Add more content or refine existing content"
        
        return WorkflowStateResponse(
            campaign_id=str(campaign_id),
            suggested_step=workflow_summary["current_step"],
            workflow_preference=workflow_summary["workflow_preference"],
            progress_summary={
                "completion_percentage": workflow_summary["completion_percentage"],
                "analysis_status": auto_analysis_status,
                "analysis_confidence": workflow_summary["analysis_confidence"],
                "content_generated": workflow_summary["content_count"],
                "total_steps": 2
            },
            progress={
                "steps": {
                    "step_1": campaign.step_states.get("step_1", {}).get("progress", 0),
                    "step_2": campaign.step_states.get("step_2", {}).get("progress", 0)
                }
            },
            available_actions=available_actions,
            primary_suggestion=primary_suggestion,
            auto_analysis_status=auto_analysis_status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow state: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow state: {str(e)}"
        )

# ============================================================================
# REMAINING ROUTES (keeping existing functionality)
# ============================================================================

@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: UUID,
    campaign_data: CampaignUpdate,
    db: AsyncSession = Depends(get_async_db),
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
            
            # Auto-analysis fields
            competitor_url=campaign.competitor_url,
            auto_analysis_enabled=campaign.auto_analysis_enabled,
            auto_analysis_status=campaign.auto_analysis_status.value if campaign.auto_analysis_status else "pending",
            analysis_confidence_score=campaign.analysis_confidence_score or 0.0,
            
            workflow_state=campaign.workflow_state.value if campaign.workflow_state else "basic_setup",
            completion_percentage=campaign.calculate_completion_percentage(),
            sources_count=campaign.sources_count or 0,
            intelligence_count=campaign.intelligence_extracted or 0,
            content_count=campaign.content_generated or 0,
            total_steps=2
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
    db: AsyncSession = Depends(get_async_db),
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

# Dashboard stats and other existing endpoints remain the same...
@router.get("/dashboard/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics"""
    try:
        logger.info(f"Getting dashboard stats for user {current_user.id}, company {current_user.company_id}")
        
        # Get basic campaign counts including new analyzing status
        total_query = select(func.count(Campaign.id)).where(Campaign.company_id == current_user.company_id)
        active_query = select(func.count(Campaign.id)).where(
            Campaign.company_id == current_user.company_id,
            Campaign.status.in_([CampaignStatus.ACTIVE, CampaignStatus.ANALYZING])  # 🆕 Include analyzing
        )
        draft_query = select(func.count(Campaign.id)).where(
            Campaign.company_id == current_user.company_id,
            Campaign.status == CampaignStatus.DRAFT
        )
        completed_query = select(func.count(Campaign.id)).where(
            Campaign.company_id == current_user.company_id,
            Campaign.status == CampaignStatus.COMPLETED
        )
        
        # 🆕 NEW: Count campaigns with auto-analysis completed
        analysis_complete_query = select(func.count(Campaign.id)).where(
            Campaign.company_id == current_user.company_id,
            Campaign.auto_analysis_status == AutoAnalysisStatus.COMPLETED
        )
        
        # Execute queries
        total_result = await db.execute(total_query)
        active_result = await db.execute(active_query)
        draft_result = await db.execute(draft_query)
        completed_result = await db.execute(completed_query)
        analysis_complete_result = await db.execute(analysis_complete_query)
        
        total_campaigns_created = total_result.scalar() or 0
        active_campaigns = active_result.scalar() or 0
        draft_campaigns = draft_result.scalar() or 0
        completed_campaigns = completed_result.scalar() or 0
        analysis_complete_campaigns = analysis_complete_result.scalar() or 0
        
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
        
        # Calculate average completion (enhanced for 2-step workflow)
        if total_campaigns_created > 0:
            completion_query = select(func.avg(
                func.case(
                    (Campaign.auto_analysis_status == AutoAnalysisStatus.COMPLETED, 60),
                    (Campaign.content_generated > 0, 100),
                    else_=25
                )
            )).where(Campaign.company_id == current_user.company_id)
            
            avg_result = await db.execute(completion_query)
            avg_completion = avg_result.scalar() or 25.0
        else:
            avg_completion = 0.0
        
        return {
            "total_campaigns_created": total_campaigns_created,
            "active_campaigns": active_campaigns,
            "draft_campaigns": draft_campaigns,
            "completed_campaigns": completed_campaigns,
            "analysis_complete_campaigns": analysis_complete_campaigns,  # 🆕 NEW metric
            "total_sources": total_sources,
            "total_content": total_content,
            "avg_completion": avg_completion,
            "workflow_type": "streamlined_2_step",  # 🆕 NEW: Indicate streamlined workflow
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