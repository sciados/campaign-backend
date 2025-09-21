# src/campaigns/api/routes.py
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional

from src.campaigns.services.campaign_service import CampaignService
from src.campaigns.schemas.campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse, 
    CampaignListResponse, CampaignStatsResponse
)
from src.core.database.session import get_async_db
from src.core.shared.responses import success_response, error_response
from src.users.services.auth_service import AuthService

from src.core.factories.service_factory import ServiceFactory
from src.campaigns.services.enhanced_campaign_service import EnhancedCampaignService

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])
security = HTTPBearer()

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

@router.get("/", response_model=CampaignListResponse)
async def get_campaigns(
    status: Optional[str] = None,
    campaign_type: Optional[str] = None,
    sort: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Get user campaigns with optional sorting"""
    campaign_service = CampaignService(db)
    
    campaigns = await campaign_service.get_user_campaigns(
        user_id=user_id,
        status=status,
        campaign_type=campaign_type,
        skip=skip,
        limit=limit
    )
    
    # Apply sorting if requested
    if sort == "recent":
        campaigns = sorted(campaigns, key=lambda x: x.created_at, reverse=True)
    
    return CampaignListResponse(
        campaigns=[campaign.to_dict() for campaign in campaigns],
        total=len(campaigns),
        page=skip // limit + 1,
        per_page=limit
    )

@router.get("/stats", response_model=CampaignStatsResponse)
async def get_campaign_stats(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Get campaign statistics"""
    campaign_service = CampaignService(db)
    stats = await campaign_service.get_campaign_stats(user_id=user_id)
    
    return CampaignStatsResponse(**stats)

@router.get("/stats/stats")
async def get_dashboard_stats(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Get dashboard statistics (frontend compatibility endpoint)"""
    campaign_service = CampaignService(db)
    stats = await campaign_service.get_campaign_stats(user_id=user_id)
    
    # Return in format expected by frontend
    return {
        "monthly_recurring_revenue": stats.get("total_revenue", 0),
        "growth_percentage": stats.get("growth_rate", 0),
        "conversion_rate": stats.get("avg_conversion_rate", 0),
        "total_campaigns": stats.get("total_campaigns", 0),
        "active_campaigns": stats.get("active_campaigns", 0),
        "paused_campaigns": stats.get("paused_campaigns", 0),
        "testing_campaigns": stats.get("testing_campaigns", 0),
        "winning_campaigns": stats.get("winning_campaigns", 0)
    }

@router.get("/affiliate/performance")
async def get_affiliate_performance(
    days: int = 30,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Get affiliate performance metrics"""
    campaign_service = CampaignService(db)
    
    # Get affiliate-specific performance data
    stats = await campaign_service.get_campaign_stats(user_id=user_id)
    campaigns = await campaign_service.get_user_campaigns(user_id=user_id, limit=10)
    
    # Calculate affiliate-specific metrics
    total_revenue = stats.get("total_revenue", 0)
    total_campaigns = len(campaigns)
    avg_conversion = stats.get("avg_conversion_rate", 0)
    
    # Mock competitor feed for now (can be enhanced later)
    competitor_feed = [
        {
            "id": 1,
            "competitor": "CompetitorPro",
            "offer": "Health Supplement Campaign",
            "detected_change": "New landing page detected",
            "timestamp": "2024-01-15T10:30:00Z"
        },
        {
            "id": 2,
            "competitor": "AffiliateKing", 
            "offer": "Crypto Trading Course",
            "detected_change": "Ad spend increased 45%",
            "timestamp": "2024-01-15T08:15:00Z"
        }
    ]
    
    return {
        "commission_metrics": {
            "thisMonth": total_revenue,
            "growth": stats.get("growth_rate", 0),
            "epc": round(total_revenue / max(total_campaigns, 1), 2),
            "topOffer": campaigns[0].name if campaigns else "No campaigns yet"
        },
        "campaign_status": {
            "active": stats.get("active_campaigns", 0),
            "paused": stats.get("paused_campaigns", 0), 
            "testing": stats.get("testing_campaigns", 0),
            "winners": stats.get("winning_campaigns", 0)
        },
        "competitor_feed": competitor_feed
    }

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Get campaign by ID"""
    campaign_service = CampaignService(db)
    
    campaign = await campaign_service.get_campaign_by_id(
        campaign_id=campaign_id,
        user_id=user_id
    )
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return CampaignResponse(**campaign.to_dict())

@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    campaign_data: CampaignUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Update campaign"""
    campaign_service = CampaignService(db)
    
    campaign = await campaign_service.update_campaign(
        campaign_id=campaign_id,
        user_id=user_id,
        **campaign_data.dict(exclude_unset=True)
    )
    
    return CampaignResponse(**campaign.to_dict())

@router.delete("/{campaign_id}", response_model=Dict[str, Any])
async def delete_campaign(
    campaign_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Delete campaign"""
    campaign_service = CampaignService(db)
    
    success = await campaign_service.delete_campaign(
        campaign_id=campaign_id,
        user_id=user_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return success_response(message="Campaign deleted successfully")

@router.post("/")
async def create_campaign_enhanced(
    request: Dict[str, Any],
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Create campaign with optional content generation"""
    try:
        # Extract request data - use authenticated user_id
        company_id = request.get("company_id")
        name = request.get("title") or request.get("name")
        campaign_type = request.get("campaign_type", "universal")
        description = request.get("description")
        
        # Campaign form data
        target_audience = request.get("target_audience")
        goals = request.get("goals", [])
        keywords = request.get("keywords", [])
        
        # Content generation options
        auto_generate_content = request.get("auto_generate_content", False)
        content_types = request.get("content_types", [])
        
        if not all([company_id, name]):
            raise HTTPException(
                status_code=400,
                detail="company_id and name are required"
            )
        
        async with ServiceFactory.create_transactional_service(EnhancedCampaignService) as campaign_service:
            result = await campaign_service.create_campaign_with_content_generation(
                user_id=user_id,
                name=name,
                campaign_type=campaign_type,
                description=description,
                target_audience=target_audience,
                goals=goals,
                keywords=keywords,
                auto_generate_content=auto_generate_content,
                content_types=content_types,
                company_id=company_id
            )
        
        return {
            "success": True,
            "message": "Campaign created successfully",
            **result
        }
        
    except Exception as e:
        import traceback
        import logging

        logger = logging.getLogger(__name__)
        error_msg = str(e) if str(e) else f"Unknown error: {type(e).__name__}"

        logger.error(f"Campaign creation failed: {error_msg}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error traceback: {traceback.format_exc()}")
        logger.error(f"Request data: {request}")

        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/{campaign_id}/workflow", response_model=Dict[str, Any])
async def get_workflow_state(
    campaign_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Get campaign workflow state"""
    campaign_service = CampaignService(db)
    
    campaign = await campaign_service.get_campaign_by_id(
        campaign_id=campaign_id,
        user_id=user_id
    )
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return {
        "campaign_id": str(campaign.id),
        "workflow_step": campaign.workflow_step or "INITIAL",
        "is_complete": campaign.is_workflow_complete or False,
        "workflow_data": campaign.workflow_data or {}
    }

@router.get("/{campaign_id}/workflow-state", response_model=Dict[str, Any])
async def get_workflow_state_alias(
    campaign_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Get campaign workflow state (frontend compatibility alias)"""
    # Reuse the existing workflow endpoint logic
    return await get_workflow_state(campaign_id, user_id, db)

@router.get("/{campaign_id}/content", response_model=Dict[str, Any])
async def get_generated_content(
    campaign_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Get generated content for campaign"""
    campaign_service = CampaignService(db)

    campaign = await campaign_service.get_campaign_by_id(
        campaign_id=campaign_id,
        user_id=user_id
    )

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # For now, return empty content - this can be enhanced later
    return {
        "campaign_id": str(campaign.id),
        "content_items": [],
        "total_items": 0,
        "status": "pending"
    }


# ===== AFFILIATE-SPECIFIC ENDPOINTS =====

# Create affiliate router to handle /api/affiliate/* routes
affiliate_router = APIRouter(prefix="/api/affiliate", tags=["affiliate"])

@affiliate_router.get("/campaigns")
async def get_affiliate_campaigns(
    limit: int = 10,
    sort: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Get affiliate campaigns"""
    campaign_service = CampaignService(db)

    campaigns = await campaign_service.get_user_campaigns(
        user_id=user_id,
        limit=limit
    )

    # Apply sorting if requested
    if sort == "recent":
        campaigns = sorted(campaigns, key=lambda x: x.created_at, reverse=True)

    # Transform to affiliate-specific format
    affiliate_campaigns = []
    for campaign in campaigns:
        affiliate_campaigns.append({
            "id": str(campaign.id),
            "name": campaign.name,
            "product_name": campaign.name,  # Use campaign name as product name for now
            "product_creator": "Creator",  # Placeholder - can be enhanced later
            "affiliate_link": f"https://affiliate.link/{campaign.id}",  # Placeholder
            "shortened_link": f"https://cf.link/{str(campaign.id)[:8]}",  # Placeholder
            "content_type": campaign.campaign_type or "email",
            "target_audience": "General",  # Can be enhanced from campaign data
            "clicks": 0,  # Placeholder - integrate with analytics later
            "conversions": 0,  # Placeholder
            "earnings": 0,  # Placeholder
            "status": campaign.status or "active",
            "created_at": campaign.created_at.isoformat() if campaign.created_at else "",
            "last_updated": campaign.updated_at.isoformat() if campaign.updated_at else ""
        })

    return {
        "campaigns": affiliate_campaigns,
        "total": len(affiliate_campaigns)
    }

@affiliate_router.post("/campaigns")
async def create_affiliate_campaign(
    campaign_data: Dict[str, Any],
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Create affiliate campaign"""
    campaign_service = CampaignService(db)

    # Extract affiliate-specific data
    name = campaign_data.get("name")
    product_id = campaign_data.get("product_id")
    content_type = campaign_data.get("content_type", "email")
    target_audience = campaign_data.get("target_audience", "")
    affiliate_link = campaign_data.get("affiliate_link")

    if not name or not affiliate_link:
        raise HTTPException(status_code=400, detail="Name and affiliate_link are required")

    # Create campaign using existing service
    campaign_data_formatted = {
        "name": name,
        "campaign_type": content_type,
        "description": f"Affiliate campaign for {name}",
        "target_audience": target_audience,
        "company_id": "default",  # Will need to get from user context
        "affiliate_link": affiliate_link,
        "product_id": product_id
    }

    try:
        # Use the existing enhanced campaign creation logic
        async with ServiceFactory.create_transactional_service(EnhancedCampaignService) as enhanced_service:
            result = await enhanced_service.create_campaign_with_content_generation(
                user_id=user_id,
                name=name,
                campaign_type=content_type,
                description=campaign_data_formatted["description"],
                target_audience=target_audience,
                goals=[],
                keywords=[],
                auto_generate_content=False,
                content_types=[content_type],
                company_id=campaign_data_formatted["company_id"]
            )

        return {
            "id": result.get("campaign_id"),
            "name": name,
            "status": "active",
            "message": "Campaign created successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create campaign: {str(e)}")

@affiliate_router.patch("/campaigns/{campaign_id}/status")
async def update_affiliate_campaign_status(
    campaign_id: str,
    status_data: Dict[str, Any],
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Update affiliate campaign status"""
    campaign_service = CampaignService(db)

    new_status = status_data.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Status is required")

    campaign = await campaign_service.update_campaign(
        campaign_id=campaign_id,
        user_id=user_id,
        status=new_status
    )

    return {
        "id": str(campaign.id),
        "status": campaign.status,
        "message": f"Campaign status updated to {new_status}"
    }

