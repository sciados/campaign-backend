"""
Intelligence Module - Refactored
"""

# Import main router (this replaces the old routes.py functionality)
from .routes import router

# Export handlers for external use if needed
from .handlers import AnalysisHandler, ContentHandler, IntelligenceHandler

# Export key utilities
from .utils import (
    ensure_intelligence_structure,
    validate_intelligence_section,
    get_analyzer
)

# Export enhancement functions directly for external use if needed
try:
    from .amplifier.enhancement import (
        identify_opportunities,
        generate_enhancements,
        create_enriched_intelligence
    )
    ENHANCEMENT_FUNCTIONS_AVAILABLE = True
except ImportError:
    ENHANCEMENT_FUNCTIONS_AVAILABLE = False
    # Create dummy functions for compatibility
    async def identify_opportunities(*args, **kwargs):
        return {"opportunity_metadata": {"total_opportunities": 0, "note": "Enhancement functions not available"}}
    
    async def generate_enhancements(*args, **kwargs):
        return {"enhancement_metadata": {"total_enhancements": 0, "note": "Enhancement functions not available"}}
    
    def create_enriched_intelligence(base_intel, enhancements):
        return base_intel

__all__ = [
    "router",
    "AnalysisHandler", 
    "ContentHandler",
    "IntelligenceHandler",
    "ensure_intelligence_structure",
    "validate_intelligence_section",
    "get_analyzer",
    "identify_opportunities",
    "generate_enhancements", 
    "create_enriched_intelligence",
    "ENHANCEMENT_FUNCTIONS_AVAILABLE"
]