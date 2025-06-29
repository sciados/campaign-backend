# src/intelligence/generators/__init__.py
"""
Content Generators Package
Comprehensive content generation system with multiple specialized generators
"""

import logging

logger = logging.getLogger(__name__)

# Package metadata
__version__ = "1.0.0"
__author__ = "CampaignForge Team"
__description__ = "Comprehensive content generation system for marketing campaigns"

# Initialize availability flags
GENERATORS_AVAILABLE = {}

# ============================================================================
# CORE GENERATORS IMPORT
# ============================================================================

# Email Sequence Generator (Primary)
try:
    from .email_generator import EmailSequenceGenerator, CampaignAngleGenerator
    GENERATORS_AVAILABLE["email_sequence"] = True
    GENERATORS_AVAILABLE["campaign_angles"] = True
    logger.info("✅ Email Sequence Generator and Campaign Angle Generator available")
except ImportError as e:
    logger.warning(f"⚠️ Email generators not available: {str(e)}")
    GENERATORS_AVAILABLE["email_sequence"] = False
    GENERATORS_AVAILABLE["campaign_angles"] = False
    
    # Fallback classes
    class EmailSequenceGenerator:
        def __init__(self):
            pass
        async def generate_email_sequence(self, intelligence_data, preferences=None):
            return {"error": "Email generator not available", "fallback": True}
    
    class CampaignAngleGenerator:
        def __init__(self):
            pass
        async def generate_angles(self, intelligence_data, **kwargs):
            return {"error": "Campaign angle generator not available", "fallback": True}

# Social Media Generator
try:
    from .social_media_generator import SocialMediaGenerator
    GENERATORS_AVAILABLE["social_media"] = True
    logger.info("✅ Social Media Generator available")
except ImportError as e:
    logger.warning(f"⚠️ Social Media Generator not available: {str(e)}")
    GENERATORS_AVAILABLE["social_media"] = False
    
    class SocialMediaGenerator:
        def __init__(self):
            pass
        async def generate_social_posts(self, intelligence_data, preferences=None):
            return {"error": "Social media generator not available", "fallback": True}

# Ad Copy Generator
try:
    # Try to import from dedicated file first, then from social_media_generator
    try:
        from .ad_copy_generator import AdCopyGenerator
    except ImportError:
        from .social_media_generator import AdCopyGenerator
    GENERATORS_AVAILABLE["ad_copy"] = True
    logger.info("✅ Ad Copy Generator available")
except ImportError as e:
    logger.warning(f"⚠️ Ad Copy Generator not available: {str(e)}")
    GENERATORS_AVAILABLE["ad_copy"] = False
    
    class AdCopyGenerator:
        def __init__(self):
            pass
        async def generate_ad_copy(self, intelligence_data, preferences=None):
            return {"error": "Ad copy generator not available", "fallback": True}

# Blog Post Generator
try:
    # Try to import from dedicated file first, then from social_media_generator
    try:
        from .blog_post_generator import BlogPostGenerator
    except ImportError:
        from .social_media_generator import BlogPostGenerator
    GENERATORS_AVAILABLE["blog_post"] = True
    logger.info("✅ Blog Post Generator available")
except ImportError as e:
    logger.warning(f"⚠️ Blog Post Generator not available: {str(e)}")
    GENERATORS_AVAILABLE["blog_post"] = False
    
    class BlogPostGenerator:
        def __init__(self):
            pass
        async def generate_blog_post(self, intelligence_data, preferences=None):
            return {"error": "Blog post generator not available", "fallback": True}

# Landing Page Generator
try:
    from .landing_page.core.generator import EnhancedLandingPageGenerator as LandingPageGenerator
    GENERATORS_AVAILABLE["landing_page"] = True
    logger.info("✅ Landing Page Generator available")
except ImportError as e:
    logger.warning(f"⚠️ Landing Page Generator not available: {str(e)}")
    GENERATORS_AVAILABLE["landing_page"] = False
    
    class LandingPageGenerator:
        def __init__(self):
            pass
        async def generate_landing_page(self, intelligence_data, preferences=None):
            return {"error": "Landing page generator not available", "fallback": True}

