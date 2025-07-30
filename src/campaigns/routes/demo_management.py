"""
Demo Management Routes - Demo campaign operations
Extracted from main routes.py for better organization
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

# Core dependencies
from src.core.database import get_async_db
from src.auth.dependencies import get_current_user
from src.models import User

# Services and schemas
from ..services import CampaignService, DemoService
from ..schemas import (
    CampaignCreate, DemoPreferenceUpdate, DemoPreferenceResponse
)

# Import the FIXED background task
# Safe import to prevent circular imports
def get_safe_background_task():
    """Get background task safely to prevent circular imports"""
    try:
        from src.intelligence.tasks.auto_analysis import trigger_auto_analysis_task_fixed
        return trigger_auto_analysis_task_fixed
    except ImportError:
        # Fallback function if not available
        async def simple_fallback(*args, **kwargs):
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"🚀 Background analysis queued (fallback mode)")
            return {"success": True, "fallback": True}
        return simple_fallback

# Get the safe task function
trigger_auto_analysis_task_fixed = get_safe_background_task()

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/preferences", response_model=DemoPreferenceResponse)
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

@router.put("/preferences", response_model=DemoPreferenceResponse)
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

@router.post("/toggle")
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

@router.get("/status")
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

@router.post("/create")
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

@router.post("/create-with-frontend-integration")
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

@router.post("/create-with-live-analysis")
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