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
from src.intelligence.services.product_detection_service import product_detection_service

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
        
        logger.info(f"Intelligence analysis requested by user {user_id} for {request.salespage_url}")
        
        result = await intelligence_service.analyze_url(
            request=request,
            user_id=user_id,
            session=session
        )
        
        return SuccessResponse(
            data=result,
            message=f"Analysis completed for {request.salespage_url}"
        )
        
    except CampaignForgeException:
        raise
    except Exception as e:
        logger.error(f"Intelligence analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Intelligence analysis failed"
        )

@router.post("/analyze-with-product-detection", response_model=SuccessResponse[Dict[str, Any]])
async def analyze_url_with_product_detection(
    request: IntelligenceRequest,
    campaign_id: Optional[str] = Body(None, description="Campaign ID for automatic product linking"),
    credentials: HTTPBearer = Depends(security),
    session: AsyncSession = Depends(get_async_db)
):
    """
    Analyze a URL and automatically detect and link products to campaigns.

    Enhanced URL analysis that identifies products from sales pages and
    automatically establishes Campaign → Product → Creator relationships.
    """
    try:
        user_id = AuthMiddleware.require_authentication(credentials)

        logger.info(f"Enhanced analysis with product detection requested by user {user_id} for {request.salespage_url}")

        # Perform standard intelligence analysis
        intelligence_result = await intelligence_service.analyze_url(
            request=request,
            user_id=user_id,
            session=session
        )

        # If campaign_id provided, attempt smart product detection and linking
        product_detection_result = None
        if campaign_id:
            product_detection_result = await product_detection_service.detect_and_link_product_from_url(
                salespage_url=request.salespage_url,
                campaign_id=campaign_id,
                user_id=user_id,
                intelligence_result=intelligence_result.model_dump() if hasattr(intelligence_result, 'model_dump') else intelligence_result
            )

            logger.info(f"Product detection result for campaign {campaign_id}: {product_detection_result.get('status', 'unknown')}")

        # Combine results
        enhanced_result = {
            "intelligence_analysis": intelligence_result,
            "product_detection": product_detection_result,
            "campaign_id": campaign_id,
            "enhanced_analysis": True
        }

        return SuccessResponse(
            data=enhanced_result,
            message=f"Enhanced analysis completed for {request.salespage_url}"
        )

    except CampaignForgeException:
        raise
    except Exception as e:
        logger.error(f"Enhanced intelligence analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Enhanced intelligence analysis failed"
        )

@router.post("/link-campaign-to-product", response_model=SuccessResponse[Dict[str, Any]])
async def link_campaign_to_product(
    campaign_id: str = Body(..., description="Campaign ID"),
    product_source: str = Body(..., description="Source of product: 'content_library' or 'manual'"),
    product_id: Optional[str] = Body(None, description="Product ID from content library"),
    platform: Optional[str] = Body(None, description="Platform (for manual linking)"),
    product_sku: Optional[str] = Body(None, description="Product SKU (for manual linking)"),
    product_name: Optional[str] = Body(None, description="Product name (for manual linking)"),
    creator_user_id: Optional[str] = Body(None, description="Creator user ID (for manual linking)"),
    credentials: HTTPBearer = Depends(security),
    session: AsyncSession = Depends(get_async_db)
):
    """
    Link a campaign to a product via content library selection or manual input.

    Supports both content library selection and manual product specification
    for establishing Campaign → Product → Creator relationships.
    """
    try:
        user_id = AuthMiddleware.require_authentication(credentials)

        logger.info(f"Product linking requested by user {user_id} for campaign {campaign_id} via {product_source}")

        if product_source == "content_library":
            if not product_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="product_id required for content_library source"
                )

            result = await product_detection_service.link_campaign_to_content_library_product(
                campaign_id=campaign_id,
                content_library_product_id=product_id,
                user_id=user_id
            )

        elif product_source == "manual":
            if not all([platform, product_sku, product_name, creator_user_id]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="platform, product_sku, product_name, and creator_user_id required for manual linking"
                )

            from src.intelligence.services.campaign_product_analytics_service import campaign_product_analytics_service

            result = await campaign_product_analytics_service.link_campaign_to_product(
                campaign_id=campaign_id,
                platform=platform,
                product_sku=product_sku,
                product_name=product_name,
                creator_user_id=creator_user_id
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="product_source must be 'content_library' or 'manual'"
            )

        return SuccessResponse(
            data=result,
            message=f"Campaign {campaign_id} linked to product via {product_source}"
        )

    except CampaignForgeException:
        raise
    except Exception as e:
        logger.error(f"Campaign product linking failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Campaign product linking failed"
        )

