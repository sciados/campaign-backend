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
from src.core.database.connection import get_async_db
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
    skip: int = 0,
    limit: int = 100,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Get user campaigns"""
    campaign_service = CampaignService(db)
    
    campaigns = await campaign_service.get_user_campaigns(
        user_id=user_id,
        status=status,
        campaign_type=campaign_type,
        skip=skip,
        limit=limit
    )
    
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
async def create_campaign_enhanced(request: Dict[str, Any]):
    """Create campaign with optional content generation"""
    try:
        # Extract request data
        user_id = request.get("user_id")
        company_id = request.get("company_id")
        name = request.get("title") or request.get("name")
        campaign_type = request.get("campaign_type", "universal")
        description = request.get("description")
        
        # Content generation options
        auto_generate_content = request.get("auto_generate_content", False)
        content_types = request.get("content_types", [])
        
        if not all([user_id, company_id, name]):
            raise HTTPException(
                status_code=400,
                detail="user_id, company_id, and name are required"
            )
        
        async with ServiceFactory.create_transactional_service(EnhancedCampaignService) as campaign_service:
            result = await campaign_service.create_campaign_with_content_generation(
                user_id=user_id,
                name=name,
                campaign_type=campaign_type,
                description=description,
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
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{campaign_id}")
async def get_campaign_with_content(
    campaign_id: UUID,
    company_id: str,
    include_content: bool = True
):
    """Get campaign with associated content"""
    try:
        async with ServiceFactory.create_service(EnhancedCampaignService) as campaign_service:
            result = await campaign_service.get_campaign_with_content(
                campaign_id=campaign_id,
                company_id=company_id,
                include_content=include_content
            )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))