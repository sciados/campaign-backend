# src/content/generators/blog_content_generator.py
"""
AI-Powered Blog Content Generator with Intelligence Integration
Uses modular architecture: Intelligence → Prompt → AI → Content
"""

import logging
import re
from typing import Dict, Any, Optional, Union, List
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


class BlogContentGenerator:
    """
    AI-powered Blog Content Generator integrating with Intelligence Engine
    Implements modular architecture from content-generation-implementation-plan.md
    """

    def __init__(self, db_session=None):
        self.name = "blog_content_generator"
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
            "articles_generated": 0,
            "ai_generations": 0,
            "total_cost": 0.0,
            "prompts_saved": 0
        }

        logger.info(f"✅ BlogContentGenerator v{self.version} - Modular architecture with AI")

    async def generate_blog_post(
        self,
        campaign_id: Union[str, UUID],
        intelligence_data: Dict[str, Any],
        topic: Optional[str] = None,
        word_count: int = 1500,
        tone: str = "informative",
        target_audience: Optional[str] = None,
        include_sections: Optional[List[str]] = None,
        preferences: Optional[Dict[str, Any]] = None,
        user_id: Optional[Union[str, UUID]] = None
    ) -> Dict[str, Any]:
        """
        Generate blog article using AI
        Implements Intelligence → Prompt → AI → Content pipeline

        Args:
            campaign_id: Campaign identifier
            intelligence_data: Campaign intelligence from analysis
            topic: Blog topic (auto-generated if not provided)
            word_count: Target word count
            tone: Content tone (informative, conversational, expert, casual)
            target_audience: Optional audience description
            include_sections: Optional list of sections to include
            preferences: Additional generation preferences

        Returns:
            Dictionary with generated blog article
        """

        if preferences is None:
            preferences = {}

        try:
            logger.info(f"🎯 Generating blog post (~{word_count} words) for campaign {campaign_id}")

            # Enhance intelligence data with preferences
            if target_audience:
                if "psychology_intelligence" not in intelligence_data:
                    intelligence_data["psychology_intelligence"] = {}
                intelligence_data["psychology_intelligence"]["target_audience"] = target_audience

            if tone:
                if "brand_intelligence" not in intelligence_data:
                    intelligence_data["brand_intelligence"] = {}
                intelligence_data["brand_intelligence"]["tone"] = tone

            # Add blog-specific preferences
            preferences["word_count"] = word_count
            preferences["topic"] = topic or self._generate_topic_from_intelligence(intelligence_data)
            preferences["include_sections"] = include_sections or ["introduction", "main_content", "conclusion", "call_to_action"]

            # Step 1: Generate optimized prompt from intelligence
            prompt_result = await self.prompt_service.generate_prompt(
                content_type=ContentType.BLOG_ARTICLE,
                intelligence_data=intelligence_data,
                psychology_stage=SalesPsychologyStage.SOLUTION_REVEAL,
                preferences=preferences
            )

            if not prompt_result["success"]:
                raise Exception(f"Prompt generation failed: {prompt_result.get('error')}")

            logger.info(f"✅ Generated prompt with quality score: {prompt_result['quality_score']}")

            # Step 2: Generate content using AI (blog posts are complex, use standard complexity)
            ai_result = await self.ai_service.generate_text(
                prompt=prompt_result["prompt"],
                system_message=prompt_result["system_message"],
                max_tokens=word_count * 2,  # ~2 tokens per word
                temperature=0.75,
                task_complexity=TaskComplexity.STANDARD
            )

            if not ai_result["success"]:
                raise Exception(f"AI generation failed: {ai_result.get('error')}")

            logger.info(f"✅ AI generated content using {ai_result['provider_name']} (cost: ${ai_result['cost']:.4f})")

            # Save prompt to database for future reuse (if storage available)
            prompt_id = None
            if self.prompt_storage:
                try:
                    storage_user_id = str(user_id) if user_id else "00000000-0000-0000-0000-000000000000"

                    prompt_id = await self.prompt_storage.save_prompt(
                        campaign_id=str(campaign_id),
                        user_id=storage_user_id,
                        content_type="blog_article",
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

            # Step 3: Parse blog article from AI response
            article = self._parse_blog_article(
                ai_response=ai_result["content"],
                topic=preferences["topic"],
                product_name=prompt_result["variables"].get("PRODUCT_NAME", "this product")
            )

            # Step 4: Enhance article with metadata
            enhanced_article = self._enhance_article_with_metadata(
                article=article,
                intelligence_data=intelligence_data,
                prompt_result=prompt_result
            )

            # Update stats
            self._generation_stats["articles_generated"] += 1
            self._generation_stats["ai_generations"] += 1
            self._generation_stats["total_cost"] += ai_result["cost"]

            return {
                "success": True,
                "campaign_id": str(campaign_id),
                "article": enhanced_article,
                "content_info": {
                    "topic": preferences["topic"],
                    "word_count": enhanced_article.get("word_count", 0),
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
            logger.error(f"❌ Blog content generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "campaign_id": str(campaign_id)
            }

    def _generate_topic_from_intelligence(self, intelligence_data: Dict[str, Any]) -> str:
        """Generate a blog topic from intelligence data"""
        product_name = intelligence_data.get("product_name", "Product")

        # Try to extract a compelling topic from intelligence
        if "psychology_intelligence" in intelligence_data:
            pain_points = intelligence_data["psychology_intelligence"].get("pain_points", [])
            if pain_points:
                return f"How {product_name} Solves {pain_points[0]}"

        if "offer_intelligence" in intelligence_data:
            benefits = intelligence_data["offer_intelligence"].get("benefits", [])
            if benefits:
                return f"The Ultimate Guide to {benefits[0]} with {product_name}"

        return f"Everything You Need to Know About {product_name}"

    def _parse_blog_article(
        self,
        ai_response: str,
        topic: str,
        product_name: str
    ) -> Dict[str, Any]:
        """Parse AI response into structured blog article"""

        try:
            # Extract title (usually the first line or H1)
            title_match = re.search(r'^#\s+(.+)$', ai_response, re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip()
                content = ai_response[title_match.end():].strip()
            else:
                # Use first line as title if no H1 found
                lines = ai_response.split('\n', 1)
                title = lines[0].strip('#').strip()
                content = lines[1] if len(lines) > 1 else ai_response

            # Extract sections
            sections = self._extract_sections(content)

            # Calculate metrics
            word_count = len(content.split())
            char_count = len(content)
            reading_time = max(1, word_count // 200)  # ~200 words per minute

            # Extract SEO elements
            seo_elements = self._extract_seo_elements(title, content, product_name)

            return {
                "title": title or topic,
                "content": content,
                "sections": sections,
                "word_count": word_count,
                "character_count": char_count,
                "reading_time_minutes": reading_time,
                "seo_elements": seo_elements,
                "product_name": product_name,
                "generation_method": "ai"
            }

        except Exception as e:
            logger.warning(f"⚠️ Failed to parse article, using fallback: {e}")
            return self._generate_placeholder_article(topic, product_name)

    def _extract_sections(self, content: str) -> List[Dict[str, str]]:
        """Extract sections from markdown content"""
        sections = []

        # Find all headings (H2, H3)
        section_pattern = r'^(#{2,3})\s+(.+)$'
        matches = list(re.finditer(section_pattern, content, re.MULTILINE))

        for i, match in enumerate(matches):
            level = len(match.group(1))  # Number of # characters
            heading = match.group(2).strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            section_content = content[start:end].strip()

            sections.append({
                "level": level,
                "heading": heading,
                "content": section_content
            })

        return sections

    def _extract_seo_elements(self, title: str, content: str, product_name: str) -> Dict[str, Any]:
        """Extract SEO-relevant elements"""

        # Generate meta description (first 160 chars of content)
        clean_content = re.sub(r'#.*\n', '', content)  # Remove headings
        clean_content = re.sub(r'\[.*?\]\(.*?\)', '', clean_content)  # Remove links
        clean_content = ' '.join(clean_content.split())  # Normalize whitespace
        meta_description = clean_content[:157] + "..." if len(clean_content) > 160 else clean_content

        # Extract keywords (simple frequency-based)
        words = re.findall(r'\b\w{4,}\b', content.lower())
        word_freq = {}
        for word in words:
            if word not in ['this', 'that', 'with', 'from', 'have', 'will', 'your', 'their']:
                word_freq[word] = word_freq.get(word, 0) + 1

        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        keywords = [word for word, freq in keywords]

        # Add product name as keyword
        if product_name.lower() not in keywords:
            keywords.insert(0, product_name.lower())

        return {
            "meta_title": title[:60] if len(title) > 60 else title,
            "meta_description": meta_description,
            "keywords": keywords[:5],  # Top 5 keywords
            "slug": self._generate_slug(title)
        }

    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title"""
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars
        slug = re.sub(r'[-\s]+', '-', slug)   # Replace spaces with hyphens
        slug = slug.strip('-')
        return slug[:50]  # Limit length

    def _enhance_article_with_metadata(
        self,
        article: Dict[str, Any],
        intelligence_data: Dict[str, Any],
        prompt_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add rich metadata to article"""

        enhanced = {
            **article,
            "metadata": {
                "intelligence_enhanced": True,
                "variables_used": prompt_result.get("variables", {}),
                "prompt_quality_score": prompt_result.get("quality_score", 0),
                "intelligence_sources": len(intelligence_data.get("intelligence_sources", [])),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "generator_version": self.version
            }
        }

        return enhanced

    def _generate_placeholder_article(
        self,
        topic: str,
        product_name: str
    ) -> Dict[str, Any]:
        """Generate placeholder article as emergency fallback"""

        content = f"""
# {topic}

## Introduction

Discover how {product_name} can transform your experience and help you achieve your goals.

## The Power of {product_name}

{product_name} offers innovative solutions that address your most pressing needs. With cutting-edge features and proven results, it's the perfect choice for those seeking excellence.

## Key Benefits

- Enhanced performance and reliability
- User-friendly interface and experience
- Proven track record of success
- Comprehensive support and resources

## Getting Started

Ready to experience the difference? {product_name} makes it easy to get started and see results quickly.

## Conclusion

Whether you're new to this space or looking to upgrade, {product_name} provides everything you need to succeed.
        """.strip()

        return {
            "title": topic,
            "content": content,
            "sections": [],
            "word_count": len(content.split()),
            "character_count": len(content),
            "reading_time_minutes": 2,
            "seo_elements": {
                "meta_title": topic,
                "meta_description": f"Learn about {product_name} and how it can help you.",
                "keywords": [product_name.lower()],
                "slug": self._generate_slug(topic)
            },
            "product_name": product_name,
            "generation_method": "placeholder_fallback"
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get blog generator statistics"""
        return {
            "generator": self.name,
            "version": self.version,
            "stats": self._generation_stats,
            "ai_service_stats": self.ai_service.get_stats()
        }
