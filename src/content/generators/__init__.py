# src/intelligence/__init__.py
"""
Intelligence Engine Module

Provides AI-powered analysis, content enhancement, and research capabilities
using the consolidated intelligence schema and modular architecture.
"""

from src.intelligence.services.intelligence_service import IntelligenceService
from src.intelligence.services.analysis_service import AnalysisService
from src.intelligence.services.enhancement_service import EnhancementService
from src.intelligence.models.intelligence_models import IntelligenceRequest, IntelligenceResponse
from src.intelligence.api.intelligence_routes import router as intelligence_router
from src.intelligence.intelligence_module import IntelligenceModule
from src.intelligence.analysis.enhanced_handler import EnhancedAnalysisHandler

__version__ = "2.0.0"
__all__ = [
    "IntelligenceService",
    "AnalysisService", 
    "EnhancementService",
    "IntelligenceRequest",
    "IntelligenceResponse",
    "intelligence_router",
    "IntelligenceModule",
    "EnhancedAnalysisHandler"    
]