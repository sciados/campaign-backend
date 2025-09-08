# src/intelligence/amplifier/enhancements/__init__.py
"""
AI Enhancement Modules Package
Individual AI enhancement modules for each intelligence category
"""

# Import all AI enhancement modules
try:
    from src.intelligence.amplifier.enhancements.scientific_enhancer import ScientificIntelligenceEnhancer
    from src.intelligence.amplifier.enhancements.market_enhancer import MarketIntelligenceEnhancer
    from src.intelligence.amplifier.enhancements.credibility_enhancer import CredibilityIntelligenceEnhancer
    from src.intelligence.amplifier.enhancements.content_enhancer import ContentIntelligenceEnhancer
    from src.intelligence.amplifier.enhancements.emotional_enhancer import EmotionalTransformationEnhancer
    from src.intelligence.amplifier.enhancements.authority_enhancer import ScientificAuthorityEnhancer
    
    ENHANCEMENT_MODULES_AVAILABLE = True
    
    # Make these available when importing the package
    __all__ = [
        'ScientificIntelligenceEnhancer',
        'MarketIntelligenceEnhancer',
        'CredibilityIntelligenceEnhancer',
        'ContentIntelligenceEnhancer',
        'EmotionalTransformationEnhancer',
        'ScientificAuthorityEnhancer'
    ]
    
    # Package metadata
    __version__ = "2.0.0"
    __author__ = "CampaignForge Team"
    __description__ = "Modular AI enhancement system for comprehensive intelligence generation"
    
    # Success flag for import checking
    ENHANCEMENT_MODULES_AVAILABLE = True
    
except ImportError as e:
    # Handle missing dependencies gracefully
    __all__ = []
    ENHANCEMENT_MODULES_AVAILABLE = False
    
    # Create fallback classes for each module
    class ScientificIntelligenceEnhancer:
        def __init__(self, ai_providers):
            pass
        
        async def generate_scientific_intelligence(self, product_data, base_intelligence):
            return {
                "scientific_backing": ["AI enhancement not available"],
                "enhancement_confidence": 0.5,
                "note": f"Scientific enhancement module missing: {str(e)}"
            }
    
    class MarketIntelligenceEnhancer:
        def __init__(self, ai_providers):
            pass
        
        async def generate_market_intelligence(self, product_data, base_intelligence):
            return {
                "market_analysis": {"note": "Market enhancement not available"},
                "enhancement_confidence": 0.5,
                "note": f"Market enhancement module missing: {str(e)}"
            }
    
    class CredibilityIntelligenceEnhancer:
        def __init__(self, ai_providers):
            pass
        
        async def generate_credibility_intelligence(self, product_data, base_intelligence):
            return {
                "trust_indicators": {"note": "Credibility enhancement not available"},
                "enhancement_confidence": 0.5,
                "note": f"Credibility enhancement module missing: {str(e)}"
            }
    
    class ContentIntelligenceEnhancer:
        def __init__(self, ai_providers):
            pass
        
        async def generate_content_intelligence(self, product_data, base_intelligence):
            return {
                "enhanced_key_messages": {"note": "Content enhancement not available"},
                "enhancement_confidence": 0.5,
                "note": f"Content enhancement module missing: {str(e)}"
            }
    
    class EmotionalTransformationEnhancer:
        def __init__(self, ai_providers):
            pass
        
        async def generate_emotional_transformation_intelligence(self, product_data, base_intelligence):
            return {
                "emotional_journey_mapping": {"note": "Emotional enhancement not available"},
                "enhancement_confidence": 0.5,
                "note": f"Emotional enhancement module missing: {str(e)}"
            }
    
    class ScientificAuthorityEnhancer:
        def __init__(self, ai_providers):
            pass
        
        async def generate_scientific_authority_intelligence(self, product_data, base_intelligence):
            return {
                "research_validation_framework": {"note": "Authority enhancement not available"},
                "enhancement_confidence": 0.5,
                "note": f"Authority enhancement module missing: {str(e)}"
            }

