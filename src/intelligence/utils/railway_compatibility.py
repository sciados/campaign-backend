# src/intelligence/utils/railway_compatibility.py
"""
RAILWAY COMPATIBILITY LAYER - FIXED
✅ Fixes async/await issues for Railway deployment
✅ Handles ChunkedIteratorResult properly
✅ Provides backward compatibility with existing handlers
✅ Ultra-cheap AI integration support
✅ FIXED: Correct method calls for generators
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class RailwayCompatibilityLayer:
    """Compatibility layer for Railway deployment"""
    
    @staticmethod
    async def safe_database_operation(db_operation):
        """Safely handle database operations that might return ChunkedIteratorResult"""
        try:
            # If it's already a coroutine, await it
            if asyncio.iscoroutine(db_operation):
                result = await db_operation
            # If it's a ChunkedIteratorResult or similar, convert to list
            elif hasattr(db_operation, '__aiter__'):
                result = []
                async for item in db_operation:
                    result.append(item)
            # If it's already a regular object, return as-is
            else:
                result = db_operation
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Database operation failed: {str(e)}")
            return None
    
    @staticmethod
    async def safe_generator_call(generator_instance, method_name: str, *args, **kwargs):
        """Safely call generator methods with proper error handling"""
        try:
            # Get the method
            method = getattr(generator_instance, method_name)
            
            # Call the method
            if asyncio.iscoroutinefunction(method):
                result = await method(*args, **kwargs)
            else:
                result = method(*args, **kwargs)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Generator {method_name} failed: {str(e)}")
            # Return a basic fallback response
            return {
                "success": False,
                "error": str(e),
                "fallback_content": "Generator temporarily unavailable",
                "provider_used": "compatibility_fallback"
            }
    
    @staticmethod
    def ensure_generator_compatibility(generator_class):
        """Ensure generator class has required methods for Railway compatibility"""
        
        # Check if class has required methods
        required_methods = ['generate_content']
        
        for method_name in required_methods:
            if not hasattr(generator_class, method_name):
                logger.warning(f"⚠️ Generator {generator_class.__name__} missing {method_name} method")
                
                # Add a basic generate_content method if missing
                if method_name == 'generate_content':
                    async def default_generate_content(self, intelligence_data, preferences=None):
                        return {
                            "content_type": "fallback",
                            "content": "Generator method not implemented",
                            "metadata": {"fallback": True}
                        }
                    setattr(generator_class, method_name, default_generate_content)
        
        return generator_class


#  content handler compatibility
class ContentHandler:
    """ content handler with ultra-cheap AI and Railway compatibility"""
    
    def __init__(self):
        self.compatibility_layer = RailwayCompatibilityLayer()
        self.ultra_cheap_generators = {}
        self._initialize_ultra_cheap_generators()
    
    def _initialize_ultra_cheap_generators(self):
        """Initialize ultra-cheap generators with compatibility checks - FIXED"""
        
        generator_mappings = {
            "email_sequence": {
                "module": "src.intelligence.generators.email_generator", 
                "class": "EmailSequenceGenerator",
                "method": "generate_email_sequence"  # ✅ FIXED: Correct method name
            },
            "ad_copy": {
                "module": "src.intelligence.generators.ad_copy_generator",
                "class": "AdCopyGenerator",
                "method": "generate_ad_copy"  # ✅ FIXED: Correct method name
            },
            "social_media": {
                "module": "src.intelligence.generators.social_media_generator",
                "class": "SocialMediaGenerator",
                "method": "generate_social_posts"  # ✅ FIXED: Correct method name
            }
        }
        
        for content_type, config in generator_mappings.items():
            try:
                # Dynamic import with error handling
                module = __import__(config["module"], fromlist=[config["class"]])
                generator_class = getattr(module, config["class"])
                
                # Ensure compatibility
                generator_class = self.compatibility_layer.ensure_generator_compatibility(generator_class)
                
                # Initialize generator
                generator_instance = generator_class()
                
                # ✅ FIXED: Store with method info for correct method calls
                self.ultra_cheap_generators[content_type] = {
                    "instance": generator_instance,
                    "method": config["method"]
                }
                
                logger.info(f"✅ Ultra-cheap generator loaded: {content_type}")
                
            except ImportError as e:
                logger.warning(f"⚠️ Could not import {content_type} generator: {str(e)}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize {content_type} generator: {str(e)}")
    
    async def generate_ultra_cheap_content(
        self, 
        content_type: str, 
        intelligence_data: Dict[str, Any],
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate content using ultra-cheap AI with Railway compatibility - FIXED"""
        
        if preferences is None:
            preferences = {}
        
        logger.info(f"🚂 Railway compatibility generation: {content_type}")
        
        try:
            # ✅ FIXED: Use specific generator methods with correct parameters
            if content_type == "email_sequence":
                if "email_sequence" in self.ultra_cheap_generators:
                    gen_info = self.ultra_cheap_generators["email_sequence"]
                    generator = gen_info["instance"]
                    method_name = gen_info["method"]  # "generate_email_sequence"
                    
                    result = await self.compatibility_layer.safe_generator_call(
                        generator, method_name, intelligence_data, preferences
                    )
                    if result and not result.get("error"):
                        logger.info(f"✅ Ultra-cheap AI generation successful for {content_type}")
                        return result
                
            elif content_type == "ad_copy":
                if "ad_copy" in self.ultra_cheap_generators:
                    gen_info = self.ultra_cheap_generators["ad_copy"]
                    generator = gen_info["instance"]
                    method_name = gen_info["method"]  # "generate_ad_copy"
                    
                    result = await self.compatibility_layer.safe_generator_call(
                        generator, method_name, intelligence_data, preferences
                    )
                    if result and not result.get("error"):
                        logger.info(f"✅ Ultra-cheap AI generation successful for {content_type}")
                        return result
                
            elif content_type in ["SOCIAL_POSTS", "social_media"]:
                if "social_media" in self.ultra_cheap_generators:
                    gen_info = self.ultra_cheap_generators["social_media"]
                    generator = gen_info["instance"]
                    method_name = gen_info["method"]  # "generate_social_posts"
                    
                    result = await self.compatibility_layer.safe_generator_call(
                        generator, method_name, intelligence_data, preferences
                    )
                    if result and not result.get("error"):
                        logger.info(f"✅ Ultra-cheap AI generation successful for {content_type}")
                        return result
            
            logger.warning(f"⚠️ Ultra-cheap generation not available for {content_type}, using fallback")
                
        except Exception as e:
            logger.error(f"❌ Ultra-cheap generator error for {content_type}: {str(e)}")
        
        # Fallback to basic response
        return self._create_compatibility_fallback(content_type, intelligence_data, preferences)
    
    def _create_compatibility_fallback(
        self, 
        content_type: str, 
        intelligence_data: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create compatibility fallback response"""
        
        product_name = self._extract_product_name_safe(intelligence_data)
        
        fallback_content = {
            "email_sequence": {
                "title": f"{product_name} Email Sequence",
                "content": {
                    "emails": [
                        {
                            "email_number": 1,
                            "subject": f"Discover {product_name} Benefits",
                            "body": f"Transform your health naturally with {product_name}. Science-backed approach to wellness.",
                            "send_delay": "Day 1"
                        }
                    ],
                    "sequence_title": f"{product_name} Campaign"
                }
            },
            "ad_copy": {
                "title": f"{product_name} Ad Copy",
                "content": {
                    "ads": [
                        {
                            "ad_number": 1,
                            "headline": f"Discover {product_name} Benefits",
                            "description": f"Natural health optimization with {product_name}. Science-backed results.",
                            "cta": "Learn More",
                            "platform": preferences.get("platform", "facebook")
                        }
                    ],
                    "total_ads": 1
                }
            },
            "social_media": {
                "title": f"{product_name} Social Media",
                "content": {
                    "posts": [
                        {
                            "post_number": 1,
                            "platform": preferences.get("platform", "facebook"),
                            "content": f"Discover the natural benefits of {product_name}! 🌿 #health #wellness",
                            "hashtags": ["#health", "#wellness", "#natural"]
                        }
                    ],
                    "total_posts": 1
                }
            }
        }
        
        return {
            "content_type": content_type,
            "title": fallback_content.get(content_type, {}).get("title", f"{product_name} Content"),
            "content": fallback_content.get(content_type, {}).get("content", {}),
            "metadata": {
                "generated_by": "railway_compatibility_fallback",
                "product_name": product_name,
                "fallback_reason": "Ultra-cheap AI temporarily unavailable",
                "railway_compatible": True,
                "generated_at": datetime.now(timezone.utc).astimezone().isoformat()
            }
        }
    
    def _extract_product_name_safe(self, intelligence_data: Dict[str, Any]) -> str:
        """Safely extract product name with fallback"""
        try:
            offer_intel = intelligence_data.get("offer_intelligence", {})
            if isinstance(offer_intel, dict):
                insights = offer_intel.get("insights", [])
                for insight in insights:
                    if "called" in str(insight).lower():
                        words = str(insight).split()
                        for i, word in enumerate(words):
                            if word.lower() == "called" and i + 1 < len(words):
                                return words[i + 1].upper().replace(",", "").replace(".", "")
        except Exception as e:
            logger.warning(f"⚠️ Product name extraction failed: {str(e)}")
        
        return "PRODUCT"


# Railway-compatible factory function
def create_railway_compatible_generator(content_type: str):
    """Create Railway-compatible generator instance"""
    
    handler = ContentHandler()
    
    async def generate_content_wrapper(intelligence_data: Dict[str, Any], preferences: Dict[str, Any] = None):
        """Wrapper function for Railway compatibility"""
        return await handler.generate_ultra_cheap_content(content_type, intelligence_data, preferences)
    
    return generate_content_wrapper


# Global compatibility handler instance
_global_compatibility_handler = None

def get_railway_compatibility_handler() -> ContentHandler:
    """Get global Railway compatibility handler"""
    global _global_compatibility_handler
    
    if _global_compatibility_handler is None:
        _global_compatibility_handler = ContentHandler()
    
    return _global_compatibility_handler


# Export functions for easy integration
async def railway_safe_generate_content(
    content_type: str,
    intelligence_data: Dict[str, Any], 
    preferences: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Railway-safe content generation with ultra-cheap AI"""
    
    handler = get_railway_compatibility_handler()
    return await handler.generate_ultra_cheap_content(content_type, intelligence_data, preferences)


# Backward compatibility aliases
railway_generate_email_sequence = lambda intelligence_data, preferences=None: railway_safe_generate_content("email_sequence", intelligence_data, preferences)
railway_generate_ad_copy = lambda intelligence_data, preferences=None: railway_safe_generate_content("ad_copy", intelligence_data, preferences)
railway_generate_social_media = lambda intelligence_data, preferences=None: railway_safe_generate_content("social_media", intelligence_data, preferences)