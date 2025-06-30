"""
File: src/intelligence/routers/management_routes.py
Management Routes - Intelligence data management endpoints
Extracted from main routes.py for better organization
"""
from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.models.user import User
from src.models.campaign import Campaign
from src.models.intelligence import CampaignIntelligence, GeneratedContent
from ..handlers.intelligence_handler import IntelligenceHandler

router = APIRouter()

@router.get("/{campaign_id}/intelligence")
async def get_campaign_intelligence(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all intelligence sources for a campaign with proper error handling"""
    
    handler = IntelligenceHandler(db, current_user)
    
    try:
        result = await handler.get_campaign_intelligence(campaign_id)
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        # Always return a valid response to prevent infinite loading
        return {
            "campaign_id": campaign_id,
            "intelligence_sources": [],
            "generated_content": [],
            "summary": {
                "total_intelligence_sources": 0,
                "total_generated_content": 0,
                "avg_confidence_score": 0.0,
                "amplification_summary": {
                    "sources_amplified": 0,
                    "sources_available_for_amplification": 0,
                    "total_scientific_enhancements": 0,
                    "amplification_available": False,
                    "amplification_coverage": "0/0"
                }
            },
            "error": "Failed to load intelligence data",
            "fallback_response": True
        }

@router.delete("/{campaign_id}/intelligence/{intelligence_id}")
async def delete_intelligence_source(
    campaign_id: str,
    intelligence_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an intelligence source"""
    
    handler = IntelligenceHandler(db, current_user)
    
    try:
        result = await handler.delete_intelligence_source(campaign_id, intelligence_id)
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete intelligence source: {str(e)}"
        )

@router.post("/{campaign_id}/intelligence/{intelligence_id}/amplify")
async def amplify_intelligence_source(
    campaign_id: str,
    intelligence_id: str,
    amplification_preferences: dict = {},
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Amplify an existing intelligence source"""
    
    handler = IntelligenceHandler(db, current_user)
    
    try:
        result = await handler.amplify_intelligence_source(
            campaign_id, intelligence_id, amplification_preferences
        )
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to amplify intelligence source: {str(e)}"
        )

@router.get("/{campaign_id}/statistics")
async def get_campaign_statistics(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed statistics for a campaign's intelligence and content"""
    
    handler = IntelligenceHandler(db, current_user)
    
    try:
        result = await handler.get_campaign_statistics(campaign_id)
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign statistics: {str(e)}"
        )

@router.post("/{campaign_id}/export")
async def export_campaign_data(
    campaign_id: str,
    export_format: str = "json",
    include_content: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export campaign intelligence and content data"""
    
    handler = IntelligenceHandler(db, current_user)
    
    try:
        result = await handler.export_campaign_data(
            campaign_id, export_format, include_content
        )
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export campaign data: {str(e)}"
        )