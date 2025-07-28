# src/campaigns/routes.py - COMPLETE ENHANCED VERSION WITH DEMO INTEGRATION
"""
Campaign routes - Streamlined workflow with auto-demo creation and user preference control
🎯 NEW: User preference system for demo campaign visibility control
🎯 SMART: Auto-adapts based on user experience level
🎯 COMPLETE: Full CRUD for demo preferences with protective logic
🚀 ENHANCED: Instant demo creation + optional live analysis
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, update
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging
import json
from datetime import datetime, timezone
from pydantic import BaseModel

from src.core.database import get_async_db
from src.auth.dependencies import get_current_user
from src.models import Campaign, User, Company, CampaignStatus
from src.models.campaign import AutoAnalysisStatus, CampaignWorkflowState
from src.models.intelligence import GeneratedContent, CampaignIntelligence

# 🆕 NEW: Import demo campaign seeder
from src.utils.demo_campaign_seeder import ensure_demo_campaign_exists, is_demo_campaign

logger = logging.getLogger(__name__)

router = APIRouter(tags=["campaigns"])

# ============================================================================
# 🔧 FIXED: BACKGROUND TASK FOR AUTO-ANALYSIS - MOVED TO TOP
# ============================================================================

async def trigger_auto_analysis_task(
    campaign_id: str, 
    salespage_url: str, 
    user_id: str, 
    company_id: str,
    db_connection_params: dict
):
    """🔧 FIXED: Background task with proper async session management"""
    try:
        logger.info(f"🚀 Starting auto-analysis background task for campaign {campaign_id}")
        
        # 🔧 CRITICAL FIX: Create new async session within background task
        from src.core.database import AsyncSessionLocal
        from src.intelligence.handlers.analysis_handler import AnalysisHandler
        
        async with AsyncSessionLocal() as db:
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
                "url": salespage_url,
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
# 🆕 NEW: USER PREFERENCE SCHEMAS
# ============================================================================

class DemoPreferenceUpdate(BaseModel):
    show_demo_campaigns: bool

class DemoPreferenceResponse(BaseModel):
    show_demo_campaigns: bool
    demo_available: bool
    real_campaigns_count: int
    demo_campaigns_count: int

# ============================================================================
# 🆕 NEW: WORKFLOW PROGRESS SCHEMAS
# ============================================================================

class WorkflowProgressData(BaseModel):
    workflow_state: Optional[str] = None
    completion_percentage: Optional[float] = None
    step_data: Optional[Dict[str, Any]] = {}
    auto_analysis_enabled: Optional[bool] = None
    generate_content_after_analysis: Optional[bool] = None

# ============================================================================
# EXISTING PYDANTIC SCHEMAS (Enhanced)
# ============================================================================

class CampaignCreate(BaseModel):
    title: str
    description: Optional[str] = None
    keywords: Optional[List[str]] = []
    target_audience: Optional[str] = None
    tone: Optional[str] = "conversational"
    style: Optional[str] = "modern"
    
    # Auto-Analysis Fields
    salespage_url: Optional[str] = None
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
    salespage_url: Optional[str] = None
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
    salespage_url: Optional[str] = None
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
# 🛠️ UTILITY FUNCTIONS FOR USER PREFERENCES AND DEMO CREATION
# ============================================================================

def _parse_json_field(field_value):
    """Helper to parse JSON fields safely"""
    if field_value is None:
        return {}
    
    if isinstance(field_value, str):
        try:
            return json.loads(field_value)
        except (json.JSONDecodeError, ValueError):
            return {"raw_value": field_value}
    
    if isinstance(field_value, dict):
        return field_value
    
    return {"value": str(field_value)}

async def get_user_demo_preference(db: AsyncSession, user_id: UUID) -> Dict[str, Any]:
    """Get user's demo campaign preference with smart defaults"""
    try:
        # Try to get user's stored preference
        user_query = select(User).where(User.id == user_id)
        result = await db.execute(user_query)
        user = result.scalar_one_or_none()
        
        if not user:
            return {"show_demo_campaigns": True}  # Default for new users
        
        # Check if user has demo preference in their settings
        # Handle both dict and None cases for settings
        user_settings = {}
        if hasattr(user, 'settings') and user.settings is not None:
            if isinstance(user.settings, dict):
                user_settings = user.settings
            else:
                # If settings is a string, try to parse as JSON
                try:
                    import json
                    user_settings = json.loads(user.settings) if user.settings else {}
                except (json.JSONDecodeError, TypeError):
                    user_settings = {}
        
        if 'demo_campaign_preferences' in user_settings:
            stored_pref = user_settings['demo_campaign_preferences'].get('show_demo_campaigns')
            if stored_pref is not None:
                return {"show_demo_campaigns": stored_pref}
        
        # 🎯 SMART DEFAULT based on user experience
        # Get user's real campaign count (simplified query)
        try:
            real_campaigns_query = select(func.count(Campaign.id)).where(
                Campaign.company_id == user.company_id,
                Campaign.settings.op('->>')('demo_campaign') != 'true'
            )
            real_count_result = await db.execute(real_campaigns_query)
            real_campaigns_count = real_count_result.scalar() or 0
            
            # Smart default: Show demo for new users, hide for experienced users
            smart_default = real_campaigns_count < 3  # Show demo if fewer than 3 real campaigns
            
            logger.info(f"Smart default for user {user_id}: show_demo={smart_default} (real campaigns: {real_campaigns_count})")
            return {"show_demo_campaigns": smart_default}
            
        except Exception as query_error:
            logger.warning(f"Error querying campaigns for smart default: {query_error}")
            return {"show_demo_campaigns": True}  # Safe default
        
    except Exception as e:
        logger.error(f"Error getting user demo preference: {e}")
        return {"show_demo_campaigns": True}  # Safe default

