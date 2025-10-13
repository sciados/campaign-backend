# src/content/generators/long_form_article_generator.py
"""
AI-Powered Long-Form Article Generator with Intelligence Integration
Uses modular architecture: Intelligence → Prompt → AI → Content
Generates comprehensive articles (2000-10,000 words) with SEO optimization
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


class LongFormArticleGenerator:
    """
    AI-powered Long-Form Article Generator integrating with Intelligence Engine
    Generates ultimate guides, pillar articles, and deep-dive content
    """

    def __init__(self, db_session=None):
        self.name = "long_form_article_generator"
        self.version = "1.1.0"

        # Initialize modular services
        self.prompt_service = PromptGenerationService()
        self.ai_service = AIProviderService()

        # Initialize prompt storage (optional)
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

        logger.info(f"✅ LongFormArticleGenerator v{self.version} - Modular architecture with AI")

    async def generate_long_form_article(
        self,
        campaign_id: Union[str, UUID],
        intelligence_data: Dict[str, Any],
        topic: str,
        word_count: int = 5000,
        article_type: str = "ultimate_guide",
        target_keywords: Optional[List[str]] = None,
        tone: str = "authoritative",
        target_audience: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
        user_id: Optional[Union[str, UUID]] = None
    ) -> Dict[str, Any]:
        """
        Generate long-form article using AI
        Implements Intelligence → Prompt → AI → Content pipeline

        Args:
            campaign_id: Campaign identifier
            intelligence_data: Campaign intelligence from analysis
            topic: Article topic/title
            word_count: Target word count (2000-10000)
            article_type: Type (ultimate_guide, pillar_article, deep_dive, research_report)
            target_keywords: SEO keywords to target
            tone: Content tone (authoritative, educational, conversational, expert)
            target_audience: Optional audience description
            preferences: Additional generation preferences

        Returns:
            Dictionary with generated long-form article
        """

        if preferences is None:
            preferences = {}

        try:
            logger.info(f"📚 Generating {word_count}-word {article_type} on '{topic}' for campaign {campaign_id}")

            # Enhance intelligence data with preferences
            if target_audience:
                if "psychology_intelligence" not in intelligence_data:
                    intelligence_data["psychology_intelligence"] = {}
                intelligence_data["psychology_intelligence"]["target_audience"] = target_audience

            if tone:
                if "brand_intelligence" not in intelligence_data:
                    intelligence_data["brand_intelligence"] = {}
                intelligence_data["brand_intelligence"]["tone"] = tone

            # Add long-form specific preferences
            preferences["topic"] = topic
            preferences["word_count"] = word_count
            preferences["article_type"] = article_type
            preferences["target_keywords"] = target_keywords or []

            # Generate comprehensive prompt
            prompt_template = self._build_long_form_template(
                topic=topic,
                word_count=word_count,
                article_type=article_type,
                target_keywords=target_keywords or []
            )

            # Step 1: Generate optimized prompt from intelligence
            prompt_result = await self.prompt_service.generate_prompt(
                content_type=ContentType.BLOG_ARTICLE,  # Use blog post type as base
                intelligence_data=intelligence_data,
                psychology_stage=SalesPsychologyStage.BENEFIT_PROOF,  # Educational content proving value
                preferences=preferences
            )

            if not prompt_result["success"]:
                raise Exception(f"Prompt generation failed: {prompt_result.get('error')}")

            # Enhance prompt with long-form specific instructions
            enhanced_prompt = prompt_template.format(
                **prompt_result["variables"]
            )

            logger.info(f"✅ Generated long-form prompt with quality score: {prompt_result['quality_score']}")

            # Step 2: Generate article using AI (high token limit for long-form)
            ai_result = await self.ai_service.generate_text(
                prompt=enhanced_prompt,
                system_message=prompt_result["system_message"],
                max_tokens=12000,  # High limit for long-form content
                temperature=0.7,   # Balanced creativity/accuracy
                task_complexity=TaskComplexity.COMPLEX  # High quality needed
            )

            if not ai_result["success"]:
                raise Exception(f"AI generation failed: {ai_result.get('error')}")

            logger.info(f"✅ AI generated long-form article using {ai_result['provider_name']} (cost: ${ai_result['cost']:.4f})")

            # Save prompt to database for future reuse (if storage available)
            prompt_id = None
            if self.prompt_storage:
                try:
                    # Use provided user_id or fallback to system UUID if not provided
                    storage_user_id = str(user_id) if user_id else "00000000-0000-0000-0000-000000000000"

                    prompt_id = await self.prompt_storage.save_prompt(
                        campaign_id=str(campaign_id),
                        user_id=storage_user_id,
                        content_type="long_form_article",
                        user_prompt=enhanced_prompt,
                        system_message=prompt_result["system_message"],
                        intelligence_variables=prompt_result["variables"],
                        prompt_result=prompt_result,
                        ai_result=ai_result,
                        content_id=None
                    )
                    self._generation_stats["prompts_saved"] += 1
                    logger.info(f"✅ Saved long-form article prompt {prompt_id} for future reuse")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to save long-form article prompt (non-critical): {e}")

            # Step 3: Parse article into structured format
            article = self._parse_long_form_article(
                ai_response=ai_result["content"],
                topic=topic,
                word_count=word_count,
                article_type=article_type
            )

            # Update stats
            self._generation_stats["articles_generated"] += 1
            self._generation_stats["ai_generations"] += 1
            self._generation_stats["total_cost"] += ai_result["cost"]

            return {
                "success": True,
                "campaign_id": str(campaign_id),
                "article": article,
                "article_info": {
                    "topic": topic,
                    "word_count": word_count,
                    "actual_word_count": len(article.get("content", "").split()),
                    "article_type": article_type,
                    "tone": tone,
                    "sections_count": len(article.get("sections", [])),
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
            logger.error(f"❌ Long-form article generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "campaign_id": str(campaign_id)
            }

    def _build_long_form_template(
        self,
        topic: str,
        word_count: int,
        article_type: str,
        target_keywords: List[str]
    ) -> str:
        """Build comprehensive long-form article template"""

        template = f"""
