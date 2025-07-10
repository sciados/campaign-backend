# src/intelligence/generators/video_script_generator.py
"""
MODERNIZED VIDEO SCRIPT GENERATOR
🚀 90% cost savings with ultra-cheap AI providers
💰 $0.002 per 1K tokens (vs $0.060 OpenAI)
✅ Multiple video formats (social, ads, educational)
✅ Platform-specific optimization
✅ Shot-by-shot breakdowns
🔥 MODERNIZED: Ultra-cheap AI integration with smart failover
"""

import os
import logging
import uuid
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.models.base import EnumSerializerMixin
from ..utils.ultra_cheap_ai_provider import UltraCheapAIProvider

logger = logging.getLogger(__name__)

class VideoScriptGenerator(EnumSerializerMixin):
    """Generate video scripts with 90% cost savings using ultra-cheap AI"""
    
    def __init__(self):
        # 🚀 MODERNIZED: Use ultra-cheap AI provider (90% savings)
        self.ultra_cheap_provider = UltraCheapAIProvider()
        self.video_types = ["social_media", "advertisement", "educational", "testimonial", "product_demo"]
        self.platforms = ["youtube", "tiktok", "instagram", "facebook", "linkedin"]
        logger.info("🚀 Video Script Generator initialized with ultra-cheap AI (90% cost savings)")
        
    async def generate_video_script(
        self, 
        intelligence_data: Dict[str, Any], 
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate video script with ultra-cheap AI"""
        
        if preferences is None:
            preferences = {}
            
        video_type = preferences.get("video_type", "social_media")
        platform = preferences.get("platform", "youtube")
        duration = preferences.get("duration", 60)  # seconds
        style = preferences.get("style", "engaging")
        
        product_name = self._extract_product_name(intelligence_data)
        
        script_data = None
        generation_cost = None
        
        try:
            script_data, generation_cost = await self._generate_script_ultra_cheap(
                video_type, platform, duration, style, product_name, intelligence_data
            )
                
        except Exception as e:
            logger.error(f"Ultra-cheap video script generation failed: {str(e)}")
            script_data = self._generate_fallback_script(product_name, video_type, platform, duration)
            generation_cost = {"cost": 0, "fallback": True}
        
        return {
            "content_type": "video_script",
            "title": f"{product_name} Video Script - {video_type.title()}",
            "content": {
                "script": script_data,
                "video_type": video_type,
                "platform": platform,
                "duration": duration,
                "style": style
            },
            "metadata": {
                "generated_by": "ultra_cheap_video_ai",
                "product_name": product_name,
                "content_type": "video_script",
                "platform_optimized": True,
                "cost_optimization": {
                    "generation_cost": generation_cost.get("cost", 0),
                    "provider_used": generation_cost.get("provider", "fallback"),
                    "savings_vs_openai": generation_cost.get("savings_vs_openai", {})
                }
            }
        }
    
    async def _generate_script_ultra_cheap(self, video_type, platform, duration, style, product_name, intelligence_data):
        """Generate video script using ultra-cheap AI"""
        
        # 🔥 FIXED: Extract intelligence with proper enum serialization
        emotional_intel = self._serialize_enum_field(intelligence_data.get("emotional_transformation_intelligence", {}))
        scientific_intel = self._serialize_enum_field(intelligence_data.get("scientific_authority_intelligence", {}))
        
        platform_specs = {
            "youtube": {"hook_time": 5, "cta_placement": "end", "style": "informative"},
            "tiktok": {"hook_time": 3, "cta_placement": "middle_and_end", "style": "fast_paced"},
            "instagram": {"hook_time": 3, "cta_placement": "end", "style": "visual_focused"},
            "facebook": {"hook_time": 5, "cta_placement": "middle", "style": "conversational"},
            "linkedin": {"hook_time": 5, "cta_placement": "end", "style": "professional"}
        }
        
        spec = platform_specs.get(platform, platform_specs["youtube"])
        
        prompt = f"""
Create a {duration}-second {video_type} video script for {product_name} on {platform}.

Product: {product_name}
Video Type: {video_type}
Platform: {platform}
Duration: {duration} seconds
Style: {style}

Platform Requirements:
- Hook within {spec['hook_time']} seconds
- Style: {spec['style']}
- CTA placement: {spec['cta_placement']}

Script Structure:
[0-{spec['hook_time']}s] HOOK - Grab attention immediately
[{spec['hook_time']+1}-{duration//3}s] PROBLEM/PAIN POINT - Identify viewer's struggle
[{duration//3+1}-{duration*2//3}s] SOLUTION - Introduce {product_name} as the answer
[{duration*2//3+1}-{duration}s] CALL TO ACTION - Clear next step

Include:
- Spoken narration for each time segment
- Visual cues [in brackets]
- Text overlays "in quotes"
- Emotional triggers and benefits
- Strong call-to-action

Focus on {emotional_intel.get('target_audience', 'health-conscious individuals')} audience.
Make it {platform}-optimized and conversion-focused.
"""
        
        try:
            # 🚀 ULTRA-CHEAP SCRIPT GENERATION
            result = await self.ultra_cheap_provider.generate_text(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.8,
                cost_target="ultra_cheap"
            )
            
            if result["success"]:
                script_data = self._parse_video_script(result["content"], video_type, platform, duration)
                script_data["ultra_cheap_generated"] = True
                script_data["generation_cost"] = result["cost"]
                script_data["provider_used"] = result["provider"]
                
                logger.info(f"✅ Generated {platform} video script - Cost: ${result['cost']:.4f} (Savings: {result['savings_vs_openai']['savings_percent']:.1f}%)")
                
                return script_data, result
            else:
                logger.warning("Ultra-cheap script generation failed, using fallback")
                return self._generate_fallback_script(product_name, video_type, platform, duration), {"cost": 0, "fallback": True}
        
        except Exception as e:
            logger.error(f"Video script generation failed: {str(e)}")
            return self._generate_fallback_script(product_name, video_type, platform, duration), {"cost": 0, "error": str(e)}
    
    def _parse_video_script(self, content, video_type, platform, duration):
        """Parse video script from AI response"""
        
        lines = content.split('\n')
        
        script_segments = []
        current_segment = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for time markers [0-5s], [5-15s], etc.
            if '[' in line and 's]' in line and ('HOOK' in line.upper() or 'PROBLEM' in line.upper() or 'SOLUTION' in line.upper() or 'CTA' in line.upper() or 'CALL' in line.upper()):
                if current_segment:
                    script_segments.append(current_segment)
                
                current_segment = {
                    "segment_type": self._extract_segment_type(line),
                    "time_range": self._extract_time_range(line),
                    "narration": "",
                    "visual_cues": [],
                    "text_overlays": []
                }
            elif current_segment:
                # Process content for current segment
                if line.startswith('[') and line.endswith(']'):
                    current_segment["visual_cues"].append(line[1:-1])
                elif line.startswith('"') and line.endswith('"'):
                    current_segment["text_overlays"].append(line[1:-1])
                else:
                    current_segment["narration"] += line + " "
        
        # Add last segment
        if current_segment:
            script_segments.append(current_segment)
        
        # Clean up narration
        for segment in script_segments:
            segment["narration"] = segment["narration"].strip()
        
        return {
            "full_script": content,
            "segments": script_segments,
            "video_type": video_type,
            "platform": platform,
            "duration": duration,
            "generated_at": datetime.utcnow().isoformat()
        }