# src/content/generators/social_media_generator.py
"""
AI-Powered Social Media Content Generator with Intelligence Integration
Uses modular architecture: Intelligence → Prompt → AI → Content
"""

import logging
import re
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone
from uuid import UUID

from src.content.services.prompt_generation_service import (
    PromptGenerationService,
    ContentType,
    SalesPsychologyStage
)
from src.content.services.ai_provider_service import (
    AIProviderService,
    TaskComplexity
)

logger = logging.getLogger(__name__)


class SocialMediaGenerator:
    """
    AI-powered Social Media Content Generator integrating with Intelligence Engine
    Implements modular architecture from content-generation-implementation-plan.md
    """

    def __init__(self, db_session=None):
        self.name = "social_media_generator"
        self.version = "3.0.0"

        # Initialize modular services
        self.prompt_service = PromptGenerationService()
        self.ai_service = AIProviderService()

        # Optional: Prompt storage service (if db session provided)
        self.db_session = db_session
        self.prompt_storage = None
        if db_session:
            from src.content.services.prompt_storage_service import PromptStorageService
            self.prompt_storage = PromptStorageService(db_session)

        self._generation_stats = {
            "posts_generated": 0,
            "ai_generations": 0,
            "total_cost": 0.0,
            "prompts_saved": 0
        }

        logger.info(f"✅ SocialMediaGenerator v{self.version} - Modular architecture with AI")

    async def generate_social_content(
        self,
        campaign_id: Union[str, UUID],
        intelligence_data: Dict[str, Any],
        platform: str = "instagram",
        post_count: int = 5,
        tone: str = "engaging",
        target_audience: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate social media content using AI
        Implements Intelligence → Prompt → AI → Content pipeline

        Args:
            campaign_id: Campaign identifier
            intelligence_data: Campaign intelligence from analysis
            platform: Social platform (instagram, linkedin, twitter, facebook)
            post_count: Number of posts to generate
            tone: Content tone (engaging, professional, casual, bold)
            target_audience: Optional audience description
            preferences: Additional generation preferences

        Returns:
            Dictionary with generated social media posts
        """

        if preferences is None:
            preferences = {}

        try:
            logger.info(f"🎯 Generating {post_count} {platform} posts for campaign {campaign_id}")

            # Enhance intelligence data with preferences
            if target_audience:
                if "psychology_intelligence" not in intelligence_data:
                    intelligence_data["psychology_intelligence"] = {}
                intelligence_data["psychology_intelligence"]["target_audience"] = target_audience

            if tone:
                if "brand_intelligence" not in intelligence_data:
                    intelligence_data["brand_intelligence"] = {}
                intelligence_data["brand_intelligence"]["tone"] = tone

            # Add platform-specific preferences
            preferences["platform"] = platform
            preferences["post_count"] = post_count

            # Step 1: Generate optimized prompt from intelligence
            content_type = self._map_platform_to_content_type(platform)
            prompt_result = await self.prompt_service.generate_prompt(
                content_type=content_type,
                intelligence_data=intelligence_data,
                psychology_stage=SalesPsychologyStage.BENEFIT_PROOF,
                preferences=preferences
            )

            if not prompt_result["success"]:
                raise Exception(f"Prompt generation failed: {prompt_result.get('error')}")

            logger.info(f"✅ Generated prompt with quality score: {prompt_result['quality_score']}")

            # Step 2: Generate content using AI
            ai_result = await self.ai_service.generate_text(
                prompt=prompt_result["prompt"],
                system_message=prompt_result["system_message"],
                max_tokens=2000,
                temperature=0.85,  # Higher creativity for social media
                task_complexity=TaskComplexity.SIMPLE
            )

            if not ai_result["success"]:
                raise Exception(f"AI generation failed: {ai_result.get('error')}")

            logger.info(f"✅ AI generated content using {ai_result['provider_name']} (cost: ${ai_result['cost']:.4f})")

            # Save prompt to database for future reuse (if storage available)
            prompt_id = None
            if self.prompt_storage:
                try:
                    prompt_id = await self.prompt_storage.save_prompt(
                        campaign_id=str(campaign_id),
                        user_id="system",
                        content_type=platform.lower(),
                        user_prompt=prompt_result["prompt"],
                        system_message=prompt_result["system_message"],
                        intelligence_variables=prompt_result["variables"],
                        prompt_result=prompt_result,
                        ai_result=ai_result,
                        content_id=None
                    )
                    self._generation_stats["prompts_saved"] += 1
                    logger.info(f"✅ Saved prompt {prompt_id} for future reuse")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to save prompt (non-critical): {e}")

            # Step 3: Parse social posts from AI response
            posts = self._parse_social_posts(
                ai_response=ai_result["content"],
                platform=platform,
                post_count=post_count,
                product_name=prompt_result["variables"].get("PRODUCT_NAME", "this product")
            )

            if not posts or len(posts) < post_count:
                logger.warning(f"⚠️ Only parsed {len(posts)} posts, expected {post_count}")

            # Step 4: Enhance posts with metadata
            enhanced_posts = self._enhance_posts_with_metadata(
                posts=posts,
                intelligence_data=intelligence_data,
                prompt_result=prompt_result,
                platform=platform
            )

            # Update stats
            self._generation_stats["posts_generated"] += len(enhanced_posts)
            self._generation_stats["ai_generations"] += 1
            self._generation_stats["total_cost"] += ai_result["cost"]

            return {
                "success": True,
                "campaign_id": str(campaign_id),
                "posts": enhanced_posts,
                "content_info": {
                    "total_posts": len(enhanced_posts),
                    "platform": platform,
                    "product_name": prompt_result["variables"].get("PRODUCT_NAME"),
                    "tone": tone,
                    "target_audience": target_audience,
                    "generation_method": "ai_with_intelligence",
                    "ai_provider": ai_result["provider_name"]
                },
                "generation_metadata": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "generator_version": self.version,
                    "prompt_quality_score": prompt_result["quality_score"],
                    "ai_cost": ai_result["cost"],
                    "ai_provider": ai_result["provider"],
                    "generation_time": ai_result["generation_time"],
                    "intelligence_sources": len(intelligence_data.get("intelligence_sources", [])),
                    "variables_used": len(prompt_result["variables"])
                }
            }

        except Exception as e:
            logger.error(f"❌ Social media content generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "campaign_id": str(campaign_id)
            }

    def _map_platform_to_content_type(self, platform: str) -> ContentType:
        """Map social platform to ContentType enum"""
        platform_map = {
            "instagram": ContentType.SOCIAL_POST,
            "linkedin": ContentType.SOCIAL_POST,
            "twitter": ContentType.SOCIAL_POST,
            "facebook": ContentType.SOCIAL_POST,
            "tiktok": ContentType.SOCIAL_POST
        }
        return platform_map.get(platform.lower(), ContentType.SOCIAL_POST)

    def _parse_social_posts(
        self,
        ai_response: str,
        platform: str,
        post_count: int,
        product_name: str
    ) -> List[Dict[str, Any]]:
        """Parse AI response into structured social posts"""

        posts = []

        # Try to parse structured format (POST_1, POST_2, etc.)
        try:
            post_pattern = r'POST[_\s]?(\d+)[:\s]*(.*?)(?=POST[_\s]?\d+|$)'
            matches = re.findall(post_pattern, ai_response, re.DOTALL | re.IGNORECASE)

            for match in matches:
                post_num = int(match[0])
                post_content = match[1].strip()

                post_data = self._extract_post_components(
                    content=post_content,
                    post_number=post_num,
                    platform=platform,
                    product_name=product_name
                )

                if post_data:
                    posts.append(post_data)

            if posts:
                logger.info(f"✅ Parsed {len(posts)} posts using structured format")
                return posts[:post_count]

        except Exception as e:
            logger.warning(f"⚠️ Structured parsing failed: {e}")

        # Fallback: split by separators or double newlines
        try:
            sections = re.split(r'\n\s*\n---+\n|\n\s*\n===+\n|\n\s*\n\s*\n', ai_response)

            for idx, section in enumerate(sections):
                section = section.strip()
                if len(section) < 20:
                    continue

                post_data = self._extract_post_components(
                    content=section,
                    post_number=idx + 1,
                    platform=platform,
                    product_name=product_name
                )

                if post_data:
                    posts.append(post_data)

            if posts:
                logger.info(f"✅ Parsed {len(posts)} posts using fallback method")
                return posts[:post_count]

        except Exception as e:
            logger.error(f"❌ Fallback parsing failed: {e}")

        logger.warning("⚠️ Using emergency placeholder posts")
        return self._generate_placeholder_posts(post_count, platform, product_name)

    def _extract_post_components(
        self,
        content: str,
        post_number: int,
        platform: str,
        product_name: str
    ) -> Optional[Dict[str, Any]]:
        """Extract caption, hashtags, and metadata from post content"""

        try:
            lines = content.split('\n')
            caption_lines = []
            hashtags = []

            for line in lines:
                line_stripped = line.strip()

                if not line_stripped:
                    continue

                # Extract hashtags
                if line_stripped.startswith('#') or '#' in line_stripped:
                    # Extract all hashtags from the line
                    found_hashtags = re.findall(r'#\w+', line_stripped)
                    hashtags.extend(found_hashtags)
                    # Also include the line in caption if it has non-hashtag content
                    non_hashtag_content = re.sub(r'#\w+', '', line_stripped).strip()
                    if non_hashtag_content:
                        caption_lines.append(line_stripped)
                elif not any(line_stripped.lower().startswith(p) for p in ['post_', 'post ', 'caption:', 'hashtags:', '---', '===']):
                    caption_lines.append(line_stripped)

            caption = '\n'.join(caption_lines).strip()

            if not caption:
                return None

            # Remove duplicate hashtags
            hashtags = list(dict.fromkeys(hashtags))

            return {
                "post_number": post_number,
                "platform": platform,
                "caption": caption,
                "hashtags": hashtags,
                "product_name": product_name,
                "generation_method": "ai",
                "character_count": len(caption),
                "hashtag_count": len(hashtags)
            }

        except Exception as e:
            logger.warning(f"⚠️ Failed to extract post {post_number}: {e}")
            return None

    def _enhance_posts_with_metadata(
        self,
        posts: List[Dict[str, Any]],
        intelligence_data: Dict[str, Any],
        prompt_result: Dict[str, Any],
        platform: str
    ) -> List[Dict[str, Any]]:
        """Add rich metadata to each post"""

        enhanced = []

        for post in posts:
            enhanced_post = {
                **post,
                "metadata": {
                    "intelligence_enhanced": True,
                    "variables_used": prompt_result.get("variables", {}),
                    "prompt_quality_score": prompt_result.get("quality_score", 0),
                    "intelligence_sources": len(intelligence_data.get("intelligence_sources", [])),
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "generator_version": self.version,
                    "platform": platform
                }
            }
            enhanced.append(enhanced_post)

        return enhanced

    def _generate_placeholder_posts(
        self,
        count: int,
        platform: str,
        product_name: str
    ) -> List[Dict[str, Any]]:
        """Generate placeholder posts as emergency fallback"""

        posts = []
        for i in range(count):
            posts.append({
                "post_number": i + 1,
                "platform": platform,
                "caption": f"Discover the amazing benefits of {product_name}! Transform your life today. 🚀",
                "hashtags": [f"#{product_name.replace(' ', '')}", "#amazing", "#transformation", "#success"],
                "product_name": product_name,
                "generation_method": "placeholder_fallback",
                "character_count": 80,
                "hashtag_count": 4
            })

        return posts

    def get_stats(self) -> Dict[str, Any]:
        """Get social media generator statistics"""
        return {
            "generator": self.name,
            "version": self.version,
            "stats": self._generation_stats,
            "ai_service_stats": self.ai_service.get_stats()
        }
