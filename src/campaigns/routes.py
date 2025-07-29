# src/campaigns/routes.py - Phase 1C: Updated to use Service Layer
"""
Campaign routes - Updated to use service layer architecture
🎯 Phase 1C: Routes now use services instead of direct database calls
🔧 CRITICAL FIX: Background task async session management preserved
🏗️ Clean separation: Routes handle HTTP, Services handle business logic
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging
from datetime import datetime, timezone

# Core dependencies
from src.core.database import get_async_db, AsyncSessionLocal
from src.auth.dependencies import get_current_user
from src.models import User

# 🆕 Import services and schemas (Phase 1C)
from src.campaigns.services import CampaignService, DemoService, WorkflowService
from src.campaigns.schemas import (
    CampaignCreate, CampaignUpdate, CampaignResponse,
    DemoPreferenceUpdate, DemoPreferenceResponse,
    WorkflowProgressData
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["campaigns"])

# ============================================================================
# 🔧 CRITICAL FIX: BACKGROUND TASK - PRESERVED FROM PHASE 1B
# ============================================================================

async def trigger_auto_analysis_task_fixed(
    campaign_id: str, 
    salespage_url: str, 
    user_id: str, 
    company_id: str
):
    """
    🔧 CRITICAL FIX: Background task with proper async session management
    This replaces the broken version that caused SQLAlchemy async context errors
    *** PRESERVED FROM PHASE 1B - DO NOT MODIFY ***
    """
    try:
        logger.info(f"🚀 Starting FIXED auto-analysis background task for campaign {campaign_id}")
        
        # 🔧 CRITICAL FIX: Create new async session within background task
        async with AsyncSessionLocal() as db:
            try:
                # Use CampaignService to handle the background analysis
                campaign_service = CampaignService(db)
                
                # Get user for analysis handler
                from sqlalchemy import select
                user_result = await db.execute(select(User).where(User.id == user_id))
                user = user_result.scalar_one_or_none()
                
                if not user:
                    logger.error(f"❌ User {user_id} not found for auto-analysis")
                    return
                
                # Get campaign using service
                campaign = await campaign_service.get_campaign_by_id(UUID(campaign_id))
                if not campaign:
                    logger.error(f"❌ Campaign {campaign_id} not found for auto-analysis")
                    return
                
                # Start analysis using campaign's method
                campaign.start_auto_analysis()
                await db.commit()
                
                # Create analysis handler and run analysis
                from src.intelligence.handlers.analysis_handler import AnalysisHandler
                handler = AnalysisHandler(db, user)
                
                analysis_request = {
                    "url": salespage_url,
                    "campaign_id": str(campaign_id),
                    "analysis_type": "sales_page"
                }
                
                try:
                    analysis_result = await handler.analyze_url(analysis_request)
                    
                    # Update campaign with results using service
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
                        
                        # Complete analysis using campaign model method
                        campaign.complete_auto_analysis(intelligence_id, confidence_score, analysis_summary)
                        logger.info(f"✅ FIXED auto-analysis completed for campaign {campaign_id}")
                        
                    else:
                        raise Exception("Analysis failed - no intelligence ID returned")
                        
                except Exception as analysis_error:
                    logger.error(f"❌ Auto-analysis failed: {str(analysis_error)}")
                    campaign.fail_auto_analysis(str(analysis_error))
                
                # Final commit for campaign updates
                await db.commit()
                logger.info(f"✅ FIXED background task completed successfully for campaign {campaign_id}")
                
            except Exception as inner_error:
                logger.error(f"❌ Error in FIXED background task inner loop: {str(inner_error)}")
                await db.rollback()
                raise inner_error
            
    except Exception as task_error:
        logger.error(f"❌ FIXED auto-analysis background task failed: {str(task_error)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")

# ============================================================================
# 🎯 MAIN ENDPOINTS - Updated to use Service Layer
# ============================================================================

@router.get("", response_model=List[CampaignResponse])
async def get_campaigns(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """🆕 Get campaigns using service layer with automatic demo creation"""
    try:
        logger.info(f"Getting campaigns for user {current_user.id}, company {current_user.company_id}")
        
        # Initialize services
        campaign_service = CampaignService(db)
        demo_service = DemoService(db)
        
        # Get campaigns using service
        campaigns = await campaign_service.get_campaigns_by_company(
            current_user.company_id, skip, limit, status
        )
        
        # Handle demo campaign logic using demo service
        demo_campaigns = [c for c in campaigns if demo_service.is_demo_campaign(c)]
        real_campaigns = [c for c in campaigns if not demo_service.is_demo_campaign(c)]
        
        # Auto-create demo if none exists
        if len(demo_campaigns) == 0:
            logger.info("No demo campaigns found, creating demo...")
            try:
                demo_campaign = await demo_service.create_demo_campaign(
                    current_user.company_id, current_user.id
                )
                if demo_campaign:
                    demo_campaigns = [demo_campaign]
                    campaigns = real_campaigns + demo_campaigns
            except Exception as demo_error:
                logger.warning(f"Demo creation failed: {demo_error}")
        
        # Apply user demo preferences
        user_pref = await demo_service.get_user_demo_preference(current_user.id)
        
        if user_pref.get("show_demo_campaigns", True) or len(real_campaigns) == 0:
            campaigns_to_return = campaigns
        else:
            campaigns_to_return = real_campaigns
        
        # Convert to response format using service
        campaign_responses = []
        for campaign in campaigns_to_return:
            response = campaign_service.to_response(campaign)
            campaign_responses.append(response)
        
        # Smart sorting based on user experience
        if len(real_campaigns) == 0:
            # New user - demo first
            campaign_responses.sort(key=lambda c: (not c.is_demo, c.updated_at), reverse=True)
        else:
            # Experienced user - real campaigns first
            campaign_responses.sort(key=lambda c: (c.is_demo, c.updated_at), reverse=True)
        
        logger.info(f"Returned {len(campaign_responses)} campaigns")
        return campaign_responses
        
    except Exception as e:
        logger.error(f"Error getting campaigns: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve campaigns: {str(e)}"
        )

@router.post("", response_model=CampaignResponse)
async def create_campaign(
    campaign_data: CampaignCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Create new campaign using service layer"""
    try:
        logger.info(f"🎯 Creating campaign for user {current_user.id}")
        
        # Initialize service
        campaign_service = CampaignService(db)
        
        # Create campaign using service
        new_campaign = await campaign_service.create_campaign(
            campaign_data, current_user.id, current_user.company_id
        )
        
        # 🔧 CRITICAL FIX: Trigger auto-analysis if enabled and URL provided
        if (campaign_data.auto_analysis_enabled and 
            campaign_data.salespage_url and 
            campaign_data.salespage_url.strip()):
            
            logger.info(f"🚀 Triggering FIXED auto-analysis for {campaign_data.salespage_url}")
            
            # Use the FIXED background task
            background_tasks.add_task(
                trigger_auto_analysis_task_fixed,
                str(new_campaign.id),
                campaign_data.salespage_url.strip(),
                str(current_user.id),
                str(current_user.company_id)
            )
        
        # Convert to response using service
        return campaign_service.to_response(new_campaign)
        
    except Exception as e:
        logger.error(f"❌ Error creating campaign: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific campaign using service layer"""
    try:
        # Initialize service
        campaign_service = CampaignService(db)
        
        # Get campaign using service
        campaign = await campaign_service.get_campaign_by_id_and_company(
            campaign_id, current_user.company_id
        )
        
        if not campaign:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Convert to response using service
        return campaign_service.to_response(campaign)
        
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
    """Update a campaign using service layer"""
    try:
        # Initialize service
        campaign_service = CampaignService(db)
        
        # Update campaign using service
        updated_campaign = await campaign_service.update_campaign(
            campaign_id, campaign_update, current_user.company_id
        )
        
        if not updated_campaign:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Convert to response using service
        return campaign_service.to_response(updated_campaign)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating campaign {campaign_id}: {e}")
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
    """Delete campaign using service layer with demo protection"""
    try:
        logger.info(f"Deleting campaign {campaign_id} for user {current_user.id}")
        
        # Initialize services
        campaign_service = CampaignService(db)
        demo_service = DemoService(db)
        
        # Get the campaign
        campaign = await campaign_service.get_campaign_by_id_and_company(
            campaign_id, current_user.company_id
        )
        
        if not campaign:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Check if this is a demo campaign and apply protection logic
        if demo_service.is_demo_campaign(campaign):
            can_delete, message = await demo_service.can_delete_demo_campaign(
                current_user.company_id
            )
            
            if not can_delete:
                return {
                    "error": "Cannot delete demo campaign",
                    "message": message,
                    "suggestion": "Create your first real campaign, then you can delete the demo",
                    "alternative": "You can hide demo campaigns in your preferences instead"
                }
        
        # Delete campaign using service
        await campaign_service.delete_campaign(campaign_id, current_user.company_id)
        
        logger.info(f"✅ Campaign {campaign_id} deleted")
        return {"message": "Campaign deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting campaign: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete campaign: {str(e)}"
        )

# ============================================================================
# 🎭 DEMO CAMPAIGN ENDPOINTS - Using Demo Service
# ============================================================================

@router.get("/demo/preferences", response_model=DemoPreferenceResponse)
async def get_demo_preferences(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's demo campaign preferences using service layer"""
    try:
        # Initialize service
        demo_service = DemoService(db)
        
        # Get preferences using service
        preferences = await demo_service.get_demo_preferences(
            current_user.id, current_user.company_id
        )
        
        return preferences
        
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
    """Update user's demo campaign preferences using service layer"""
    try:
        logger.info(f"Updating demo preferences for user {current_user.id}: show_demo={preferences.show_demo_campaigns}")
        
        # Initialize service
        demo_service = DemoService(db)
        
        # Update preferences using service
        updated_preferences = await demo_service.update_demo_preferences(
            current_user.id, current_user.company_id, preferences.show_demo_campaigns
        )
        
        return updated_preferences
        
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
    """Quick toggle demo campaign visibility using service layer"""
    try:
        # Initialize service
        demo_service = DemoService(db)
        
        # Toggle preference using service
        result = await demo_service.toggle_demo_visibility(current_user.id)
        
        logger.info(f"Toggled demo visibility for user {current_user.id}: {result['show_demo_campaigns']}")
        
        return {
            "success": True,
            "show_demo_campaigns": result["show_demo_campaigns"],
            "message": f"Demo campaigns {'shown' if result['show_demo_campaigns'] else 'hidden'}",
            "action": "toggled"
        }
        
    except Exception as e:
        logger.error(f"Error toggling demo visibility: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle demo visibility: {str(e)}"
        )

@router.get("/demo/status")
async def get_demo_campaign_status(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get demo campaign status using service layer"""
    try:
        # Initialize service
        demo_service = DemoService(db)
        
        # Get demo status using service
        status = await demo_service.get_demo_status(current_user.company_id)
        
        return status
        
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
    """Manually create a demo campaign using service layer"""
    try:
        # Initialize service
        demo_service = DemoService(db)
        
        # Create demo using service
        demo_campaign = await demo_service.create_demo_campaign(
            current_user.company_id, current_user.id
        )
        
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

@router.post("/demo/create-with-frontend-integration")
async def create_demo_with_frontend_integration(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Create demo campaign with immediate UI response using service layer"""
    try:
        logger.info(f"🎭 Creating demo with frontend integration for user {current_user.id}")
        
        # Initialize service
        demo_service = DemoService(db)
        
        # Create demo using service
        demo_campaign = await demo_service.create_demo_campaign(
            current_user.company_id, current_user.id
        )
        
        if not demo_campaign:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create demo campaign"
            )
        
        # Return structured response for frontend
        return {
            "success": True,
            "message": "Demo campaign created successfully",
            "demo_campaign": {
                "id": str(demo_campaign.id),
                "title": demo_campaign.title,
                "status": demo_campaign.status.value if demo_campaign.status else "active",
                "completion_percentage": 85.0,
                "workflow_state": "analysis_complete",
                "auto_analysis_status": "completed",
                "confidence_score": 0.92,
                "content_count": 3,
                "intelligence_count": 1,
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
        
    except Exception as e:
        logger.error(f"❌ Demo creation failed: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create demo campaign: {str(e)}"
        )

@router.post("/demo/create-with-live-analysis")
async def create_demo_with_live_analysis(
    background_tasks: BackgroundTasks,
    competitor_url: str = "https://mailchimp.com",
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Create demo campaign with real-time analysis using service layer"""
    try:
        logger.info(f"🎓 Creating educational demo with live analysis for user {current_user.id}")
        
        # Initialize services
        campaign_service = CampaignService(db)
        demo_service = DemoService(db)
        
        # Create educational demo data
        demo_data = CampaignCreate(
            title="🎓 Educational Demo - Live Analysis",
            description="This demo shows real-time competitor analysis in action. Watch as our AI analyzes your competitor and generates content!",
            keywords=["live demo", "real-time analysis", "educational"],
            target_audience="Users who want to see the analysis process",
            salespage_url=competitor_url,
            auto_analysis_enabled=True,
            content_types=["email", "social_post", "ad_copy"],
            content_tone="professional",
            content_style="modern",
            settings={
                "demo_campaign": "true",
                "demo_type": "live_analysis", 
                "educational": True
            }
        )
        
        # Create demo campaign using service
        demo_campaign = await campaign_service.create_campaign(
            demo_data, current_user.id, current_user.company_id
        )
        
        # 🔧 Use the fixed background task for live analysis
        background_tasks.add_task(
            trigger_auto_analysis_task_fixed,
            str(demo_campaign.id),
            competitor_url,
            str(current_user.id),
            str(current_user.company_id)
        )
        
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
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create educational demo: {str(e)}"
        )

# ============================================================================
# ⚡ WORKFLOW ENDPOINTS - Using Workflow Service
# ============================================================================

@router.get("/{campaign_id}/workflow-state")
async def get_workflow_state(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed workflow state and progress using service layer"""
    try:
        logger.info(f"Getting workflow state for campaign {campaign_id}")
        
        # Initialize services
        campaign_service = CampaignService(db)
        workflow_service = WorkflowService(db)
        
        # Get campaign
        campaign = await campaign_service.get_campaign_by_id_and_company(
            campaign_id, current_user.company_id
        )
        
        if not campaign:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Get workflow progress using service
        workflow_data = await workflow_service.get_workflow_progress(campaign)
        
        return workflow_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow state: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow state: {str(e)}"
        )

@router.post("/{campaign_id}/workflow/save-progress")
async def save_progress(
    campaign_id: UUID,
    progress_data: WorkflowProgressData,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Save workflow progress using service layer"""
    try:
        logger.info(f"Saving workflow progress for campaign {campaign_id}")
        
        # Initialize services
        campaign_service = CampaignService(db)
        workflow_service = WorkflowService(db)
        
        # Get campaign
        campaign = await campaign_service.get_campaign_by_id_and_company(
            campaign_id, current_user.company_id
        )
        
        if not campaign:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Save progress using service
        result = await workflow_service.save_workflow_progress(campaign, progress_data)
        
        logger.info(f"✅ Workflow progress saved for campaign {campaign_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving workflow progress: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save workflow progress: {str(e)}"
        )

@router.get("/{campaign_id}/analysis-progress")
async def get_analysis_progress(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get real-time analysis progress using service layer"""
    try:
        # Initialize services
        campaign_service = CampaignService(db)
        workflow_service = WorkflowService(db)
        
        # Get campaign
        campaign = await campaign_service.get_campaign_by_id_and_company(
            campaign_id, current_user.company_id
        )
        
        if not campaign:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Get analysis progress using service
        progress_data = await workflow_service.get_analysis_progress(campaign)
        
        return progress_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis progress: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis progress: {str(e)}"
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
    """Get intelligence entries for a campaign using service layer"""
    try:
        logger.info(f"Getting intelligence for campaign {campaign_id}")
        
        # Initialize services
        campaign_service = CampaignService(db)
        workflow_service = WorkflowService(db)
        
        # Verify campaign ownership
        campaign = await campaign_service.get_campaign_by_id_and_company(
            campaign_id, current_user.company_id
        )
        
        if not campaign:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Get intelligence data using service
        intelligence_data = await workflow_service.get_campaign_intelligence(
            campaign_id, skip, limit, intelligence_type
        )
        
        return intelligence_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign intelligence: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign intelligence: {str(e)}"
        )

# ============================================================================
# 📊 DASHBOARD ENDPOINTS - Using Services
# ============================================================================

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard stats with demo preference info using service layer"""
    try:
        # Initialize services
        campaign_service = CampaignService(db)
        demo_service = DemoService(db)
        
        # Get campaign stats using service
        stats = await campaign_service.get_dashboard_stats(current_user.company_id)
        
        # Get demo preferences using service
        demo_prefs = await demo_service.get_demo_preferences(
            current_user.id, current_user.company_id
        )
        
        # Combine stats with demo info
        return {
            **stats,
            "demo_system": {
                "demo_available": demo_prefs.demo_available,
                "user_demo_preference": demo_prefs.show_demo_campaigns,
                "demo_visible_in_current_view": demo_prefs.show_demo_campaigns or stats["real_campaigns"] == 0,
                "can_toggle_demo": True,
                "helps_onboarding": True,
                "user_control": "Users can show/hide demo campaigns in preferences"
            },
            "user_experience": {
                "is_new_user": stats["real_campaigns"] == 0,
                "demo_recommended": stats["real_campaigns"] < 3,
                "onboarding_complete": stats["real_campaigns"] >= 1
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
# 🔧 ADMIN ENDPOINTS - Using Services
# ============================================================================

@router.get("/admin/demo/overview")
async def get_demo_overview_admin(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Admin view of demo campaigns using service layer"""
    try:
        # Initialize service
        demo_service = DemoService(db)
        
        # Get demo overview using service
        overview = await demo_service.get_demo_overview(current_user.company_id)
        
        return overview
        
    except Exception as e:
        logger.error(f"Error getting demo overview: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get demo overview: {str(e)}"
        )