# Video Script Generator
try:
    from .video_script_generator import VideoScriptGenerator
    GENERATORS_AVAILABLE["video_script"] = True
    logger.info("✅ Video Script Generator available")
except ImportError as e:
    logger.warning(f"⚠️ Video Script Generator not available: {str(e)}")
    GENERATORS_AVAILABLE["video_script"] = False
    
    class VideoScriptGenerator:
        def __init__(self):
            pass
        async def generate_video_script(self, intelligence_data, preferences=None):
            return {"error": "Video script generator not available", "fallback": True}

# ============================================================================
# FACTORY SYSTEM
# ============================================================================

# Content Generator Factory
try:
    from .factory import ContentGeneratorFactory, create_content_generator_factory
    GENERATORS_AVAILABLE["factory"] = True
    logger.info("✅ Content Generator Factory available")
except ImportError as e:
    logger.warning(f"⚠️ Content Generator Factory not available: {str(e)}")
    GENERATORS_AVAILABLE["factory"] = False
    
    # Fallback factory
    class ContentGeneratorFactory:
        def __init__(self):
            self._generators = {}
        
        def get_generator(self, content_type):
            raise ValueError(f"Factory system not available: {content_type}")
        
        def get_available_generators(self):
            return []
        
        async def generate_content(self, content_type, intelligence_data, preferences=None):
            return {"error": "Factory system not available", "fallback": True}
    
    def create_content_generator_factory():
        return ContentGeneratorFactory()

# ============================================================================
# PACKAGE EXPORTS
# ============================================================================

# Main exports for easy access
__all__ = [
    # Core Generators
    'EmailSequenceGenerator',
    'CampaignAngleGenerator',  # Added this!
    'SocialMediaGenerator', 
    'AdCopyGenerator',
    'BlogPostGenerator',
    'LandingPageGenerator',
    'VideoScriptGenerator',
    
    # Factory System
    'ContentGeneratorFactory',
    'create_content_generator_factory',
    
    # Utility Functions
    'get_available_generators',
    'get_generator_status',
    'is_generator_available',
    
    # Backward Compatibility
    'ContentGenerator',  # Alias for EmailSequenceGenerator
    'ProductionEmailGenerator'  # Alias for EmailSequenceGenerator
]

# ============================================================================
# BACKWARD COMPATIBILITY ALIASES
# ============================================================================

# Maintain backward compatibility with existing code
ContentGenerator = EmailSequenceGenerator
ProductionEmailGenerator = EmailSequenceGenerator

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_available_generators() -> dict:
    """Get status of all available generators"""
    return GENERATORS_AVAILABLE.copy()

def get_generator_status() -> dict:
    """Get detailed status of generator system"""
    
    available_count = sum(1 for available in GENERATORS_AVAILABLE.values() if available)
    total_count = len(GENERATORS_AVAILABLE)
    
    return {
        "package_version": __version__,
        "generators_available": available_count,
        "total_generators": total_count,
        "availability_rate": f"{(available_count/total_count)*100:.1f}%" if total_count > 0 else "0%",
        "generator_status": GENERATORS_AVAILABLE,
        "fully_operational": available_count == total_count,
        "core_generators_available": GENERATORS_AVAILABLE.get("email_sequence", False),
        "campaign_angles_available": GENERATORS_AVAILABLE.get("campaign_angles", False),
        "factory_available": GENERATORS_AVAILABLE.get("factory", False),
        "recommendations": _get_setup_recommendations()
    }

def is_generator_available(generator_type: str) -> bool:
    """Check if specific generator type is available"""
    return GENERATORS_AVAILABLE.get(generator_type, False)

