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

router = APIRouter()

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
    from ..utils.amplifier_service import get_amplifier_status
    
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
        ]
    }