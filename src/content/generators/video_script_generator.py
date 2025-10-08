# src/content/generators/video_script_generator.py
"""
AI-Powered Video Script Generator with Intelligence Integration
Uses modular architecture: Intelligence → Prompt → AI → Script
Generates shot-by-shot breakdowns for various video formats
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


class VideoScriptGenerator:
    """
    AI-powered Video Script Generator integrating with Intelligence Engine
    Implements modular architecture from content-generation-implementation-plan.md
    Supports multiple formats: VSL, Social Ads, Explainer, Testimonial
    """

    def __init__(self, db_session=None):
        self.name = "video_script_generator"
        self.version = "3.0.0"

        # Initialize modular services
        self.prompt_service = PromptGenerationService()
        self.ai_service = AIProviderService()

        # Optional: Prompt storage service
        self.db_session = db_session
        self.prompt_storage = None
        if db_session:
            from src.content.services.prompt_storage_service import PromptStorageService
            self.prompt_storage = PromptStorageService(db_session)

        self._generation_stats = {
            "scripts_generated": 0,
            "ai_generations": 0,
            "total_cost": 0.0,
            "prompts_saved": 0
        }

        logger.info(f"✅ VideoScriptGenerator v{self.version} - Modular architecture with AI")

    async def generate_video_script(
        self,
        campaign_id: Union[str, UUID],
        intelligence_data: Dict[str, Any],
        video_type: str = "vsl",
        duration: int = 60,
        platform: str = "youtube",
        tone: str = "engaging",
        target_audience: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
        user_id: Optional[Union[str, UUID]] = None
    ) -> Dict[str, Any]:
        """
        Generate video script using AI
        Implements Intelligence → Prompt → AI → Script pipeline

        Args:
            campaign_id: Campaign identifier
            intelligence_data: Campaign intelligence from analysis
            video_type: Type of video (vsl, social_ad, explainer, testimonial, demo)
            duration: Target duration in seconds (15, 30, 60, 90, 120)
            platform: Target platform (youtube, facebook, instagram, tiktok, linkedin)
            tone: Content tone (engaging, professional, urgent, educational, entertaining)
            target_audience: Optional audience description
            preferences: Additional generation preferences

        Returns:
            Dictionary with generated video script
        """

        if preferences is None:
            preferences = {}

        try:
            logger.info(f"🎬 Generating {duration}s {video_type} script for {platform}")

            # Enhance intelligence data with preferences
            if target_audience:
                if "psychology_intelligence" not in intelligence_data:
                    intelligence_data["psychology_intelligence"] = {}
                intelligence_data["psychology_intelligence"]["target_audience"] = target_audience

            if tone:
                if "brand_intelligence" not in intelligence_data:
                    intelligence_data["brand_intelligence"] = {}
                intelligence_data["brand_intelligence"]["tone"] = tone

            # Add video-specific preferences
            preferences["video_type"] = video_type
            preferences["duration"] = duration
            preferences["platform"] = platform

            # Step 1: Generate optimized prompt from intelligence
            prompt_result = await self.prompt_service.generate_prompt(
                content_type=ContentType.VIDEO_SCRIPT,
                intelligence_data=intelligence_data,
                psychology_stage=SalesPsychologyStage.URGENCY_CREATION,
                preferences=preferences
            )

            if not prompt_result["success"]:
                raise Exception(f"Prompt generation failed: {prompt_result.get('error')}")

            logger.info(f"✅ Generated prompt with quality score: {prompt_result['quality_score']}")

            # Step 2: Generate script using AI
            ai_result = await self.ai_service.generate_text(
                prompt=prompt_result["prompt"],
                system_message=prompt_result["system_message"],
                max_tokens=3000,
                temperature=0.8,
                task_complexity=TaskComplexity.STANDARD
            )

            if not ai_result["success"]:
                raise Exception(f"AI generation failed: {ai_result.get('error')}")

            logger.info(f"✅ AI generated script using {ai_result['provider_name']} (cost: ${ai_result['cost']:.4f})")

            # Step 3: Parse script into structured format
            script = self._parse_video_script(
                ai_response=ai_result["content"],
                video_type=video_type,
                duration=duration,
                platform=platform,
                product_name=prompt_result["variables"].get("PRODUCT_NAME", "this product")
            )

            if not script:
                logger.warning("⚠️ Script parsing produced empty result")

            # Update stats
            self._generation_stats["scripts_generated"] += 1
            self._generation_stats["ai_generations"] += 1
            self._generation_stats["total_cost"] += ai_result["cost"]

            return {
                "success": True,
                "campaign_id": str(campaign_id),
                "script": script,
                "script_info": {
                    "video_type": video_type,
                    "duration": duration,
                    "platform": platform,
                    "tone": tone,
                    "product_name": prompt_result["variables"].get("PRODUCT_NAME"),
                    "scene_count": len(script.get("scenes", [])),
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
            logger.error(f"❌ Video script generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "campaign_id": str(campaign_id)
            }

    def _parse_video_script(
        self,
        ai_response: str,
        video_type: str,
        duration: int,
        platform: str,
        product_name: str
    ) -> Dict[str, Any]:
        """Parse AI response into structured video script"""

        script = {
            "title": "",
            "hook": "",
            "scenes": [],
            "total_duration": duration,
            "cta": ""
        }

        try:
            # Extract title
            title_match = re.search(r'Title:\s*(.+)', ai_response, re.IGNORECASE)
            if title_match:
                script["title"] = title_match.group(1).strip()

            # Extract hook
            hook_match = re.search(r'Hook:\s*(.+?)(?=\n\n|Scene|$)', ai_response, re.IGNORECASE | re.DOTALL)
            if hook_match:
                script["hook"] = hook_match.group(1).strip()

            # Extract scenes
            scene_pattern = r'Scene\s+(\d+):(.*?)(?=Scene\s+\d+:|CTA:|$)'
            scene_matches = re.findall(scene_pattern, ai_response, re.DOTALL | re.IGNORECASE)

            for scene_num, scene_content in scene_matches:
                scene_data = self._parse_scene(scene_content, int(scene_num))
                if scene_data:
                    script["scenes"].append(scene_data)

            # Extract CTA
            cta_match = re.search(r'CTA:\s*(.+?)(?=\n\n|$)', ai_response, re.IGNORECASE | re.DOTALL)
            if cta_match:
                script["cta"] = cta_match.group(1).strip()

            # If parsing failed, create basic structure
            if not script["scenes"]:
                logger.warning("⚠️ No scenes parsed, creating fallback structure")
                script["scenes"] = [{
                    "scene_number": 1,
                    "duration": duration,
                    "visual": f"Show {product_name}",
                    "voiceover": ai_response[:500],
                    "text_overlay": "",
                    "music": "Upbeat background music"
                }]

            return script

        except Exception as e:
            logger.error(f"❌ Script parsing failed: {e}")
            return {
                "title": f"Video Script for {product_name}",
                "hook": "Compelling video hook",
                "scenes": [{
                    "scene_number": 1,
                    "duration": duration,
                    "visual": f"Product showcase",
                    "voiceover": "Generated content",
                    "text_overlay": "",
                    "music": "Background music"
                }],
                "total_duration": duration,
                "cta": "Learn More"
            }

    def _parse_scene(self, scene_content: str, scene_number: int) -> Optional[Dict[str, Any]]:
        """Parse individual scene from script"""

        try:
            scene = {
                "scene_number": scene_number,
                "duration": 0,
                "visual": "",
                "voiceover": "",
                "text_overlay": "",
                "music": ""
            }

            # Extract duration
            duration_match = re.search(r'Duration:\s*(\d+)', scene_content, re.IGNORECASE)
            if duration_match:
                scene["duration"] = int(duration_match.group(1))

            # Extract visual
            visual_match = re.search(r'Visual:\s*(.+?)(?=\n[A-Z]|$)', scene_content, re.IGNORECASE | re.DOTALL)
            if visual_match:
                scene["visual"] = visual_match.group(1).strip()

            # Extract voiceover
            vo_match = re.search(r'Voiceover:\s*(.+?)(?=\n[A-Z]|$)', scene_content, re.IGNORECASE | re.DOTALL)
            if vo_match:
                scene["voiceover"] = vo_match.group(1).strip()

            # Extract text overlay
            text_match = re.search(r'Text.*?:\s*(.+?)(?=\n[A-Z]|$)', scene_content, re.IGNORECASE | re.DOTALL)
            if text_match:
                scene["text_overlay"] = text_match.group(1).strip()

            # Extract music
            music_match = re.search(r'Music:\s*(.+?)(?=\n[A-Z]|$)', scene_content, re.IGNORECASE | re.DOTALL)
            if music_match:
                scene["music"] = music_match.group(1).strip()

            return scene if scene["visual"] or scene["voiceover"] else None

        except Exception as e:
            logger.warning(f"⚠️ Failed to parse scene {scene_number}: {e}")
            return None

    def get_stats(self) -> Dict[str, Any]:
        """Get video script generator statistics"""
        return {
            "generator": self.name,
            "version": self.version,
            "stats": self._generation_stats,
            "ai_service_stats": self.ai_service.get_stats()
        }
