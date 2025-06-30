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
    get_analyzer,
    get_amplifier_service
)

__all__ = [  # ← Fix: Double underscores, not **all**
    "router",
    "AnalysisHandler", 
    "ContentHandler",
    "IntelligenceHandler",
    "ensure_intelligence_structure",
    "validate_intelligence_section",
    "get_analyzer",
    "get_amplifier_service"
]