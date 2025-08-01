# src/intelligence/generators/__init__.py
"""
 Generators with Ultra-Cheap AI Integration
Railway deployment compatible
"""

import logging

logger = logging.getLogger(__name__)

# ============================================================================
# RAILWAY-COMPATIBLE GENERATOR IMPORTS
# ============================================================================

# Export main generators
try:
    from .email_generator import EmailSequenceGenerator, EmailGenerator
    EMAIL_GENERATOR_AVAILABLE = True
    logger.info("✅ Email generators imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Email generator import failed: {e}")
    EMAIL_GENERATOR_AVAILABLE = False

try:
    from .ad_copy_generator import AdCopyGenerator
    AD_COPY_GENERATOR_AVAILABLE = True
    logger.info("✅ Ad copy generator imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Ad copy generator import failed: {e}")
    AD_COPY_GENERATOR_AVAILABLE = False

try:
    from .social_media_generator import SocialMediaGenerator
    SOCIAL_MEDIA_GENERATOR_AVAILABLE = True
    logger.info("✅ Social media generator imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Social media generator import failed: {e}")
    SOCIAL_MEDIA_GENERATOR_AVAILABLE = False

# Blog Post Generator (try multiple import paths)
try:
    try:
        from .blog_post_generator import BlogPostGenerator
    except ImportError:
        from .social_media_generator import BlogPostGenerator
    BLOG_POST_GENERATOR_AVAILABLE = True
    logger.info("✅ Blog post generator imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Blog post generator import failed: {e}")
    BLOG_POST_GENERATOR_AVAILABLE = False

# Landing Page Generator
try:
    from .landing_page.core.generator import LandingPageGenerator as LandingPageGenerator
    LANDING_PAGE_GENERATOR_AVAILABLE = True
    logger.info("✅ Landing page generator imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Landing page generator import failed: {e}")
    LANDING_PAGE_GENERATOR_AVAILABLE = False

# Video Script Generator
try:
    from .video_script_generator import VideoScriptGenerator
    VIDEO_SCRIPT_GENERATOR_AVAILABLE = True
    logger.info("✅ Video script generator imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Video script generator import failed: {e}")
    VIDEO_SCRIPT_GENERATOR_AVAILABLE = False

# Campaign Angle Generator
try:
    from .campaign_angle_generator import CampaignAngleGenerator
    CAMPAIGN_ANGLE_GENERATOR_AVAILABLE = True
    logger.info("✅ Campaign angle generator imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Campaign angle generator import failed: {e}")
    CAMPAIGN_ANGLE_GENERATOR_AVAILABLE = False

# Ultra-Cheap Image Generator
try:
    from .image_generator import UltraCheapImageGenerator
    ULTRA_CHEAP_IMAGE_GENERATOR_AVAILABLE = True
    logger.info("✅ Ultra-cheap image generator imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Ultra-cheap image generator import failed: {e}")
    ULTRA_CHEAP_IMAGE_GENERATOR_AVAILABLE = False

# Factory integration
try:
    from .factory import ContentGeneratorFactory
    FACTORY_AVAILABLE = True
    logger.info("✅ Content generator factory imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Factory import failed: {e}")
    FACTORY_AVAILABLE = False

# Railway compatibility
try:
    from ..utils.railway_compatibility import (
        get_railway_compatibility_handler,
        railway_safe_generate_content
    )
    RAILWAY_COMPATIBILITY_AVAILABLE = True
    logger.info("✅ Railway compatibility imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Railway compatibility failed: {e}")
    RAILWAY_COMPATIBILITY_AVAILABLE = False

# ============================================================================
# EXPORT CONFIGURATION
# ============================================================================

# Export what's available
__all__ = []

if EMAIL_GENERATOR_AVAILABLE:
    __all__.extend(["EmailSequenceGenerator", "EmailGenerator"])

if AD_COPY_GENERATOR_AVAILABLE:
    __all__.append("AdCopyGenerator")

if SOCIAL_MEDIA_GENERATOR_AVAILABLE:
    __all__.append("SocialMediaGenerator")

if BLOG_POST_GENERATOR_AVAILABLE:
    __all__.append("BlogPostGenerator")

