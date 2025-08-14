# src/intelligence/__init__.py
"""
Intelligence Module - CORRECTED to match actual file structure
"""

# Import main router (this should work according to sitemap)
try:
    from .routes import router
    ROUTER_AVAILABLE = True
except ImportError as e:
    print(f"❌ Router import failed: {e}")
    ROUTER_AVAILABLE = False
    router = None

# Import handlers (corrected path)
try:
    from .handlers import AnalysisHandler, ContentHandler, IntelligenceHandler
    HANDLERS_AVAILABLE = True
except ImportError as e:
    print(f"❌ Handlers import failed: {e}")
    HANDLERS_AVAILABLE = False
    AnalysisHandler = None
    ContentHandler = None
    IntelligenceHandler = None

# Import utilities (according to sitemap, these exist)
try:
    from .utils.campaign_helpers import update_campaign_counters
    from .utils.enum_serializer import EnumSerializerMixin
    UTILS_AVAILABLE = True
except ImportError as e:
    print(f"❌ Utils import failed: {e}")
    UTILS_AVAILABLE = False
    # Create dummy functions only if import fails
    async def update_campaign_counters(*args, **kwargs):
        pass
    class EnumSerializerMixin:
        pass

# Enhancement functions (optional - may not exist)
try:
    from .amplifier.enhancement import (
        identify_opportunities,
        generate_enhancements,
        create_enriched_intelligence
    )
    ENHANCEMENT_FUNCTIONS_AVAILABLE = True
except ImportError:
    ENHANCEMENT_FUNCTIONS_AVAILABLE = False
    # Create dummy functions
    async def identify_opportunities(*args, **kwargs):
        return {"opportunity_metadata": {"total_opportunities": 0}}
    
    async def generate_enhancements(*args, **kwargs):
        return {"enhancement_metadata": {"total_enhancements": 0}}
    
    def create_enriched_intelligence(base_intel, enhancements):
        return base_intel

# Other utility functions that may exist
try:
    from .utils import (
        ensure_intelligence_structure,
        validate_intelligence_section,
        get_analyzer
    )
    ADVANCED_UTILS_AVAILABLE = True
except ImportError:
    ADVANCED_UTILS_AVAILABLE = False
    def ensure_intelligence_structure(*args, **kwargs):
        return {}
    def validate_intelligence_section(*args, **kwargs):
        return True
    def get_analyzer(*args, **kwargs):
        return None

__all__ = [
    "update_campaign_counters",
    "EnumSerializerMixin",
    "identify_opportunities", 
    "generate_enhancements",
    "create_enriched_intelligence",
    "ensure_intelligence_structure",
    "validate_intelligence_section",
    "get_analyzer"
]

if ROUTER_AVAILABLE:
    __all__.append("router")
if HANDLERS_AVAILABLE:
    __all__.extend(["AnalysisHandler", "ContentHandler", "IntelligenceHandler"])

# Status for main.py
INTELLIGENCE_SYSTEM_HEALTHY = ROUTER_AVAILABLE