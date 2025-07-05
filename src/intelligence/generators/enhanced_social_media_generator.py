# src/intelligence/generators/enhanced_social_media_generator.py
"""
ENHANCED SOCIAL MEDIA GENERATOR
✅ Platform-specific content (text, image, video)
✅ Uses Global Cache intelligence
✅ AI-generated visuals and video concepts
✅ Ready-to-publish formats
🔥 FIXED: Enum serialization issues resolved
"""

import os
import logging
import re
import uuid
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.models.base import EnumSerializerMixin

logger = logging.getLogger(__name__)

class EnhancedSocialMediaGenerator(EnumSerializerMixin):
    """Generate platform-specific social media content including visuals"""
    
    def __init__(self):
        self.ai_providers = self._initialize_ai_providers()
        
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
        
    def _initialize_ai_providers(self):
        """Initialize AI providers"""
        providers = []
        
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                import openai
                providers.append({
                    "name": "openai",
                    "client": openai.AsyncOpenAI(api_key=api_key),
                    "models": ["gpt-4", "dall-e-3"],
                    "capabilities": ["text", "image_generation", "creative_concepts"]
                })
                logger.info("✅ OpenAI provider initialized for enhanced social media")
        except Exception as e:
            logger.warning(f"OpenAI not available: {str(e)}")
            
        return providers
    
    async def generate_social_campaign(
        self, 
        intelligence_data: Dict[str, Any], 
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate complete social media campaign across platforms"""
        
        if preferences is None:
            preferences = {}
            
        platforms = preferences.get("platforms", ["instagram", "facebook", "tiktok"])
        content_count = preferences.get("content_count", 5)
        campaign_theme = preferences.get("theme", "product_benefits")
        
        # 🔥 FIXED: Extract intelligence from Global Cache with enum serialization
        campaign_intelligence = self._extract_campaign_intelligence(intelligence_data)
        
        campaign_content = {}
        
        for platform in platforms:
            platform_content = await self._generate_platform_content(
                platform, 
                campaign_intelligence, 
                content_count, 
                campaign_theme
            )
            campaign_content[platform] = platform_content
        
        return {
            "content_type": "social_media_campaign",
            "title": f"{campaign_intelligence['product_name']} Social Media Campaign",
            "content": {
                "platforms": campaign_content,
                "campaign_intelligence": campaign_intelligence,
                "total_pieces": sum(len(content["posts"]) for content in campaign_content.values()),
                "ready_to_publish": True
            },
            "metadata": {
                "generated_by": "enhanced_social_ai",
                "product_name": campaign_intelligence["product_name"],
                "platforms_covered": len(platforms),
                "content_types_generated": self._count_content_types(campaign_content),
                "campaign_theme": campaign_theme
            }
        }
    
    def _extract_campaign_intelligence(self, intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key intelligence for social media campaigns with enum serialization"""
        
        # Extract product name
        product_name = self._extract_product_name(intelligence_data)
        
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
            "product_name": product_name,
            "key_benefits": key_benefits,
            "emotional_triggers": emotional_triggers,
            "social_proof": social_proof,
            "key_messages": key_messages,
            "target_audience": emotional_intel.get("target_audience", "health-conscious individuals"),
            "unique_selling_points": self._extract_usps(intelligence_data)
        }
    
    async def _generate_platform_content(
        self, 
        platform: str, 
        intelligence: Dict[str, Any], 
        count: int, 
        theme: str
    ) -> Dict[str, Any]:
        """Generate content for specific platform"""
        
        spec = self.platform_specs.get(platform, self.platform_specs["facebook"])
        
        posts = []
        
        for i in range(count):
            if spec["primary_format"] == "visual":
                post = await self._generate_visual_post(platform, intelligence, theme, i)
            elif spec["primary_format"] == "video":
                post = await self._generate_video_post(platform, intelligence, theme, i)
            else:
                post = await self._generate_mixed_post(platform, intelligence, theme, i)
            
            posts.append(post)
        
        return {
            "platform": platform,
            "posts": posts,
            "platform_optimization": self._get_platform_optimization(platform),
            "publishing_schedule": self._suggest_publishing_schedule(platform, count)
        }
    
    async def _generate_visual_post(
        self, 
        platform: str, 
        intelligence: Dict[str, Any], 
        theme: str, 
        post_number: int
    ) -> Dict[str, Any]:
        """Generate image-based social media post"""
        
        spec = self.platform_specs[platform]
        product_name = intelligence["product_name"]
        
        # Generate visual concept first
        visual_concept = await self._generate_visual_concept(
            platform, intelligence, theme, post_number
        )
        
        # Generate caption
        caption = await self._generate_caption(
            platform, intelligence, visual_concept, spec["text_limit"]
        )
        
        # Generate hashtags
        hashtags = await self._generate_hashtags(
            platform, intelligence, theme, spec["hashtag_limit"]
        )
        
        # Generate image prompt for DALL-E or other AI
        image_prompt = await self._generate_image_prompt(visual_concept, intelligence)
        
        return {
            "post_type": "visual_post",
            "platform": platform,
            "post_number": post_number + 1,
            "visual_concept": visual_concept,
            "image_prompt": image_prompt,
            "caption": caption,
            "hashtags": hashtags,
            "aspect_ratio": spec["aspect_ratios"][0],
            "content_type": spec["content_types"][0],
            "publishing_notes": f"Optimized for {platform} {spec['content_types'][0]}",
            "engagement_elements": self._identify_engagement_elements(caption)
        }
    
    async def _generate_video_post(
        self, 
        platform: str, 
        intelligence: Dict[str, Any], 
        theme: str, 
        post_number: int
    ) -> Dict[str, Any]:
        """Generate video-based social media post"""
        
        spec = self.platform_specs[platform]
        product_name = intelligence["product_name"]
        
        # Generate video concept
        video_concept = await self._generate_video_concept(
            platform, intelligence, theme, post_number
        )
        
        # Generate script/narration
        script = await self._generate_video_script(
            platform, intelligence, video_concept
        )
        
        # Generate visual shots breakdown
        shots = await self._generate_video_shots(video_concept, intelligence)
        
        # Generate caption
        caption = await self._generate_caption(
            platform, intelligence, video_concept, spec["text_limit"]
        )
        
        # Generate hashtags
        hashtags = await self._generate_hashtags(
            platform, intelligence, theme, spec["hashtag_limit"]
        )
        
        return {
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
            "engagement_elements": self._identify_engagement_elements(caption)
        }
    
    async def _generate_mixed_post(
        self, 
        platform: str, 
        intelligence: Dict[str, Any], 
        theme: str, 
        post_number: int
    ) -> Dict[str, Any]:
        """Generate mixed content post (text + visual)"""
        
        spec = self.platform_specs[platform]
        
        # Alternate between image and video
        is_visual = (post_number % 2 == 0)
        
        if is_visual:
            return await self._generate_visual_post(platform, intelligence, theme, post_number)
        else:
            # Generate text-focused post with optional visual
            return await self._generate_text_post(platform, intelligence, theme, post_number)
    
    async def _generate_text_post(
        self, 
        platform: str, 
        intelligence: Dict[str, Any], 
        theme: str, 
        post_number: int
    ) -> Dict[str, Any]:
        """Generate text-focused post with optional visual support"""
        
        spec = self.platform_specs[platform]
        product_name = intelligence["product_name"]
        
        # Generate main text content
        text_content = await self._generate_text_content(
            platform, intelligence, theme, spec["text_limit"]
        )
        
        # Generate hashtags
        hashtags = await self._generate_hashtags(
            platform, intelligence, theme, spec["hashtag_limit"]
        )
        
        # Optional: suggest supporting visual
        visual_suggestion = await self._suggest_supporting_visual(text_content, intelligence)
        
        return {
            "post_type": "text_post",
            "platform": platform,
            "post_number": post_number + 1,
            "text_content": text_content,
            "hashtags": hashtags,
            "visual_suggestion": visual_suggestion,
            "content_type": "text_with_visual",
            "publishing_notes": f"Text-focused post for {platform}",
            "engagement_elements": self._identify_engagement_elements(text_content)
        }
    
    async def _generate_visual_concept(
        self, 
        platform: str, 
        intelligence: Dict[str, Any], 
        theme: str, 
        post_number: int
    ) -> Dict[str, Any]:
        """Generate visual concept using AI"""
        
        provider = self.ai_providers[0] if self.ai_providers else None
        if not provider:
            return self._fallback_visual_concept(intelligence, theme)
        
        product_name = intelligence["product_name"]
        key_benefits = intelligence["key_benefits"]
        
        prompt = f"""
        Create a visual concept for a {platform} post about {product_name}.
        
        Product: {product_name}
        Key Benefits: {', '.join(key_benefits[:3])}
        Theme: {theme}
        Platform: {platform}
        
        Generate a visual concept that includes:
        1. Main visual focus (what's the hero of the image?)
        2. Style/mood (modern, natural, scientific, lifestyle?)
        3. Colors (brand-appropriate color palette)
        4. Text overlay (if any)
        5. Composition (layout and focus points)
        
        Make it {platform}-optimized and engaging for health-conscious audience.
        """
        
        try:
            if provider["name"] == "openai":
                response = await provider["client"].chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": f"You are a visual content strategist creating {platform} content concepts."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=500
                )
                
                concept_text = response.choices[0].message.content
                return self._parse_visual_concept(concept_text, intelligence)
        
        except Exception as e:
            logger.error(f"Visual concept generation failed: {str(e)}")
            return self._fallback_visual_concept(intelligence, theme)
    
    async def _generate_image_prompt(
        self, 
        visual_concept: Dict[str, Any], 
        intelligence: Dict[str, Any]
    ) -> str:
        """Generate DALL-E prompt from visual concept"""
        
        product_name = intelligence["product_name"]
        
        # Create detailed prompt for image generation
        prompt_parts = [
            f"Professional marketing image for {product_name}",
            visual_concept.get("main_focus", "product showcase"),
            f"Style: {visual_concept.get('style', 'modern and clean')}",
            f"Colors: {visual_concept.get('colors', 'natural health-focused palette')}",
            "High quality, social media optimized",
            "No text overlay"  # We'll add text separately
        ]
        
        return ", ".join(prompt_parts)
    
    async def generate_actual_image(
        self, 
        image_prompt: str, 
        size: str = "1024x1024"
    ) -> Dict[str, Any]:
        """Generate actual image using DALL-E 3"""
        
        provider = self.ai_providers[0] if self.ai_providers else None
        if not provider or "dall-e-3" not in provider.get("models", []):
            return {
                "error": "DALL-E 3 not available",
                "fallback_suggestion": "Use stock photo or manual creation"
            }
        
        try:
            response = await provider["client"].images.generate(
                model="dall-e-3",
                prompt=image_prompt,
                size=size,
                quality="standard",
                n=1
            )
            
            return {
                "success": True,
                "image_url": response.data[0].url,
                "revised_prompt": response.data[0].revised_prompt,
                "original_prompt": image_prompt,
                "cost": 0.040,
                "download_instructions": "Download and save locally for social media use"
            }
            
        except Exception as e:
            logger.error(f"DALL-E image generation failed: {str(e)}")
            return {
                "error": str(e),
                "fallback_suggestion": "Use stock photo or try alternative prompt"
            }
    
    async def _generate_caption(
        self, 
        platform: str, 
        intelligence: Dict[str, Any], 
        concept: Dict[str, Any], 
        text_limit: int
    ) -> str:
        """Generate engaging caption for the post"""
        
        provider = self.ai_providers[0] if self.ai_providers else None
        if not provider:
            return self._fallback_caption(intelligence, platform)
        
        product_name = intelligence["product_name"]
        key_benefits = intelligence["key_benefits"]
        
        prompt = f"""
        Write an engaging {platform} caption for {product_name}.
        
        Product: {product_name}
        Key Benefits: {', '.join(key_benefits[:3])}
        Visual Concept: {concept.get('description', 'Product focused')}
        Character Limit: {text_limit}
        
        Create a caption that:
        1. Hooks attention in first line
        2. Provides value or insight
        3. Naturally mentions {product_name}
        4. Includes a call-to-action
        5. Encourages engagement
        
        Platform: {platform}
        Style: Conversational and authentic
        """
        
        try:
            if provider["name"] == "openai":
                response = await provider["client"].chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": f"Write engaging {platform} captions that drive engagement."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.9,
                    max_tokens=300
                )
                
                caption = response.choices[0].message.content.strip()
                
                # Ensure it's within character limit
                if len(caption) > text_limit:
                    caption = caption[:text_limit-3] + "..."
                
                return caption
        
        except Exception as e:
            logger.error(f"Caption generation failed: {str(e)}")
            return self._fallback_caption(intelligence, platform)
    
    async def _generate_hashtags(
        self, 
        platform: str, 
        intelligence: Dict[str, Any], 
        theme: str, 
        limit: int
    ) -> List[str]:
        """Generate relevant hashtags"""
        
        product_name = intelligence["product_name"]
        
        # Base hashtags for health products
        base_tags = [
            "#health", "#wellness", "#natural", "#healthy", "#fitness",
            "#nutrition", "#supplement", "#healthylifestyle", "#wellbeing"
        ]
        
        # Product-specific tags
        product_tags = [
            f"#{product_name.lower()}",
            "#liverhealth", "#detox", "#energy", "#metabolism"
        ]
        
        # Platform-specific trending tags
        platform_tags = {
            "instagram": ["#instagood", "#photooftheday", "#healthylife"],
            "tiktok": ["#fyp", "#viral", "#healthtips"],
            "facebook": ["#sponsored", "#ad"],
            "linkedin": ["#healthtech", "#business", "#professional"],
            "twitter": ["#HealthTech", "#WellnessTips"],
            "pinterest": ["#healthyrecipes", "#wellnesstips", "#naturalhealth"]
        }
        
        # Combine and select best hashtags
        all_tags = base_tags + product_tags + platform_tags.get(platform, [])
        
        # Return top hashtags up to limit
        return all_tags[:limit]
    
    def _fallback_visual_concept(self, intelligence: Dict[str, Any], theme: str) -> Dict[str, Any]:
        """Fallback visual concept when AI fails"""
        
        return {
            "main_focus": f"{intelligence['product_name']} product shot",
            "style": "clean and professional",
            "colors": "natural greens and whites",
            "text_overlay": intelligence['product_name'],
            "composition": "centered product with lifestyle background",
            "description": f"Professional product photography of {intelligence['product_name']}"
        }
    
    def _fallback_caption(self, intelligence: Dict[str, Any], platform: str) -> str:
        """Fallback caption when AI fails"""
        
        product_name = intelligence["product_name"]
        
        captions = {
            "instagram": f"Transform your health journey with {product_name} 🌿 Natural wellness made simple. What's your health goal this month? 💪",
            "tiktok": f"POV: You discovered {product_name} and your energy levels are through the roof! ✨ #health #wellness",
            "facebook": f"Looking for natural health support? {product_name} combines science with nature for optimal wellness. Learn more in comments!",
            "linkedin": f"Investing in your health is investing in your success. {product_name} supports professionals who prioritize wellness.",
            "twitter": f"Game-changer alert: {product_name} is transforming how we approach natural health 🙌",
            "pinterest": f"Save this: {product_name} - your natural path to better health and energy. Click to learn more!"
        }
        
        return captions.get(platform, f"Discover the benefits of {product_name} for natural health optimization.")
    
    def _parse_visual_concept(self, concept_text: str, intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI-generated visual concept"""
        
        # Simple parsing - extract key elements
        lines = concept_text.split('\n')
        
        concept = {
            "description": concept_text,
            "main_focus": "product showcase",
            "style": "modern and clean",
            "colors": "health-focused palette",
            "text_overlay": intelligence["product_name"],
            "composition": "professional layout"
        }
        
        # Try to extract specific elements
        for line in lines:
            line = line.strip()
            if "focus:" in line.lower():
                concept["main_focus"] = line.split(":", 1)[1].strip()
            elif "style:" in line.lower():
                concept["style"] = line.split(":", 1)[1].strip()
            elif "color" in line.lower():
                concept["colors"] = line.split(":", 1)[1].strip()
        
        return concept
    
    def _get_platform_optimization(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific optimization tips"""
        
        optimizations = {
            "instagram": {
                "best_times": "11am-2pm, 5pm-7pm",
                "posting_frequency": "1-2 times daily",
                "story_strategy": "Use polls, questions, behind-scenes",
                "hashtag_strategy": "Mix popular and niche tags"
            },
            "tiktok": {
                "best_times": "6am-10am, 7pm-9pm",
                "posting_frequency": "1-3 times daily",
                "trend_strategy": "Use trending sounds and effects",
                "hashtag_strategy": "3-5 relevant hashtags max"
            },
            "facebook": {
                "best_times": "9am-10am, 3pm-4pm",
                "posting_frequency": "3-5 times weekly",
                "engagement_strategy": "Ask questions, share content",
                "hashtag_strategy": "1-2 hashtags maximum"
            }
        }
        
        return optimizations.get(platform, {})
    
    def _suggest_publishing_schedule(self, platform: str, count: int) -> List[Dict[str, Any]]:
        """Suggest publishing schedule for content"""
        
        # Simple scheduling logic
        schedule = []
        
        for i in range(count):
            schedule.append({
                "post_number": i + 1,
                "suggested_day": f"Day {i + 1}",
                "optimal_time": self._get_optimal_time(platform),
                "content_spacing": "24 hours apart"
            })
        
        return schedule
    
    def _get_optimal_time(self, platform: str) -> str:
        """Get optimal posting time for platform"""
        
        times = {
            "instagram": "12:00 PM",
            "tiktok": "7:00 PM", 
            "facebook": "3:00 PM",
            "linkedin": "9:00 AM",
            "twitter": "12:00 PM",
            "pinterest": "8:00 PM"
        }
        
        return times.get(platform, "12:00 PM")
    
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
        
        return elements
    
    def _count_content_types(self, campaign_content: Dict) -> Dict[str, int]:
        """Count different content types generated"""
        
        counts = {"visual_posts": 0, "video_posts": 0, "text_posts": 0}
        
        for platform_data in campaign_content.values():
            for post in platform_data["posts"]:
                post_type = post["post_type"]
                if post_type == "visual_post":
                    counts["visual_posts"] += 1
                elif post_type == "video_post":
                    counts["video_posts"] += 1
                elif post_type == "text_post":
                    counts["text_posts"] += 1
        
        return counts
    
    def _extract_product_name(self, intelligence_data: Dict[str, Any]) -> str:
        """Extract product name from intelligence data"""
        
        # Try multiple sources for product name
        if "product_name" in intelligence_data:
            return intelligence_data["product_name"]
        
        # 🔥 FIXED: Use enum serialization for offer intelligence
        offer_intel = self._serialize_enum_field(intelligence_data.get("offer_intelligence", {}))
        insights = offer_intel.get("insights", [])
        
        for insight in insights:
            if "called" in str(insight).lower():
                words = str(insight).split()
                for i, word in enumerate(words):
                    if word.lower() == "called" and i + 1 < len(words):
                        return words[i + 1].upper().replace(",", "").replace(".", "")
        
        return "PRODUCT"
    
    def _extract_usps(self, intelligence_data: Dict[str, Any]) -> List[str]:
        """Extract unique selling points from intelligence with enum serialization"""
        
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
    
    # Additional helper methods for video content
    async def _generate_video_concept(self, platform: str, intelligence: Dict[str, Any], theme: str, post_number: int) -> Dict[str, Any]:
        """Generate video concept for platform"""
        return {
            "concept": f"Short {platform} video showcasing {intelligence['product_name']} benefits",
            "style": "dynamic and engaging",
            "duration": "15-30 seconds" if platform == "tiktok" else "30-60 seconds",
            "focus": theme
        }
    
    async def _generate_video_script(self, platform: str, intelligence: Dict[str, Any], concept: Dict[str, Any]) -> str:
        """Generate video script"""
        product_name = intelligence["product_name"]
        return f"Transform your health with {product_name}! Discover natural wellness that actually works. Ready to feel amazing? Link in bio!"
    
    async def _generate_video_shots(self, concept: Dict[str, Any], intelligence: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate video shots breakdown"""
        return [
            {"shot": 1, "description": f"Close-up of {intelligence['product_name']} product", "duration": "3 seconds"},
            {"shot": 2, "description": "Person looking energetic and healthy", "duration": "5 seconds"},
            {"shot": 3, "description": "Product in lifestyle setting", "duration": "4 seconds"}
        ]
    
    async def _generate_text_content(self, platform: str, intelligence: Dict[str, Any], theme: str, limit: int) -> str:
        """Generate text content for platform"""
        product_name = intelligence["product_name"]
        content = f"Ready to transform your health naturally? {product_name} is here to support your wellness journey with science-backed ingredients. What's your biggest health goal this year?"
        
        if len(content) > limit:
            content = content[:limit-3] + "..."
        
        return content
    
    async def _suggest_supporting_visual(self, text: str, intelligence: Dict[str, Any]) -> Dict[str, str]:
        """Suggest supporting visual for text post"""
        return {
            "suggestion": f"Product shot of {intelligence['product_name']} with natural background",
            "style": "clean and professional",
            "optional": True
        }