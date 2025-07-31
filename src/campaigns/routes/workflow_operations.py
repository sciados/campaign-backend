"""
Workflow Operations Routes - Workflow and intelligence operations
Extracted from main routes.py for better organization
🔧 CRITICAL FIX: Corrected service method calls and parameter passing
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
        workflow_service = WorkflowService(db)
        
        # 🔧 CRITICAL FIX: Use correct method with proper parameters
        workflow_data = await workflow_service.get_workflow_state(
            campaign_id, 
            current_user.company_id  # Pass UUID directly
        )
        
        if not workflow_data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
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
        
        # Initialize service
        workflow_service = WorkflowService(db)
        
        # 🔧 CRITICAL FIX: Use correct method with proper parameters
        result = await workflow_service.save_workflow_progress(
            campaign_id,
            current_user.company_id,  # Pass UUID directly
            progress_data
        )
        
        if not result:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
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
        # Initialize service
        workflow_service = WorkflowService(db)
        
        # 🔧 CRITICAL FIX: Use get_workflow_state since get_analysis_progress doesn't exist
        # The workflow state contains all the analysis progress information
        workflow_data = await workflow_service.get_workflow_state(
            campaign_id,
            current_user.company_id  # Pass UUID directly
        )
        
        if not workflow_data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Extract analysis-specific progress data
        analysis_progress = {
            "campaign_id": workflow_data["campaign_id"],
            "auto_analysis": workflow_data["auto_analysis"],
            "completion_percentage": workflow_data["completion_percentage"],
            "current_step": workflow_data["current_step"],
            "total_steps": workflow_data["total_steps"],
            "can_analyze": workflow_data["can_analyze"],
            "can_generate_content": workflow_data["can_generate_content"],
            "next_steps": workflow_data["next_steps"],
            "metrics": workflow_data["metrics"]
        }
        
        return analysis_progress
        
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
        
        # Initialize service
        workflow_service = WorkflowService(db)
        
        # 🔧 CRITICAL FIX: Use correct method with proper parameters
        intelligence_data = await workflow_service.get_campaign_intelligence(
            campaign_id, 
            current_user.company_id,  # Pass UUID directly
            skip, 
            limit, 
            intelligence_type
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