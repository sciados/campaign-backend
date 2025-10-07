# src/content/generators/ad_copy_generator.py
"""
AI-Powered Ad Copy Generator with Intelligence Integration
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


class AdCopyGenerator:
    """
    AI-powered Ad Copy Generator integrating with Intelligence Engine
    Implements modular architecture from content-generation-implementation-plan.md
    Supports multiple ad platforms: Google Ads, Facebook Ads, Instagram Ads, LinkedIn Ads
    """

    def __init__(self, db_session=None):
        self.name = "ad_copy_generator"
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
            "ads_generated": 0,
            "ai_generations": 0,
            "total_cost": 0.0,
            "prompts_saved": 0
        }

        logger.info(f"✅ AdCopyGenerator v{self.version} - Modular architecture with AI")

    async def generate_ad_copy(
        self,
        campaign_id: Union[str, UUID],
        intelligence_data: Dict[str, Any],
        platform: str = "google",
        ad_format: str = "responsive",
        variation_count: int = 3,
        tone: str = "persuasive",
        target_audience: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate ad copy using AI
        Implements Intelligence → Prompt → AI → Content pipeline

        Args:
            campaign_id: Campaign identifier
            intelligence_data: Campaign intelligence from analysis
            platform: Ad platform (google, facebook, instagram, linkedin)
            ad_format: Ad format (responsive, search, display, video, carousel)
            variation_count: Number of ad variations to generate
            tone: Content tone (persuasive, urgent, informative, casual)
            target_audience: Optional audience description
            preferences: Additional generation preferences

        Returns:
            Dictionary with generated ad variations
        """

        if preferences is None:
            preferences = {}

        try:
            logger.info(f"🎯 Generating {variation_count} {platform} ads for campaign {campaign_id}")

            # Enhance intelligence data with preferences
            if target_audience:
                if "psychology_intelligence" not in intelligence_data:
                    intelligence_data["psychology_intelligence"] = {}
                intelligence_data["psychology_intelligence"]["target_audience"] = target_audience

            if tone:
                if "brand_intelligence" not in intelligence_data:
                    intelligence_data["brand_intelligence"] = {}
                intelligence_data["brand_intelligence"]["tone"] = tone

            # Add ad-specific preferences
            preferences["platform"] = platform
            preferences["ad_format"] = ad_format
            preferences["variation_count"] = variation_count
            preferences["character_limits"] = self._get_character_limits(platform, ad_format)

            # Step 1: Generate optimized prompt from intelligence
            prompt_result = await self.prompt_service.generate_prompt(
                content_type=ContentType.AD_COPY,
                intelligence_data=intelligence_data,
                psychology_stage=SalesPsychologyStage.URGENCY_CREATION,
                preferences=preferences
            )

            if not prompt_result["success"]:
                raise Exception(f"Prompt generation failed: {prompt_result.get('error')}")

            logger.info(f"✅ Generated prompt with quality score: {prompt_result['quality_score']}")

            # Step 2: Generate content using AI
            ai_result = await self.ai_service.generate_text(
                prompt=prompt_result["prompt"],
                system_message=prompt_result["system_message"],
                max_tokens=1500,
                temperature=0.9,  # High creativity for ad copy
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
                        content_type=f"{platform}_ad",
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

            # Step 3: Parse ad variations from AI response
            ads = self._parse_ad_variations(
                ai_response=ai_result["content"],
                platform=platform,
                ad_format=ad_format,
                variation_count=variation_count,
                product_name=prompt_result["variables"].get("PRODUCT_NAME", "this product")
            )

            if not ads or len(ads) < variation_count:
                logger.warning(f"⚠️ Only parsed {len(ads)} ads, expected {variation_count}")

            # Step 4: Enhance ads with metadata
            enhanced_ads = self._enhance_ads_with_metadata(
                ads=ads,
                intelligence_data=intelligence_data,
                prompt_result=prompt_result,
                platform=platform
            )

            # Update stats
            self._generation_stats["ads_generated"] += len(enhanced_ads)
            self._generation_stats["ai_generations"] += 1
            self._generation_stats["total_cost"] += ai_result["cost"]

            return {
                "success": True,
                "campaign_id": str(campaign_id),
                "ads": enhanced_ads,
                "content_info": {
                    "total_variations": len(enhanced_ads),
                    "platform": platform,
                    "ad_format": ad_format,
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
            logger.error(f"❌ Ad copy generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "campaign_id": str(campaign_id)
            }

    def _get_character_limits(self, platform: str, ad_format: str) -> Dict[str, int]:
        """Get character limits for specific platform and format"""

        limits = {
            "google": {
                "responsive": {"headline": 30, "description": 90, "headlines_count": 15, "descriptions_count": 4},
                "search": {"headline": 30, "description": 90},
                "display": {"headline": 30, "description": 90, "long_headline": 90}
            },
            "facebook": {
                "responsive": {"headline": 40, "primary_text": 125, "description": 30},
                "single_image": {"headline": 40, "primary_text": 125},
                "video": {"headline": 40, "primary_text": 125},
                "carousel": {"headline": 40, "description": 20}
            },
            "instagram": {
                "story": {"headline": 40, "primary_text": 125},
                "feed": {"headline": 40, "primary_text": 125},
                "reel": {"headline": 40, "caption": 2200}
            },
            "linkedin": {
                "single_image": {"headline": 70, "introductory_text": 150},
                "video": {"headline": 70, "introductory_text": 150},
                "carousel": {"headline": 70, "introductory_text": 150}
            }
        }

        return limits.get(platform.lower(), {}).get(ad_format.lower(), {"headline": 40, "description": 90})

    def _parse_ad_variations(
        self,
        ai_response: str,
        platform: str,
        ad_format: str,
        variation_count: int,
        product_name: str
    ) -> List[Dict[str, Any]]:
        """Parse AI response into structured ad variations"""

        ads = []

        # Try to parse structured format (AD_1, AD_2, VARIATION_1, etc.)
        try:
            ad_pattern = r'(?:AD|VARIATION)[_\s]?(\d+)[:\s]*(.*?)(?=(?:AD|VARIATION)[_\s]?\d+|$)'
            matches = re.findall(ad_pattern, ai_response, re.DOTALL | re.IGNORECASE)

            for match in matches:
                ad_num = int(match[0])
                ad_content = match[1].strip()

                ad_data = self._extract_ad_components(
                    content=ad_content,
                    variation_number=ad_num,
                    platform=platform,
                    ad_format=ad_format,
                    product_name=product_name
                )

                if ad_data:
                    ads.append(ad_data)

            if ads:
                logger.info(f"✅ Parsed {len(ads)} ads using structured format")
                return ads[:variation_count]

        except Exception as e:
            logger.warning(f"⚠️ Structured parsing failed: {e}")

        # Fallback: split by separators
        try:
            sections = re.split(r'\n\s*\n---+\n|\n\s*\n===+\n', ai_response)

            for idx, section in enumerate(sections):
                section = section.strip()
                if len(section) < 20:
                    continue

                ad_data = self._extract_ad_components(
                    content=section,
                    variation_number=idx + 1,
                    platform=platform,
                    ad_format=ad_format,
                    product_name=product_name
                )

                if ad_data:
                    ads.append(ad_data)

            if ads:
                logger.info(f"✅ Parsed {len(ads)} ads using fallback method")
                return ads[:variation_count]

        except Exception as e:
            logger.error(f"❌ Fallback parsing failed: {e}")

        logger.warning("⚠️ Using emergency placeholder ads")
        return self._generate_placeholder_ads(variation_count, platform, ad_format, product_name)

    def _extract_ad_components(
        self,
        content: str,
        variation_number: int,
        platform: str,
        ad_format: str,
        product_name: str
    ) -> Optional[Dict[str, Any]]:
        """Extract headlines, descriptions, and metadata from ad content"""

        try:
            lines = content.split('\n')
            headlines = []
            descriptions = []
            primary_text = ""
            call_to_action = ""

            for line in lines:
                line_stripped = line.strip()

                if not line_stripped:
                    continue

                # Extract based on labels
                if line_stripped.lower().startswith('headline:'):
                    headlines.append(line_stripped[9:].strip())
                elif line_stripped.lower().startswith('description:'):
                    descriptions.append(line_stripped[12:].strip())
                elif line_stripped.lower().startswith('primary text:'):
                    primary_text = line_stripped[13:].strip()
                elif line_stripped.lower().startswith(('cta:', 'call to action:')):
                    call_to_action = line_stripped.split(':', 1)[1].strip()
                elif not any(line_stripped.lower().startswith(p) for p in ['ad_', 'ad ', 'variation_', 'variation ', '---', '===']):
                    # If no label, try to intelligently categorize
                    if len(line_stripped) <= 40 and not headlines:
                        headlines.append(line_stripped)
                    elif len(line_stripped) > 40:
                        if not descriptions:
                            descriptions.append(line_stripped)

            # If we only got one headline and no descriptions, split the content
            if len(headlines) == 0 and len(descriptions) == 0:
                # Use first 30 chars as headline, rest as description
                if len(content) > 30:
                    headlines.append(content[:30])
                    descriptions.append(content[30:].strip())
                else:
                    headlines.append(content)

            if not headlines:
                return None

            character_limits = self._get_character_limits(platform, ad_format)

            return {
                "variation_number": variation_number,
                "platform": platform,
                "ad_format": ad_format,
                "headlines": headlines[:5],  # Limit to 5 headlines
                "descriptions": descriptions[:3],  # Limit to 3 descriptions
                "primary_text": primary_text,
                "call_to_action": call_to_action or "Learn More",
                "product_name": product_name,
                "generation_method": "ai",
                "character_limits": character_limits,
                "compliance_status": self._check_compliance(headlines, descriptions, character_limits)
            }

        except Exception as e:
            logger.warning(f"⚠️ Failed to extract ad {variation_number}: {e}")
            return None

    def _check_compliance(
        self,
        headlines: List[str],
        descriptions: List[str],
        limits: Dict[str, int]
    ) -> Dict[str, Any]:
        """Check if ad copy complies with platform character limits"""

        headline_limit = limits.get("headline", 40)
        description_limit = limits.get("description", 90)

        headline_compliance = all(len(h) <= headline_limit for h in headlines)
        description_compliance = all(len(d) <= description_limit for d in descriptions)

        return {
            "is_compliant": headline_compliance and description_compliance,
            "headline_compliance": headline_compliance,
            "description_compliance": description_compliance,
            "headline_violations": [h for h in headlines if len(h) > headline_limit],
            "description_violations": [d for d in descriptions if len(d) > description_limit]
        }

    def _enhance_ads_with_metadata(
        self,
        ads: List[Dict[str, Any]],
        intelligence_data: Dict[str, Any],
        prompt_result: Dict[str, Any],
        platform: str
    ) -> List[Dict[str, Any]]:
        """Add rich metadata to each ad"""

        enhanced = []

        for ad in ads:
            enhanced_ad = {
                **ad,
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
            enhanced.append(enhanced_ad)

        return enhanced

    def _generate_placeholder_ads(
        self,
        count: int,
        platform: str,
        ad_format: str,
        product_name: str
    ) -> List[Dict[str, Any]]:
        """Generate placeholder ads as emergency fallback"""

        ads = []
        character_limits = self._get_character_limits(platform, ad_format)

        for i in range(count):
            ads.append({
                "variation_number": i + 1,
                "platform": platform,
                "ad_format": ad_format,
                "headlines": [
                    f"Try {product_name} Today",
                    f"Discover {product_name}",
                    f"Get Started with {product_name}"
                ],
                "descriptions": [
                    f"Experience the benefits of {product_name}. Transform your results today.",
                    f"Join thousands who trust {product_name} for success."
                ],
                "primary_text": f"Ready to transform your results? {product_name} is here to help.",
                "call_to_action": "Learn More",
                "product_name": product_name,
                "generation_method": "placeholder_fallback",
                "character_limits": character_limits,
                "compliance_status": {
                    "is_compliant": True,
                    "headline_compliance": True,
                    "description_compliance": True,
                    "headline_violations": [],
                    "description_violations": []
                }
            })

        return ads

    def get_stats(self) -> Dict[str, Any]:
        """Get ad copy generator statistics"""
        return {
            "generator": self.name,
            "version": self.version,
            "stats": self._generation_stats,
            "ai_service_stats": self.ai_service.get_stats()
        }
