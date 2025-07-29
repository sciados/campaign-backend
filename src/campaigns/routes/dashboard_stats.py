"""
Dashboard Stats Routes - Dashboard and analytics operations
Extracted from main routes.py for better organization
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
import logging

# Core dependencies
from src.core.database import get_async_db
from src.auth.dependencies import get_current_user
from src.models import User

# Services
from ..services import CampaignService, DemoService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/stats")
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