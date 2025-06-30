# src/intelligence/__init__.py
"""
Intelligence Package - Core analysis and generation capabilities
"""

import logging

logger = logging.getLogger(__name__)

# Package metadata
__version__ = "1.0.0"
__author__ = "CampaignForge Team" 
__description__ = "Comprehensive intelligence analysis and content generation system"

# ============================================================================
# CORE ANALYZERS IMPORT
# ============================================================================

try:
    from .analyzers import (
        SalesPageAnalyzer,
        DocumentAnalyzer,
        WebAnalyzer, 
        EnhancedSalesPageAnalyzer,
        VSLAnalyzer
    )
    ANALYZERS_AVAILABLE = True
    logger.info("✅ SUCCESS: Core analyzers imported successfully")
    
except ImportError as e:
    logger.error(f"❌ CRITICAL: Core analyzers import failed: {str(e)}")
    ANALYZERS_AVAILABLE = False
    
    # Fallback analyzer classes
    class SalesPageAnalyzer:
        async def analyze(self, url: str):
            return {
                "error": f"Analyzer dependencies missing: {str(e)}",
                "confidence_score": 0.0,
                "offer_intelligence": {"products": [], "pricing": [], "bonuses": [], "guarantees": [], "value_propositions": []},
                "psychology_intelligence": {"emotional_triggers": [], "pain_points": [], "target_audience": "Unknown", "persuasion_techniques": []},
                "competitive_intelligence": {"opportunities": [], "gaps": [], "positioning": "Unknown", "advantages": [], "weaknesses": []},
                "content_intelligence": {"key_messages": [], "success_stories": [], "social_proof": [], "content_structure": "Analysis failed"},
                "brand_intelligence": {"tone_voice": "Unknown", "messaging_style": "Unknown", "brand_positioning": "Unknown"},
                "campaign_suggestions": ["Install missing dependencies: aiohttp, beautifulsoup4, lxml", "Check server logs for import errors"],
                "source_url": url,
                "page_title": "Analysis Failed - Dependencies Missing",
                "product_name": "Unknown",
                "raw_content": "",
                "analysis_note": f"Missing dependencies: {str(e)}"
            }
    
    class DocumentAnalyzer:
        async def analyze_document(self, content: bytes, extension: str):
            return {"error": "Document analyzer dependencies missing"}
    
    class WebAnalyzer:
        async def analyze(self, url: str):
            return {"error": "Web analyzer dependencies missing", "confidence_score": 0.0}
    
    class EnhancedSalesPageAnalyzer:
        async def analyze_enhanced(self, url: str, **kwargs):
            return {"error": "Enhanced analyzer dependencies missing", "confidence_score": 0.0}
    
    class VSLAnalyzer:
        async def detect_vsl(self, url: str):
            return {"error": "VSL analyzer dependencies missing"}
        
        async def analyze_vsl(self, url: str, campaign_id: str, extract_transcript: bool = True):
            return {"error": "VSL analyzer dependencies missing"}

# ============================================================================
# EXTRACTORS IMPORT  
# ============================================================================

try:
    from .extractors import (
        ProductNameExtractor,
        extract_product_name,
        EXTRACTORS_AVAILABLE
    )
    if EXTRACTORS_AVAILABLE:
        logger.info("✅ SUCCESS: Product extractors imported successfully")
    else:
        logger.warning("⚠️ WARNING: Product extractors using fallback mode")
        
except ImportError as e:
    logger.warning(f"⚠️ WARNING: Product extractors import failed: {str(e)}")
    
    # Fallback extractor classes
    class ProductNameExtractor:
        def extract_product_name(self, content: str, title: str = None):
            return "Product"
    
    def extract_product_name(content: str, title: str = None):
        return "Product"
    
    EXTRACTORS_AVAILABLE = False

# ============================================================================
# GENERATORS IMPORT
# ============================================================================

try:
    from .generators import (
        EmailSequenceGenerator,
        CampaignAngleGenerator,
        SocialMediaGenerator,
        AdCopyGenerator,
        BlogPostGenerator,
        LandingPageGenerator,
        VideoScriptGenerator,
        ContentGeneratorFactory,
        GENERATORS_AVAILABLE,
        get_available_generators
    )
    
    available_count = sum(1 for available in GENERATORS_AVAILABLE.values() if available)
    total_count = len(GENERATORS_AVAILABLE)
    
    if available_count == total_count:
        logger.info(f"✅ SUCCESS: All {total_count} content generators imported successfully")
    elif available_count > 0:
        logger.info(f"✅ PARTIAL: {available_count}/{total_count} content generators available")
    else:
        logger.warning("⚠️ WARNING: No content generators available")
        