Write a comprehensive, SEO-optimized long-form article about {topic}.

=== ARTICLE SPECIFICATIONS ===
Target Word Count: {word_count} words
Article Type: {article_type}
Target Keywords: {', '.join(target_keywords) if target_keywords else 'SEO-optimized terms'}

=== PRODUCT INTELLIGENCE ===
PRODUCT: {{PRODUCT_NAME}}
PRIMARY BENEFIT: {{PRIMARY_BENEFIT}}
TARGET AUDIENCE: {{TARGET_AUDIENCE}}
PAIN POINT: {{PAIN_POINT}}
COMPETITIVE ADVANTAGE: {{COMPETITIVE_ADVANTAGE}}
KEY MESSAGES: {{KEY_MESSAGES}}

=== AI-ENHANCED INTELLIGENCE ===
Scientific Backing: {{SCIENTIFIC_BACKING}}
Research Credibility: {{RESEARCH_CREDIBILITY}}
Authority Markers: {{AUTHORITY_MARKERS}}
Credibility Signals: {{CREDIBILITY_SIGNALS}}

=== REQUIRED STRUCTURE ===

**1. SEO-OPTIMIZED TITLE (H1)**
Format: "Title: [Compelling, keyword-rich title 50-60 chars]"
- Include primary keyword naturally
- Create curiosity or promise value
- Use power words or numbers when appropriate

**2. META DESCRIPTION**
Format: "Meta Description: [150-160 character summary]"
- Compelling summary with primary keyword
- Include call-to-action
- Drive click-through from search results

**3. EXECUTIVE SUMMARY (150-200 words)**
Format: "Executive Summary: [Your summary]"
- Key takeaways in bullet points
- What readers will learn
- Why this matters to {{TARGET_AUDIENCE}}

**4. TABLE OF CONTENTS**
Format: "Table of Contents:"
- List all major sections (H2 headings)
- Include subsections (H3 headings)
- Make it clickable-friendly

**5. INTRODUCTION (300-400 words)**
Format: "Introduction: [Your introduction]"
- Hook with surprising statistic, question, or story
- Establish credibility and authority
- Preview the value and insights to come
- Address {{PAIN_POINT}} clearly
- Set expectations for the article

**6. MAIN CONTENT SECTIONS (6-10 sections)**