def _get_setup_recommendations() -> list:
    """Get setup recommendations based on availability"""
    
    recommendations = []
    
    if not GENERATORS_AVAILABLE.get("email_sequence", False):
        recommendations.append("🚨 CRITICAL: Email Sequence Generator unavailable - core functionality affected")
    
    if not GENERATORS_AVAILABLE.get("campaign_angles", False):
        recommendations.append("⚠️ Campaign Angle Generator unavailable - angle generation affected")
    
    if not GENERATORS_AVAILABLE.get("factory", False):
        recommendations.append("⚠️ Factory system unavailable - use individual generators directly")
    
    missing_generators = [gen for gen, available in GENERATORS_AVAILABLE.items() if not available]
    if missing_generators and len(missing_generators) < len(GENERATORS_AVAILABLE):
        recommendations.append(f"💡 Consider installing missing dependencies for: {', '.join(missing_generators)}")
    
    if all(GENERATORS_AVAILABLE.values()):
        recommendations.append("✅ All generators operational - system ready for production")
    
    if not any(GENERATORS_AVAILABLE.values()):
        recommendations.append("❌ No generators available - check dependencies and installation")
    
    return recommendations

def get_package_info() -> dict:
    """Get comprehensive package information"""
    
    return {
        "name": "Content Generators",
        "version": __version__,
        "author": __author__, 
        "description": __description__,
        "status": get_generator_status(),
        "features": [
            "Email sequence generation with 5 diverse angles",
            "Campaign angle generation for strategic positioning",
            "Social media posts for multiple platforms", 
            "Ad copy generation with conversion optimization",
            "Long-form blog post creation",
            "Complete HTML landing page generation",
            "Video scripts with scene breakdowns",
            "Unified factory system for easy access",
            "Fallback handling and error management"
        ],
        "supported_content_types": [
            "email_sequence",
            "campaign_angles",
            "social_posts",
            "ad_copy", 
            "blog_post",
            "landing_page",
            "video_script"
        ]
    }

# ============================================================================
# EASY ACCESS FUNCTIONS
# ============================================================================

async def generate_emails(intelligence_data: dict, preferences: dict = None) -> dict:
    """Quick access function for email generation"""
    generator = EmailSequenceGenerator()
    return await generator.generate_email_sequence(intelligence_data, preferences)

async def generate_campaign_angles(intelligence_data: list, **kwargs) -> dict:
    """Quick access function for campaign angle generation"""
    generator = CampaignAngleGenerator()
    return await generator.generate_angles(intelligence_data, **kwargs)

async def generate_social_posts(intelligence_data: dict, preferences: dict = None) -> dict:
    """Quick access function for social media generation"""
    generator = SocialMediaGenerator()
    return await generator.generate_social_posts(intelligence_data, preferences)

async def generate_ads(intelligence_data: dict, preferences: dict = None) -> dict:
    """Quick access function for ad copy generation"""
    generator = AdCopyGenerator()
    return await generator.generate_ad_copy(intelligence_data, preferences)

async def generate_blog(intelligence_data: dict, preferences: dict = None) -> dict:
    """Quick access function for blog post generation"""
    generator = BlogPostGenerator()
    return await generator.generate_blog_post(intelligence_data, preferences)

async def generate_landing_page(intelligence_data: dict, preferences: dict = None) -> dict:
    """Quick access function for landing page generation"""
    generator = LandingPageGenerator()
    return await generator.generate_landing_page(intelligence_data, preferences)

async def generate_video_script(intelligence_data: dict, preferences: dict = None) -> dict:
    """Quick access function for video script generation"""
    generator = VideoScriptGenerator()
    return await generator.generate_video_script(intelligence_data, preferences)

# ============================================================================
# INITIALIZATION LOGGING
# ============================================================================

# Log initialization status
available_generators = [gen for gen, available in GENERATORS_AVAILABLE.items() if available]
total_generators = len(GENERATORS_AVAILABLE)

if len(available_generators) == total_generators:
    logger.info(f"🚀 Content Generators Package fully initialized - All {total_generators} generators available")
elif len(available_generators) > 0:
    logger.info(f"⚠️ Content Generators Package partially initialized - {len(available_generators)}/{total_generators} generators available")
    logger.info(f"✅ Available: {', '.join(available_generators)}")
    missing = [gen for gen, available in GENERATORS_AVAILABLE.items() if not available]
    logger.warning(f"❌ Missing: {', '.join(missing)}")
else:
    logger.error("❌ Content Generators Package initialization failed - No generators available")

# Success flag for external checking
PACKAGE_INITIALIZED = len(available_generators) > 0
PACKAGE_FULLY_OPERATIONAL = len(available_generators) == total_generators