@router.post("/check-product-in-library", response_model=SuccessResponse[Dict[str, Any]])
async def check_product_in_library(
    salespage_url: str = Body(..., description="Sales page URL to check"),
    campaign_id: Optional[str] = Body(None, description="Campaign ID for linking if product exists"),
    credentials: HTTPBearer = Depends(security),
    session: AsyncSession = Depends(get_async_db)
):
    """
    Check if a product exists in the library by URL.

    If product exists and campaign_id provided, automatically link them.
    If product doesn't exist, return analysis_required status.
    """
    try:
        user_id = AuthMiddleware.require_authentication(credentials)

        logger.info(f"Library check requested by user {user_id} for URL: {salespage_url}")

        # Use the smart detection with no intelligence result to just check library
        result = await product_detection_service.detect_and_link_product_from_url(
            salespage_url=salespage_url,
            campaign_id=campaign_id,
            user_id=user_id,
            intelligence_result=None  # No analysis provided - just check library
        )

        # Determine if analysis is needed
        analysis_needed = result.get("status") == "analysis_required"

        return SuccessResponse(
            data={
                "library_check_result": result,
                "analysis_needed": analysis_needed,
                "product_exists_in_library": not analysis_needed,
                "salespage_url": salespage_url
            },
            message="Library check completed"
        )

    except CampaignForgeException:
        raise
    except Exception as e:
        logger.error(f"Library check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Library check failed"
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


# Admin routes are included separately in main.py under /api/admin/intelligence

# Value Attribution Routes
@router.post("/track-campaign-usage", response_model=SuccessResponse[Dict[str, Any]])
async def track_campaign_usage(
    campaign_id: str = Body(..., description="Campaign ID"),
    affiliate_user_id: str = Body(..., description="Affiliate user ID"),
    product_sku: str = Body(..., description="Product SKU"),
    platform: str = Body(..., description="Platform name"),
    content_types_used: List[str] = Body(..., description="Content types used"),
    ai_features_used: List[str] = Body(..., description="AI features used"),
    credentials: HTTPBearer = Depends(security)
):
    """
    Track CampaignForge usage for value attribution.

    Records when affiliates use CampaignForge features for specific products,
    enabling measurement of platform effectiveness and value delivery.
    """
    try:
        user_id = AuthMiddleware.require_authentication(credentials)

        from src.intelligence.services.campaignforge_value_attribution_service import campaignforge_value_attribution_service

        result = await campaignforge_value_attribution_service.track_campaign_usage(
            campaign_id=campaign_id,
            affiliate_user_id=affiliate_user_id,
            product_sku=product_sku,
            platform=platform,
            content_types_used=content_types_used,
            ai_features_used=ai_features_used
        )

        return SuccessResponse(
            data=result,
            message="CampaignForge usage tracked successfully"
        )

    except CampaignForgeException:
        raise
    except Exception as e:
        logger.error(f"Campaign usage tracking failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track campaign usage"
        )

@router.post("/track-performance-attribution", response_model=SuccessResponse[Dict[str, Any]])
async def track_performance_attribution(
    campaign_id: str = Body(..., description="Campaign ID"),
    performance_metrics: Dict[str, Any] = Body(..., description="Performance metrics"),
    attribution_markers: Dict[str, Any] = Body(..., description="Attribution confidence markers"),
    credentials: HTTPBearer = Depends(security)
):
    """
    Track performance that can be attributed to CampaignForge platform.

    Records performance metrics with attribution confidence to measure
    the specific impact of CampaignForge features on campaign success.
    """
    try:
        user_id = AuthMiddleware.require_authentication(credentials)

        from src.intelligence.services.campaignforge_value_attribution_service import campaignforge_value_attribution_service

        result = await campaignforge_value_attribution_service.track_performance_attribution(
            campaign_id=campaign_id,
            performance_metrics=performance_metrics,
            attribution_markers=attribution_markers
        )

        return SuccessResponse(
            data=result,
            message="Performance attribution tracked successfully"
        )

    except CampaignForgeException:
        raise
    except Exception as e:
        logger.error(f"Performance attribution tracking failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track performance attribution"
        )

@router.get("/creator-value-report/{creator_user_id}", response_model=SuccessResponse[Dict[str, Any]])
async def get_creator_value_report(
    creator_user_id: str,
    days: int = Query(30, description="Number of days for the report period"),
    credentials: HTTPBearer = Depends(security)
):
    """
    Generate CampaignForge value report for a product creator.

    Shows how CampaignForge is benefiting the creator through:
    - Platform adoption metrics
    - AI feature utilization
    - Attributed performance data
    - Value indicators and confidence scores
    """
    try:
        user_id = AuthMiddleware.require_authentication(credentials)

        from src.intelligence.services.campaignforge_value_attribution_service import campaignforge_value_attribution_service

        result = await campaignforge_value_attribution_service.generate_creator_value_report(
            creator_user_id=creator_user_id,
            days=days
        )

        return SuccessResponse(
            data=result,
            message=f"Creator value report generated for {days} days"
        )

    except CampaignForgeException:
        raise
    except Exception as e:
        logger.error(f"Creator value report generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate creator value report"
        )

@router.get("/platform-effectiveness-metrics/{creator_user_id}", response_model=SuccessResponse[Dict[str, Any]])
async def get_platform_effectiveness_metrics(
    creator_user_id: str,
    credentials: HTTPBearer = Depends(security)
):
    """
    Get CampaignForge platform effectiveness metrics for a creator.

    Returns detailed analytics on how effectively the CampaignForge platform
    is being utilized for the creator's products, including adoption trends
    and feature usage patterns.
    """
    try:
        user_id = AuthMiddleware.require_authentication(credentials)

        from src.intelligence.services.campaignforge_value_attribution_service import campaignforge_value_attribution_service

        result = await campaignforge_value_attribution_service.get_platform_effectiveness_metrics(
            creator_user_id=creator_user_id
        )

        return SuccessResponse(
            data=result,
            message="Platform effectiveness metrics retrieved successfully"
        )

    except CampaignForgeException:
        raise
    except Exception as e:
        logger.error(f"Platform effectiveness metrics retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve platform effectiveness metrics"
        )


@router.get("/campaigns/{campaign_id}", response_model=SuccessResponse[List[Dict[str, Any]]])
async def get_campaign_intelligence(
    campaign_id: str,
    credentials: HTTPBearer = Depends(security)
):
    """Get intelligence data for a specific campaign"""
    try:
        user_id = AuthMiddleware.require_authentication(credentials)

        from src.intelligence.services.intelligence_service import IntelligenceService

        intelligence_service = IntelligenceService()

        # Get intelligence data linked to this campaign
        intelligence_data = await intelligence_service.get_campaign_intelligence(campaign_id, user_id)

        return SuccessResponse(
            data=intelligence_data,
            message="Campaign intelligence retrieved successfully"
        )

    except CampaignForgeException:
        raise
    except Exception as e:
        logger.error(f"Failed to get campaign intelligence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve campaign intelligence"
        )


@router.get("/progress/{analysis_id}", response_model=SuccessResponse[Dict[str, Any]])
async def get_analysis_progress(
    analysis_id: str,
    credentials: HTTPBearer = Depends(security)
):
    """
    Get real-time progress of an ongoing intelligence analysis.

    Returns current stage, progress percentage, and status message
    for the MAXIMUM analysis pipeline including internet search RAG.
    """
    try:
        user_id = AuthMiddleware.require_authentication(credentials)

        # Get real progress from the intelligence service
        progress_data = intelligence_service.get_analysis_progress(analysis_id)

        # If analysis not found, return not found status
        if progress_data.get("stage") == "not_found":
            return SuccessResponse(
                data={
                    "analysis_id": analysis_id,
                    "stage": "not_found",
                    "progress": 0,
                    "message": "Analysis not found",
                    "completed": False
                },
                message="Analysis not found"
            )

        # Add analysis_id to response
        progress_data["analysis_id"] = analysis_id

        return SuccessResponse(
            data=progress_data,
            message="Analysis progress retrieved successfully"
        )

    except CampaignForgeException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analysis progress"
        )


# Include ClickBank routes
try:
    from src.intelligence.routes.routes_clickbank import router as clickbank_router
    router.include_router(clickbank_router)
    logger.info("ClickBank routes included successfully")
except ImportError as e:
    logger.warning(f"Could not import ClickBank routes: {e}")