except ImportError as e:
    logger.warning(f"⚠️ WARNING: Content generators import failed: {str(e)}")
    
    # Fallback generator classes
    class EmailSequenceGenerator:
        async def generate_email_sequence(self, *args, **kwargs):
            return {"error": "Email generator dependencies missing", "fallback": True}
    
    class CampaignAngleGenerator:
        async def generate_angles(self, *args, **kwargs):
            return {"error": "Campaign angle generator dependencies missing", "fallback": True}
    
    class SocialMediaGenerator:
        async def generate_social_posts(self, *args, **kwargs):
            return {"error": "Social media generator dependencies missing", "fallback": True}
    
    class AdCopyGenerator:
        async def generate_ad_copy(self, *args, **kwargs):
            return {"error": "Ad copy generator dependencies missing", "fallback": True}
    
    class BlogPostGenerator:
        async def generate_blog_post(self, *args, **kwargs):
            return {"error": "Blog post generator dependencies missing", "fallback": True}
    
    class LandingPageGenerator:
        async def generate_landing_page(self, *args, **kwargs):
            return {"error": "Landing page generator dependencies missing", "fallback": True}
    
    class VideoScriptGenerator:
        async def generate_video_script(self, *args, **kwargs):
            return {"error": "Video script generator dependencies missing", "fallback": True}
    
    class ContentGeneratorFactory:
        def get_available_generators(self):
            return []
    
    GENERATORS_AVAILABLE = {}
    
    def get_available_generators():
        return {}

# ============================================================================
# AMPLIFIER IMPORT
# ============================================================================

try:
    from .amplifier import (
        IntelligenceAmplificationService,
        IntelligenceAmplifier,
        is_amplifier_available,
        get_amplifier_status,
        AMPLIFIER_PACKAGE_AVAILABLE
    )
    
    if AMPLIFIER_PACKAGE_AVAILABLE:
        logger.info("✅ SUCCESS: Intelligence Amplifier imported successfully")
    else:
        logger.warning("⚠️ WARNING: Intelligence Amplifier using fallback mode")
        
except ImportError as e:
    logger.warning(f"⚠️ WARNING: Intelligence Amplifier import failed: {str(e)}")
    
    # Fallback amplifier classes
    class IntelligenceAmplificationService:
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
    
    def is_amplifier_available():
        return False
    
    def get_amplifier_status():
        return {"available": False, "status": "dependencies_missing"}
    
    AMPLIFIER_PACKAGE_AVAILABLE = False

# ============================================================================
# PACKAGE EXPORTS
# ============================================================================

__all__ = [
    # Core Analyzers
    'SalesPageAnalyzer',
    'DocumentAnalyzer', 
    'WebAnalyzer',
    'EnhancedSalesPageAnalyzer',
    'VSLAnalyzer',
    
    # Extractors
    'ProductNameExtractor',
    'extract_product_name',
    
    # Generators
    'EmailSequenceGenerator',
    'CampaignAngleGenerator', 
    'SocialMediaGenerator',
    'AdCopyGenerator',
    'BlogPostGenerator',
    'LandingPageGenerator',
    'VideoScriptGenerator',
    'ContentGeneratorFactory',
    
    # Amplifier
    'IntelligenceAmplificationService',
    'IntelligenceAmplifier',
    
    # Utility Functions
    'is_amplifier_available',
    'get_amplifier_status',
    'get_available_generators',
    
    # Status Flags
    'ANALYZERS_AVAILABLE',
    'EXTRACTORS_AVAILABLE', 
    'AMPLIFIER_PACKAGE_AVAILABLE',
    'INTELLIGENCE_AVAILABLE'
]

# ============================================================================
# MAIN INTELLIGENCE STATUS
# ============================================================================

# Overall intelligence system status
INTELLIGENCE_AVAILABLE = ANALYZERS_AVAILABLE

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_intelligence_status():
    """Get comprehensive intelligence system status"""
    
    return {
        "package_version": __version__,
        "analyzers_available": ANALYZERS_AVAILABLE,
        "extractors_available": EXTRACTORS_AVAILABLE if 'EXTRACTORS_AVAILABLE' in globals() else False,
        "amplifier_available": AMPLIFIER_PACKAGE_AVAILABLE if 'AMPLIFIER_PACKAGE_AVAILABLE' in globals() else False,
        "generators_status": GENERATORS_AVAILABLE if 'GENERATORS_AVAILABLE' in globals() else {},
        "overall_status": "operational" if INTELLIGENCE_AVAILABLE else "limited",
        "core_functionality": "available" if ANALYZERS_AVAILABLE else "fallback_mode"
    }

def is_intelligence_operational():
    """Check if core intelligence system is operational"""
    return INTELLIGENCE_AVAILABLE

# ============================================================================
# INITIALIZATION LOGGING
# ============================================================================

# Log final initialization status
status = get_intelligence_status()

if status["analyzers_available"]:
    logger.info("🚀 Intelligence Package fully initialized - Core analyzers operational")
else:
    logger.error("❌ Intelligence Package initialization failed - Core analyzers not available")
    logger.error("🔧 Please install missing dependencies: aiohttp, beautifulsoup4, lxml, openai")

# Log component status
components_status = []
if status["analyzers_available"]:
    components_status.append("✅ Analyzers")
else:
    components_status.append("❌ Analyzers")

if status["extractors_available"]:
    components_status.append("✅ Extractors")
else:
    components_status.append("⚠️ Extractors (fallback)")

if status["amplifier_available"]:
    components_status.append("✅ Amplifier")
else:
    components_status.append("⚠️ Amplifier (fallback)")

generator_count = len([g for g in status["generators_status"].values() if g]) if status["generators_status"] else 0
total_generators = len(status["generators_status"]) if status["generators_status"] else 0

if generator_count == total_generators and total_generators > 0:
    components_status.append("✅ Generators")
elif generator_count > 0:
    components_status.append(f"⚠️ Generators ({generator_count}/{total_generators})")
else:
    components_status.append("❌ Generators")

logger.info(f"📊 Intelligence Components: {' | '.join(components_status)}")