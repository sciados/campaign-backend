# =====================================
# File: src/intelligence/services/__init__.py
# =====================================

"""
Intelligence Engine services for business logic.

Provides service layer implementations for intelligence analysis,
enhancement, and research operations.
"""

from src.intelligence.services.intelligence_service import IntelligenceService
from src.intelligence.services.analysis_service import AnalysisService
from src.intelligence.services.enhancement_service import EnhancementService

# Import the clickbank_service module directly to make it available for import
try:
    from . import clickbank_service
    CLICKBANK_AVAILABLE = True
except ImportError:
    CLICKBANK_AVAILABLE = False

__all__ = [
    "IntelligenceService",
    "AnalysisService",
    "EnhancementService",
]

if CLICKBANK_AVAILABLE:
    __all__.append("clickbank_service")