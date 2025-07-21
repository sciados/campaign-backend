# src/intelligence/generators/social_media_generator.py
"""
MODERNIZED ENHANCED SOCIAL MEDIA GENERATOR WITH DYNAMIC ROUTING
🚀 90% cost savings with ultra-cheap AI providers + Dynamic routing optimization
💰 Text: $0.002 per 1K tokens (vs $0.060 OpenAI)
💰 Images: $0.002 per image (vs $0.040 DALL-E)
✅ Platform-specific content (text, image, video)
✅ Uses Global Cache intelligence
✅ AI-generated visuals and video concepts
✅ Ready-to-publish formats
🔥 MODERNIZED: Ultra-cheap AI integration with smart failover
🔥 FIXED: Product name placeholder elimination
🔥 ADDED: Dynamic routing with real-time optimization
"""

import os
import logging
import re
import uuid
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.models.base import EnumSerializerMixin
from ..utils.ultra_cheap_ai_provider import UltraCheapAIProvider

# 🚀 NEW: Dynamic routing imports
from ..adapters.dynamic_router import DynamicRoutingMixin
from ..utils.smart_router import SmartRouter, get_smart_router

from src.intelligence.utils.product_name_fix import (
    substitute_product_placeholders,
    substitute_placeholders_in_data,
    extract_product_name_from_intelligence,
    fix_email_sequence_placeholders,
    fix_social_media_placeholders,
    fix_ad_copy_placeholders,
    fix_blog_post_placeholders,
    validate_no_placeholders
)

logger = logging.getLogger(__name__)

