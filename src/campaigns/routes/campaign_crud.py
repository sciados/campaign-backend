"""
Campaign CRUD Routes - Core campaign operations
Extracted from main routes.py for better organization
FIXED VERSION - Resolves route path and circular import issues
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
import logging

# Core dependencies
from src.core.database import get_async_db
from src.auth.dependencies import get_current_user
from src.models import User

# Services and schemas
from ..services import CampaignService, DemoService
from ..schemas import CampaignCreate, CampaignUpdate, CampaignResponse

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================================================
# ✅ SAFE TASK IMPORT (Prevent Circular Import)
# ============================================================================

def get_safe_auto_analysis_task():
    """
    Safely import auto analysis task to prevent circular imports
    """
    try:
        # Try to import from intelligence tasks
        from src.intelligence.tasks.auto_analysis import trigger_auto_analysis_task_fixed
        return trigger_auto_analysis_task_fixed
    except ImportError:
        # Return a safe fallback function
        async def fallback_analysis_task(*args, **kwargs):
            logging.warning("⚠️ Auto analysis task not available - using fallback")
            return {
                "success": False,
                "error": "Auto analysis task not available",
                "fallback_used": True
            }
        return fallback_analysis_task

# Get the safe task function
safe_trigger_auto_analysis_task = get_safe_auto_analysis_task()

# ============================================================================
# ✅ FIXED CRUD ENDPOINTS (Correct Route Paths)
# ============================================================================

@router.get("/", response_model=List[CampaignResponse])  # ✅ FIXED: "/" instead of ""
async def get_campaigns(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get campaigns using service layer with automatic demo creation"""
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

@router.post("/", response_model=CampaignResponse)  # ✅ FIXED: "/" instead of ""
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
            
            logger.info(f"🚀 Triggering SAFE auto-analysis for {campaign_data.salespage_url}")
            
            # Use the SAFE background task (prevents circular import)
            background_tasks.add_task(
                safe_trigger_auto_analysis_task,
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
# ✅ ADDITIONAL ENDPOINTS FOR COMPATIBILITY
# ============================================================================

@router.get("/health/status")
async def crud_health():
    """Health check for CRUD operations"""
    return {
        "status": "healthy",
        "module": "campaign_crud",
        "endpoints": [
            "GET /api/campaigns/",
            "POST /api/campaigns/",
            "GET /api/campaigns/{id}",
            "PUT /api/campaigns/{id}",
            "DELETE /api/campaigns/{id}"
        ],
        "services_available": {
            "campaign_service": True,
            "demo_service": True,
            "auto_analysis": safe_trigger_auto_analysis_task is not None
        }
    }

# ============================================================================
# ✅ FALLBACK FOR QUERY PARAMETER COMPATIBILITY
# ============================================================================

@router.get("")  # Keep the old route for backwards compatibility
async def get_campaigns_legacy(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Legacy endpoint - redirects to main get_campaigns"""
    return await get_campaigns(skip, limit, status, db, current_user)

# Log successful load
logger.info("✅ Campaign CRUD routes loaded successfully with fixed paths and safe imports")