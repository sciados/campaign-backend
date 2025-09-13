# =====================================
# File: src/intelligence/api/intelligence_routes.py
# =====================================

"""
FastAPI routes for Intelligence Engine operations.

Provides REST API endpoints for intelligence analysis, retrieval, and management.
Enhanced with 3-step intelligence-driven content generation.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging

from src.core.database import get_async_db
from src.users.middleware.auth_middleware import AuthMiddleware
from src.core.shared.responses import SuccessResponse, PaginatedResponse
from src.core.shared.exceptions import CampaignForgeException
from src.intelligence.models.intelligence_models import IntelligenceRequest, IntelligenceResponse, AnalysisResult, AnalysisMethod
from src.intelligence.services.intelligence_service import IntelligenceService
from src.intelligence.services.intelligence_content_service import IntelligenceContentService, generate_intelligence_driven_content

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Intelligence"])
security = HTTPBearer()
intelligence_service = IntelligenceService()
intelligence_content_service = IntelligenceContentService()

# Request models for 3-step content generation
class IntelligenceContentRequest(BaseModel):
    """Request model for 3-step intelligence-driven content generation"""
    content_type: str = Field(..., description="Type of content to generate")
    campaign_id: Optional[str] = Field(None, description="Campaign context")
    company_id: Optional[str] = Field(None, description="Company context")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")

class IntelligenceContentResponse(BaseModel):
    """Response model for 3-step content generation"""
    success: bool
    content_type: str
    content: Dict[str, Any]
    intelligence_driven: bool
    three_step_process: Dict[str, Any]
    metadata: Dict[str, Any]


@router.post("/analyze", response_model=SuccessResponse[IntelligenceResponse])
async def analyze_url(
    request: IntelligenceRequest,
    credentials: HTTPBearer = Depends(security),
    session: AsyncSession = Depends(get_async_db)
):
    """
    Analyze a URL and extract intelligence.
    
    Performs AI-powered analysis of web content to extract product information,
    market data, and related research using the consolidated intelligence schema.
    """
    try:
        user_id = AuthMiddleware.require_authentication(credentials)
        
        logger.info(f"Intelligence analysis requested by user {user_id} for {request.source_url}")
        
        result = await intelligence_service.analyze_url(
            request=request,
            user_id=user_id,
            session=session
        )
        
        return SuccessResponse(
            data=result,
            message=f"Analysis completed for {request.source_url}"
        )
        
    except CampaignForgeException:
        raise
    except Exception as e:
        logger.error(f"Intelligence analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Intelligence analysis failed"
        )


@router.get("/analysis/{intelligence_id}", response_model=SuccessResponse[AnalysisResult])
async def get_intelligence(
    intelligence_id: str,
    credentials: HTTPBearer = Depends(security),
    session: AsyncSession = Depends(get_async_db)
):
    """
    Get existing intelligence analysis by ID.
    
    Retrieves a previously completed intelligence analysis including
    product information, market data, and associated research.
    """
    try:
        user_id = AuthMiddleware.require_authentication(credentials)
        
        result = await intelligence_service.get_intelligence(
            intelligence_id=intelligence_id,
            user_id=user_id,
            session=session
        )
        
        return SuccessResponse(
            data=result,
            message="Intelligence retrieved successfully"
        )
        
    except CampaignForgeException:
        raise
    except Exception as e:
        logger.error(f"Intelligence retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve intelligence"
        )


@router.get("/analysis", response_model=PaginatedResponse[AnalysisResult])
async def list_intelligence(
    analysis_method: Optional[AnalysisMethod] = Query(None, description="Filter by analysis method"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    credentials: HTTPBearer = Depends(security),
    session: AsyncSession = Depends(get_async_db)
):
    """
    List intelligence analyses for the authenticated user.
    
    Returns a paginated list of intelligence analyses with optional filtering
    by analysis method.
    """
    try:
        user_id = AuthMiddleware.require_authentication(credentials)
        
        results = await intelligence_service.list_intelligence(
            user_id=user_id,
            analysis_method=analysis_method,
            limit=limit,
            offset=offset,
            session=session
        )
        
        # For demonstration, we'll use the length of results as total
        # In production, you'd want a separate count query
        total = len(results)
        
        return PaginatedResponse(
            data=results,
            total=total,
            page=(offset // limit) + 1,
            size=limit,
            message="Intelligence list retrieved successfully"
        )
        
    except CampaignForgeException:
        raise
    except Exception as e:
        logger.error(f"Intelligence list failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve intelligence list"
        )


@router.post("/generate-content", response_model=SuccessResponse[IntelligenceContentResponse])
async def generate_intelligence_driven_content_endpoint(
    request: IntelligenceContentRequest,
    credentials: HTTPBearer = Depends(security),
    session: AsyncSession = Depends(get_async_db)
):
    """
    Generate content using 3-step intelligence-driven process.
    
    This endpoint implements the strategic 3-step process:
    1. Extract relevant data from user's intelligence database
    2. Generate optimized prompts using extracted intelligence  
    3. Route to cost-effective AI providers for content generation
    
    The process leverages your existing intelligence data to create
    highly targeted, personalized content at a fraction of the cost
    of traditional AI content generation.
    """
    try:
        user_id = AuthMiddleware.require_authentication(credentials)
        
        logger.info(f"3-step intelligence content generation requested by user {user_id}")
        logger.info(f"Content type: {request.content_type}, Campaign: {request.campaign_id}")
        
        # Generate using the 3-step service
        result = await intelligence_content_service.generate_intelligence_driven_content(
            content_type=request.content_type,
            user_id=user_id,
            company_id=request.company_id,
            campaign_id=request.campaign_id,
            preferences=request.preferences,
            session=session
        )
        
        # Convert to response model
        response_data = IntelligenceContentResponse(
            success=result.get("success", True),
            content_type=result.get("content_type"),
            content=result.get("content", {}),
            intelligence_driven=result.get("intelligence_driven", True),
            three_step_process=result.get("three_step_process", {}),
            metadata=result.get("metadata", {})
        )
        
        logger.info(f"3-step generation completed: intelligence_driven={result.get('intelligence_driven')}")
        
        return SuccessResponse(
            data=response_data,
            message="Intelligence-driven content generated successfully"
        )
        
    except CampaignForgeException:
        raise
    except Exception as e:
        logger.error(f"Intelligence content generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate intelligence-driven content"
        )


@router.get("/content-service/metrics", response_model=SuccessResponse[Dict[str, Any]])
async def get_intelligence_content_service_metrics(
    credentials: HTTPBearer = Depends(security)
):
    """
    Get metrics for the 3-step intelligence content service.
    
    Returns performance metrics including:
    - Step-by-step operation counts
    - Cost savings and optimization metrics
    - Intelligence utilization scores
    - Service performance analytics
    """
    try:
        user_id = AuthMiddleware.require_authentication(credentials)
        
        metrics = intelligence_content_service.get_service_metrics()
        
        return SuccessResponse(
            data=metrics,
            message="Service metrics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Service metrics retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve service metrics"
        )


@router.delete("/analysis/{intelligence_id}", response_model=SuccessResponse[bool])
async def delete_intelligence(
    intelligence_id: str,
    credentials: HTTPBearer = Depends(security),
    session: AsyncSession = Depends(get_async_db)
):
    """
    Delete an intelligence analysis.
    
    Permanently removes an intelligence analysis and all associated data
    including product information, market data, and research links.
    """
    try:
        user_id = AuthMiddleware.require_authentication(credentials)
        
        success = await intelligence_service.delete_intelligence(
            intelligence_id=intelligence_id,
            user_id=user_id,
            session=session
        )
        
        return SuccessResponse(
            data=success,
            message="Intelligence deleted successfully" if success else "Intelligence not found"
        )
        
    except CampaignForgeException:
        raise
    except Exception as e:
        logger.error(f"Intelligence deletion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete intelligence"
        )


@router.get("/health", response_model=SuccessResponse[dict])
async def intelligence_health():
    """
    Health check for Intelligence Engine module.
    
    Returns the health status of the Intelligence Engine including
    AI provider availability and system metrics.
    """
    try:
        from src.core.config import ai_provider_config
        
        # Check AI provider availability
        available_providers = []
        for provider_name, provider in ai_provider_config.providers.items():
            if provider.enabled:
                available_providers.append({
                    "name": provider_name,
                    "tier": provider.tier.value,
                    "cost_per_1k_tokens": provider.cost_per_1k_tokens
                })
        
        health_data = {
            "status": "healthy",
            "available_providers": available_providers,
            "total_providers": len(available_providers),
            "cheapest_provider": ai_provider_config.get_cheapest_provider().name if ai_provider_config.get_cheapest_provider() else None
        }
        
        return SuccessResponse(
            data=health_data,
            message="Intelligence Engine is healthy"
        )
        
    except Exception as e:
        logger.error(f"Intelligence health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Intelligence health check failed"
        )