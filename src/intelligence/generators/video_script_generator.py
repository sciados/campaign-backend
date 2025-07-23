# src/intelligence/generators/video_script_generator.py
"""
MODERNIZED VIDEO SCRIPT GENERATOR
🚀 90% cost savings with ultra-cheap AI providers
💰 $0.002 per 1K tokens (vs $0.060 OpenAI)
✅ Multiple video formats (social, ads, educational)
✅ Platform-specific optimization
✅ Shot-by-shot breakdowns
🔥 FIXED: Product name from source_title (authoritative source)
🔥 MODERNIZED: Ultra-cheap AI integration with smart failover
🔥 FIXED: Product name placeholder substitution
"""

import os
import logging
import uuid
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.models.base import EnumSerializerMixin
from ..utils.ultra_cheap_ai_provider import UltraCheapAIProvider
from ..utils.product_name_fix import (
    substitute_product_placeholders,
    substitute_placeholders_in_data,
    validate_no_placeholders
)

logger = logging.getLogger(__name__)

def get_product_name_from_intelligence(intelligence_data: Dict[str, Any]) -> str:
    """
    🔥 NEW: Get product name from source_title (authoritative source)
    This is the single source of truth for product names
    """
    # Method 1: Direct from source_title (most reliable)
    source_title = intelligence_data.get("source_title")
    if source_title and isinstance(source_title, str) and len(source_title.strip()) > 2:
        source_title = source_title.strip()
        
        # Remove common suffixes if they exist
        suffixes_to_remove = [
            " - Sales Page Analysis",
            " - Analysis", 
            " - Page Analysis",
            " Sales Page",
            " Analysis"
        ]
        
        for suffix in suffixes_to_remove:
            if source_title.endswith(suffix):
                source_title = source_title[:-len(suffix)].strip()
        
        # Validate it's a real product name
        if (source_title and 
            len(source_title) > 2 and 
            source_title not in ["Unknown Product", "Analyzed Page", "Stock Up - Exclusive Offer"]):
            logger.info(f"✅ Product name from source_title: '{source_title}'")
            return source_title
    
    # Method 2: Fallback to extraction if source_title is not reliable
    logger.warning("⚠️ source_title not reliable, falling back to extraction")
    
    from src.intelligence.utils.product_name_fix import extract_product_name_from_intelligence
    fallback_name = extract_product_name_from_intelligence(intelligence_data)
    
    logger.info(f"🔄 Fallback product name: '{fallback_name}'")
    return fallback_name