if LANDING_PAGE_GENERATOR_AVAILABLE:
    __all__.append("LandingPageGenerator")

if VIDEO_SCRIPT_GENERATOR_AVAILABLE:
    __all__.append("VideoScriptGenerator")

if CAMPAIGN_ANGLE_GENERATOR_AVAILABLE:
    __all__.append("CampaignAngleGenerator")

if ULTRA_CHEAP_IMAGE_GENERATOR_AVAILABLE:
    __all__.append("UltraCheapImageGenerator")

if FACTORY_AVAILABLE:
    __all__.append("ContentGeneratorFactory")

if RAILWAY_COMPATIBILITY_AVAILABLE:
    __all__.extend(["get_railway_compatibility_handler", "railway_safe_generate_content"])

# ============================================================================
# FALLBACK GENERATORS FOR RAILWAY COMPATIBILITY
# ============================================================================

# Create fallback generators for unavailable ones
if not EMAIL_GENERATOR_AVAILABLE:
    class EmailSequenceGenerator:
        def __init__(self):
            logger.warning("Using fallback EmailSequenceGenerator")
        
        async def generate_email_sequence(self, intelligence_data, preferences=None):
            return {
                "error": "Email generator not available",
                "fallback": True,
                "content": {"emails": []},
                "metadata": {"status": "fallback"}
            }
        
        async def generate_content(self, intelligence_data, preferences=None):
            return await self.generate_email_sequence(intelligence_data, preferences)
    
    class EmailGenerator:
        def __init__(self):
            logger.warning("Using fallback EmailGenerator")
        
        async def generate_content(self, intelligence_data, preferences=None):
            generator = EmailSequenceGenerator()
            return await generator.generate_content(intelligence_data, preferences)
    
    __all__.extend(["EmailSequenceGenerator", "EmailGenerator"])

if not AD_COPY_GENERATOR_AVAILABLE:
    class AdCopyGenerator:
        def __init__(self):
            logger.warning("Using fallback AdCopyGenerator")
        
        async def generate_ad_copy(self, intelligence_data, preferences=None):
            return {
                "error": "Ad copy generator not available",
                "fallback": True,
                "content": {"ads": []},
                "metadata": {"status": "fallback"}
            }
        
        async def generate_content(self, intelligence_data, preferences=None):
            return await self.generate_ad_copy(intelligence_data, preferences)
    
    __all__.append("AdCopyGenerator")

if not SOCIAL_MEDIA_GENERATOR_AVAILABLE:
    class SocialMediaGenerator:
        def __init__(self):
            logger.warning("Using fallback SocialMediaGenerator")
        
        async def generate_social_posts(self, intelligence_data, preferences=None):
            return {
                "error": "Social media generator not available",
                "fallback": True,
                "content": {"posts": []},
                "metadata": {"status": "fallback"}
            }
        
        async def generate_content(self, intelligence_data, preferences=None):
            return await self.generate_social_posts(intelligence_data, preferences)
    
    __all__.append("SocialMediaGenerator")

if not FACTORY_AVAILABLE:
    class ContentGeneratorFactory:
        def __init__(self):
            logger.warning("Using fallback ContentGeneratorFactory")
            self._generators = {}
        
        def get_generator(self, content_type):
            raise ValueError(f"Factory system not available: {content_type}")
        
        def get_available_generators(self):
            return []
        
        async def generate_content(self, content_type, intelligence_data, preferences=None):
            return {
                "error": "Factory system not available",
                "fallback": True,
                "content": {},
                "metadata": {"status": "fallback"}
            }
    
    __all__.append("ContentGeneratorFactory")

if not RAILWAY_COMPATIBILITY_AVAILABLE:
    def get_railway_compatibility_handler():
        class FallbackHandler:
            def __init__(self):
                self.ultra_cheap_generators = []
            
            async def generate_ultra_cheap_content(self, content_type, intelligence_data, preferences=None):
                return {
                    "error": "Railway compatibility not available",
                    "fallback": True,
                    "content": {},
                    "metadata": {"status": "fallback"}
                }
        
        return FallbackHandler()
    
    async def railway_safe_generate_content(content_type, intelligence_data, preferences=None):
        handler = get_railway_compatibility_handler()
        return await handler.generate_ultra_cheap_content(content_type, intelligence_data, preferences)
    
    __all__.extend(["get_railway_compatibility_handler", "railway_safe_generate_content"])

