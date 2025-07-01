"""
File: src/intelligence/routers/analysis_routes.py
Analysis Routes - URL analysis endpoints
Extracted from main routes.py for better organization
"""
from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.models.user import User
from ..handlers.analysis_handler import AnalysisHandler
from ..schemas.requests import AnalyzeURLRequest
from ..schemas.responses import AnalysisResponse

# Check credits availability
try:
    from src.core.credits import check_and_consume_credits
    CREDITS_AVAILABLE = True
except ImportError:
    CREDITS_AVAILABLE = False
    async def check_and_consume_credits(*args, **kwargs):
        pass

# Check if enhancement functions are available
try:
    from ..amplifier.enhancement import (
        identify_opportunities,
        generate_enhancements,
        create_enriched_intelligence
    )
    ENHANCEMENT_FUNCTIONS_AVAILABLE = True
except ImportError:
    ENHANCEMENT_FUNCTIONS_AVAILABLE = False

router = APIRouter()

def get_amplifier_status():
    """Get amplifier system status"""
    if not ENHANCEMENT_FUNCTIONS_AVAILABLE:
        return {
            "status": "unavailable",
            "available": False,
            "error": "Enhancement dependencies not installed",
            "capabilities": {},
            "recommendations": [
                "Install amplifier dependencies",
                "Check amplifier package configuration"
            ]
        }
    
    return {
        "status": "available",
        "available": True,
        "capabilities": {
            "direct_enhancement_functions": True,
            "scientific_enhancement": True,
            "credibility_boost": True,
            "competitive_analysis": True,
            "content_optimization": True
        },
        "architecture": "direct_modular_enhancement",
        "functions_available": [
            "identify_opportunities",
            "generate_enhancements", 
            "create_enriched_intelligence"
        ]
    }

@router.post("/url", response_model=AnalysisResponse)
async def analyze_url(
    request: AnalyzeURLRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Analyze competitor sales page with amplifier integration"""
    
    # Check credits if system is available
    if CREDITS_AVAILABLE:
        try:
            await check_and_consume_credits(
                user=current_user,
                operation="intelligence_analysis",
                credits_required=5,
                db=db
            )
        except Exception as e:
            raise HTTPException(
                status_code=http_status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits: {str(e)}"
            )
    
    # Create handler and process request
    handler = AnalysisHandler(db, current_user)
    
    try:
        result = await handler.analyze_url({
            "url": str(request.url),
            "campaign_id": request.campaign_id,
            "analysis_type": request.analysis_type
        })
        
        return AnalysisResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@router.get("/status")
async def get_analysis_status(
    current_user: User = Depends(get_current_user)
):
    """Get analysis system status"""
    from ..utils.analyzer_factory import test_analyzer_functionality, get_available_analyzers
    
    analyzer_status = test_analyzer_functionality()
    available_analyzers = get_available_analyzers()
    amplifier_status = get_amplifier_status()
    
    return {
        "analysis_system": {
            "status": analyzer_status["overall_status"],
            "analyzers_available": analyzer_status["analyzers_available"],
            "successful_analyzers": analyzer_status.get("successful_analyzers", 0),
            "total_analyzers": analyzer_status.get("total_analyzers", 0)
        },
        "available_analyzers": available_analyzers,
        "amplifier_status": amplifier_status,
        "credits_system": {
            "available": CREDITS_AVAILABLE,
            "cost_per_analysis": 5
        }
    }

@router.get("/capabilities")
async def get_analysis_capabilities(
    current_user: User = Depends(get_current_user)
):
    """Get detailed analysis capabilities"""
    from ..utils.analyzer_factory import get_available_analyzers, get_analyzer_requirements
    
    return {
        "available_analyzers": get_available_analyzers(),
        "system_requirements": get_analyzer_requirements(),
        "supported_analysis_types": [
            "sales_page",
            "website", 
            "document",
            "enhanced_sales_page",
            "vsl"
        ],
        "supported_formats": [
            "URL",
            "HTML",
            "PDF",
            "DOC",
            "TXT"
        ],
        "enhancement_system": {
            "available": ENHANCEMENT_FUNCTIONS_AVAILABLE,
            "architecture": "direct_modular_enhancement" if ENHANCEMENT_FUNCTIONS_AVAILABLE else "not_available",
            "functions": [
                "identify_opportunities",
                "generate_enhancements", 
                "create_enriched_intelligence"
            ] if ENHANCEMENT_FUNCTIONS_AVAILABLE else []
        }
    }