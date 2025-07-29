"""
Workflow Operations Routes - Workflow and intelligence operations
Extracted from main routes.py for better organization
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
import logging

# Core dependencies
from src.core.database import get_async_db
from src.auth.dependencies import get_current_user
from src.models import User

# Services and schemas
from ..services import CampaignService, WorkflowService
from ..schemas import WorkflowProgressData

logger = logging.getLogger(__name__)
router = APIRouter()

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