# Convenience functions
def is_enhancement_modules_available():
    """Check if all enhancement modules are available"""
    return ENHANCEMENT_MODULES_AVAILABLE

def get_enhancement_modules_status():
    """Get detailed enhancement modules status"""
    if ENHANCEMENT_MODULES_AVAILABLE:
        return {
            "available": True,
            "version": __version__,
            "modules": __all__,
            "count": len(__all__),
            "status": "fully_functional",
            "architecture": "modular_individual_enhancers"
        }
    else:
        return {
            "available": False,
            "version": None,
            "modules": [],
            "count": 0,
            "status": "dependencies_missing",
            "fallback_mode": True,
            "architecture": "fallback_stubs"
        }

def get_available_enhancers():
    """Get list of available enhancement modules"""
    if ENHANCEMENT_MODULES_AVAILABLE:
        return [
            {
                "name": "ScientificIntelligenceEnhancer",
                "focus": "Research-backed product validation and health claims",
                "generates": ["scientific_backing", "ingredient_research", "mechanism_of_action", "clinical_evidence", "safety_profile"]
            },
            {
                "name": "MarketIntelligenceEnhancer", 
                "focus": "Market analysis and competitive intelligence",
                "generates": ["market_analysis", "competitive_landscape", "pricing_analysis", "target_market_insights", "market_opportunities"]
            },
            {
                "name": "CredibilityIntelligenceEnhancer",
                "focus": "Trust indicators and authority signals",
                "generates": ["trust_indicators", "authority_signals", "social_proof_enhancement", "credibility_scoring", "reputation_factors"]
            },
            {
                "name": "ContentIntelligenceEnhancer",
                "focus": " messaging and social proof",
                "generates": ["enhanced_key_messages", "social_proof_amplification", "success_story_frameworks", "messaging_hierarchy", "engagement_optimization"]
            },
            {
                "name": "EmotionalTransformationEnhancer",
                "focus": "Customer journey and psychological triggers",
                "generates": ["emotional_journey_mapping", "psychological_triggers", "emotional_value_propositions", "transformation_narratives", "emotional_engagement_strategies"]
            },
            {
                "name": "ScientificAuthorityEnhancer",
                "focus": "Scientific credibility and professional positioning", 
                "generates": ["research_validation_framework", "professional_authority_markers", "expertise_demonstration", "thought_leadership_positioning", "scientific_credibility_framework"]
            }
        ]
    else:
        return []

# Module mapping for easy access
ENHANCEMENT_MODULE_MAP = {
    "scientific": "ScientificIntelligenceEnhancer",
    "market": "MarketIntelligenceEnhancer", 
    "credibility": "CredibilityIntelligenceEnhancer",
    "content": "ContentIntelligenceEnhancer",
    "emotional": "EmotionalTransformationEnhancer",
    "authority": "ScientificAuthorityEnhancer"
}

# Legacy support for old coordinator (if needed)
class AIIntelligenceGenerator:
    """Legacy compatibility class - redirects to modular system"""
    
    def __init__(self, ai_providers):
        self.ai_providers = ai_providers
        # Initialize all individual modules
        self.scientific_enhancer = ScientificIntelligenceEnhancer(ai_providers)
        self.market_enhancer = MarketIntelligenceEnhancer(ai_providers)
        self.credibility_enhancer = CredibilityIntelligenceEnhancer(ai_providers)
        self.content_enhancer = ContentIntelligenceEnhancer(ai_providers)
        self.emotional_enhancer = EmotionalTransformationEnhancer(ai_providers)
        self.authority_enhancer = ScientificAuthorityEnhancer(ai_providers)
    
    async def generate_complete_intelligence(self, product_data, base_intelligence, preferences=None):
        """Legacy method - now uses individual modules"""
        # This method is now handled by the refactored enhancement.py
        # Kept for backwards compatibility
        return {
            "note": "This method is now handled by the refactored enhancement.py system",
            "recommendation": "Use the individual enhancement modules directly"
        }