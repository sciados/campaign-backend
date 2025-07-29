"""
Admin Endpoints Routes - Administrative operations
Extracted from main routes.py for better organization
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

# Core dependencies
from src.core.database import get_async_db
from src.auth.dependencies import get_current_user
from src.models import User

# Services
from ..services import DemoService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/demo/overview")
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