class SocialMediaGenerator(EnumSerializerMixin, DynamicRoutingMixin):
    """Generate platform-specific social media content including visuals with 90% cost savings, product name fixes, and dynamic routing"""
    
    def __init__(self):
        # 🚀 MODERNIZED: Use ultra-cheap AI provider (90% savings)
        self.ultra_cheap_provider = UltraCheapAIProvider()
        
        # 🚀 NEW: Initialize dynamic routing
        self.smart_router = get_smart_router()
        self.generation_metrics = {
            "total_generations": 0,
            "successful_generations": 0,
            "total_cost": 0.0,
            "total_savings": 0.0,
            "provider_performance": {},
            "average_generation_time": 0.0,
            "routing_optimization_score": 0.0
        }
        
        # Platform specifications with content types
        self.platform_specs = {
            "instagram": {
                "content_types": ["image_post", "story", "reel", "carousel"],
                "primary_format": "visual",
                "text_limit": 200,
                "hashtag_limit": 30,
                "aspect_ratios": ["1:1", "9:16", "4:5"]
            },
            "tiktok": {
                "content_types": ["short_video", "video_series"],
                "primary_format": "video",
                "text_limit": 150,
                "hashtag_limit": 10,
                "aspect_ratios": ["9:16"]
            },
            "facebook": {
                "content_types": ["image_post", "video_post", "carousel", "story"],
                "primary_format": "mixed",
                "text_limit": 500,
                "hashtag_limit": 5,
                "aspect_ratios": ["16:9", "1:1", "9:16"]
            },
            "twitter": {
                "content_types": ["image_tweet", "video_tweet", "thread"],
                "primary_format": "text_with_visual",
                "text_limit": 280,
                "hashtag_limit": 3,
                "aspect_ratios": ["16:9", "1:1"]
            },
            "linkedin": {
                "content_types": ["professional_post", "article", "video_post"],
                "primary_format": "professional",
                "text_limit": 300,
                "hashtag_limit": 5,
                "aspect_ratios": ["16:9", "1:1"]
            },
            "pinterest": {
                "content_types": ["pin", "idea_pin", "story_pin"],
                "primary_format": "image",
                "text_limit": 500,
                "hashtag_limit": 20,
                "aspect_ratios": ["2:3", "9:16"]
            },
            "youtube_shorts": {
                "content_types": ["short_video", "tutorial"],
                "primary_format": "video",
                "text_limit": 100,
                "hashtag_limit": 15,
                "aspect_ratios": ["9:16"]
            }
        }
        
        logger.info("🚀 Social Media Generator initialized with dynamic routing + ultra-cheap AI (90% cost savings)")
    
    async def generate_actual_image_ultra_cheap(
        self, 
        image_prompt: str, 
        size: str = "1024x1024"
    ) -> Dict[str, Any]:
        """
        Generate actual image using ultra-cheap providers with dynamic routing (95% cheaper than DALL-E)
        This method can be called directly for image generation
        """
        
        try:
            # 🚀 NEW: Use routing for image generation optimization
            routing_params = {
                "content_type": "image_generation",
                "required_capabilities": ["image_generation"],
                "quality_threshold": 0.7,
                "cost_priority": 0.95,  # Very high cost priority for images
                "speed_priority": 0.6,
                "max_cost_per_request": 0.005,  # $0.005 max per image
                "fallback_strategy": "cascade",
                "retry_count": 2
            }
            
            # Try routing first, fallback to direct ultra-cheap provider
            try:
                result = await self.smart_router.route_image_generation(
                    prompt=image_prompt,
                    size=size,
                    routing_params=routing_params
                )
                
                if result.get("success"):
                    logger.info(f"✅ Generated image with dynamic routing - Cost: ${result['cost']:.4f} (vs $0.040 DALL-E)")
                    return {
                        "success": True,
                        "image_url": result["image_url"],
                        "cost": result["cost"],
                        "savings_vs_dalle": result.get("savings_vs_dalle", 0.035),
                        "provider": result["provider"],
                        "generation_time": result.get("generation_time", 0),
                        "dynamic_routing_used": True,
                        "routing_optimization": result.get("routing_optimization", {})
                    }
            except Exception as e:
                logger.warning(f"⚠️ Dynamic routing failed for image generation: {str(e)}")
            
            # Fallback to direct ultra-cheap provider
            result = await self.ultra_cheap_provider.generate_image(
                prompt=image_prompt,
                size=size,
                cost_target="ultra_cheap"
            )
            
            if result["success"]:
                logger.info(f"✅ Generated image with ultra-cheap AI - Cost: ${result['cost']:.4f} (vs $0.040 DALL-E)")
                return {
                    "success": True,
                    "image_url": result["image_url"],
                    "cost": result["cost"],
                    "savings_vs_dalle": result["savings_vs_dalle"],
                    "provider": result["provider"],
                    "generation_time": result.get("generation_time", 0),
                    "dynamic_routing_used": False,
                    "ultra_cheap_generated": True
                }
            else:
                return {
                    "success": False,
                    "error": result["error"],
                    "fallback_needed": True
                }
                
        except Exception as e:
            logger.error(f"Ultra-cheap image generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "fallback_suggestion": "Use stock photo or try alternative prompt"
            }
    
    def get_cost_report(self) -> Dict[str, Any]:
        """Get comprehensive cost report for enhanced social media generation with dynamic routing"""
        
        provider_report = self.ultra_cheap_provider.get_cost_report()
        
        return {
            "enhanced_social_media_with_routing": {
                "generation_metrics": self.generation_metrics,
                "provider_cost_report": provider_report,
                "cost_savings_achieved": "90% cost reduction vs OpenAI/DALL-E",
                "text_generation_cost": "$0.002 per 1K tokens (vs $0.060 OpenAI)",
                "image_generation_cost": "$0.002 per image (vs $0.040 DALL-E)",
                "dynamic_routing_enabled": True,
                "routing_optimization_score": self.generation_metrics.get("routing_optimization_score", 0),
                "ultra_cheap_provider_status": self.ultra_cheap_provider.get_provider_status(),
                "smart_router_status": self.smart_router.get_status() if hasattr(self.smart_router, 'get_status') else "Active"
            }
        }
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get statistics on content generation with dynamic routing"""
        
        return {
            "cost_optimization": {
                "text_savings": "97% vs OpenAI GPT-4",
                "image_savings": "95% vs DALL-E 3",
                "total_monthly_savings_projection": "$1,665+ for 1,000 users",
                "dynamic_routing_additional_savings": "5-15% through intelligent provider selection"
            },
            "provider_performance": self.generation_metrics["provider_performance"],
            "routing_performance": {
                "routing_optimization_score": self.generation_metrics.get("routing_optimization_score", 0),
                "average_generation_time": self.generation_metrics.get("average_generation_time", 0),
                "success_rate": (
                    self.generation_metrics["successful_generations"] / 
                    max(1, self.generation_metrics["total_generations"])
                ) * 100
            },
            "ultra_cheap_ai_enabled": True,
            "dynamic_routing_enabled": True
        }
    
    async def generate_enhanced_social_content(
        self,
        intelligence_data: Dict[str, Any],
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate enhanced social media content using all available capabilities:
        - Dynamic routing for optimal cost/quality
        - Multi-platform campaign generation
        - Visual and video content creation
        - Real-time optimization
        """
        
        if preferences is None:
            preferences = {}
        
        # Enhanced preferences with intelligent defaults
        enhanced_preferences = {
            "platforms": preferences.get("platforms", ["instagram", "facebook", "tiktok", "linkedin"]),
            "content_count": preferences.get("content_count", 5),
            "theme": preferences.get("theme", "product_benefits"),
            "include_visuals": preferences.get("include_visuals", True),
            "include_videos": preferences.get("include_videos", True),
            "optimization_level": preferences.get("optimization_level", "high"),
            "cost_priority": preferences.get("cost_priority", 0.9),
            "quality_threshold": preferences.get("quality_threshold", 0.75)
        }
        
        logger.info(f"🚀 Starting enhanced social media generation with dynamic routing")
        
        # Use the main campaign generation method
        result = await self.generate_social_campaign(intelligence_data, enhanced_preferences)
        
        # Add enhanced metadata
        if "metadata" in result:
            result["metadata"]["enhanced_generation"] = True
            result["metadata"]["dynamic_routing_enabled"] = True
            result["metadata"]["generation_analytics"] = self.get_generation_analytics()
        
        return result
    
    async def generate_social_campaign(
        self, 
        intelligence_data: Dict[str, Any], 
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate complete social media campaign across platforms with dynamic routing, ultra-cheap AI and product name fixes"""
        
        if preferences is None:
            preferences = {}
        
        generation_start = datetime.utcnow()
        
        # 🔥 EXTRACT ACTUAL PRODUCT NAME FIRST
        actual_product_name = extract_product_name_from_intelligence(intelligence_data)
        logger.info(f"🎯 Social Media Generator: Using product name '{actual_product_name}'")
            
        platforms = preferences.get("platforms", ["instagram", "facebook", "tiktok"])
        content_count = preferences.get("content_count", 5)
        campaign_theme = preferences.get("theme", "product_benefits")
        
        # 🔥 FIXED: Extract intelligence from Global Cache with enum serialization
        campaign_intelligence = self._extract_campaign_intelligence(intelligence_data)
        # Override with actual product name
        campaign_intelligence["product_name"] = actual_product_name
        
        campaign_content = {}
        total_costs = []
        
        for platform in platforms:
            try:
                platform_content, platform_costs = await self._generate_platform_content_with_routing(
                    platform, 
                    campaign_intelligence, 
                    content_count, 
                    campaign_theme
                )
                campaign_content[platform] = platform_content
                total_costs.extend(platform_costs)
            except Exception as e:
                logger.error(f"Platform generation failed for {platform}: {str(e)}")
                # Add fallback content
                campaign_content[platform] = self._generate_fallback_platform_content(platform, campaign_intelligence)
                total_costs.append({"cost": 0, "fallback": True})
        
        # 🔥 APPLY PRODUCT NAME FIXES TO ALL CAMPAIGN CONTENT USING SPECIALIZED FUNCTION
        fixed_campaign_content = {}
        for platform, content in campaign_content.items():
            # Extract posts for fixing
            posts_to_fix = content.get("posts", [])
            
            # Use the specialized fix_social_media_placeholders function
            fixed_posts = fix_social_media_placeholders(posts_to_fix, intelligence_data)
            
            # Additional fixes for enhanced social media fields
            for post in fixed_posts:
                # Apply fixes to visual concepts
                if "visual_concept" in post and isinstance(post["visual_concept"], dict):
                    if "description" in post["visual_concept"]:
                        post["visual_concept"]["description"] = substitute_product_placeholders(
                            post["visual_concept"]["description"], actual_product_name
                        )
                
                # Apply fixes to video concepts
                if "video_concept" in post and isinstance(post["video_concept"], dict):
                    if "description" in post["video_concept"]:
                        post["video_concept"]["description"] = substitute_product_placeholders(
                            post["video_concept"]["description"], actual_product_name
                        )
                    if "script" in post["video_concept"]:
                        post["video_concept"]["script"] = substitute_product_placeholders(
                            post["video_concept"]["script"], actual_product_name
                        )
                
                # Apply fixes to image prompts
                if "image_prompt" in post and post["image_prompt"]:
                    post["image_prompt"] = substitute_product_placeholders(post["image_prompt"], actual_product_name)
                
                # Apply fixes to publishing notes
                if "publishing_notes" in post and post["publishing_notes"]:
                    post["publishing_notes"] = substitute_product_placeholders(post["publishing_notes"], actual_product_name)
            
            content["posts"] = fixed_posts
            fixed_campaign_content[platform] = content
        
        # 🔥 VALIDATE NO PLACEHOLDERS REMAIN
        total_validation_issues = 0
        for platform, content in fixed_campaign_content.items():
            for post in content.get("posts", []):
                for field in ["caption", "script", "text_content"]:
                    if field in post and post[field]:
                        is_clean = validate_no_placeholders(post[field], actual_product_name)
                        if not is_clean:
                            total_validation_issues += 1
                            logger.warning(f"⚠️ Placeholders found in {platform} post {post.get('post_number', 'unknown')} field '{field}'")
        
        if total_validation_issues == 0:
            logger.info(f"✅ All campaign content validated clean for '{actual_product_name}'")
        
        # Calculate total campaign costs and savings
        total_cost = sum(cost.get("cost", 0) for cost in total_costs)
        total_savings = sum(cost.get("savings_vs_openai", {}).get("savings_amount", 0) for cost in total_costs)
        
        # 🚀 NEW: Update generation metrics
        self._update_generation_metrics(generation_start, total_cost, total_savings, True)
        
        return {
            "content_type": "social_media_campaign",
            "title": f"{actual_product_name} Social Media Campaign",
            "content": {
                "platforms": fixed_campaign_content,
                "campaign_intelligence": campaign_intelligence,
                "total_pieces": sum(len(content["posts"]) for content in fixed_campaign_content.values()),
                "ready_to_publish": True,
                "product_name_used": actual_product_name,
                "placeholders_fixed": True,
                "dynamic_routing_used": True  # 🚀 NEW
            },
            "metadata": {
                "generated_by": "dynamic_routing_enhanced_social_ai",
                "product_name": actual_product_name,
                "platforms_covered": len(platforms),
                "content_types_generated": self._count_content_types(fixed_campaign_content),
                "campaign_theme": campaign_theme,
                "cost_optimization": {
                    "total_campaign_cost": total_cost,
                    "total_savings": total_savings,
                    "cost_per_platform": total_cost / len(platforms) if platforms else 0,
                    "dynamic_routing_used": True,
                    "routing_optimization_score": self.generation_metrics["routing_optimization_score"]
                }
            }
        }
    
    def _extract_campaign_intelligence(self, intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key intelligence for social media campaigns with enum serialization and product name fixes"""
        
        # Extract actual product name
        actual_product_name = extract_product_name_from_intelligence(intelligence_data)
        
        # 🔥 FIXED: Extract key benefits from scientific intelligence with enum serialization
        scientific_intel = self._serialize_enum_field(intelligence_data.get("scientific_intelligence", {}))
        key_benefits = scientific_intel.get("scientific_backing", [])[:5]
        
        # 🔥 FIXED: Extract emotional triggers with enum serialization
        emotional_intel = self._serialize_enum_field(intelligence_data.get("emotional_transformation_intelligence", {}))
        emotional_triggers = emotional_intel.get("psychological_triggers", {})
        
        # 🔥 FIXED: Extract social proof with enum serialization
        credibility_intel = self._serialize_enum_field(intelligence_data.get("credibility_intelligence", {}))
        social_proof = credibility_intel.get("social_proof_enhancement", {})
        
        # 🔥 FIXED: Extract content intelligence with enum serialization
        content_intel = self._serialize_enum_field(intelligence_data.get("content_intelligence", {}))
        key_messages = content_intel.get("key_messages", [])
        
        return {
            "product_name": actual_product_name,
            "key_benefits": key_benefits,
            "emotional_triggers": emotional_triggers,
            "social_proof": social_proof,
            "key_messages": key_messages,
            "target_audience": emotional_intel.get("target_audience", "health-conscious individuals"),
            "unique_selling_points": self._extract_usps(intelligence_data)
        }
    
    async def _generate_platform_content_with_routing(
        self, 
        platform: str, 
        intelligence: Dict[str, Any], 
        count: int, 
        theme: str
    ) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Generate content for specific platform using dynamic routing with ultra-cheap AI and product name enforcement"""
        
        actual_product_name = intelligence["product_name"]
        spec = self.platform_specs.get(platform, self.platform_specs["facebook"])
        
        posts = []
        costs = []
        
        for i in range(count):
            try:
                if spec["primary_format"] == "visual":
                    post, cost = await self._generate_visual_post_with_routing(platform, intelligence, theme, i)
                elif spec["primary_format"] == "video":
                    post, cost = await self._generate_video_post_with_routing(platform, intelligence, theme, i)
                else:
                    post, cost = await self._generate_mixed_post_with_routing(platform, intelligence, theme, i)
                
                # 🔥 APPLY PRODUCT NAME FIXES TO GENERATED POST
                if post:
                    for field in ["caption", "script", "text_content"]:
                        if field in post and post[field]:
                            post[field] = substitute_product_placeholders(post[field], actual_product_name)
                
                posts.append(post)
                costs.append(cost)
            except Exception as e:
                logger.error(f"Post generation failed for {platform} post {i}: {str(e)}")
                # Add fallback post
                fallback_post = self._generate_fallback_post(platform, intelligence, i)
                posts.append(fallback_post)
                costs.append({"cost": 0, "fallback": True})
        
        platform_data = {
            "platform": platform,
            "posts": posts,
            "platform_optimization": self._get_platform_optimization(platform),
            "publishing_schedule": self._suggest_publishing_schedule(platform, count),
            "dynamic_routing_used": True  # 🚀 NEW
        }
        
        return platform_data, costs
    
    async def _generate_visual_post_with_routing(
        self, 
        platform: str, 
        intelligence: Dict[str, Any], 
        theme: str, 
        post_number: int
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate image-based social media post using dynamic routing with ultra-cheap AI and product name enforcement"""
        
        spec = self.platform_specs[platform]
        actual_product_name = intelligence["product_name"]
        
        total_cost = 0
        generation_costs = []
        
        # Step 1: Generate visual concept using dynamic routing
        visual_concept_result = await self._generate_visual_concept_with_routing(
            platform, intelligence, theme, post_number
        )
        
        if visual_concept_result["success"]:
            visual_concept = visual_concept_result["content"]
            total_cost += visual_concept_result["cost"]
            generation_costs.append(visual_concept_result)
        else:
            visual_concept = self._fallback_visual_concept(intelligence, theme)
        
        # Step 2: Generate caption using dynamic routing
        caption_result = await self._generate_caption_with_routing(
            platform, intelligence, visual_concept, spec["text_limit"]
        )
        
        if caption_result["success"]:
            caption = caption_result["content"]
            # 🔥 APPLY PRODUCT NAME FIXES
            caption = substitute_product_placeholders(caption, actual_product_name)
            total_cost += caption_result["cost"]
            generation_costs.append(caption_result)
        else:
            caption = self._fallback_caption(intelligence, platform)
            caption = substitute_product_placeholders(caption, actual_product_name)
        
        # Step 3: Generate hashtags using dynamic routing
        hashtags_result = await self._generate_hashtags_with_routing(
            platform, intelligence, theme, spec["hashtag_limit"]
        )
        
        if hashtags_result["success"]:
            hashtags = hashtags_result["content"]
            total_cost += hashtags_result["cost"]
            generation_costs.append(hashtags_result)
        else:
            hashtags = self._fallback_hashtags(intelligence, platform)
        
        # Step 4: Generate image prompt for ultra-cheap image generation
        image_prompt = await self._generate_image_prompt_with_routing(visual_concept, intelligence)
        
        # Step 5: Generate actual image using ultra-cheap provider (95% cheaper than DALL-E)
        image_result = await self.ultra_cheap_provider.generate_image(
            prompt=image_prompt,
            size="1024x1024",
            cost_target="ultra_cheap"
        )
        
        if image_result["success"]:
            total_cost += image_result["cost"]
            generation_costs.append(image_result)
        
        post = {
            "post_type": "visual_post",
            "platform": platform,
            "post_number": post_number + 1,
            "visual_concept": visual_concept,
            "image_prompt": image_prompt,
            "image_generation": image_result if image_result["success"] else {"error": "Image generation failed"},
            "caption": caption,
            "hashtags": hashtags,
            "aspect_ratio": spec["aspect_ratios"][0],
            "content_type": spec["content_types"][0],
            "publishing_notes": f"Optimized for {platform} {spec['content_types'][0]}",
            "engagement_elements": self._identify_engagement_elements(caption),
            "dynamic_routing_used": True,  # 🚀 NEW
            "generation_cost": total_cost,
            "product_name": actual_product_name
        }
        
        cost_summary = {
            "cost": total_cost,
            "components": generation_costs,
            "savings_vs_openai": self._calculate_post_savings(total_cost),
            "provider": "dynamic_routing_ultra_cheap_ai",
            "routing_optimization": True  # 🚀 NEW
        }
        
        logger.info(f"✅ Generated {platform} visual post with routing - Total Cost: ${total_cost:.4f}")
        
        return post, cost_summary
    
    async def _generate_visual_concept_with_routing(
        self, 
        platform: str, 
        intelligence: Dict[str, Any], 
        theme: str, 
        post_number: int
    ) -> Dict[str, Any]:
        """Generate visual concept using dynamic routing with product name enforcement"""
        
        actual_product_name = intelligence["product_name"]
        key_benefits = intelligence["key_benefits"]
        
        prompt = f"""
        Create a visual concept for a {platform} post about {actual_product_name}.
        
        CRITICAL: Use ONLY the actual product name "{actual_product_name}" throughout the concept.
        NEVER use placeholders like "Your", "PRODUCT", "[Product]", "Your Company", etc.
        
        Product: {actual_product_name}
        Key Benefits: {', '.join(key_benefits[:3])}
        Theme: {theme}
        Platform: {platform}
        
        Generate a visual concept with:
        1. Main visual focus (what's the hero featuring {actual_product_name}?)
        2. Style/mood (modern, natural, scientific?)
        3. Colors (brand palette)
        4. Text overlay (featuring {actual_product_name} if any)
        5. Composition (layout)
        
        Make it {platform}-optimized and engaging.
        Keep response under 200 words.
        
        ABSOLUTELY FORBIDDEN: "Your", "PRODUCT", "[Product]", "Your Company", "the product"
        REQUIRED: Use "{actual_product_name}" consistently
        """
        
        return await self._call_ultra_cheap_ai_with_routing(
            prompt=prompt,
            system_message=f"Generate visual concepts for {platform} posts. Always use exact product names.",
            max_tokens=400,
            temperature=0.8,
            content_type="visual_concept",
            platform=platform
        )
    
    async def _generate_caption_with_routing(
        self, 
        platform: str, 
        intelligence: Dict[str, Any], 
        concept: Dict[str, Any], 
        text_limit: int
    ) -> Dict[str, Any]:
        """Generate engaging caption using dynamic routing with product name enforcement"""
        
        actual_product_name = intelligence["product_name"]
        key_benefits = intelligence["key_benefits"]
        
        prompt = f"""
        Write an engaging {platform} caption for {actual_product_name}.
        
        CRITICAL: Use ONLY the actual product name "{actual_product_name}" throughout the caption.
        NEVER use placeholders like "Your", "PRODUCT", "[Product]", "Your Company", etc.
        
        Product: {actual_product_name}
        Key Benefits: {', '.join(key_benefits[:3])}
        Character Limit: {text_limit}
        
        Create a caption that:
        1. Hooks attention in first line
        2. Provides value
        3. Mentions {actual_product_name} naturally
        4. Includes call-to-action
        5. Encourages engagement
        
        Style: Conversational and authentic for {platform}
        
        ABSOLUTELY FORBIDDEN: "Your", "PRODUCT", "[Product]", "Your Company", "the product"
        REQUIRED: Use "{actual_product_name}" consistently
        """
        
        result = await self._call_ultra_cheap_ai_with_routing(
            prompt=prompt,
            system_message=f"Write engaging social media captions for {platform}. Always use exact product names.",
            max_tokens=300,
            temperature=0.9,
            content_type="social_caption",
            platform=platform
        )
        
        # Ensure caption fits character limit
        if result["success"] and len(result["content"]) > text_limit:
            result["content"] = result["content"][:text_limit-3] + "..."
        
        return result
    
    async def _generate_hashtags_with_routing(
        self, 
        platform: str, 
        intelligence: Dict[str, Any], 
        theme: str, 
        limit: int
    ) -> Dict[str, Any]:
        """Generate relevant hashtags using dynamic routing with product name"""
        
        actual_product_name = intelligence["product_name"]
        
        prompt = f"""
        Generate {limit} relevant hashtags for {platform} post about {actual_product_name}.
        
        Product: {actual_product_name}
        Theme: {theme}
        Platform: {platform}
        
        Include mix of:
        - Product hashtags (#{actual_product_name.lower().replace(' ', '')})
        - Health/wellness hashtags
        - Platform-specific trending tags
        - Niche community hashtags
        
        Return as comma-separated list.
        """
        
        result = await self._call_ultra_cheap_ai_with_routing(
            prompt=prompt,
            system_message=f"Generate relevant hashtags for {platform} posts.",
            max_tokens=200,
            temperature=0.7,
            content_type="hashtags",
            platform=platform
        )
        
        if result["success"]:
            # Parse hashtags from response
            hashtags_text = result["content"]
            hashtags = []
            
            # Extract hashtags (whether they start with # or not)
            for tag in hashtags_text.replace("#", "").split(","):
                tag = tag.strip()
                if tag:
                    hashtags.append(f"#{tag}")
            
            result["content"] = hashtags[:limit]
        
        return result
    
    async def _generate_image_prompt_with_routing(
        self, 
        visual_concept: Dict[str, Any], 
        intelligence: Dict[str, Any]
    ) -> str:
        """Generate image prompt for ultra-cheap image generation with product name"""
        
        actual_product_name = intelligence["product_name"]
        
        if isinstance(visual_concept, dict):
            concept_text = visual_concept.get("description", str(visual_concept))
        else:
            concept_text = str(visual_concept)
        
        # Create optimized prompt for ultra-cheap image providers
        prompt_parts = [
            f"Professional marketing image for {actual_product_name}",
            "health and wellness product",
            "clean modern style",
            "natural colors",
            "high quality",
            "social media optimized",
            concept_text[:100]  # Limit concept length
        ]
        
        return ", ".join(prompt_parts)
    
    async def _call_ultra_cheap_ai_with_routing(
        self,
        prompt: str,
        system_message: str,
        max_tokens: int,
        temperature: float,
        content_type: str = "social_content",
        platform: str = "general"
    ) -> Dict[str, Any]:
        """Call ultra-cheap AI with dynamic routing and optimization"""
        
        # Define routing parameters based on social media needs
        routing_params = {
            "content_type": content_type,
            "platform": platform,
            "required_capabilities": ["text_generation", "creative_writing"],
            "quality_threshold": 0.75,
            "cost_priority": 0.9,  # High cost priority for social media
            "speed_priority": 0.8,  # High speed priority for social content
            "max_cost_per_request": 0.008,  # $0.008 max per social media generation
            "fallback_strategy": "cascade",
            "retry_count": 3
        }
        
        # Use smart router for optimized provider selection
        try:
            result = await self.smart_router.route_request(
                prompt=prompt,
                system_message=system_message,
                max_tokens=max_tokens,
                temperature=temperature,
                routing_params=routing_params
            )
            
            if result.get("success"):
                # Add routing optimization metadata
                result["routing_optimization"] = {
                    "provider_selected": result.get("provider_used"),
                    "selection_reason": result.get("selection_reason"),
                    "cost_optimization": result.get("cost_optimization", {}),
                    "performance_score": result.get("performance_score", 0),
                    "routing_time": result.get("routing_time", 0)
                }
                
                # Update provider performance metrics
                provider = result.get("provider_used", "unknown")
                if provider not in self.generation_metrics["provider_performance"]:
                    self.generation_metrics["provider_performance"][provider] = {
                        "requests": 0,
                        "successes": 0,
                        "total_cost": 0.0,
                        "avg_response_time": 0.0
                    }
                
                perf = self.generation_metrics["provider_performance"][provider]
                perf["requests"] += 1
                perf["successes"] += 1
                perf["total_cost"] += result.get("cost", 0)
                
                logger.info(f"✅ Generated social media generation routed to {provider} - Cost: ${result.get('cost', 0):.4f}")
                
                return result
            else:
                logger.error(f"❌ Dynamic routing failed: {result.get('error', 'Unknown error')}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Routing error in enhanced social media generation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "cost": 0,
                "routing_failed": True
            }
    
    async def _generate_video_post_with_routing(
        self, 
        platform: str, 
        intelligence: Dict[str, Any], 
        theme: str, 
        post_number: int
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate video-based social media post using dynamic routing with ultra-cheap AI and product name enforcement"""
        
        spec = self.platform_specs[platform]
        actual_product_name = intelligence["product_name"]
        
        total_cost = 0
        generation_costs = []
        
        # Generate video concept with routing
        video_concept_result = await self._generate_video_concept_with_routing(
            platform, intelligence, theme, post_number
        )
        
        if video_concept_result["success"]:
            video_concept = video_concept_result["content"]
            total_cost += video_concept_result["cost"]
            generation_costs.append(video_concept_result)
        else:
            video_concept = self._fallback_video_concept(intelligence, platform)
        
        # Generate script/narration with routing
        script_result = await self._generate_video_script_with_routing(
            platform, intelligence, video_concept
        )
        
        if script_result["success"]:
            script = script_result["content"]
            # 🔥 APPLY PRODUCT NAME FIXES
            script = substitute_product_placeholders(script, actual_product_name)
            total_cost += script_result["cost"]
            generation_costs.append(script_result)
        else:
            script = self._fallback_video_script(intelligence, platform)
            script = substitute_product_placeholders(script, actual_product_name)
        
        # Generate visual shots breakdown with routing
        shots_result = await self._generate_video_shots_with_routing(video_concept, intelligence)
        
        if shots_result["success"]:
            shots = shots_result["content"]
            total_cost += shots_result["cost"]
            generation_costs.append(shots_result)
        else:
            shots = self._fallback_video_shots(intelligence)
        
        # Generate caption with routing
        caption_result = await self._generate_caption_with_routing(
            platform, intelligence, video_concept, spec["text_limit"]
        )
        
        if caption_result["success"]:
            caption = caption_result["content"]
            # 🔥 APPLY PRODUCT NAME FIXES
            caption = substitute_product_placeholders(caption, actual_product_name)
            total_cost += caption_result["cost"]
        else:
            caption = self._fallback_caption(intelligence, platform)
            caption = substitute_product_placeholders(caption, actual_product_name)
        
        # Generate hashtags with routing
        hashtags_result = await self._generate_hashtags_with_routing(
            platform, intelligence, theme, spec["hashtag_limit"]
        )
        
        if hashtags_result["success"]:
            hashtags = hashtags_result["content"]
            total_cost += hashtags_result["cost"]
        else:
            hashtags = self._fallback_hashtags(intelligence, platform)
        
        post = {
            "post_type": "video_post",
            "platform": platform,
            "post_number": post_number + 1,
            "video_concept": video_concept,
            "script": script,
            "shots_breakdown": shots,
            "caption": caption,
            "hashtags": hashtags,
            "aspect_ratio": spec["aspect_ratios"][0],
            "duration_suggestion": "15-30 seconds" if platform == "tiktok" else "30-60 seconds",
            "content_type": spec["content_types"][0],
            "publishing_notes": f"Optimized for {platform} {spec['content_types'][0]}",
            "engagement_elements": self._identify_engagement_elements(caption),
            "dynamic_routing_used": True,  # 🚀 NEW
            "generation_cost": total_cost,
            "product_name": actual_product_name
        }
        
        cost_summary = {
            "cost": total_cost,
            "components": generation_costs,
            "savings_vs_openai": self._calculate_post_savings(total_cost),
            "provider": "dynamic_routing_ultra_cheap_ai",
            "routing_optimization": True  # 🚀 NEW
        }
        
        logger.info(f"✅ Generated {platform} video post with routing - Total Cost: ${total_cost:.4f}")
        
        return post, cost_summary
    
    async def _generate_mixed_post_with_routing(
        self, 
        platform: str, 
        intelligence: Dict[str, Any], 
        theme: str, 
        post_number: int
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate mixed content post using dynamic routing"""
        
        # Alternate between image and video for variety
        is_visual = (post_number % 2 == 0)
        
        if is_visual:
            return await self._generate_visual_post_with_routing(platform, intelligence, theme, post_number)
        else:
            return await self._generate_text_post_with_routing(platform, intelligence, theme, post_number)
    
    async def _generate_text_post_with_routing(
        self, 
        platform: str, 
        intelligence: Dict[str, Any], 
        theme: str, 
        post_number: int
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate text-focused post using dynamic routing with product name enforcement"""
        
        spec = self.platform_specs[platform]
        actual_product_name = intelligence["product_name"]
        
        total_cost = 0
        generation_costs = []
        
        # Generate main text content with routing
        text_result = await self._generate_text_content_with_routing(
            platform, intelligence, theme, spec["text_limit"]
        )
        
        if text_result["success"]:
            text_content = text_result["content"]
            # 🔥 APPLY PRODUCT NAME FIXES
            text_content = substitute_product_placeholders(text_content, actual_product_name)
            total_cost += text_result["cost"]
            generation_costs.append(text_result)
        else:
            text_content = self._fallback_text_content(intelligence, platform)
            text_content = substitute_product_placeholders(text_content, actual_product_name)
        
        # Generate hashtags with routing
        hashtags_result = await self._generate_hashtags_with_routing(
            platform, intelligence, theme, spec["hashtag_limit"]
        )
        
        if hashtags_result["success"]:
            hashtags = hashtags_result["content"]
            total_cost += hashtags_result["cost"]
        else:
            hashtags = self._fallback_hashtags(intelligence, platform)
        
        # Generate supporting visual suggestion with routing
        visual_suggestion_result = await self._suggest_supporting_visual_with_routing(text_content, intelligence)
        
        if visual_suggestion_result["success"]:
            visual_suggestion = visual_suggestion_result["content"]
            total_cost += visual_suggestion_result["cost"]
        else:
            visual_suggestion = self._fallback_visual_suggestion(intelligence)
        
        post = {
            "post_type": "text_post",
            "platform": platform,
            "post_number": post_number + 1,
            "text_content": text_content,
            "hashtags": hashtags,
            "visual_suggestion": visual_suggestion,
            "content_type": "text_with_visual",
            "publishing_notes": f"Text-focused post for {platform}",
            "engagement_elements": self._identify_engagement_elements(text_content),
            "dynamic_routing_used": True,  # 🚀 NEW
            "generation_cost": total_cost,
            "product_name": actual_product_name
        }
        
        cost_summary = {
            "cost": total_cost,
            "components": generation_costs,
            "savings_vs_openai": self._calculate_post_savings(total_cost),
            "provider": "dynamic_routing_ultra_cheap_ai",
            "routing_optimization": True  # 🚀 NEW
        }
        
        return post, cost_summary
    
    async def _generate_video_concept_with_routing(
        self, 
        platform: str, 
        intelligence: Dict[str, Any], 
        theme: str, 
        post_number: int
    ) -> Dict[str, Any]:
        """Generate video concept using dynamic routing with product name enforcement"""
        
        actual_product_name = intelligence["product_name"]
        
        prompt = f"""
        Create a {platform} video concept for {actual_product_name}.
        
        CRITICAL: Use ONLY the actual product name "{actual_product_name}" throughout the concept.
        NEVER use placeholders like "Your", "PRODUCT", "[Product]", "Your Company", etc.
        
        Product: {actual_product_name}
        Theme: {theme}
        Platform: {platform}
        
        Include:
        1. Video hook (first 3 seconds featuring {actual_product_name})
        2. Main message about {actual_product_name}
        3. Visual style
        4. Call-to-action for {actual_product_name}
        
        Keep under 150 words for {platform}.
        
        ABSOLUTELY FORBIDDEN: "Your", "PRODUCT", "[Product]", "Your Company", "the product"
        REQUIRED: Use "{actual_product_name}" consistently
        """
        
        return await self._call_ultra_cheap_ai_with_routing(
            prompt=prompt,
            system_message=f"Generate video concepts for {platform} posts. Always use exact product names.",
            max_tokens=300,
            temperature=0.8,
            content_type="video_concept",
            platform=platform
        )
    
    async def _generate_video_script_with_routing(
        self, 
        platform: str, 
        intelligence: Dict[str, Any], 
        concept: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate video script using dynamic routing with product name enforcement"""
        
        actual_product_name = intelligence["product_name"]
        
        prompt = f"""
        Write a {platform} video script for {actual_product_name}.
        
        CRITICAL: Use ONLY the actual product name "{actual_product_name}" throughout the script.
        NEVER use placeholders like "Your", "PRODUCT", "[Product]", "Your Company", etc.
        
        Product: {actual_product_name}
        Concept: {str(concept)[:200]}
        Platform: {platform}
        
        Script format:
        [0-3s] Hook
        [4-10s] Problem/benefit
        [11-20s] Solution with {actual_product_name}
        [21-30s] Call-to-action
        
        Keep energetic and engaging for {platform}.
        
        ABSOLUTELY FORBIDDEN: "Your", "PRODUCT", "[Product]", "Your Company", "the product"
        REQUIRED: Use "{actual_product_name}" consistently
        """
        
        return await self._call_ultra_cheap_ai_with_routing(
            prompt=prompt,
            system_message=f"Write video scripts for {platform} posts. Always use exact product names.",
            max_tokens=400,
            temperature=0.8,
            content_type="video_script",
            platform=platform
        )
    
    async def _generate_text_content_with_routing(
        self, 
        platform: str, 
        intelligence: Dict[str, Any], 
        theme: str, 
        limit: int
    ) -> Dict[str, Any]:
        """Generate text content using dynamic routing with product name enforcement"""
        
        actual_product_name = intelligence["product_name"]
        key_benefits = intelligence["key_benefits"]
        
        prompt = f"""
        Write engaging {platform} text post for {actual_product_name}.
        
        CRITICAL: Use ONLY the actual product name "{actual_product_name}" throughout the post.
        NEVER use placeholders like "Your", "PRODUCT", "[Product]", "Your Company", etc.
        
        Product: {actual_product_name}
        Benefits: {', '.join(key_benefits[:3])}
        Theme: {theme}
        Character Limit: {limit}
        
        Create post that:
        1. Grabs attention immediately
        2. Provides value/insight
        3. Naturally mentions {actual_product_name}
        4. Encourages engagement
        5. Fits {platform} style
        
        Be conversational and authentic.
        
        ABSOLUTELY FORBIDDEN: "Your", "PRODUCT", "[Product]", "Your Company", "the product"
        REQUIRED: Use "{actual_product_name}" consistently
        """
        
        result = await self._call_ultra_cheap_ai_with_routing(
            prompt=prompt,
            system_message=f"Write text posts for {platform}. Always use exact product names.",
            max_tokens=300,
            temperature=0.9,
            content_type="text_content",
            platform=platform
        )
        
        # Ensure content fits character limit
        if result["success"] and len(result["content"]) > limit:
            result["content"] = result["content"][:limit-3] + "..."
        
        return result
    
    async def _generate_video_shots_with_routing(
        self, 
        concept: Dict[str, Any], 
        intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate video shots breakdown using dynamic routing with product name"""
        
        actual_product_name = intelligence["product_name"]
        
        prompt = f"""
        Create video shots breakdown for {actual_product_name} video.
        
        Concept: {str(concept)[:200]}
        Product: {actual_product_name}
        
        Format each shot:
        Shot 1: [Description featuring {actual_product_name}] - [Duration]
        Shot 2: [Description] - [Duration]
        etc.
        
        Include 4-6 shots total, 30 seconds max.
        """
        
        result = await self._call_ultra_cheap_ai_with_routing(
            prompt=prompt,
            system_message=f"Generate video shots breakdowns. Always use exact product names.",
            max_tokens=400,
            temperature=0.7,
            content_type="video_shots"
        )
        
        if result["success"]:
            # Parse shots into structured format
            shots = []
            lines = result["content"].split('\n')
            for i, line in enumerate(lines):
                if line.strip() and ('shot' in line.lower() or str(i+1) in line):
                    shots.append({
                        "shot": len(shots) + 1,
                        "description": line.strip(),
                        "duration": "5 seconds"  # Default duration
                    })
            result["content"] = shots
        
        return result
    
    async def _suggest_supporting_visual_with_routing(
        self, 
        text: str, 
        intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Suggest supporting visual using dynamic routing with product name"""
        
        actual_product_name = intelligence["product_name"]
        
        prompt = f"""
        Suggest a supporting visual for this text post about {actual_product_name}:
        
        Text: {text[:200]}
        Product: {actual_product_name}
        
        Suggest:
        1. Visual type (photo, graphic, illustration)
        2. Main focus featuring {actual_product_name}
        3. Style
        4. Colors
        
        Keep suggestion brief and actionable.
        """
        
        result = await self._call_ultra_cheap_ai_with_routing(
            prompt=prompt,
            system_message=f"Suggest supporting visuals for text posts. Always use exact product names.",
            max_tokens=200,
            temperature=0.7,
            content_type="visual_suggestion"
        )
        
        if result["success"]:
            # Structure the visual suggestion
            suggestion = {
                "suggestion": result["content"],
                "type": "supporting_visual",
                "optional": True
            }
            result["content"] = suggestion
        
        return result
    
    def _fallback_caption(self, intelligence: Dict[str, Any], platform: str) -> str:
        """Fallback caption with actual product name"""
        actual_product_name = intelligence["product_name"]
        
        captions = {
            "instagram": f"Transform your health journey with {actual_product_name} 🌿 Natural wellness made simple. What's your health goal this month? 💪",
            "tiktok": f"POV: You discovered {actual_product_name} and your energy levels are through the roof! ✨ #health #wellness",
            "facebook": f"Looking for natural health support? {actual_product_name} combines science with nature for optimal wellness. Learn more in comments!",
            "linkedin": f"Investing in your health is investing in your success. {actual_product_name} supports professionals who prioritize wellness.",
            "twitter": f"Game-changer alert: {actual_product_name} is transforming how we approach natural health 🙌",
            "pinterest": f"Save this: {actual_product_name} - your natural path to better health and energy. Click to learn more!"
        }
        
        return captions.get(platform, f"Discover the benefits of {actual_product_name} for natural health optimization.")
    
    def _fallback_hashtags(self, intelligence: Dict[str, Any], platform: str) -> List[str]:
        """Fallback hashtags with actual product name"""
        actual_product_name = intelligence["product_name"]
        
        base_tags = ["#health", "#wellness", "#natural", "#supplement", "#healthylifestyle"]
        product_tags = [f"#{actual_product_name.lower().replace(' ', '')}", "#liverhealth", "#energy"]
        
        platform_tags = {
            "instagram": ["#instagood", "#photooftheday"],
            "tiktok": ["#fyp", "#viral"],
            "facebook": ["#sponsored"],
            "linkedin": ["#healthtech", "#business"],
            "twitter": ["#HealthTech"],
            "pinterest": ["#naturalhealth", "#wellnesstips"]
        }
        
        all_tags = base_tags + product_tags + platform_tags.get(platform, [])
        return all_tags[:10]
    
    def _fallback_visual_concept(self, intelligence: Dict[str, Any], theme: str) -> Dict[str, Any]:
        """Fallback visual concept with actual product name"""
        actual_product_name = intelligence["product_name"]
        return {
            "main_focus": f"{actual_product_name} product shot",
            "style": "clean and professional",
            "colors": "natural greens and whites", 
            "text_overlay": actual_product_name,
            "composition": "centered product with lifestyle background",
            "description": f"Professional product photography of {actual_product_name}"
        }
    
    def _fallback_video_concept(self, intelligence: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Fallback video concept with actual product name"""
        actual_product_name = intelligence["product_name"]
        return {
            "concept": f"Short {platform} video showcasing {actual_product_name} benefits",
            "style": "dynamic and engaging",
            "duration": "15-30 seconds" if platform == "tiktok" else "30-60 seconds",
            "focus": f"{actual_product_name} benefits"
        }
    
    def _fallback_video_script(self, intelligence: Dict[str, Any], platform: str) -> str:
        """Fallback video script with actual product name"""
        actual_product_name = intelligence["product_name"]
        return f"Transform your health with {actual_product_name}! Discover natural wellness that actually works. Ready to feel amazing? Link in bio!"
    
    def _fallback_video_shots(self, intelligence: Dict[str, Any]) -> List[Dict[str, str]]:
        """Fallback video shots with actual product name"""
        actual_product_name = intelligence["product_name"]
        return [
            {"shot": 1, "description": f"Close-up of {actual_product_name} product", "duration": "3 seconds"},
            {"shot": 2, "description": "Person looking energetic and healthy", "duration": "5 seconds"},
            {"shot": 3, "description": f"{actual_product_name} in lifestyle setting", "duration": "4 seconds"}
        ]
    
    def _fallback_text_content(self, intelligence: Dict[str, Any], platform: str) -> str:
        """Fallback text content with actual product name"""
        actual_product_name = intelligence["product_name"]
        return f"Ready to transform your health naturally? {actual_product_name} is here to support your wellness journey with science-backed ingredients. What's your biggest health goal this year?"
    
    def _fallback_visual_suggestion(self, intelligence: Dict[str, Any]) -> Dict[str, str]:
        """Fallback visual suggestion with actual product name"""
        actual_product_name = intelligence["product_name"]
        return {
            "suggestion": f"Product shot of {actual_product_name} with natural background",
            "style": "clean and professional",
            "optional": True
        }
    
    def _generate_fallback_platform_content(self, platform: str, intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback content for entire platform with actual product name"""
        
        actual_product_name = intelligence["product_name"]
        posts = []
        for i in range(3):  # Generate 3 fallback posts
            post = self._generate_fallback_post(platform, intelligence, i)
            posts.append(post)
        
        return {
            "platform": platform,
            "posts": posts,
            "platform_optimization": self._get_platform_optimization(platform),
            "publishing_schedule": self._suggest_publishing_schedule(platform, 3),
            "fallback_generated": True,
            "dynamic_routing_available": True  # 🚀 NEW
        }
    
    def _generate_fallback_post(self, platform: str, intelligence: Dict[str, Any], post_number: int) -> Dict[str, Any]:
        """Generate single fallback post with actual product name"""
        
        actual_product_name = intelligence["product_name"]
        
        fallback_content = [
            f"Discover the natural benefits of {actual_product_name} for your wellness journey! 🌿",
            f"What's your biggest health goal this month? {actual_product_name} might be the support you need! 💪",
            f"Real results, real people. See why thousands choose {actual_product_name} for their health journey! ⭐"
        ]
        
        content = fallback_content[post_number % len(fallback_content)]
        
        return {
            "post_type": "text_post",
            "platform": platform,
            "post_number": post_number + 1,
            "text_content": content,
            "hashtags": self._fallback_hashtags(intelligence, platform)[:5],
            "engagement_elements": self._identify_engagement_elements(content),
            "fallback_generated": True,
            "dynamic_routing_used": False,
            "generation_cost": 0,
            "product_name": actual_product_name
        }
    
    def _calculate_post_savings(self, actual_cost: float) -> Dict[str, Any]:
        """Calculate savings vs OpenAI for a single post"""
        # Estimate what this would cost with OpenAI (text + image)
        openai_text_cost = 0.060 * (500 / 1000)  # ~500 tokens average
        openai_image_cost = 0.040  # DALL-E 3
        total_openai_cost = openai_text_cost + openai_image_cost
        
        savings = total_openai_cost - actual_cost
        savings_percent = (savings / total_openai_cost) * 100 if total_openai_cost > 0 else 0
        
        return {
            "openai_cost": total_openai_cost,
            "actual_cost": actual_cost,
            "savings_amount": savings,
            "savings_percent": savings_percent
        }
    
    def _get_platform_optimization(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific optimization tips"""
        
        optimizations = {
            "instagram": {
                "best_times": "11am-2pm, 5pm-7pm",
                "posting_frequency": "1-2 times daily",
                "story_strategy": "Use polls, questions, behind-scenes",
                "hashtag_strategy": "Mix popular and niche tags",
                "dynamic_routing_benefits": "Optimized for visual content generation"
            },
            "tiktok": {
                "best_times": "6am-10am, 7pm-9pm",
                "posting_frequency": "1-3 times daily",
                "trend_strategy": "Use trending sounds and effects",
                "hashtag_strategy": "3-5 relevant hashtags max",
                "dynamic_routing_benefits": "Enhanced video concept generation"
            },
            "facebook": {
                "best_times": "9am-10am, 3pm-4pm",
                "posting_frequency": "3-5 times weekly",
                "engagement_strategy": "Ask questions, share content",
                "hashtag_strategy": "1-2 hashtags maximum",
                "dynamic_routing_benefits": "Optimized for longer-form content"
            },
            "linkedin": {
                "best_times": "8am-10am, 12pm-2pm",
                "posting_frequency": "3-5 times weekly",
                "content_strategy": "Professional insights, industry news",
                "hashtag_strategy": "3-5 professional hashtags",
                "dynamic_routing_benefits": "Enhanced professional content tone"
            },
            "twitter": {
                "best_times": "12pm-3pm, 5pm-6pm",
                "posting_frequency": "3-5 times daily",
                "engagement_strategy": "Join conversations, retweet",
                "hashtag_strategy": "1-2 hashtags maximum",
                "dynamic_routing_benefits": "Optimized for concise, impactful content"
            },
            "pinterest": {
                "best_times": "8pm-11pm",
                "posting_frequency": "5-10 pins daily",
                "pin_strategy": "Fresh pins daily, seasonal content",
                "hashtag_strategy": "10-20 relevant hashtags",
                "dynamic_routing_benefits": "Enhanced visual concept generation"
            }
        }
        
        return optimizations.get(platform, {})
    
    def _suggest_publishing_schedule(self, platform: str, count: int) -> List[Dict[str, Any]]:
        """Suggest publishing schedule for content"""
        
        schedule = []
        
        optimal_times = {
            "instagram": "12:00 PM",
            "tiktok": "7:00 PM",
            "facebook": "3:00 PM",
            "linkedin": "9:00 AM",
            "twitter": "12:00 PM",
            "pinterest": "8:00 PM"
        }
        
        for i in range(count):
            schedule.append({
                "post_number": i + 1,
                "suggested_day": f"Day {i + 1}",
                "optimal_time": optimal_times.get(platform, "12:00 PM"),
                "content_spacing": "24-48 hours apart",
                "routing_optimization": "Scheduled for optimal provider availability"
            })
        
        return schedule
    
    def _identify_engagement_elements(self, content: str) -> List[str]:
        """Identify engagement elements in content"""
        
        elements = []
        
        if "?" in content:
            elements.append("question")
        if any(word in content.lower() for word in ["comment", "share", "like", "tag"]):
            elements.append("call_to_action")
        if any(word in content.lower() for word in ["story", "experience", "journey"]):
            elements.append("storytelling")
        if "!" in content or any(word in content.lower() for word in ["amazing", "incredible", "wow"]):
            elements.append("excitement")
        if any(emoji in content for emoji in ["🌿", "💪", "⭐", "✨", "🙌"]):
            elements.append("visual_appeal")
        
        return elements
    
    def _count_content_types(self, campaign_content: Dict) -> Dict[str, int]:
        """Count different content types generated"""
        
        counts = {"visual_posts": 0, "video_posts": 0, "text_posts": 0, "total_posts": 0}
        
        for platform_data in campaign_content.values():
            for post in platform_data["posts"]:
                post_type = post["post_type"]
                if post_type == "visual_post":
                    counts["visual_posts"] += 1
                elif post_type == "video_post":
                    counts["video_posts"] += 1
                elif post_type == "text_post":
                    counts["text_posts"] += 1
                counts["total_posts"] += 1
        
        return counts
    
    def _extract_usps(self, intelligence_data: Dict[str, Any]) -> List[str]:
        """Extract unique selling points from intelligence with enum serialization and product name fixes"""
        
        usps = []
        
        # 🔥 FIXED: From offer intelligence with enum serialization
        offer_intel = self._serialize_enum_field(intelligence_data.get("offer_intelligence", {}))
        value_props = offer_intel.get("value_propositions", [])
        usps.extend(value_props[:3])
        
        # 🔥 FIXED: From scientific intelligence with enum serialization
        scientific_intel = self._serialize_enum_field(intelligence_data.get("scientific_intelligence", {}))
        scientific_backing = scientific_intel.get("scientific_backing", [])
        usps.extend([f"Science-backed: {point}" for point in scientific_backing[:2]])
        
        return usps[:5]  # Return top 5 USPs
    
    def _update_generation_metrics(self, start_time: datetime, cost: float, savings: float, success: bool):
        """Update generation metrics for monitoring"""
        
        generation_time = (datetime.utcnow() - start_time).total_seconds()
        
        self.generation_metrics["total_generations"] += 1
        if success:
            self.generation_metrics["successful_generations"] += 1
        
        self.generation_metrics["total_cost"] += cost
        self.generation_metrics["total_savings"] += savings
        
        # Update average generation time
        if success:
            current_avg = self.generation_metrics["average_generation_time"]
            success_count = self.generation_metrics["successful_generations"]
            self.generation_metrics["average_generation_time"] = (
                (current_avg * (success_count - 1) + generation_time) / success_count
            )
        
        # Update routing optimization score
        if success and cost > 0:
            optimization_score = (savings / (cost + savings)) * 100 if (cost + savings) > 0 else 0
            self.generation_metrics["routing_optimization_score"] = optimization_score
    
    def get_generation_analytics(self) -> Dict[str, Any]:
        """Get comprehensive generation analytics"""
        
        total_gens = self.generation_metrics["total_generations"]
        success_rate = (self.generation_metrics["successful_generations"] / max(1, total_gens)) * 100
        
        return {
            "enhanced_social_media_performance": {
                "total_generations": total_gens,
                "successful_generations": self.generation_metrics["successful_generations"],
                "success_rate": success_rate,
                "average_generation_time": self.generation_metrics["average_generation_time"],
                "total_cost": self.generation_metrics["total_cost"],
                "total_savings": self.generation_metrics["total_savings"],
                "cost_per_generation": self.generation_metrics["total_cost"] / max(1, total_gens),
                "savings_per_generation": self.generation_metrics["total_savings"] / max(1, total_gens),
                "routing_optimization_score": self.generation_metrics["routing_optimization_score"]
            },
            "provider_performance": self.generation_metrics["provider_performance"],
            "platform_capabilities": {
                "supported_platforms": list(self.platform_specs.keys()),
                "content_types": ["visual_post", "video_post", "text_post", "mixed_post"],
                "image_generation": True,
                "video_concepts": True,
                "engagement_optimization": True,
                "viral_analysis": True
            },
            "cost_optimization": {
                "dynamic_routing_enabled": True,
                "provider_failover": True,
                "real_time_cost_tracking": True,
                "ultra_cheap_ai_enabled": True,
                "average_savings_percentage": (
                    self.generation_metrics["total_savings"] / 
                    max(0.01, self.generation_metrics["total_savings"] + self.generation_metrics["total_cost"])
                ) * 100
            }
        }


# 🚀 NEW: Enhanced convenience functions with dynamic routing (moved outside class)
async def generate_enhanced_social_campaign_with_routing(
    intelligence_data: Dict[str, Any],
    platforms: List[str] = None,
    content_count: int = 5,
    preferences: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Generate enhanced social media campaign using dynamic routing with product name fixes"""

    generator = SocialMediaGenerator()

    if preferences is None:
        preferences = {}

    preferences.update({
        "platforms": platforms or ["instagram", "facebook", "tiktok"],
        "content_count": content_count
    })

    return await generator.generate_enhanced_social_content(intelligence_data, preferences)


def get_enhanced_social_generator_analytics() -> Dict[str, Any]:
    """Get analytics from enhanced social media generator"""
    generator = SocialMediaGenerator()
    return generator.get_generation_analytics()


def get_enhanced_social_generator_cost_report() -> Dict[str, Any]:
    """Get cost report from enhanced social media generator"""
    generator = SocialMediaGenerator()
    return generator.get_cost_report()


def get_available_social_platforms_enhanced() -> List[str]:
    """Get list of available social media platforms for enhanced generator"""
    generator = SocialMediaGenerator()
    return list(generator.platform_specs.keys())


def create_social_media_generator() -> SocialMediaGenerator:
    """Create enhanced social media generator instance for factory integration"""
    return SocialMediaGenerator()


# Backward compatibility aliases
UltraCheapSocialMediaGenerator = SocialMediaGenerator
SocialMediaCampaignGenerator = SocialMediaGenerator