Create {max(6, word_count // 800)} main sections with H2 headings.

Each section format:
"Section: [H2 Heading Title]
[Section content 400-800 words with H3 subsections]"

Required sections to include:
- Deep dive into {{PAIN_POINT}} and its implications
- Comprehensive exploration of solutions
- Detailed explanation of {{PRODUCT_NAME}} and {{PRIMARY_BENEFIT}}
- Scientific evidence and {{SCIENTIFIC_BACKING}}
- Expert insights and {{AUTHORITY_MARKERS}}
- Case studies or real-world examples
- Implementation guidelines
- Common mistakes to avoid
- Advanced strategies and best practices
- Future trends and predictions

For each section:
- Start with H2 subheading
- Include 2-3 H3 subsections
- Use bullet points and numbered lists
- Add data, statistics, or research citations
- Include actionable takeaways
- Maintain {{TONE}} throughout
- Connect to {{TARGET_AUDIENCE}} needs

**7. COMPREHENSIVE CONCLUSION (300-400 words)**
Format: "Conclusion: [Your conclusion]"
- Summarize key insights and takeaways
- Reinforce {{COMPETITIVE_ADVANTAGE}}
- Create sense of urgency or next steps
- Strong call-to-action
- Circle back to opening hook
- Inspire action

**8. KEY TAKEAWAYS**
Format: "Key Takeaways:"
- 5-7 bullet points of main insights
- Actionable and memorable
- Reinforce core message

**9. SEO ELEMENTS**
Format: "SEO Keywords: [5-7 target keywords]"
Format: "LSI Keywords: [10-15 related keywords]"
Format: "Internal Link Suggestions: [5-7 relevant topics]"
Format: "External Authority Links: [3-5 authoritative sources]"

**10. RESOURCES & REFERENCES**
Format: "Resources:"
- Studies cited
- Tools mentioned
- Further reading suggestions

=== WRITING GUIDELINES ===
- Write for {{TARGET_AUDIENCE}} comprehension level
- Use conversational yet authoritative {{TONE}}
- Include transition sentences between all sections
- Use active voice (80%+ of sentences)
- Vary sentence length: mix short punchy sentences with detailed explanations
- Add relevant examples, analogies, and metaphors
- Use power words and emotional triggers strategically
- Optimize for featured snippets (use tables, lists, Q&A format)
- Include statistics and data points ({{SCIENTIFIC_BACKING}})
- Natural keyword integration - avoid stuffing
- Use storytelling techniques where appropriate
- Break up text with formatting (bold, italics, quotes)

=== CRITICAL REQUIREMENTS ===
- MUST be exactly {word_count} words (±5%)
- ALWAYS use "{{PRODUCT_NAME}}" exactly - NEVER use placeholders
- Include ALL required structural elements
- Maintain {{BRAND_VOICE}} consistently
- Address {{TARGET_AUDIENCE}} directly
- Leverage {{COMPETITIVE_ADVANTAGE}} throughout
- Build credibility with {{AUTHORITY_MARKERS}}
- Create emotional connection with reader
- Provide unique insights and value
- Make content actionable and practical
- Ensure content is comprehensive and authoritative
"""

        return template

    def _parse_long_form_article(
        self,
        ai_response: str,
        topic: str,
        word_count: int,
        article_type: str
    ) -> Dict[str, Any]:
        """Parse AI response into structured article format"""

        article = {
            "title": "",
            "meta_description": "",
            "executive_summary": "",
            "table_of_contents": [],
            "introduction": "",
            "sections": [],
            "conclusion": "",
            "key_takeaways": [],
            "seo_keywords": [],
            "lsi_keywords": [],
            "internal_links": [],
            "external_links": [],
            "resources": [],
            "content": ai_response,  # Full raw content
            "word_count": len(ai_response.split())
        }

        try:
            # Extract title
            title_match = re.search(r'Title:\s*(.+?)(?=\n|$)', ai_response, re.IGNORECASE)
            if title_match:
                article["title"] = title_match.group(1).strip()
            else:
                article["title"] = topic

            # Extract meta description
            meta_match = re.search(r'Meta Description:\s*(.+?)(?=\n|$)', ai_response, re.IGNORECASE)
            if meta_match:
                article["meta_description"] = meta_match.group(1).strip()

            # Extract executive summary
            exec_match = re.search(r'Executive Summary:\s*(.+?)(?=\n\n|Table of Contents)', ai_response, re.IGNORECASE | re.DOTALL)
            if exec_match:
                article["executive_summary"] = exec_match.group(1).strip()

            # Extract introduction
            intro_match = re.search(r'Introduction:\s*(.+?)(?=\n\nSection:|$)', ai_response, re.IGNORECASE | re.DOTALL)
            if intro_match:
                article["introduction"] = intro_match.group(1).strip()

            # Extract sections
            section_pattern = r'Section:\s*(.+?)\n(.+?)(?=\nSection:|Conclusion:|$)'
            section_matches = re.findall(section_pattern, ai_response, re.DOTALL | re.IGNORECASE)

            for heading, content in section_matches:
                article["sections"].append({
                    "heading": heading.strip(),
                    "content": content.strip()
                })

            # Extract conclusion
            conclusion_match = re.search(r'Conclusion:\s*(.+?)(?=\n\nKey Takeaways:|SEO Keywords:|$)', ai_response, re.IGNORECASE | re.DOTALL)
            if conclusion_match:
                article["conclusion"] = conclusion_match.group(1).strip()

            # Extract key takeaways
            takeaways_match = re.search(r'Key Takeaways:\s*(.+?)(?=\n\nSEO Keywords:|$)', ai_response, re.IGNORECASE | re.DOTALL)
            if takeaways_match:
                takeaways_text = takeaways_match.group(1).strip()
                article["key_takeaways"] = [
                    line.strip('- •').strip()
                    for line in takeaways_text.split('\n')
                    if line.strip() and line.strip().startswith(('-', '•', '*'))
                ]

            # Extract SEO keywords
            seo_match = re.search(r'SEO Keywords:\s*(.+?)(?=\n|$)', ai_response, re.IGNORECASE)
            if seo_match:
                article["seo_keywords"] = [kw.strip() for kw in seo_match.group(1).split(',')]

            logger.info(f"✅ Parsed long-form article: {len(article['sections'])} sections, {article['word_count']} words")

        except Exception as e:
            logger.warning(f"⚠️ Partial parsing failure: {e}")

        return article

    def get_stats(self) -> Dict[str, Any]:
        """Get long-form article generator statistics"""
        return {
            "generator": self.name,
            "version": self.version,
            "stats": self._generation_stats,
            "ai_service_stats": self.ai_service.get_stats()
        }