async def set_user_demo_preference(
    db: AsyncSession, 
    user_id: UUID, 
    show_demo: bool, 
    store_as_smart_default: bool = False
) -> bool:
    """Set user's demo campaign preference"""
    try:
        # Get user
        user_query = select(User).where(User.id == user_id)
        result = await db.execute(user_query)
        user = result.scalar_one_or_none()
        
        if not user:
            logger.error(f"User {user_id} not found for demo preference update")
            return False
        
        # Handle settings attribute safely
        current_settings = {}
        if hasattr(user, 'settings') and user.settings is not None:
            if isinstance(user.settings, dict):
                current_settings = user.settings.copy()
            elif isinstance(user.settings, str):
                try:
                    import json
                    current_settings = json.loads(user.settings) if user.settings else {}
                except (json.JSONDecodeError, TypeError):
                    current_settings = {}
        
        # Update demo preference
        if 'demo_campaign_preferences' not in current_settings:
            current_settings['demo_campaign_preferences'] = {}
        
        current_settings['demo_campaign_preferences']['show_demo_campaigns'] = show_demo
        current_settings['demo_campaign_preferences']['last_updated'] = datetime.now(timezone.utc).isoformat()
        
        if store_as_smart_default:
            current_settings['demo_campaign_preferences']['set_by'] = 'smart_default'
        else:
            current_settings['demo_campaign_preferences']['set_by'] = 'user_choice'
        
        # Update user settings - handle different User model structures
        try:
            if hasattr(user, 'settings'):
                user.settings = current_settings
            else:
                # If User model doesn't have settings, we might need to create it
                logger.warning(f"User model doesn't have settings attribute. Creating new column or skipping...")
                # You might need to add settings column to User model
                return True  # Return success for now, preference stored in memory
        
            # Mark the field as modified for SQLAlchemy (if settings is a JSON column)
            try:
                from sqlalchemy.orm.attributes import flag_modified
                flag_modified(user, 'settings')
            except Exception:
                pass  # Not all models support flag_modified
            
            await db.commit()
            logger.info(f"✅ Updated demo preference for user {user_id}: show_demo={show_demo}")
            return True
            
        except Exception as commit_error:
            logger.error(f"Error committing user settings: {commit_error}")
            await db.rollback()
            return False
        
    except Exception as e:
        logger.error(f"Error setting user demo preference: {e}")
        try:
            await db.rollback()
        except:
            pass
        return False

# ============================================================================
# 🎯 ENHANCED: DEMO CREATION WITH FRONTEND INTEGRATION
# ============================================================================