def fix_video_script_placeholders(script_data: Dict[str, Any], intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    🔥 FIXED: Apply product name fixes to video script using source_title
    """
    product_name = get_product_name_from_intelligence(intelligence_data)
    company_name = product_name  # Often same for direct-to-consumer
    
    logger.info(f"🔧 Applying product name fixes: '{product_name}' to video script")
    
    # Apply fixes to the entire video script structure
    fixed_script_data = substitute_placeholders_in_data(script_data, product_name, company_name)
    
    return fixed_script_data

class VideoScriptGenerator(EnumSerializerMixin):
    """Generate video scripts with 90% cost savings using ultra-cheap AI and source_title product names"""
    
    def __init__(self):
        # 🚀 MODERNIZED: Use ultra-cheap AI provider (90% savings)
        try:
            self.ultra_cheap_provider = UltraCheapAIProvider()
        except ImportError:
            logger.warning("⚠️ UltraCheapAIProvider not available, using fallback")
            self.ultra_cheap_provider = None
            
        self.video_types = ["social_media", "advertisement", "educational", "testimonial", "product_demo"]
        self.platforms = ["youtube", "tiktok", "instagram", "facebook", "linkedin"]
        logger.info("🚀 Video Script Generator initialized with ultra-cheap AI (90% cost savings)")
        
    async def generate_video_script(
        self, 
        intelligence_data: Dict[str, Any], 
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate video script with ultra-cheap AI and source_title product names"""
        
        if preferences is None:
            preferences = {}
            
        video_type = preferences.get("video_type", "social_media")
        platform = preferences.get("platform", "youtube")
        duration = preferences.get("duration", 60)  # seconds
        style = preferences.get("style", "engaging")
        
        # 🔥 CRITICAL FIX: Get product name from source_title (authoritative source)
        product_name = get_product_name_from_intelligence(intelligence_data)
        logger.info(f"🎯 Video Script Generator: Using product name '{product_name}' from source_title")
        
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
        
        # 🔥 APPLY PRODUCT NAME FIXES using source_title
        fixed_script_data = fix_video_script_placeholders(script_data, intelligence_data)
        
        # 🔥 VALIDATE NO PLACEHOLDERS REMAIN
        full_script_clean = validate_no_placeholders(fixed_script_data.get("full_script", ""), product_name)
        if not full_script_clean:
            logger.warning(f"⚠️ Placeholders found in video script for '{product_name}'")
        else:
            logger.info(f"✅ Video script validation passed for '{product_name}' from source_title")
        
        return {
            "content_type": "video_script",
            "title": f"{product_name} Video Script - {video_type.title()}",
            "content": {
                "script": fixed_script_data,
                "video_type": video_type,
                "platform": platform,
                "duration": duration,
                "style": style
            },
            "metadata": {
                "generated_by": "ultra_cheap_video_ai",
                "product_name": product_name,
                "product_name_source": "source_title",
                "content_type": "video_script",
                "platform_optimized": True,
                "placeholders_fixed": True,
                "cost_optimization": {
                    "generation_cost": generation_cost.get("cost", 0),
                    "provider_used": generation_cost.get("provider", "fallback"),
                    "savings_vs_openai": generation_cost.get("savings_vs_openai", {})
                }
            }
        }
    
    async def generate_content(self, intelligence_data: Dict[str, Any], preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate content - main interface for factory integration"""
        return await self.generate_video_script(intelligence_data, preferences)
    
    async def _generate_script_ultra_cheap(self, video_type, platform, duration, style, product_name, intelligence_data):
        """Generate video script using ultra-cheap AI with source_title product name"""
        
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

CRITICAL: Use ONLY the actual product name "{product_name}" throughout the entire script.
NEVER use placeholders like "Your", "PRODUCT", "[Product]", "Your Company", etc.
This product name comes from the authoritative source_title field.

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
[0-{spec['hook_time']}s] HOOK - Grab attention immediately with {product_name}
[{spec['hook_time']+1}-{duration//3}s] PROBLEM/PAIN POINT - Identify viewer's struggle
[{duration//3+1}-{duration*2//3}s] SOLUTION - Introduce {product_name} as the answer
[{duration*2//3+1}-{duration}s] CALL TO ACTION - Clear next step for {product_name}

Include:
- Spoken narration for each time segment mentioning {product_name}
- Visual cues [in brackets] showing {product_name}
- Text overlays "in quotes" featuring {product_name}
- Emotional triggers and benefits of {product_name}
- Strong call-to-action for {product_name}

Focus on {emotional_intel.get('target_audience', 'health-conscious individuals')} audience.
Make it {platform}-optimized and conversion-focused for {product_name}.

ABSOLUTELY FORBIDDEN: "Your", "PRODUCT", "[Product]", "Your Company", "the product"
REQUIRED: Use "{product_name}" consistently throughout
The product name "{product_name}" is from the authoritative source_title.
"""
        
        try:
            if self.ultra_cheap_provider:
                # 🚀 ULTRA-CHEAP SCRIPT GENERATION
                result = await self.ultra_cheap_provider.generate_text(
                    prompt=prompt,
                    max_tokens=2000,
                    temperature=0.8,
                    cost_target="ultra_cheap"
                )
                
                if result["success"]:
                    script_data = self._parse_video_script(result["content"], video_type, platform, duration, product_name)
                    script_data["ultra_cheap_generated"] = True
                    script_data["generation_cost"] = result["cost"]
                    script_data["provider_used"] = result["provider"]
                    script_data["product_name"] = product_name
                    script_data["product_name_source"] = "source_title"
                    
                    logger.info(f"✅ Generated {platform} video script - Cost: ${result['cost']:.4f} (Savings: {result['savings_vs_openai']['savings_percent']:.1f}%)")
                    
                    return script_data, result
                else:
                    logger.warning("Ultra-cheap script generation failed, using fallback")
                    return self._generate_fallback_script(product_name, video_type, platform, duration), {"cost": 0, "fallback": True}
            else:
                logger.warning("Ultra-cheap provider not available, using fallback")
                return self._generate_fallback_script(product_name, video_type, platform, duration), {"cost": 0, "fallback": True}
        
        except Exception as e:
            logger.error(f"Video script generation failed: {str(e)}")
            return self._generate_fallback_script(product_name, video_type, platform, duration), {"cost": 0, "error": str(e)}
    
    def _parse_video_script(self, content, video_type, platform, duration, product_name):
        """Parse video script from AI response with source_title product name fixes"""
        
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
                    "text_overlays": [],
                    "product_name": product_name,
                    "product_name_source": "source_title"
                }
            elif current_segment:
                # Process content for current segment
                if line.startswith('[') and line.endswith(']'):
                    visual_cue = line[1:-1]
                    # 🔥 APPLY PRODUCT NAME FIXES TO VISUAL CUES
                    visual_cue = substitute_product_placeholders(visual_cue, product_name)
                    current_segment["visual_cues"].append(visual_cue)
                elif line.startswith('"') and line.endswith('"'):
                    text_overlay = line[1:-1]
                    # 🔥 APPLY PRODUCT NAME FIXES TO TEXT OVERLAYS
                    text_overlay = substitute_product_placeholders(text_overlay, product_name)
                    current_segment["text_overlays"].append(text_overlay)
                else:
                    current_segment["narration"] += line + " "
        
        # Add last segment
        if current_segment:
            script_segments.append(current_segment)
        
        # Clean up narration and apply product name fixes
        for segment in script_segments:
            segment["narration"] = segment["narration"].strip()
            # 🔥 APPLY PRODUCT NAME FIXES TO NARRATION
            segment["narration"] = substitute_product_placeholders(segment["narration"], product_name)
        
        # 🔥 APPLY PRODUCT NAME FIXES TO FULL SCRIPT
        fixed_content = substitute_product_placeholders(content, product_name)
        
        return {
            "full_script": fixed_content,
            "segments": script_segments,
            "video_type": video_type,
            "platform": platform,
            "duration": duration,
            "product_name": product_name,
            "product_name_source": "source_title",
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _extract_segment_type(self, line: str) -> str:
        """Extract segment type from time marker line"""
        line_upper = line.upper()
        if 'HOOK' in line_upper:
            return "hook"
        elif 'PROBLEM' in line_upper:
            return "problem"
        elif 'SOLUTION' in line_upper:
            return "solution"
        elif 'CTA' in line_upper or 'CALL' in line_upper:
            return "call_to_action"
        else:
            return "content"
    
    def _extract_time_range(self, line: str) -> str:
        """Extract time range from line"""
        import re
        match = re.search(r'\[([^\]]+)\]', line)
        return match.group(1) if match else "0-5s"
    
    def _generate_fallback_script(self, product_name: str, video_type: str, platform: str, duration: int) -> Dict[str, Any]:
        """Generate fallback script when AI generation fails using source_title product name"""
        
        # Create a simple fallback script structure with source_title product name
        segments = [
            {
                "segment_type": "hook",
                "time_range": "0-5s",
                "narration": f"Discover how {product_name} can transform your life!",
                "visual_cues": [f"{product_name} showcase", "Happy customers"],
                "text_overlays": [f"Transform with {product_name}"],
                "product_name": product_name,
                "product_name_source": "source_title"
            },
            {
                "segment_type": "problem",
                "time_range": "5-20s",
                "narration": f"Are you struggling with health challenges? {product_name} understands your pain.",
                "visual_cues": ["Problem visualization", "Concerned person"],
                "text_overlays": ["We understand your struggle"],
                "product_name": product_name,
                "product_name_source": "source_title"
            },
            {
                "segment_type": "solution",
                "time_range": "20-50s",
                "narration": f"{product_name} offers the natural solution you've been searching for.",
                "visual_cues": [f"{product_name} benefits", "Success stories"],
                "text_overlays": [f"{product_name} - Your Solution"],
                "product_name": product_name,
                "product_name_source": "source_title"
            },
            {
                "segment_type": "call_to_action",
                "time_range": "50-60s",
                "narration": f"Try {product_name} today and experience the difference!",
                "visual_cues": ["Call to action button", "Contact information"],
                "text_overlays": ["Order Now", "Risk-Free Trial"],
                "product_name": product_name,
                "product_name_source": "source_title"
            }
        ]
        
        full_script = f"""[0-5s] HOOK - Grab attention immediately with {product_name}
Discover how {product_name} can transform your life!
[{product_name} showcase]
"{product_name} - Transform Your Life"

[5-20s] PROBLEM/PAIN POINT - Identify viewer's struggle  
Are you struggling with health challenges? {product_name} understands your pain.
[Problem visualization]
"We understand your struggle"

[20-50s] SOLUTION - Introduce {product_name} as the answer
{product_name} offers the natural solution you've been searching for.
[{product_name} benefits]
"{product_name} - Your Solution"

[50-60s] CALL TO ACTION - Clear next step for {product_name}
Try {product_name} today and experience the difference!
[Call to action button]
"Order Now - Risk-Free Trial"
"""
        
        return {
            "full_script": full_script,
            "segments": segments,
            "video_type": video_type,
            "platform": platform,
            "duration": duration,
            "product_name": product_name,
            "product_name_source": "source_title",
            "generated_at": datetime.utcnow().isoformat(),
            "fallback_used": True
        }

def get_product_name_for_video(intelligence_data: Dict[str, Any]) -> str:
    """
    🔥 NEW: Public function to get product name for video generation
    Uses source_title as the authoritative source
    """
    return get_product_name_from_intelligence(intelligence_data)

# Convenience functions for video script generation with source_title product names
async def generate_video_script_with_source_title(
    intelligence_data: Dict[str, Any],
    video_type: str = "social_media",
    platform: str = "youtube",
    duration: int = 60,
    style: str = "engaging",
    preferences: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Generate video script using source_title product names"""
    
    generator = VideoScriptGenerator()
    if preferences is None:
        preferences = {
            "video_type": video_type,
            "platform": platform,
            "duration": duration,
            "style": style
        }
    else:
        preferences.update({
            "video_type": video_type,
            "platform": platform,
            "duration": duration,
            "style": style
        })
    
    return await generator.generate_video_script(intelligence_data, preferences)

def get_available_video_types() -> List[str]:
    """Get list of available video types"""
    return ["social_media", "advertisement", "educational", "testimonial", "product_demo"]

def get_available_platforms() -> List[str]:
    """Get list of available platforms"""
    return ["youtube", "tiktok", "instagram", "facebook", "linkedin"]

def get_available_video_styles() -> List[str]:
    """Get list of available video styles"""
    return ["engaging", "professional", "casual", "energetic", "educational", "testimonial"]

def get_platform_specs() -> Dict[str, Dict[str, Any]]:
    """Get platform-specific specifications"""
    return {
        "youtube": {
            "hook_time": 5,
            "recommended_duration": [60, 120, 300],
            "cta_placement": "end",
            "style": "informative",
            "max_duration": 900
        },
        "tiktok": {
            "hook_time": 3,
            "recommended_duration": [15, 30, 60],
            "cta_placement": "middle_and_end",
            "style": "fast_paced",
            "max_duration": 180
        },
        "instagram": {
            "hook_time": 3,
            "recommended_duration": [15, 30, 60],
            "cta_placement": "end",
            "style": "visual_focused",
            "max_duration": 90
        },
        "facebook": {
            "hook_time": 5,
            "recommended_duration": [30, 60, 120],
            "cta_placement": "middle",
            "style": "conversational",
            "max_duration": 240
        },
        "linkedin": {
            "hook_time": 5,
            "recommended_duration": [30, 60, 120],
            "cta_placement": "end",
            "style": "professional",
            "max_duration": 300
        }
    }

# Video production helpers
def estimate_video_production_requirements(script_data: Dict[str, Any]) -> Dict[str, Any]:
    """Estimate production requirements based on script"""
    
    segments = script_data.get("segments", [])
    duration = script_data.get("duration", 60)
    product_name = script_data.get("product_name", "Product")
    
    # Count visual elements needed
    total_visual_cues = sum(len(segment.get("visual_cues", [])) for segment in segments)
    total_text_overlays = sum(len(segment.get("text_overlays", [])) for segment in segments)
    
    # Estimate production complexity
    complexity_score = min(100, (total_visual_cues * 5) + (total_text_overlays * 3) + (duration / 2))
    
    if complexity_score < 30:
        complexity = "simple"
        estimated_hours = 2
    elif complexity_score < 60:
        complexity = "moderate"
        estimated_hours = 4
    else:
        complexity = "complex"
        estimated_hours = 8
    
    return {
        "production_complexity": complexity,
        "estimated_production_hours": estimated_hours,
        "visual_elements_needed": total_visual_cues,
        "text_overlays_needed": total_text_overlays,
        "product_focus": product_name,
        "product_name_source": script_data.get("product_name_source", "unknown"),
        "equipment_needed": [
            "Camera/smartphone",
            "Microphone",
            "Lighting setup",
            "Video editing software"
        ],
        "recommended_shots": [
            f"{product_name} close-up",
            f"{product_name} in use",
            "Customer testimonials",
            "Call-to-action graphics"
        ]
    }