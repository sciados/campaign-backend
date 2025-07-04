# src/intelligence/generators/factory.py
"""
CONTENT GENERATOR FACTORY
✅ Unified access to all content generators
✅ Clean initialization and provider management
✅ Type-safe generator selection
✅ Fallback handling and error management
"""

import logging
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

class ContentGeneratorFactory:
    """Factory for creating and managing content generators"""
    
    def __init__(self):
        self._generators = {}
        self._generator_registry = {
            "email_sequence": "EmailSequenceGenerator",
            "SOCIAL_POSTS": "SocialMediaGenerator", 
            "ad_copy": "AdCopyGenerator",
            "blog_post": "BlogPostGenerator",
            "landing_page": "LandingPageGenerator",
            "video_script": "VideoScriptGenerator"
        }
        self._initialize_generators()
        
    def _initialize_generators(self):
        """Initialize all available generators"""
        
        # Email Sequence Generator
        try:
            from .email_generator import EmailSequenceGenerator
            self._generators["email_sequence"] = EmailSequenceGenerator()
            logger.info("✅ Email Sequence Generator initialized")
        except Exception as e:
            logger.warning(f"⚠️ Email Sequence Generator failed to initialize: {str(e)}")
        
        # Social Media Generator
        try:
            from .social_media_generator import SocialMediaGenerator
            self._generators["SOCIAL_POSTS"] = SocialMediaGenerator()
            logger.info("✅ Social Media Generator initialized")
        except Exception as e:
            logger.warning(f"⚠️ Social Media Generator failed to initialize: {str(e)}")
        
        # Ad Copy Generator
        try:
            from .social_media_generator import AdCopyGenerator  # Combined in social_media_generator.py
            self._generators["ad_copy"] = AdCopyGenerator()
            logger.info("✅ Ad Copy Generator initialized")
        except Exception as e:
            logger.warning(f"⚠️ Ad Copy Generator failed to initialize: {str(e)}")
        
        # Blog Post Generator
        try:
            from .social_media_generator import BlogPostGenerator  # Combined in social_media_generator.py
            self._generators["blog_post"] = BlogPostGenerator()
            logger.info("✅ Blog Post Generator initialized")
        except Exception as e:
            logger.warning(f"⚠️ Blog Post Generator failed to initialize: {str(e)}")
        
        # Landing Page Generator
        try:
            from .landing_page.core.generator import EnhancedLandingPageGenerator as LandingPageGenerator
            self._generators["landing_page"] = LandingPageGenerator()
            logger.info("✅ Landing Page Generator initialized")
        except Exception as e:
            logger.warning(f"⚠️ Landing Page Generator failed to initialize: {str(e)}")
        
        # Video Script Generator
        try:
            from .video_script_generator import VideoScriptGenerator
            self._generators["video_script"] = VideoScriptGenerator()
            logger.info("✅ Video Script Generator initialized")
        except Exception as e:
            logger.warning(f"⚠️ Video Script Generator failed to initialize: {str(e)}")
    
    def get_generator(self, content_type: str):
        """Get generator instance for specified content type"""
        
        if content_type not in self._generators:
            available_types = list(self._generators.keys())
            raise ValueError(f"Content type '{content_type}' not available. Available types: {available_types}")
        
        return self._generators[content_type]
    
    def get_available_generators(self) -> List[str]:
        """Get list of available content generator types"""
        return list(self._generators.keys())
    
    def get_generator_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Get capabilities of all available generators"""
        
        capabilities = {}
        
        for content_type, generator in self._generators.items():
            try:
                if content_type == "email_sequence":
                    capabilities[content_type] = {
                        "description": "Generate email sequences with 5 diverse angles",
                        "features": ["angle_diversity", "affiliate_focus", "parsing_strategies"],
                        "output_format": "email_sequence",
                        "customization": ["length", "uniqueness_id", "angle_selection"]
                    }
                elif content_type == "SOCIAL_POSTS":
                    capabilities[content_type] = {
                        "description": "Generate platform-specific social media posts",
                        "features": ["platform_optimization", "hashtag_generation", "engagement_elements"],
                        "output_format": "SOCIAL_POSTS",
                        "platforms": ["facebook", "instagram", "twitter", "linkedin", "tiktok"],
                        "customization": ["platform", "count", "tone"]
                    }
                elif content_type == "ad_copy":
                    capabilities[content_type] = {
                        "description": "Generate paid advertising copy for different platforms",
                        "features": ["conversion_optimization", "platform_specs", "angle_variation"],
                        "output_format": "ad_copy",
                        "platforms": ["facebook", "google", "instagram", "linkedin", "youtube"],
                        "customization": ["platform", "objective", "count"]
                    }
                elif content_type == "blog_post":
                    capabilities[content_type] = {
                        "description": "Generate long-form blog posts and articles",
                        "features": ["seo_optimization", "structured_sections", "scientific_backing"],
                        "output_format": "blog_post",
                        "lengths": ["short", "medium", "long"],
                        "customization": ["topic", "length", "tone"]
                    }
                elif content_type == "LANDING_PAGE":
                    capabilities[content_type] = {
                        "description": "Generate complete HTML landing pages",
                        "features": ["conversion_optimization", "responsive_design", "complete_html"],
                        "output_format": "landing_page",
                        "page_types": ["lead_generation", "sales", "webinar", "product_demo", "free_trial"],
                        "customization": ["page_type", "objective", "color_scheme"]
                    }
                elif content_type == "video_script":
                    capabilities[content_type] = {
                        "description": "Generate platform-optimized video scripts",
                        "features": ["scene_breakdown", "visual_notes", "timing_optimization"],
                        "output_format": "video_script",
                        "video_types": ["explainer", "testimonial", "demo", "ad", "social", "webinar"],
                        "platforms": ["youtube", "tiktok", "instagram", "facebook", "linkedin"],
                        "customization": ["video_type", "platform", "duration", "tone"]
                    }
                
            except Exception as e:
                capabilities[content_type] = {
                    "description": f"Generator available but capabilities detection failed: {str(e)}",
                    "status": "limited"
                }
        
        return capabilities
    
    async def generate_content(
        self, 
        content_type: str, 
        intelligence_data: Dict[str, Any], 
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate content using specified generator"""
        
        if preferences is None:
            preferences = {}
        
        try:
            generator = self.get_generator(content_type)
            
            # Route to appropriate generation method
            if content_type == "email_sequence":
                return await generator.generate_email_sequence(intelligence_data, preferences)
            elif content_type == "SOCIAL_POSTS":
                return await generator.generate_social_posts(intelligence_data, preferences)
            elif content_type == "ad_copy":
                return await generator.generate_ad_copy(intelligence_data, preferences)
            elif content_type == "blog_post":
                return await generator.generate_blog_post(intelligence_data, preferences)
            elif content_type == "LANDING_PAGE":
                return await generator.generate_landing_page(intelligence_data, preferences)
            elif content_type == "video_script":
                return await generator.generate_video_script(intelligence_data, preferences)
            else:
                raise ValueError(f"Unknown content type: {content_type}")
                
        except Exception as e:
            logger.error(f"❌ Content generation failed for {content_type}: {str(e)}")
            
            # Return fallback response
            return self._generate_fallback_content(content_type, intelligence_data, preferences, str(e))
    
    def _generate_fallback_content(
        self, 
        content_type: str, 
        intelligence_data: Dict[str, Any], 
        preferences: Dict[str, Any],
        error_message: str
    ) -> Dict[str, Any]:
        """Generate fallback content when generators fail"""
        
        product_name = self._extract_fallback_product_name(intelligence_data)
        
        fallback_content = {
            "content_type": content_type,
            "title": f"Fallback {content_type.title()} for {product_name}",
            "content": {
                "fallback_generated": True,
                "error_message": error_message,
                "note": f"Generator for {content_type} encountered an error. Please check configuration."
            },
            "metadata": {
                "generated_by": "fallback_generator",
                "product_name": product_name,
                "content_type": content_type,
                "status": "fallback",
                "error": error_message
            }
        }
        
        # Add content-type specific fallback
        if content_type == "email_sequence":
            fallback_content["content"]["emails"] = [
                {
                    "email_number": 1,
                    "subject": f"Discover {product_name} Benefits",
                    "body": f"Learn about the natural health benefits of {product_name} and how it can support your wellness journey.",
                    "fallback_generated": True
                }
            ]
        elif content_type == "SOCIAL_POSTS":
            fallback_content["content"]["posts"] = [
                {
                    "post_number": 1,
                    "platform": "facebook",
                    "content": f"Discover the natural benefits of {product_name} for your wellness journey! 🌿 #health #wellness",
                    "fallback_generated": True
                }
            ]
        elif content_type == "LANDING_PAGE":
            fallback_content["content"]["html_code"] = f"""
<!DOCTYPE html>
<html>
<head><title>{product_name}</title></head>
<body>
    <h1>{product_name}</h1>
    <p>Natural health optimization through science-backed solutions.</p>
    <button>Learn More</button>
</body>
</html>"""
        
        return fallback_content
    
    def _extract_fallback_product_name(self, intelligence_data: Dict[str, Any]) -> str:
        """Extract product name for fallback content"""
        
        try:
            # offer_intel = intelligence_data.get("offer_intelligence", {})
            offer_intel = self._serialize_enum_field(intelligence_data.get("offer_intelligence"))
            # insights = offer_intel.get("insights", [])
            insights = self._serialize_enum_field(offer_intel.get("insights", []))
            for insight in insights:
                if "called" in str(insight).lower():
                    words = str(insight).split()
                    for i, word in enumerate(words):
                        if word.lower() == "called" and i + 1 < len(words):
                            return words[i + 1].upper().replace(",", "").replace(".", "")
        except:
            pass
        
        return "PRODUCT"
    
    def get_factory_status(self) -> Dict[str, Any]:
        """Get comprehensive factory status"""
        
        return {
            "factory_version": "1.0.0",
            "available_generators": len(self._generators),
            "generator_types": list(self._generators.keys()),
            "capabilities": self.get_generator_capabilities(),
            "status": "operational" if self._generators else "no_generators_available",
            "total_content_types": len(self._generator_registry)
        }


# Convenience functions for backward compatibility and easy access
def create_content_generator_factory() -> ContentGeneratorFactory:
    """Create and return a content generator factory instance"""
    return ContentGeneratorFactory()

def get_available_content_types() -> List[str]:
    """Get list of available content types"""
    factory = ContentGeneratorFactory()
    return factory.get_available_generators()

async def generate_content_with_factory(
    content_type: str,
    intelligence_data: Dict[str, Any],
    preferences: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate content using the factory (convenience function)"""
    factory = ContentGeneratorFactory()
    return await factory.generate_content(content_type, intelligence_data, preferences)

# Backward compatibility aliases
ContentFactory = ContentGeneratorFactory
create_factory = create_content_generator_factory