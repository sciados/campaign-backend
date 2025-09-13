# src/content/api/content_generation_routes.py
"""
Content Generation API Routes
Handles triggering content generation after intelligence analysis
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
import logging

from src.core.database.connection import get_async_db
from src.users.services.auth_service import AuthService
from src.content.services.content_orchestrator import create_content_orchestrator
from src.intelligence.services.intelligence_service import IntelligenceService

router = APIRouter(prefix="/api/content", tags=["content-generation"])
security = HTTPBearer()
logger = logging.getLogger(__name__)

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_db)
) -> str:
    """Get current user ID from token"""
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return str(user.id)

@router.post("/generate/{campaign_id}")
async def trigger_content_generation(
    campaign_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Trigger content generation for a campaign after intelligence analysis is complete
    
    This endpoint:
    1. Retrieves intelligence analysis results for the campaign
    2. Determines user type and subscription tier
    3. Orchestrates appropriate content generation based on user profile
    4. Returns generation job status and estimated completion times
    """
    
    try:
        logger.info(f"Starting content generation for campaign {campaign_id}, user {user_id}")
        
        # Get intelligence analysis results
        intelligence_service = IntelligenceService()
        intelligence_data = await intelligence_service.get_campaign_intelligence(
            campaign_id=campaign_id,
            user_id=user_id
        )
        
        if not intelligence_data or intelligence_data.get("status") != "complete":
            raise HTTPException(
                status_code=400, 
                detail="Intelligence analysis must be completed before content generation"
            )
        
        # Initialize content orchestrator
        orchestrator = create_content_orchestrator()
        
        # Orchestrate content generation
        generation_result = await orchestrator.orchestrate_content_generation(
            campaign_id=campaign_id,
            user_id=user_id,
            intelligence_data=intelligence_data
        )
        
        if not generation_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Content generation failed: {generation_result.get('error')}"
            )
        
        logger.info(f"Content generation orchestrated successfully for campaign {campaign_id}")
        
        return {
            "success": True,
            "message": "Content generation started successfully",
            "campaign_id": campaign_id,
            "generation_details": generation_result,
            "total_jobs": len(generation_result.get("jobs", [])),
            "estimated_completion_minutes": generation_result.get("estimated_completion_time", 0) // 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content generation trigger failed for campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger content generation: {str(e)}"
        )

@router.get("/status/{campaign_id}")
async def get_generation_status(
    campaign_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Get status of content generation jobs for a campaign"""
    
    try:
        # TODO: Implement job status tracking
        # This would query the job queue/database for current status
        
        # Placeholder implementation
        return {
            "campaign_id": campaign_id,
            "overall_status": "in_progress",  # queued, in_progress, completed, failed
            "jobs": [
                {
                    "job_id": "job_123",
                    "content_type": "email_sequence",
                    "status": "completed",
                    "progress": 100,
                    "created_at": "2024-01-15T10:30:00Z",
                    "completed_at": "2024-01-15T10:35:00Z"
                },
                {
                    "job_id": "job_124", 
                    "content_type": "social_posts",
                    "status": "in_progress",
                    "progress": 60,
                    "created_at": "2024-01-15T10:30:00Z",
                    "estimated_completion": "2024-01-15T10:40:00Z"
                }
            ],
            "completed_jobs": 1,
            "total_jobs": 2,
            "overall_progress": 80
        }
        
    except Exception as e:
        logger.error(f"Failed to get generation status for campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get generation status: {str(e)}"
        )

@router.get("/results/{campaign_id}")
async def get_generated_content(
    campaign_id: str,
    content_type: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Get generated content results for a campaign"""
    
    try:
        # TODO: Implement content retrieval from database
        
        # Placeholder implementation showing expected structure
        return {
            "campaign_id": campaign_id,
            "content": [
                {
                    "content_id": "content_123",
                    "content_type": "email_sequence",
                    "title": "7-Day Email Follow-up Sequence",
                    "status": "ready",
                    "generated_at": "2024-01-15T10:35:00Z",
                    "data": {
                        "emails": [
                            {
                                "email_number": 1,
                                "subject": "Welcome! Here's what you need to know...",
                                "body": "Email content here...",
                                "send_delay_hours": 0
                            },
                            {
                                "email_number": 2,
                                "subject": "The #1 mistake most people make...",
                                "body": "Email content here...",
                                "send_delay_hours": 24
                            }
                            # ... more emails
                        ]
                    },
                    "performance_score": 87,
                    "recommendations": [
                        "Consider A/B testing the subject line for email 2",
                        "Add more personalization tokens"
                    ]
                },
                {
                    "content_id": "content_124",
                    "content_type": "social_posts",
                    "title": "Social Media Post Collection",
                    "status": "ready", 
                    "generated_at": "2024-01-15T10:40:00Z",
                    "data": {
                        "posts": [
                            {
                                "platform": "facebook",
                                "content": "Post content here...",
                                "hashtags": ["#marketing", "#success"],
                                "optimal_posting_time": "2024-01-16T14:00:00Z"
                            }
                            # ... more posts
                        ]
                    },
                    "performance_score": 92
                }
            ],
            "total_content_pieces": 2,
            "last_updated": "2024-01-15T10:40:00Z"
        }
        
    except Exception as e:
        logger.error(f"Failed to get generated content for campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get generated content: {str(e)}"
        )

@router.post("/regenerate/{campaign_id}")
async def regenerate_content(
    campaign_id: str,
    request_data: Dict[str, Any],
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Regenerate specific content pieces with modifications
    
    Body should contain:
    {
        "content_type": "email_sequence",
        "modifications": {
            "tone": "more_casual",
            "length": "shorter",
            "focus": "benefits_over_features"
        }
    }
    """
    
    try:
        content_type = request_data.get("content_type")
        modifications = request_data.get("modifications", {})
        
        if not content_type:
            raise HTTPException(
                status_code=400,
                detail="content_type is required"
            )
        
        logger.info(f"Regenerating {content_type} for campaign {campaign_id} with modifications: {modifications}")
        
        # TODO: Implement content regeneration
        
        return {
            "success": True,
            "message": f"Regeneration of {content_type} started",
            "campaign_id": campaign_id,
            "job_id": f"regen_{campaign_id}_{content_type}",
            "estimated_completion_minutes": 3
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content regeneration failed for campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate content: {str(e)}"
        )

@router.get("/user-limits")
async def get_user_content_limits(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Get user's content generation limits and current usage"""
    
    try:
        # TODO: Implement actual limits tracking
        
        return {
            "user_id": user_id,
            "subscription_tier": "pro",
            "limits": {
                "monthly_tokens": 200000,
                "used_tokens": 45000,
                "remaining_tokens": 155000,
                "concurrent_generations": 5,
                "premium_content_enabled": True
            },
            "usage_this_month": {
                "campaigns_created": 3,
                "content_pieces_generated": 24,
                "regenerations_used": 8,
                "regenerations_limit": 50
            },
            "available_content_types": [
                "email_sequence",
                "social_posts", 
                "ad_copy",
                "blog_articles",
                "video_scripts",
                "competitor_intelligence",
                "market_analysis_report"
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get user content limits for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user limits: {str(e)}"
        )