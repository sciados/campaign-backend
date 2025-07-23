# src/campaigns/routes.py - ENHANCED WITH DEMO CAMPAIGN INTEGRATION
"""
Campaign routes - Streamlined workflow with auto-demo creation
🎯 NEW: Automatically creates demo campaigns to solve empty state issues
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
from src.models.campaign import AutoAnalysisStatus, CampaignWorkflowState
from src.models.intelligence import GeneratedContent, CampaignIntelligence
from pydantic import BaseModel

# 🆕 NEW: Import demo campaign seeder
from src.utils.demo_campaign_seeder import ensure_demo_campaign_exists, is_demo_campaign

logger = logging.getLogger(__name__)

router = APIRouter(tags=["campaigns"])

# ============================================================================
# PYDANTIC SCHEMAS (keeping existing schemas)
# ============================================================================

class CampaignCreate(BaseModel):
    title: str
    description: Optional[str] = None
    keywords: Optional[List[str]] = []
    target_audience: Optional[str] = None
    tone: Optional[str] = "conversational"
    style: Optional[str] = "modern"
    
    # Auto-Analysis Fields
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
    
    # Auto-Analysis Response Fields
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
    total_steps: int = 2
    
    # 🆕 NEW: Demo campaign indicator
    is_demo: bool = False

    class Config:
        from_attributes = True
        use_enum_values = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

# ============================================================================
# 🆕 UPDATED CAMPAIGNS LIST - WITH AUTO-DEMO CREATION
# ============================================================================

@router.get("", response_model=List[CampaignResponse])
async def get_campaigns(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """🆕 ENHANCED: Get all campaigns - automatically creates demo if none exist"""
    try:
        logger.info(f"Getting campaigns for user {current_user.id}, company {current_user.company_id}")
        
        # 🆕 NEW: First, ensure demo campaign exists (solves empty state issue)
        try:
            demo_created = await ensure_demo_campaign_exists(db, current_user.company_id, current_user.id)
            if demo_created:
                logger.info(f"✅ Demo campaign auto-created for company {current_user.company_id}")
        except Exception as demo_error:
            logger.warning(f"⚠️ Demo campaign creation failed (non-critical): {str(demo_error)}")
            # Continue without demo - don't block the main request
        
        # Build query for campaigns
        query = select(Campaign).where(Campaign.company_id == current_user.company_id)
        
        # Add status filter if provided
        if status:
            try:
                status_enum = CampaignStatus(status.upper())
                query = query.where(Campaign.status == status_enum)
                logger.info(f"Applied status filter: {status}")
            except ValueError:
                logger.warning(f"Invalid status filter '{status}'")
        
        # Add pagination
        query = query.offset(skip).limit(limit).order_by(Campaign.updated_at.desc())
        
        # Execute query
        result = await db.execute(query)
        campaigns = result.scalars().all()
        
        logger.info(f"Found {len(campaigns)} campaigns")
        
        # Convert to response format
        campaign_responses = []
        for campaign in campaigns:
            try:
                # Safely handle status enum
                status_value = campaign.status.value if hasattr(campaign.status, 'value') else str(campaign.status)
                
                # Safely calculate completion percentage
                completion_percentage = 25.0  # Default
                try:
                    completion_percentage = campaign.calculate_completion_percentage()
                except Exception:
                    pass
                
                # Safely get workflow state
                workflow_state = "basic_setup"
                try:
                    workflow_state = campaign.workflow_state.value if hasattr(campaign.workflow_state, 'value') else str(campaign.workflow_state)
                except Exception:
                    pass
                
                # Safely get auto-analysis status
                auto_analysis_status = "pending"
                try:
                    auto_analysis_status = campaign.auto_analysis_status.value if hasattr(campaign.auto_analysis_status, 'value') else str(campaign.auto_analysis_status)
                except Exception:
                    pass
                
                # 🆕 NEW: Check if this is a demo campaign
                is_demo = is_demo_campaign(campaign)
                
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
                    
                    # Auto-analysis fields
                    competitor_url=getattr(campaign, 'competitor_url', None),
                    auto_analysis_enabled=getattr(campaign, 'auto_analysis_enabled', True),
                    auto_analysis_status=auto_analysis_status,
                    analysis_confidence_score=getattr(campaign, 'analysis_confidence_score', 0.0) or 0.0,
                    
                    workflow_state=workflow_state,
                    completion_percentage=completion_percentage,
                    sources_count=getattr(campaign, 'sources_count', 0) or 0,
                    intelligence_count=getattr(campaign, 'intelligence_extracted', 0) or 0,
                    content_count=getattr(campaign, 'content_generated', 0) or 0,
                    total_steps=2,
                    
                    # 🆕 NEW: Demo campaign indicator
                    is_demo=is_demo
                )
                campaign_responses.append(campaign_response)
                
            except Exception as campaign_error:
                logger.error(f"Error processing campaign {campaign.id}: {campaign_error}")
                continue
        
        # 🆕 NEW: Sort campaigns - demo campaigns first for new users
        campaign_responses.sort(key=lambda c: (not c.is_demo, c.updated_at), reverse=True)
        
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

# ============================================================================
# CAMPAIGN CREATION (keeping existing logic)
# ============================================================================

@router.post("", response_model=CampaignResponse)
async def create_campaign(
    campaign_data: CampaignCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Create new campaign with optional auto-analysis trigger"""
    try:
        logger.info(f"🎯 Creating streamlined campaign for user {current_user.id}")
        
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
            
            # Auto-analysis fields
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
        
        # Trigger auto-analysis if enabled and URL provided
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
                {}
            )
        
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
            
            competitor_url=new_campaign.competitor_url,
            auto_analysis_enabled=new_campaign.auto_analysis_enabled,
            auto_analysis_status=new_campaign.auto_analysis_status.value if new_campaign.auto_analysis_status else "pending",
            analysis_confidence_score=new_campaign.analysis_confidence_score or 0.0,
            
            workflow_state=new_campaign.workflow_state.value if new_campaign.workflow_state else "basic_setup",
            completion_percentage=new_campaign.calculate_completion_percentage(),
            sources_count=0,
            intelligence_count=0,
            content_count=0,
            total_steps=2,
            is_demo=False  # User-created campaigns are not demos
        )
        
    except Exception as e:
        logger.error(f"❌ Error creating campaign: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )

# ============================================================================
# 🆕 NEW: DEMO CAMPAIGN MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/demo/status")
async def get_demo_campaign_status(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get demo campaign status for the company"""
    try:
        # Check if demo campaign exists
        demo_query = select(Campaign).where(
            Campaign.company_id == current_user.company_id,
            Campaign.settings.op('->>')('demo_campaign') == 'true'
        )
        
        result = await db.execute(demo_query)
        demo_campaign = result.scalar_one_or_none()
        
        if demo_campaign:
            return {
                "has_demo": True,
                "demo_campaign_id": str(demo_campaign.id),
                "demo_title": demo_campaign.title,
                "demo_status": demo_campaign.status.value if demo_campaign.status else "unknown",
                "demo_completion": demo_campaign.calculate_completion_percentage(),
                "content_count": demo_campaign.content_generated or 0
            }
        else:
            return {
                "has_demo": False,
                "demo_campaign_id": None
            }
            
    except Exception as e:
        logger.error(f"Error getting demo status: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get demo status: {str(e)}"
        )

@router.post("/demo/create")
async def create_demo_campaign_manually(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Manually create a demo campaign (for testing/admin use)"""
    try:
        from src.utils.demo_campaign_seeder import DemoCampaignSeeder
        
        seeder = DemoCampaignSeeder(db)
        demo_campaign = await seeder.create_demo_campaign(current_user.company_id, current_user.id)
        
        return {
            "success": True,
            "message": "Demo campaign created successfully",
            "demo_campaign_id": str(demo_campaign.id),
            "demo_title": demo_campaign.title
        }
        
    except Exception as e:
        logger.error(f"Error creating demo campaign: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create demo campaign: {str(e)}"
        )

@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """🆕 ENHANCED: Delete campaign with demo protection"""
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
        
        # 🆕 NEW: Protect demo campaigns from accidental deletion
        if is_demo_campaign(campaign):
            # Allow deletion but warn
            logger.info(f"⚠️ Deleting demo campaign {campaign_id}")
            
            # Delete the demo campaign
            await db.delete(campaign)
            await db.commit()
            
            # Automatically recreate demo for this company
            try:
                await ensure_demo_campaign_exists(db, current_user.company_id, current_user.id)
                logger.info(f"✅ Demo campaign recreated after deletion")
            except Exception as demo_error:
                logger.warning(f"⚠️ Failed to recreate demo campaign: {str(demo_error)}")
            
            return {
                "message": "Demo campaign deleted and recreated",
                "note": "Demo campaigns are automatically recreated to help with onboarding"
            }
        else:
            # Delete regular campaign
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
# DASHBOARD STATS (Enhanced with demo info)
# ============================================================================

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """🆕 ENHANCED: Dashboard stats with demo campaign info"""
    try:
        logger.info(f"Getting dashboard stats for user {current_user.id}")
        
        # Get basic campaign counts
        total_query = select(func.count(Campaign.id)).where(Campaign.company_id == current_user.company_id)
        active_query = select(func.count(Campaign.id)).where(
            Campaign.company_id == current_user.company_id,
            Campaign.status.in_([CampaignStatus.ACTIVE, CampaignStatus.ANALYZING])
        )
        
        # 🆕 NEW: Separate demo and real campaigns
        demo_query = select(func.count(Campaign.id)).where(
            Campaign.company_id == current_user.company_id,
            Campaign.settings.op('->>')('demo_campaign') == 'true'
        )
        real_query = select(func.count(Campaign.id)).where(
            Campaign.company_id == current_user.company_id,
            Campaign.settings.op('->>')('demo_campaign') != 'true'
        )
        
        # Analysis complete campaigns
        analysis_complete_query = select(func.count(Campaign.id)).where(
            Campaign.company_id == current_user.company_id,
            Campaign.auto_analysis_status == AutoAnalysisStatus.COMPLETED
        )
        
        # Execute queries
        total_result = await db.execute(total_query)
        active_result = await db.execute(active_query)
        demo_result = await db.execute(demo_query)
        real_result = await db.execute(real_query)
        analysis_complete_result = await db.execute(analysis_complete_query)
        
        total_campaigns = total_result.scalar() or 0
        active_campaigns = active_result.scalar() or 0
        demo_campaigns = demo_result.scalar() or 0
        real_campaigns = real_result.scalar() or 0
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
        
        # Calculate average completion
        if total_campaigns > 0:
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
            "total_campaigns_created": total_campaigns,
            "real_campaigns": real_campaigns,  # 🆕 NEW: Real vs demo split
            "demo_campaigns": demo_campaigns,  # 🆕 NEW
            "active_campaigns": active_campaigns,
            "analysis_complete_campaigns": analysis_complete_campaigns,
            "total_sources": total_sources,
            "total_content": total_content,
            "avg_completion": avg_completion,
            "workflow_type": "streamlined_2_step",
            "demo_system": {  # 🆕 NEW: Demo system info
                "demo_available": demo_campaigns > 0,
                "helps_onboarding": True,
                "solves_empty_state": True
            },
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
# BACKGROUND TASK FOR AUTO-ANALYSIS (keeping existing)
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
        
        from src.intelligence.handlers.analysis_handler import AnalysisHandler
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
                    
                    # Create analysis summary
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

# ============================================================================
# KEEP ALL OTHER EXISTING ENDPOINTS
# ============================================================================
# (Auto-analysis status, workflow state, content management, etc.)
# [Previous endpoints remain unchanged...]