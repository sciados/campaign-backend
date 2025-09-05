"""
Intelligence Engine Module

Provides AI-powered analysis, content enhancement, and research capabilities
using the consolidated intelligence schema and modular architecture.
"""

from .services.intelligence_service import IntelligenceService
from .services.analysis_service import AnalysisService
from .services.enhancement_service import EnhancementService
from .models.intelligence_models import IntelligenceRequest, IntelligenceResponse
from .api.intelligence_routes import router as intelligence_router

__version__ = "2.0.0"
__all__ = [
    "IntelligenceService",
    "AnalysisService", 
    "EnhancementService",
    "IntelligenceRequest",
    "IntelligenceResponse",
    "intelligence_router",
]