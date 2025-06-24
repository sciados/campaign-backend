# src/intelligence/amplifier/__init__.py
"""
Intelligence Amplifier Package
Provides enhanced intelligence processing with scientific backing and competitive analysis
"""

# Import main classes for easy access
try:
    from .service import IntelligenceAmplificationService
    from .core import IntelligenceAmplifier
    from .enhancement import identify_opportunities, generate_enhancements, create_enriched_intelligence
    
    # Make these available when importing the package
    __all__ = [
        'IntelligenceAmplificationService',
        'IntelligenceAmplifier', 
        'identify_opportunities',
        'generate_enhancements',
        'create_enriched_intelligence'
    ]
    
    # Package metadata
    __version__ = "1.0.0"
    __author__ = "CampaignForge Team"
    __description__ = "Intelligence amplification system for enhanced competitive analysis"
    
    # Success flag for import checking
    AMPLIFIER_PACKAGE_AVAILABLE = True
    
except ImportError as e:
    # Handle missing dependencies gracefully
    __all__ = []
    AMPLIFIER_PACKAGE_AVAILABLE = False
    
    # Create fallback classes
    class IntelligenceAmplificationService:
        def __init__(self):
            pass
        
        async def process_sources(self, sources, preferences=None):
            return {
                "intelligence_data": sources[0] if sources else {},
                "summary": {
                    "total": len(sources) if sources else 0,
                    "successful": 0,
                    "note": f"Amplifier dependencies missing: {str(e)}"
                }
            }
    
    class IntelligenceAmplifier:
        def __init__(self):
            pass
    
    def identify_opportunities(*args, **kwargs):
        return {"note": "Amplifier not available"}
    
    def generate_enhancements(*args, **kwargs):
        return {"note": "Amplifier not available"}
    
    def create_enriched_intelligence(*args, **kwargs):
        return {}

# Convenience function to check if amplifier is working
def is_amplifier_available():
    """Check if the amplifier system is fully functional"""
    return AMPLIFIER_PACKAGE_AVAILABLE

# Convenience function to get amplifier status
def get_amplifier_status():
    """Get detailed amplifier system status"""
    if AMPLIFIER_PACKAGE_AVAILABLE:
        return {
            "available": True,
            "version": __version__,
            "components": __all__,
            "status": "fully_functional"
        }
    else:
        return {
            "available": False,
            "version": None,
            "components": [],
            "status": "dependencies_missing",
            "fallback_mode": True
        }