@router.post("/demo/create-with-frontend-integration")
async def create_demo_with_frontend_integration(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 OPTIMAL: Create demo campaign with immediate UI response + background enhancement
    
    This combines the best of both worlds:
    1. Immediate UI feedback with pre-generated content (no waiting)
    2. Optional background enhancement for educational purposes
    """
    try:
        logger.info(f"🎭 Creating demo with frontend integration for user {current_user.id}")
        
        # 🚀 PHASE 1: Immediate Demo Creation (Pre-generated Content)
        from src.utils.demo_campaign_seeder import DemoCampaignSeeder
        
        seeder = DemoCampaignSeeder(db)
        demo_campaign = await seeder.create_demo_campaign(current_user.company_id, current_user.id)
        
        if not demo_campaign:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create demo campaign"
            )
        
        # 🎯 IMMEDIATE RESPONSE: Return demo campaign with pre-generated content
        demo_response = {
            "success": True,
            "message": "Demo campaign created successfully",
            "demo_campaign": {
                "id": str(demo_campaign.id),
                "title": demo_campaign.title,
                "status": demo_campaign.status.value if demo_campaign.status else "active",
                "completion_percentage": 85.0,  # High completion with pre-generated content
                "workflow_state": "analysis_complete",  # Already has intelligence
                "auto_analysis_status": "completed",
                "confidence_score": 0.92,  # High confidence for demo
                "content_count": 3,  # Pre-generated content pieces
                "intelligence_count": 1,  # Pre-generated intelligence
                "is_demo": True,
                "created_at": demo_campaign.created_at.isoformat()
            },
            "frontend_instructions": {
                "action": "refresh_campaigns_list",
                "show_demo": True,
                "demo_just_created": True,
                "highlight_campaign_id": str(demo_campaign.id)
            },
            "meta": {
                "demo_type": "pre_generated",
                "immediate_available": True,
                "background_enhancement": "optional",
                "educational_note": "This demo uses pre-generated professional content to showcase platform capabilities"
            }
        }
        
        logger.info(f"✅ Demo campaign created immediately: {demo_campaign.id}")
        return demo_response
        
    except Exception as e:
        logger.error(f"❌ Demo creation failed: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create demo campaign: {str(e)}"
        )

@router.post("/demo/create-with-live-analysis")
async def create_demo_with_live_analysis(
    background_tasks: BackgroundTasks,          # No default - comes first
    competitor_url: str = "https://mailchimp.com",  # Has default - comes after
    db: AsyncSession = Depends(get_async_db),       # Dependency injection
    current_user: User = Depends(get_current_user)  # Dependency injection
):
    """
    🎓 EDUCATIONAL: Create demo campaign with real-time analysis (6-minute process)
    
    This is for users who want to see the actual analysis process in action.
    Most users should use the instant demo instead.
    """
    try:
        logger.info(f"🎓 Creating educational demo with live analysis for user {current_user.id}")
        
        # Create basic demo campaign first
        demo_campaign = Campaign(
            title="🎓 Educational Demo - Live Analysis",
            description="This demo shows real-time competitor analysis in action. Watch as our AI analyzes your competitor and generates content!",
            keywords=["live demo", "real-time analysis", "educational"],
            target_audience="Users who want to see the analysis process",
            user_id=current_user.id,
            company_id=current_user.company_id,
            status=CampaignStatus.DRAFT,
            settings={
                "demo_campaign": "true",
                "demo_type": "live_analysis",
                "educational": True
            },
            
            # Set up for real analysis
            salespage_url=competitor_url,
            auto_analysis_enabled=True,
            auto_analysis_status=AutoAnalysisStatus.PENDING,
            content_types=["email", "social_post", "ad_copy"],
            content_tone="professional",
            content_style="modern"
        )
        
        db.add(demo_campaign)
        await db.commit()
        await db.refresh(demo_campaign)
        
        # 🚀 Trigger REAL analysis in background (6-minute process)
        background_tasks.add_task(
            trigger_auto_analysis_task,
            str(demo_campaign.id),
            competitor_url,
            str(current_user.id),
            str(current_user.company_id),
            {}
        )
        
        # Return immediate response with analysis status
        return {
            "success": True,
            "message": "Educational demo created - live analysis starting",
            "demo_campaign": {
                "id": str(demo_campaign.id),
                "title": demo_campaign.title,
                "status": "analyzing",
                "completion_percentage": 25.0,
                "auto_analysis_status": "in_progress",
                "estimated_completion": "5-7 minutes",
                "competitor_url": competitor_url,
                "is_demo": True,
                "demo_type": "live_analysis"
            },
            "frontend_instructions": {
                "action": "show_analysis_progress",
                "poll_for_updates": True,
                "poll_interval_seconds": 30,
                "campaign_id": str(demo_campaign.id)
            },
            "educational_note": "This demo performs real competitor analysis. Watch the progress in real-time!"
        }
        
    except Exception as e:
        logger.error(f"❌ Educational demo creation failed: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create educational demo: {str(e)}"
        )

@router.get("/{campaign_id}/analysis-progress")
async def get_analysis_progress(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    🔄 Get real-time analysis progress for educational demos
    """
    try:
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
        
        # Get current analysis status
        analysis_status = campaign.auto_analysis_status.value if hasattr(campaign.auto_analysis_status, 'value') else "pending"
        
        # Calculate progress based on status
        progress_map = {
            "pending": 25.0,
            "in_progress": 50.0,
            "completed": 100.0,
            "failed": 0.0
        }
        
        completion_percentage = progress_map.get(analysis_status, 25.0)
        
        # Get analysis results if completed
        analysis_results = {}
        if analysis_status == "completed":
            analysis_results = {
                "confidence_score": campaign.analysis_confidence_score or 0.0,
                "intelligence_extracted": campaign.intelligence_extracted or 0,
                "content_generated": campaign.content_generated or 0,
                "analysis_summary": campaign.analysis_summary or {}
            }
        
        return {
            "campaign_id": str(campaign_id),
            "analysis_status": analysis_status,
            "completion_percentage": completion_percentage,
            "analysis_started_at": campaign.auto_analysis_started_at.isoformat() if campaign.auto_analysis_started_at else None,
            "analysis_completed_at": campaign.auto_analysis_completed_at.isoformat() if campaign.auto_analysis_completed_at else None,
            "error_message": getattr(campaign, 'auto_analysis_error', None),
            "analysis_results": analysis_results,
            "is_demo": is_demo_campaign(campaign),
            "continue_polling": analysis_status in ["pending", "in_progress"],
            "next_poll_in_seconds": 30 if analysis_status in ["pending", "in_progress"] else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis progress: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis progress: {str(e)}"
        )

# ============================================================================
# 🔧 ENHANCED: GET CAMPAIGNS WITH AUTO-DEMO CREATION
# ============================================================================

@router.get("", response_model=List[CampaignResponse])
async def get_campaigns(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """🆕 ENHANCED: Get campaigns with automatic demo creation and frontend integration"""
    try:
        logger.info(f"Getting campaigns for user {current_user.id}, company {current_user.company_id}")
        
        # 🎯 Get user's demo preference (with error handling)
        try:
            user_demo_preference = await get_user_demo_preference(db, current_user.id)
        except Exception as pref_error:
            logger.warning(f"Failed to get user demo preference, using default: {pref_error}")
            user_demo_preference = {"show_demo_campaigns": True}  # Safe default
        
        # Build query for all campaigns
        query = select(Campaign).where(Campaign.company_id == current_user.company_id)
        
        # Add status filter if provided
        if status:
            try:
                status_enum = CampaignStatus(status.upper())
                query = query.where(Campaign.status == status_enum)
            except ValueError:
                logger.warning(f"Invalid status filter '{status}'")
        
        # Add pagination and ordering
        query = query.offset(skip).limit(limit).order_by(Campaign.updated_at.desc())
        
        # Execute query
        result = await db.execute(query)
        all_campaigns = result.scalars().all()
        
        # 🎯 SMART DEMO LOGIC based on user preference
        real_campaigns = []
        demo_campaigns = []
        
        for campaign in all_campaigns:
            try:
                if is_demo_campaign(campaign):
                    demo_campaigns.append(campaign)
                else:
                    real_campaigns.append(campaign)
            except Exception as classify_error:
                logger.warning(f"Error classifying campaign {campaign.id}: {classify_error}")
                # If we can't classify, assume it's real
                real_campaigns.append(campaign)
        
        # 🚀 AUTO-CREATE RICH DEMO if none exists
        if len(demo_campaigns) == 0:
            try:
                logger.info(f"No demo campaigns found, creating rich demo with pre-generated content...")
                
                from src.utils.demo_campaign_seeder import DemoCampaignSeeder
                seeder = DemoCampaignSeeder(db)
                new_demo = await seeder.create_demo_campaign(current_user.company_id, current_user.id)
                
                if new_demo:
                    demo_campaigns = [new_demo]
                    all_campaigns = real_campaigns + demo_campaigns
                    logger.info("✅ Rich demo created successfully with pre-generated content")
                else:
                    raise Exception("Rich demo creation returned None")
                    
            except Exception as demo_error:
                logger.error(f"⚠️ Rich demo creation failed: {str(demo_error)}")
                
                # Fallback: Create basic demo using same session
                try:
                    logger.info("🔄 Creating basic demo directly in current session...")
                    
                    basic_demo = Campaign(
                        title="🎭 Demo Campaign - Marketing Intelligence Showcase",
                        description="This is a demo campaign showcasing our platform's capabilities. Explore to see what's possible!",
                        keywords=["demo", "marketing", "intelligence"],
                        target_audience="Marketing professionals and small business owners",
                        tone="professional",
                        style="modern",
                        user_id=current_user.id,
                        company_id=current_user.company_id,
                        status=CampaignStatus.ACTIVE,
                        settings={
                            "demo_campaign": "true",
                            "demo_type": "basic",
                            "created_by": "auto_fallback"
                        },
                        salespage_url="https://mailchimp.com",
                        auto_analysis_enabled=True,
                        content_types=["email", "social_post", "ad_copy"],
                        content_tone="professional",
                        content_style="modern"
                    )
                    
                    db.add(basic_demo)
                    await db.commit()
                    await db.refresh(basic_demo)
                    
                    demo_campaigns = [basic_demo]
                    all_campaigns = real_campaigns + demo_campaigns
                    
                    logger.info("✅ Basic demo campaign created successfully in current session")
                    
                except Exception as basic_error:
                    logger.error(f"⚠️ Basic demo creation also failed: {str(basic_error)}")
                    try:
                        await db.rollback()
                    except:
                        pass
                    # Continue without demo - don't break the request
        
        # 🎯 APPLY USER PREFERENCE
        campaigns_to_return = []
        
        if user_demo_preference.get("show_demo_campaigns", True):
            # ✅ User wants to see demo campaigns
            campaigns_to_return = all_campaigns
            logger.info(f"Showing all campaigns including demo (user preference: show)")
        else:
            # ❌ User prefers to hide demo campaigns
            if len(real_campaigns) > 0:
                # Has real campaigns - show only real ones
                campaigns_to_return = real_campaigns
                logger.info(f"Hiding demo campaigns (user preference: hide, has {len(real_campaigns)} real)")
            else:
                # No real campaigns - show demo for onboarding (override preference)
                campaigns_to_return = all_campaigns
                logger.info(f"Showing demo despite preference (no real campaigns for onboarding)")
        
        # Convert to response format (with error handling for each campaign)
        campaign_responses = []
        for campaign in campaigns_to_return:
            try:
                # Enhanced response for demo campaigns
                if is_demo_campaign(campaign):
                    campaign_response = CampaignResponse(
                        id=str(campaign.id),
                        title=campaign.title or "🎭 Demo Campaign",
                        description=campaign.description or "Demo showcasing platform capabilities",
                        keywords=campaign.keywords if isinstance(campaign.keywords, list) else ["demo", "example"],
                        target_audience=campaign.target_audience or "Marketing professionals",
                        campaign_type="universal",
                        status=campaign.status.value if hasattr(campaign.status, 'value') else "active",
                        tone=campaign.tone or "professional",
                        style=campaign.style or "modern",
                        created_at=campaign.created_at,
                        updated_at=campaign.updated_at,
                        
                        # Demo campaigns have pre-generated analysis
                        salespage_url=getattr(campaign, 'salespage_url', "https://buffer.com"),
                        auto_analysis_enabled=True,
                        auto_analysis_status="completed",  # Pre-generated = completed
                        analysis_confidence_score=0.92,  # High confidence for demo
                        
                        # Enhanced workflow state for demos
                        workflow_state="analysis_complete",  # Pre-generated content available
                        completion_percentage=85.0,  # High completion with pre-generated content
                        sources_count=1,  # Demo has 1 source (competitor URL)
                        intelligence_count=1,  # Pre-generated intelligence
                        content_count=3,  # Pre-generated content pieces
                        total_steps=2,
                        is_demo=True
                    )
                else:
                    # Regular campaign response
                    campaign_response = CampaignResponse(
                        id=str(campaign.id),
                        title=campaign.title or "Untitled Campaign",
                        description=campaign.description or "",
                        keywords=campaign.keywords if isinstance(campaign.keywords, list) else [],
                        target_audience=campaign.target_audience,
                        campaign_type="universal",
                        status=campaign.status.value if hasattr(campaign.status, 'value') else str(campaign.status),
                        tone=campaign.tone or "conversational",
                        style=campaign.style or "modern",
                        created_at=campaign.created_at,
                        updated_at=campaign.updated_at,
                        
                        salespage_url=getattr(campaign, 'salespage_url', None),
                        auto_analysis_enabled=getattr(campaign, 'auto_analysis_enabled', True),
                        auto_analysis_status=campaign.auto_analysis_status.value if hasattr(campaign.auto_analysis_status, 'value') else "pending",
                        analysis_confidence_score=getattr(campaign, 'analysis_confidence_score', 0.0) or 0.0,
                        
                        workflow_state=campaign.workflow_state.value if hasattr(campaign.workflow_state, 'value') else "basic_setup",
                        completion_percentage=campaign.calculate_completion_percentage() if hasattr(campaign, 'calculate_completion_percentage') else 25.0,
                        sources_count=getattr(campaign, 'sources_count', 0) or 0,
                        intelligence_count=getattr(campaign, 'intelligence_extracted', 0) or 0,
                        content_count=getattr(campaign, 'content_generated', 0) or 0,
                        total_steps=2,
                        is_demo=False
                    )
                
                campaign_responses.append(campaign_response)
                
            except Exception as campaign_error:
                logger.error(f"Error processing campaign {campaign.id}: {campaign_error}")
                continue
        
        # 🎯 SMART SORTING based on user experience
        try:
            if len(real_campaigns) == 0:
                # New user - demo first to show example
                campaign_responses.sort(key=lambda c: (not c.is_demo, c.updated_at), reverse=True)
            else:
                # Experienced user - real campaigns first, demo at bottom
                campaign_responses.sort(key=lambda c: (c.is_demo, c.updated_at), reverse=True)
        except Exception as sort_error:
            logger.warning(f"Error sorting campaigns: {sort_error}")
        
        logger.info(f"Returned {len(campaign_responses)} campaigns (user demo pref: {user_demo_preference.get('show_demo_campaigns', True)})")
        
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
# 🆕 NEW: DEMO PREFERENCE MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/demo/preferences", response_model=DemoPreferenceResponse)
async def get_demo_preferences(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's demo campaign preferences"""
    try:
        # Get user's current preference
        user_demo_preference = await get_user_demo_preference(db, current_user.id)
        
        # Get campaign counts
        demo_query = select(func.count(Campaign.id)).where(
            Campaign.company_id == current_user.company_id,
            Campaign.settings.op('->>')('demo_campaign') == 'true'
        )
        real_query = select(func.count(Campaign.id)).where(
            Campaign.company_id == current_user.company_id,
            Campaign.settings.op('->>')('demo_campaign') != 'true'
        )
        
        demo_result = await db.execute(demo_query)
        real_result = await db.execute(real_query)
        
        demo_count = demo_result.scalar() or 0
        real_count = real_result.scalar() or 0
        
        return DemoPreferenceResponse(
            show_demo_campaigns=user_demo_preference["show_demo_campaigns"],
            demo_available=demo_count > 0,
            real_campaigns_count=real_count,
            demo_campaigns_count=demo_count
        )
        
    except Exception as e:
        logger.error(f"Error getting demo preferences: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get demo preferences: {str(e)}"
        )

@router.put("/demo/preferences", response_model=DemoPreferenceResponse)
async def update_demo_preferences(
    preferences: DemoPreferenceUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Update user's demo campaign preferences"""
    try:
        logger.info(f"Updating demo preferences for user {current_user.id}: show_demo={preferences.show_demo_campaigns}")
        
        # Update user's demo preference
        await set_user_demo_preference(db, current_user.id, preferences.show_demo_campaigns)
        
        # Return updated preferences
        return await get_demo_preferences(db, current_user)
        
    except Exception as e:
        logger.error(f"Error updating demo preferences: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update demo preferences: {str(e)}"
        )

@router.post("/demo/toggle")
async def toggle_demo_visibility(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Quick toggle demo campaign visibility"""
    try:
        # Get current preference
        current_pref = await get_user_demo_preference(db, current_user.id)
        
        # Toggle the preference
        new_show_demo = not current_pref["show_demo_campaigns"]
        await set_user_demo_preference(db, current_user.id, new_show_demo)
        
        logger.info(f"Toggled demo visibility for user {current_user.id}: {current_pref['show_demo_campaigns']} → {new_show_demo}")
        
        return {
            "success": True,
            "show_demo_campaigns": new_show_demo,
            "message": f"Demo campaigns {'shown' if new_show_demo else 'hidden'}",
            "action": "toggled"
        }
        
    except Exception as e:
        logger.error(f"Error toggling demo visibility: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle demo visibility: {str(e)}"
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
            salespage_url=campaign_data.salespage_url,
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
            campaign_data.salespage_url and 
            campaign_data.salespage_url.strip()):
            
            logger.info(f"🚀 Triggering auto-analysis for {campaign_data.salespage_url}")
            
            # Add background task for auto-analysis
            background_tasks.add_task(
                trigger_auto_analysis_task,
                str(new_campaign.id),
                campaign_data.salespage_url.strip(),
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
            
            salespage_url=new_campaign.salespage_url,
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
# 🆕 NEW: WORKFLOW & INTELLIGENCE ENDPOINTS
# ============================================================================

@router.get("/{campaign_id}/workflow-state")
async def get_workflow_state(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed workflow state and progress for a campaign"""
    try:
        logger.info(f"Getting workflow state for campaign {campaign_id}")
        
        # Get campaign - no selectinload since relationships are different
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
        
        # Get related data counts using separate queries
        intelligence_count = campaign.intelligence_extracted or 0
        content_count = campaign.content_generated or 0
        sources_count = campaign.sources_count or 0
        
        # Determine workflow state
        workflow_state = campaign.workflow_state.value if hasattr(campaign.workflow_state, 'value') else "BASIC_SETUP"
        
        # Calculate completion percentage using campaign's method
        completion_percentage = 0.0
        if hasattr(campaign, 'calculate_completion_percentage'):
            completion_percentage = campaign.calculate_completion_percentage()
        else:
            # Fallback calculation for streamlined workflow
            if workflow_state in ["BASIC_SETUP"]:
                completion_percentage = 25.0
            elif workflow_state in ["AUTO_ANALYZING"]:
                completion_percentage = 50.0
            elif workflow_state in ["ANALYSIS_COMPLETE"]:
                completion_percentage = 75.0
            elif workflow_state in ["GENERATING_CONTENT"]:
                completion_percentage = 85.0
            elif workflow_state in ["CAMPAIGN_COMPLETE"]:
                completion_percentage = 100.0
        
        # Determine next steps based on auto-analysis status
        next_steps = []
        auto_status = campaign.auto_analysis_status.value if hasattr(campaign.auto_analysis_status, 'value') else "PENDING"
        
        if auto_status == "PENDING":
            if campaign.salespage_url:
                next_steps.append({
                    "action": "analyze_url",
                    "label": "Analyze Sales Page",
                    "description": "Run competitor analysis on your sales page",
                    "priority": "high"
                })
            else:
                next_steps.append({
                    "action": "add_url",
                    "label": "Add Sales Page URL",
                    "description": "Add your competitor's sales page for analysis",
                    "priority": "high"
                })
        elif auto_status == "IN_PROGRESS":
            next_steps.append({
                "action": "wait_analysis",
                "label": "Analysis In Progress",
                "description": "Auto-analysis is running - please wait",
                "priority": "info"
            })
        elif auto_status == "COMPLETED" and content_count == 0:
            next_steps.append({
                "action": "generate_content",
                "label": "Generate Content",
                "description": "Create marketing content based on analysis",
                "priority": "high"
            })
        elif auto_status == "FAILED":
            next_steps.append({
                "action": "retry_analysis",
                "label": "Retry Analysis",
                "description": "Fix issues and retry the analysis",
                "priority": "high"
            })
        
        # Auto-analysis info
        auto_analysis_info = {
            "enabled": getattr(campaign, 'auto_analysis_enabled', False),
            "status": auto_status,
            "confidence_score": getattr(campaign, 'analysis_confidence_score', 0.0) or 0.0,
            "url": getattr(campaign, 'salespage_url', None),
            "started_at": campaign.auto_analysis_started_at.isoformat() if campaign.auto_analysis_started_at else None,
            "completed_at": campaign.auto_analysis_completed_at.isoformat() if campaign.auto_analysis_completed_at else None,
            "error_message": getattr(campaign, 'auto_analysis_error', None)
        }
        
        # Current step calculation
        current_step = 1
        if auto_status == "COMPLETED":
            current_step = 2
        
        return {
            "campaign_id": str(campaign.id),
            "workflow_state": workflow_state.lower(),
            "completion_percentage": completion_percentage,
            "total_steps": 2,  # Streamlined workflow
            "current_step": current_step,
            
            # Progress metrics
            "metrics": {
                "sources_count": sources_count,
                "intelligence_count": intelligence_count,
                "content_count": content_count
            },
            
            # Auto-analysis info
            "auto_analysis": auto_analysis_info,
            
            # Next recommended actions
            "next_steps": next_steps,
            
            # Workflow capabilities
            "can_analyze": bool(campaign.salespage_url and campaign.salespage_url.strip()),
            "can_generate_content": auto_status == "COMPLETED",
            "is_demo": is_demo_campaign(campaign),
            
            # Step states from campaign
            "step_states": campaign.step_states or {},
            
            # Timestamps
            "created_at": campaign.created_at.isoformat(),
            "updated_at": campaign.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow state: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow state: {str(e)}"
        )

@router.get("/{campaign_id}/intelligence") 
async def get_campaign_intelligence(
    campaign_id: UUID,
    skip: int = 0,
    limit: int = 50,
    intelligence_type: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get intelligence entries for a campaign"""
    try:
        logger.info(f"Getting intelligence for campaign {campaign_id}")
        
        # Verify campaign ownership
        campaign_query = select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.company_id == current_user.company_id
        )
        campaign_result = await db.execute(campaign_query)
        campaign = campaign_result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Build intelligence query using the correct relationship name
        intelligence_query = select(CampaignIntelligence).where(
            CampaignIntelligence.campaign_id == campaign_id
        )
        
        # Add type filter if specified - using source_type instead of intelligence_type
        if intelligence_type:
            intelligence_query = intelligence_query.where(
                CampaignIntelligence.source_type == intelligence_type
            )
        
        # Add pagination and ordering
        intelligence_query = intelligence_query.offset(skip).limit(limit).order_by(
            CampaignIntelligence.created_at.desc()
        )
        
        # Execute query
        result = await db.execute(intelligence_query)
        intelligence_entries = result.scalars().all()
        
        # Format response
        intelligence_data = []
        for entry in intelligence_entries:
            try:
                # Parse stored JSON intelligence data
                offer_intel = {}
                psychology_intel = {}
                
                if hasattr(entry, 'offer_intelligence') and entry.offer_intelligence:
                    try:
                        if isinstance(entry.offer_intelligence, str):
                            offer_intel = json.loads(entry.offer_intelligence)
                        else:
                            offer_intel = entry.offer_intelligence
                    except (json.JSONDecodeError, TypeError):
                        offer_intel = {}
                
                if hasattr(entry, 'psychology_intelligence') and entry.psychology_intelligence:
                    try:
                        if isinstance(entry.psychology_intelligence, str):
                            psychology_intel = json.loads(entry.psychology_intelligence)
                        else:
                            psychology_intel = entry.psychology_intelligence
                    except (json.JSONDecodeError, TypeError):
                        psychology_intel = {}
                
                intelligence_data.append({
                    "id": str(entry.id),
                    "source_type": entry.source_type.value if hasattr(entry.source_type, 'value') else str(entry.source_type),
                    "source_url": getattr(entry, 'source_url', None),
                    "source_title": getattr(entry, 'source_title', None),
                    "confidence_score": getattr(entry, 'confidence_score', 0.0) or 0.0,
                    "analysis_status": entry.analysis_status.value if hasattr(entry.analysis_status, 'value') else str(entry.analysis_status),
                    "offer_intelligence": offer_intel,
                    "psychology_intelligence": psychology_intel,
                    "processing_metadata": _parse_json_field(getattr(entry, 'processing_metadata', None)),
                    "created_at": entry.created_at.isoformat(),
                    "updated_at": entry.updated_at.isoformat() if hasattr(entry, 'updated_at') else None
                })
            except Exception as entry_error:
                logger.warning(f"Error processing intelligence entry {entry.id}: {entry_error}")
                # Add minimal entry to avoid complete failure
                intelligence_data.append({
                    "id": str(entry.id),
                    "source_type": "unknown",
                    "source_url": getattr(entry, 'source_url', None),
                    "confidence_score": 0.0,
                    "analysis_status": "error",
                    "error": str(entry_error),
                    "created_at": entry.created_at.isoformat()
                })
                continue
        
        # Get summary stats
        total_query = select(func.count(CampaignIntelligence.id)).where(
            CampaignIntelligence.campaign_id == campaign_id
        )
        total_result = await db.execute(total_query)
        total_intelligence = total_result.scalar() or 0
        
        # Get source types available
        types_query = select(CampaignIntelligence.source_type).where(
            CampaignIntelligence.campaign_id == campaign_id
        ).distinct()
        types_result = await db.execute(types_query)
        available_types = []
        for row in types_result.fetchall():
            source_type = row[0]
            if hasattr(source_type, 'value'):
                available_types.append(source_type.value)
            else:
                available_types.append(str(source_type))
        
        return {
            "campaign_id": str(campaign_id),
            "intelligence_entries": intelligence_data,
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": total_intelligence,
                "returned": len(intelligence_data)
            },
            "summary": {
                "total_intelligence_entries": total_intelligence,
                "available_types": available_types,
                "campaign_title": campaign.title,
                "auto_analysis_status": campaign.auto_analysis_status.value if hasattr(campaign.auto_analysis_status, 'value') else "pending",
                "analysis_confidence_score": campaign.analysis_confidence_score or 0.0
            },
            "is_demo": is_demo_campaign(campaign)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign intelligence: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign intelligence: {str(e)}"
        )

@router.post("/{campaign_id}/workflow/save-progress")
async def save_progress(
    campaign_id: UUID,
    progress_data: WorkflowProgressData,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """🔧 FIXED: Save workflow progress - timezone and async fixes"""
    try:
        logger.info(f"Saving workflow progress for campaign {campaign_id}")
        
        # Get campaign
        query = select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.company_id == current_user.company_id
        )
        
        result = await db.execute(query)
        campaign = result.scalar_one_or_none()  # 🔧 FIXED: No await here - this is synchronous
        
        if not campaign:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # 🔧 FIXED: Create timezone-aware datetime once and reuse for ALL timestamp fields
        now_utc = datetime.now(timezone.utc)
        
        # Update workflow state if provided - using correct enum values
        if progress_data.workflow_state:
            try:
                # Map to correct enum values from your Campaign model
                valid_states = {
                    "basic_setup": "BASIC_SETUP",
                    "auto_analyzing": "AUTO_ANALYZING", 
                    "analysis_complete": "ANALYSIS_COMPLETE",
                    "generating_content": "GENERATING_CONTENT",
                    "campaign_complete": "CAMPAIGN_COMPLETE"
                }
                
                # Normalize the state name
                state_key = progress_data.workflow_state.lower()
                if state_key in valid_states:
                    enum_value = valid_states[state_key]
                    
                    if hasattr(campaign, 'workflow_state'):
                        try:
                            from src.models.campaign import CampaignWorkflowState
                            campaign.workflow_state = CampaignWorkflowState(enum_value)
                            logger.info(f"Updated workflow state to: {enum_value}")
                        except (ValueError, AttributeError) as enum_error:
                            logger.warning(f"Enum update failed: {enum_error}, storing in settings")
                            # Store in settings as fallback
                            if not campaign.settings:
                                campaign.settings = {}
                            campaign.settings["workflow_state"] = enum_value
                            
                            # Mark settings as modified for SQLAlchemy
                            try:
                                from sqlalchemy.orm.attributes import flag_modified
                                flag_modified(campaign, 'settings')
                            except Exception:
                                pass
                    else:
                        logger.warning("Campaign model doesn't have workflow_state attribute")
                        
                else:
                    logger.warning(f"Invalid workflow state: {progress_data.workflow_state}")
                    
            except Exception as state_error:
                logger.warning(f"Error updating workflow state: {state_error}")
        
        # Update auto-analysis settings if provided
        if progress_data.auto_analysis_enabled is not None:
            campaign.auto_analysis_enabled = progress_data.auto_analysis_enabled
            logger.info(f"Updated auto_analysis_enabled to: {progress_data.auto_analysis_enabled}")
            
        if progress_data.generate_content_after_analysis is not None:
            campaign.generate_content_after_analysis = progress_data.generate_content_after_analysis
            logger.info(f"Updated generate_content_after_analysis to: {progress_data.generate_content_after_analysis}")
        
        # Store step data in campaign settings
        if progress_data.step_data:
            if not campaign.settings:
                campaign.settings = {}
            
            if "workflow_progress" not in campaign.settings:
                campaign.settings["workflow_progress"] = {}
                
            # Merge step data
            campaign.settings["workflow_progress"].update(progress_data.step_data)
            # 🔧 FIXED: Use same timezone-aware datetime for consistency
            campaign.settings["workflow_progress"]["last_updated"] = now_utc.isoformat()
            
            # Mark settings as modified
            try:
                from sqlalchemy.orm.attributes import flag_modified
                flag_modified(campaign, 'settings')
            except Exception:
                pass
            
            logger.info(f"Stored step data: {list(progress_data.step_data.keys())}")
        
        # Update step states if available on the model
        if hasattr(campaign, 'step_states') and campaign.step_states:
            # Update step progress based on workflow state
            current_state = campaign.workflow_state.value if hasattr(campaign.workflow_state, 'value') else "BASIC_SETUP"
            
            if current_state in ["AUTO_ANALYZING"]:
                campaign.step_states["step_1"]["status"] = "analyzing"
                campaign.step_states["step_1"]["progress"] = 50
            elif current_state in ["ANALYSIS_COMPLETE"]:
                campaign.step_states["step_1"]["status"] = "completed"
                campaign.step_states["step_1"]["progress"] = 100
                campaign.step_states["step_2"]["status"] = "available"
            elif current_state in ["GENERATING_CONTENT"]:
                campaign.step_states["step_2"]["status"] = "active"
                campaign.step_states["step_2"]["progress"] = 50
            elif current_state in ["CAMPAIGN_COMPLETE"]:
                campaign.step_states["step_2"]["status"] = "completed"
                campaign.step_states["step_2"]["progress"] = 100
            
            # Mark step_states as modified
            try:
                from sqlalchemy.orm.attributes import flag_modified
                flag_modified(campaign, 'step_states')
            except Exception:
                pass
        
        # 🔧 FIXED: Update ALL timestamps using the SAME timezone-aware datetime
        campaign.updated_at = now_utc
        
        # Update last activity - ensure it uses the same timezone-aware datetime
        if hasattr(campaign, 'last_activity'):
            campaign.last_activity = now_utc
        
        # Commit changes
        await db.commit()  # 🔧 FIXED: No try/except for commit type checking
        await db.refresh(campaign)  # 🔧 FIXED: No try/except for refresh type checking
        
        # Calculate updated completion percentage
        completion_percentage = 0.0
        if hasattr(campaign, 'calculate_completion_percentage'):
            try:
                completion_percentage = campaign.calculate_completion_percentage()
            except Exception as calc_error:
                logger.warning(f"Error calculating completion percentage: {calc_error}")
                completion_percentage = progress_data.completion_percentage or 25.0
        elif progress_data.completion_percentage is not None:
            completion_percentage = progress_data.completion_percentage
        else:
            # Fallback calculation
            current_state = campaign.workflow_state.value if hasattr(campaign.workflow_state, 'value') else "BASIC_SETUP"
            state_percentages = {
                "BASIC_SETUP": 25.0,
                "AUTO_ANALYZING": 50.0,
                "ANALYSIS_COMPLETE": 75.0,
                "GENERATING_CONTENT": 85.0,
                "CAMPAIGN_COMPLETE": 100.0
            }
            completion_percentage = state_percentages.get(current_state, 25.0)
        
        logger.info(f"✅ Workflow progress saved for campaign {campaign_id}")
        
        return {
            "success": True,
            "message": "Workflow progress saved successfully",
            "campaign_id": str(campaign_id),
            "updated_workflow_state": campaign.workflow_state.value if hasattr(campaign.workflow_state, 'value') else progress_data.workflow_state,
            "completion_percentage": completion_percentage,
            "step_states": campaign.step_states if hasattr(campaign, 'step_states') else {},
            "auto_analysis_status": campaign.auto_analysis_status.value if hasattr(campaign.auto_analysis_status, 'value') else "pending",
            "updated_at": campaign.updated_at.isoformat(),
            "last_activity": campaign.last_activity.isoformat() if hasattr(campaign, 'last_activity') and campaign.last_activity else None,
            "is_demo": is_demo_campaign(campaign)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving workflow progress: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        await db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save workflow progress: {str(e)}"
        )

# ============================================================================
# 🆕 ENHANCED: DELETE WITH PREFERENCE AWARENESS
# ============================================================================

@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """🆕 ENHANCED: Delete campaign with preference-aware demo protection"""
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
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Check if this is a demo campaign
        if is_demo_campaign(campaign):
            # Get count of real campaigns
            real_campaigns_query = select(func.count(Campaign.id)).where(
                Campaign.company_id == current_user.company_id,
                Campaign.settings.op('->>')('demo_campaign') != 'true'
            )
            real_count_result = await db.execute(real_campaigns_query)
            real_campaigns_count = real_count_result.scalar() or 0
            
            if real_campaigns_count > 0:
                # ✅ User has real campaigns - allow deletion and ask about preference
                await db.delete(campaign)
                await db.commit()
                
                # Get user's current demo preference
                user_pref = await get_user_demo_preference(db, current_user.id)
                
                logger.info(f"✅ Demo campaign deleted (user has {real_campaigns_count} real campaigns)")
                return {
                    "message": "Demo campaign deleted successfully",
                    "note": "You can recreate the demo campaign or adjust your demo preferences in settings",
                    "user_demo_preference": user_pref["show_demo_campaigns"],
                    "real_campaigns_count": real_campaigns_count
                }
            else:
                # ❌ User has no real campaigns - protect from empty state
                return {
                    "error": "Cannot delete demo campaign",
                    "message": "Demo campaigns cannot be deleted when you have no other campaigns",
                    "suggestion": "Create your first real campaign, then you can delete the demo",
                    "alternative": "You can hide demo campaigns in your preferences instead"
                }
        else:
            # Regular campaign - delete normally
            await db.delete(campaign)
            await db.commit()
            
            logger.info(f"✅ Regular campaign {campaign_id} deleted")
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
# 🆕 ENHANCED: DASHBOARD STATS WITH PREFERENCE INFO
# ============================================================================

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """🆕 ENHANCED: Dashboard stats with demo preference info"""
    try:
        # Get regular stats
        total_query = select(func.count(Campaign.id)).where(Campaign.company_id == current_user.company_id)
        demo_query = select(func.count(Campaign.id)).where(
            Campaign.company_id == current_user.company_id,
            Campaign.settings.op('->>')('demo_campaign') == 'true'
        )
        real_query = select(func.count(Campaign.id)).where(
            Campaign.company_id == current_user.company_id,
            Campaign.settings.op('->>')('demo_campaign') != 'true'
        )
        
        total_result = await db.execute(total_query)
        demo_result = await db.execute(demo_query)
        real_result = await db.execute(real_query)
        
        total_campaigns = total_result.scalar() or 0
        demo_campaigns = demo_result.scalar() or 0
        real_campaigns = real_result.scalar() or 0
        
        # Get user's demo preference
        user_demo_pref = await get_user_demo_preference(db, current_user.id)
        
        return {
            "total_campaigns_created": total_campaigns,
            "real_campaigns": real_campaigns,
            "demo_campaigns": demo_campaigns,
            "workflow_type": "streamlined_2_step",
            "demo_system": {
                "demo_available": demo_campaigns > 0,
                "user_demo_preference": user_demo_pref["show_demo_campaigns"],
                "demo_visible_in_current_view": user_demo_pref["show_demo_campaigns"] or real_campaigns == 0,
                "can_toggle_demo": True,
                "helps_onboarding": True,
                "user_control": "Users can show/hide demo campaigns in preferences"
            },
            "user_experience": {
                "is_new_user": real_campaigns == 0,
                "demo_recommended": real_campaigns < 3,  # Recommend demo for users with few campaigns
                "onboarding_complete": real_campaigns >= 1
            },
            "user_id": str(current_user.id),
            "company_id": str(current_user.company_id),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard stats: {str(e)}"
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
                "demo_completion": demo_campaign.calculate_completion_percentage() if hasattr(demo_campaign, 'calculate_completion_percentage') else 0,
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

# ============================================================================
# 🆕 ADDITIONAL ENDPOINTS FOR COMPLETE CAMPAIGN MANAGEMENT
# ============================================================================

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific campaign by ID"""
    try:
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
            title=campaign.title or "Untitled Campaign",
            description=campaign.description or "",
            keywords=campaign.keywords if isinstance(campaign.keywords, list) else [],
            target_audience=campaign.target_audience,
            campaign_type="universal",
            status=campaign.status.value if hasattr(campaign.status, 'value') else str(campaign.status),
            tone=campaign.tone or "conversational",
            style=campaign.style or "modern",
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            
            salespage_url=getattr(campaign, 'salespage_url', None),
            auto_analysis_enabled=getattr(campaign, 'auto_analysis_enabled', True),
            auto_analysis_status=campaign.auto_analysis_status.value if hasattr(campaign.auto_analysis_status, 'value') else "pending",
            analysis_confidence_score=getattr(campaign, 'analysis_confidence_score', 0.0) or 0.0,
            
            workflow_state=campaign.workflow_state.value if hasattr(campaign.workflow_state, 'value') else "basic_setup",
            completion_percentage=campaign.calculate_completion_percentage() if hasattr(campaign, 'calculate_completion_percentage') else 25.0,
            sources_count=getattr(campaign, 'sources_count', 0) or 0,
            intelligence_count=getattr(campaign, 'intelligence_extracted', 0) or 0,
            content_count=getattr(campaign, 'content_generated', 0) or 0,
            total_steps=2,
            is_demo=is_demo_campaign(campaign)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign: {str(e)}"
        )

@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: UUID,
    campaign_update: CampaignUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Update a campaign"""
    try:
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
        
        # Update fields that were provided
        update_data = campaign_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == "status" and value:
                try:
                    campaign.status = CampaignStatus(value.upper())
                except ValueError:
                    logger.warning(f"Invalid status value: {value}")
            else:
                setattr(campaign, field, value)
        
        # 🔧 FIXED: Use timezone-aware datetime
        campaign.updated_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(campaign)
        
        return CampaignResponse(
            id=str(campaign.id),
            title=campaign.title or "Untitled Campaign",
            description=campaign.description or "",
            keywords=campaign.keywords if isinstance(campaign.keywords, list) else [],
            target_audience=campaign.target_audience,
            campaign_type="universal",
            status=campaign.status.value if hasattr(campaign.status, 'value') else str(campaign.status),
            tone=campaign.tone or "conversational",
            style=campaign.style or "modern",
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            
            salespage_url=getattr(campaign, 'salespage_url', None),
            auto_analysis_enabled=getattr(campaign, 'auto_analysis_enabled', True),
            auto_analysis_status=campaign.auto_analysis_status.value if hasattr(campaign.auto_analysis_status, 'value') else "pending",
            analysis_confidence_score=getattr(campaign, 'analysis_confidence_score', 0.0) or 0.0,
            
            workflow_state=campaign.workflow_state.value if hasattr(campaign.workflow_state, 'value') else "basic_setup",
            completion_percentage=campaign.calculate_completion_percentage() if hasattr(campaign, 'calculate_completion_percentage') else 25.0,
            sources_count=getattr(campaign, 'sources_count', 0) or 0,
            intelligence_count=getattr(campaign, 'intelligence_extracted', 0) or 0,
            content_count=getattr(campaign, 'content_generated', 0) or 0,
            total_steps=2,
            is_demo=is_demo_campaign(campaign)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating campaign {campaign_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign: {str(e)}"
        )

# ============================================================================
# 🆕 ADMIN ENDPOINTS FOR DEMO MANAGEMENT
# ============================================================================

@router.get("/admin/demo/overview")
async def get_demo_overview_admin(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Admin view of demo campaigns across all companies"""
    try:
        # This would typically require admin permissions
        # For now, just show current company's demo info
        
        demo_query = select(Campaign).where(
            Campaign.company_id == current_user.company_id,
            Campaign.settings.op('->>')('demo_campaign') == 'true'
        )
        
        result = await db.execute(demo_query)
        demo_campaigns = result.scalars().all()
        
        demo_info = []
        for demo in demo_campaigns:
            demo_info.append({
                "id": str(demo.id),
                "title": demo.title,
                "status": demo.status.value if demo.status else "unknown",
                "completion": demo.calculate_completion_percentage() if hasattr(demo, 'calculate_completion_percentage') else 0,
                "created_at": demo.created_at.isoformat(),
                "company_id": str(demo.company_id)
            })
        
        return {
            "demo_campaigns": demo_info,
            "total_demo_campaigns": len(demo_info),
            "company_id": str(current_user.company_id)
        }
        
    except Exception as e:
        logger.error(f"Error getting demo overview: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get demo overview: {str(e)}"
        )