# ============================================================================
# BACKWARD COMPATIBILITY
# ============================================================================

# Maintain backward compatibility with existing code
if EMAIL_GENERATOR_AVAILABLE or 'EmailSequenceGenerator' in __all__:
    ContentGenerator = EmailSequenceGenerator
    ProductionEmailGenerator = EmailSequenceGenerator
    __all__.extend(["ContentGenerator", "ProductionEmailGenerator"])

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_available_generators() -> dict:
    """Get status of all available generators"""
    return {
        "email_sequence": EMAIL_GENERATOR_AVAILABLE,
        "ad_copy": AD_COPY_GENERATOR_AVAILABLE,
        "social_media": SOCIAL_MEDIA_GENERATOR_AVAILABLE,
        "blog_post": BLOG_POST_GENERATOR_AVAILABLE,
        "landing_page": LANDING_PAGE_GENERATOR_AVAILABLE,
        "video_script": VIDEO_SCRIPT_GENERATOR_AVAILABLE,
        "campaign_angles": CAMPAIGN_ANGLE_GENERATOR_AVAILABLE,
        "ultra_cheap_image": ULTRA_CHEAP_IMAGE_GENERATOR_AVAILABLE,
        "factory": FACTORY_AVAILABLE,
        "railway_compatibility": RAILWAY_COMPATIBILITY_AVAILABLE
    }

def get_generator_status() -> dict:
    """Get detailed status of generator system"""
    available_generators = get_available_generators()
    available_count = sum(1 for available in available_generators.values() if available)
    total_count = len(available_generators)
    
    return {
        "generators_available": available_count,
        "total_generators": total_count,
        "availability_rate": f"{(available_count/total_count)*100:.1f}%" if total_count > 0 else "0%",
        "generator_status": available_generators,
        "exports_available": len(__all__),
        "railway_compatible": True,
        "ultra_cheap_ai_enabled": available_count > 0
    }

def is_generator_available(generator_type: str) -> bool:
    """Check if specific generator type is available"""
    generator_status = get_available_generators()
    return generator_status.get(generator_type, False)

# ============================================================================
# INITIALIZATION SUMMARY
# ============================================================================

# Log initialization status
available_count = sum([
    EMAIL_GENERATOR_AVAILABLE,
    AD_COPY_GENERATOR_AVAILABLE, 
    SOCIAL_MEDIA_GENERATOR_AVAILABLE,
    BLOG_POST_GENERATOR_AVAILABLE,
    LANDING_PAGE_GENERATOR_AVAILABLE,
    VIDEO_SCRIPT_GENERATOR_AVAILABLE,
    CAMPAIGN_ANGLE_GENERATOR_AVAILABLE,
    ULTRA_CHEAP_IMAGE_GENERATOR_AVAILABLE,
    FACTORY_AVAILABLE,
    RAILWAY_COMPATIBILITY_AVAILABLE
])

logger.info(f"✅ Generators module loaded: {len(__all__)} exports available")
logger.info(f"🚀 Railway compatibility: {available_count}/10 generators operational")

if RAILWAY_COMPATIBILITY_AVAILABLE:
    logger.info("🌐 Railway compatibility layer: ACTIVE")
if FACTORY_AVAILABLE:
    logger.info("🏭 Factory system: OPERATIONAL")
if available_count >= 5:
    logger.info("✅ Core generators: SUFFICIENT for production")
elif available_count >= 3:
    logger.info("⚠️ Core generators: MINIMAL for basic operation") 
else:
    logger.warning("❌ Core generators: INSUFFICIENT - check dependencies")

# Package initialization flag
PACKAGE_INITIALIZED = available_count > 0
ULTRA_CHEAP_AI_READY = EMAIL_GENERATOR_AVAILABLE or AD_COPY_GENERATOR_AVAILABLE or SOCIAL_MEDIA_GENERATOR_AVAILABLE