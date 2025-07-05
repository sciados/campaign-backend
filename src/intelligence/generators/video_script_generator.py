# src/intelligence/generators/video_script_generator.py
"""
VIDEO SCRIPT GENERATOR
✅ Platform-specific video scripts (YouTube, TikTok, Instagram, Facebook)
✅ Multiple video types (explainer, testimonial, demo, ad)
✅ Scene breakdown with visual notes
✅ Timing and engagement optimization
🔥 FIXED: Enum serialization issues resolved
"""

import os
import logging
import uuid
import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.intelligence.utils.enum_serializer import EnumSerializerMixin

logger = logging.getLogger(__name__)

class VideoScriptGenerator(EnumSerializerMixin):
    """Generate platform-optimized video scripts for different video types"""
    
    def __init__(self):
        self.ai_providers = self._initialize_ai_providers()
        self.video_types = ["explainer", "testimonial", "demo", "ad", "social", "webinar"]
        self.platforms = ["youtube", "tiktok", "instagram", "facebook", "linkedin"]
        
    def _initialize_ai_providers(self):
        """Initialize AI providers for video scripts"""
        providers = []
        
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                import openai
                providers.append({
                    "name": "openai",
                    "client": openai.AsyncOpenAI(api_key=api_key),
                    "models": ["gpt-4"],
                    "strengths": ["creativity", "storytelling", "engagement"]
                })
                logger.info("✅ OpenAI provider initialized for video scripts")
        except Exception as e:
            logger.warning(f"OpenAI not available for video scripts: {str(e)}")
            
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                import anthropic
                providers.append({
                    "name": "anthropic",
                    "client": anthropic.AsyncAnthropic(api_key=api_key),
                    "models": ["claude-3-5-sonnet-20241022"],
                    "strengths": ["structured_content", "detailed_scripts"]
                })
                logger.info("✅ Anthropic provider initialized for video scripts")
        except Exception as e:
            logger.warning(f"Anthropic not available for video scripts: {str(e)}")
            
        return providers
    
    async def generate_video_script(
        self, 
        intelligence_data: Dict[str, Any], 
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive video script"""
        
        if preferences is None:
            preferences = {}
            
        video_type = preferences.get("video_type", "explainer")
        platform = preferences.get("platform", "youtube")
        duration = preferences.get("duration", "60-90 seconds")
        tone = preferences.get("tone", "conversational")
        
        product_name = self._extract_product_name(intelligence_data)
        
        video_script = None
        
        for provider in self.ai_providers:
            try:
                video_script = await self._generate_video_script_content(
                    provider, video_type, platform, duration, tone, product_name, intelligence_data
                )
                
                if video_script:
                    break
                    
            except Exception as e:
                logger.error(f"Video script generation failed with {provider['name']}: {str(e)}")
                continue
        
        if not video_script:
            video_script = self._generate_fallback_video_script(product_name, video_type, platform, duration)
        
        return {
            "content_type": "video_script",
            "title": f"{product_name} {video_type.title()} Script - {platform.title()}",
            "content": {
                "script_text": video_script.get("script_text"),
                "scenes": video_script.get("scenes", []),
                "visual_notes": video_script.get("visual_notes", []),
                "timing_breakdown": video_script.get("timing_breakdown", {}),
                "engagement_elements": video_script.get("engagement_elements", []),
                "platform_optimization": video_script.get("platform_optimization", {}),
                "duration_estimate": duration,
                "video_type": video_type
            },
            "metadata": {
                "generated_by": "video_script_ai",
                "product_name": product_name,
                "content_type": "video_script",
                "video_type": video_type,
                "platform": platform,
                "duration": duration,
                "tone": tone,
                "scene_count": len(video_script.get("scenes", [])),
                "engagement_optimized": True
            }
        }
    
    async def _generate_video_script_content(self, provider, video_type, platform, duration, tone, product_name, intelligence_data):
        """Generate video script content with AI"""
        
        # Platform specifications
        platform_specs = {
            "youtube": {
                "optimal_length": "3-10 minutes",
                "hook_duration": "15 seconds",
                "features": ["detailed_explanation", "subscribe_cta", "end_screen"],
                "aspect_ratio": "16:9"
            },
            "tiktok": {
                "optimal_length": "15-60 seconds",
                "hook_duration": "3 seconds", 
                "features": ["trending_audio", "quick_cuts", "text_overlay"],
                "aspect_ratio": "9:16"
            },
            "instagram": {
                "optimal_length": "30-90 seconds",
                "hook_duration": "5 seconds",
                "features": ["stories_friendly", "reels_format", "hashtags"],
                "aspect_ratio": "9:16 or 1:1"
            },
            "facebook": {
                "optimal_length": "1-3 minutes",
                "hook_duration": "10 seconds",
                "features": ["auto_play", "captions", "share_worthy"],
                "aspect_ratio": "16:9 or 1:1"
            },
            "linkedin": {
                "optimal_length": "30-90 seconds",
                "hook_duration": "10 seconds",
                "features": ["professional_tone", "thought_leadership", "industry_insights"],
                "aspect_ratio": "16:9"
            }
        }
        
        spec = platform_specs.get(platform, platform_specs["youtube"])
        
        # Video type specifications
        video_type_specs = {
            "explainer": {
                "structure": ["hook", "problem", "solution", "benefits", "cta"],
                "focus": "education and understanding"
            },
            "testimonial": {
                "structure": ["introduction", "before_situation", "discovery", "results", "recommendation"],
                "focus": "social proof and credibility"
            },
            "demo": {
                "structure": ["hook", "product_intro", "demonstration", "benefits", "cta"],
                "focus": "product functionality"
            },
            "ad": {
                "structure": ["hook", "pain_point", "solution", "benefits", "urgent_cta"],
                "focus": "conversion and action"
            },
            "social": {
                "structure": ["hook", "story", "reveal", "value", "engagement_cta"],
                "focus": "engagement and shareability"
            },
            "webinar": {
                "structure": ["intro", "agenda", "main_content", "q_and_a", "next_steps"],
                "focus": "education and lead generation"
            }
        }
        
        video_spec = video_type_specs.get(video_type, video_type_specs["explainer"])
        
        # 🔥 FIXED: Extract intelligence with proper enum serialization
        emotional_intel = self._serialize_enum_field(intelligence_data.get("emotional_transformation_intelligence", {}))
        scientific_intel = self._serialize_enum_field(intelligence_data.get("scientific_authority_intelligence", {}))
        social_proof_intel = self._serialize_enum_field(intelligence_data.get("community_social_proof_intelligence", {}))
        
        prompt = f"""
Create a detailed {video_type} video script for {product_name} optimized for {platform}.

Video Specifications:
- Type: {video_type}
- Platform: {platform}
- Duration: {duration}
- Tone: {tone}
- Hook Duration: {spec['hook_duration']}
- Aspect Ratio: {spec['aspect_ratio']}

Product: {product_name}
Focus: Health optimization, liver support, natural wellness
Scientific Support: {', '.join(scientific_intel.get('clinical_studies', ['Research-backed'])[:3])}

Script Structure: {' → '.join(video_spec['structure'])}
Focus: {video_spec['focus']}

Platform Features to Include: {', '.join(spec['features'])}

Requirements:
- Engaging hook within {spec['hook_duration']}
- Clear scene-by-scene breakdown
- Visual direction notes for each scene
- Timing estimates for each section
- Platform-specific engagement elements
- Strong call-to-action
- {tone} tone throughout

Format the script as:

SCENE 1: [Scene Name] (0:00-0:XX)
VISUAL: [Describe what viewers see]
AUDIO/DIALOGUE: [Spoken content]
TEXT OVERLAY: [Any text elements]
NOTES: [Direction notes]

[Continue for each scene...]

TIMING BREAKDOWN:
- Hook: X seconds
- Main Content: X seconds  
- CTA: X seconds
- Total: X seconds

ENGAGEMENT ELEMENTS:
- [List platform-specific engagement tactics]

Make it conversion-focused while providing value to the viewer.
"""
        
        try:
            if provider["name"] == "openai":
                response = await provider["client"].chat.completions.create(
                    model=provider["models"][0],
                    messages=[
                        {"role": "system", "content": f"You are an expert video script writer creating {video_type} scripts for {platform}. Focus on engagement, value, and conversion."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=3000
                )
                
                content = response.choices[0].message.content
                return self._parse_video_script(content, video_type, platform, product_name)
                
            elif provider["name"] == "anthropic":
                response = await provider["client"].messages.create(
                    model=provider["models"][0],
                    max_tokens=3000,
                    temperature=0.8,
                    system=f"You are an expert video script writer creating {video_type} scripts for {platform}. Focus on engagement, storytelling, and clear structure.",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                content = response.content[0].text
                return self._parse_video_script(content, video_type, platform, product_name)
        
        except Exception as e:
            logger.error(f"Video script content generation failed: {str(e)}")
            return None
    
    def _parse_video_script(self, content: str, video_type: str, platform: str, product_name: str) -> Dict[str, Any]:
        """Parse video script from AI response"""
        
        scenes = []
        timing_breakdown = {}
        engagement_elements = []
        visual_notes = []
        
        # Parse scenes using regex
        scene_pattern = r'SCENE\s+(\d+):\s*([^(]+)\s*\(([^)]+)\)(.*?)(?=SCENE\s+\d+:|TIMING BREAKDOWN:|ENGAGEMENT ELEMENTS:|$)'
        scene_matches = re.findall(scene_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for match in scene_matches:
            scene_number = match[0]
            scene_name = match[1].strip()
            timing = match[2].strip()
            scene_content = match[3].strip()
            
            # Parse scene content
            visual = ""
            audio = ""
            text_overlay = ""
            notes = ""
            
            lines = scene_content.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.upper().startswith('VISUAL:'):
                    current_section = 'visual'
                    visual = line[7:].strip()
                elif line.upper().startswith('AUDIO') or line.upper().startswith('DIALOGUE:'):
                    current_section = 'audio'
                    audio = line.split(':', 1)[1].strip() if ':' in line else line
                elif line.upper().startswith('TEXT OVERLAY:'):
                    current_section = 'text'
                    text_overlay = line[13:].strip()
                elif line.upper().startswith('NOTES:'):
                    current_section = 'notes'
                    notes = line[6:].strip()
                else:
                    # Continue previous section
                    if current_section == 'visual':
                        visual += ' ' + line
                    elif current_section == 'audio':
                        audio += ' ' + line
                    elif current_section == 'text':
                        text_overlay += ' ' + line
                    elif current_section == 'notes':
                        notes += ' ' + line
            
            scene_data = {
                "scene_number": int(scene_number),
                "scene_name": scene_name,
                "timing": timing,
                "visual_description": visual,
                "audio_dialogue": audio,
                "text_overlay": text_overlay,
                "director_notes": notes
            }
            
            scenes.append(scene_data)
            
            # Add to visual notes
            if visual:
                visual_notes.append(f"Scene {scene_number}: {visual}")
        
        # Parse timing breakdown
        timing_section = re.search(r'TIMING BREAKDOWN:(.*?)(?=ENGAGEMENT ELEMENTS:|$)', content, re.DOTALL | re.IGNORECASE)
        if timing_section:
            timing_lines = timing_section.group(1).strip().split('\n')
            for line in timing_lines:
                line = line.strip()
                if ':' in line and 'second' in line.lower():
                    parts = line.split(':')
                    if len(parts) >= 2:
                        key = parts[0].strip(' -•')
                        value = parts[1].strip()
                        timing_breakdown[key] = value
        
        # Parse engagement elements
        engagement_section = re.search(r'ENGAGEMENT ELEMENTS:(.*?)$', content, re.DOTALL | re.IGNORECASE)
        if engagement_section:
            engagement_lines = engagement_section.group(1).strip().split('\n')
            for line in engagement_lines:
                line = line.strip(' -•')
                if line:
                    engagement_elements.append(line)
        
        # Platform optimization notes
        platform_optimization = self._get_platform_optimization_notes(platform, video_type)
        
        return {
            "script_text": content,
            "scenes": scenes,
            "visual_notes": visual_notes,
            "timing_breakdown": timing_breakdown,
            "engagement_elements": engagement_elements,
            "platform_optimization": platform_optimization,
            "scene_count": len(scenes),
            "estimated_duration": self._estimate_duration_from_scenes(scenes)
        }
    
    def _get_platform_optimization_notes(self, platform: str, video_type: str) -> Dict[str, Any]:
        """Get platform-specific optimization notes"""
        
        base_notes = {
            "youtube": {
                "thumbnail_tips": "Use bright colors and clear text",
                "title_optimization": "Include keywords and emotional triggers", 
                "description_strategy": "Front-load important information",
                "end_screen_elements": "Subscribe button and related videos"
            },
            "tiktok": {
                "trending_elements": "Use popular sounds and effects",
                "hashtag_strategy": "Mix trending and niche hashtags",
                "editing_style": "Quick cuts and dynamic transitions",
                "text_overlay_tips": "Large, readable fonts"
            },
            "instagram": {
                "stories_optimization": "Use polls, questions, and stickers",
                "reels_strategy": "Follow trending audio and effects",
                "caption_approach": "Engaging first line for feed posts",
                "hashtag_mix": "Combine popular and niche tags"
            },
            "facebook": {
                "auto_play_optimization": "Strong visual hook in first 3 seconds",
                "caption_strategy": "Include captions for sound-off viewing",
                "sharing_elements": "Make content share-worthy",
                "engagement_tactics": "Ask questions to drive comments"
            },
            "linkedin": {
                "professional_tone": "Maintain business-appropriate content",
                "thought_leadership": "Share industry insights",
                "networking_focus": "Encourage professional connections",
                "value_proposition": "Lead with business benefits"
            }
        }
        
        return base_notes.get(platform, base_notes["youtube"])
    
    def _estimate_duration_from_scenes(self, scenes: List[Dict]) -> str:
        """Estimate total video duration from scenes"""
        
        total_seconds = 0
        
        for scene in scenes:
            timing = scene.get("timing", "")
            
            # Extract seconds from timing strings like "0:00-0:15" or "15 seconds"
            if "-" in timing:
                time_parts = timing.split("-")
                if len(time_parts) == 2:
                    try:
                        start_time = self._parse_time_to_seconds(time_parts[0])
                        end_time = self._parse_time_to_seconds(time_parts[1])
                        total_seconds += (end_time - start_time)
                    except:
                        total_seconds += 10  # Default 10 seconds per scene
            else:
                total_seconds += 10  # Default 10 seconds per scene
        
        if total_seconds > 0:
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            if minutes > 0:
                return f"{minutes}:{seconds:02d}"
            else:
                return f"{seconds} seconds"
        
        return "60-90 seconds"
    
    def _parse_time_to_seconds(self, time_str: str) -> int:
        """Parse time string to seconds"""
        
        time_str = time_str.strip()
        
        if ":" in time_str:
            parts = time_str.split(":")
            if len(parts) == 2:
                minutes = int(parts[0])
                seconds = int(parts[1])
                return minutes * 60 + seconds
        
        # Extract number if it's just seconds
        numbers = re.findall(r'\d+', time_str)
        if numbers:
            return int(numbers[0])
        
        return 0
    
    def _generate_fallback_video_script(self, product_name: str, video_type: str, platform: str, duration: str) -> Dict[str, Any]:
        """Generate fallback video script"""
        
        # Determine script structure based on video type
        if video_type == "explainer":
            scenes = [
                {
                    "scene_number": 1,
                    "scene_name": "Hook",
                    "timing": "0:00-0:05",
                    "visual_description": "Close-up of person looking tired and sluggish",
                    "audio_dialogue": f"Are you tired of feeling tired? {product_name} might be the answer you've been looking for.",
                    "text_overlay": "Feeling Tired?",
                    "director_notes": "Use relatable imagery to connect with audience"
                },
                {
                    "scene_number": 2,
                    "scene_name": "Problem",
                    "timing": "0:05-0:20",
                    "visual_description": "Split screen showing unhealthy vs healthy lifestyle",
                    "audio_dialogue": f"Your liver works 24/7 to keep you healthy, but modern life puts it under constant stress. That's where {product_name} comes in.",
                    "text_overlay": "Liver Health Matters",
                    "director_notes": "Use visual metaphors to explain liver function"
                },
                {
                    "scene_number": 3,
                    "scene_name": "Solution",
                    "timing": "0:20-0:45",
                    "visual_description": f"Product shots of {product_name} with natural ingredients",
                    "audio_dialogue": f"{product_name} is scientifically formulated to support your liver's natural detoxification processes using research-backed ingredients.",
                    "text_overlay": "Science-Backed Formula",
                    "director_notes": "Show product clearly with professional lighting"
                },
                {
                    "scene_number": 4,
                    "scene_name": "Benefits",
                    "timing": "0:45-1:00",
                    "visual_description": "Person looking energetic and healthy",
                    "audio_dialogue": "Experience improved energy, better metabolism, and overall wellness with natural liver support.",
                    "text_overlay": "Real Results",
                    "director_notes": "Show transformation and positive outcomes"
                },
                {
                    "scene_number": 5,
                    "scene_name": "Call to Action",
                    "timing": "1:00-1:10",
                    "visual_description": f"{product_name} bottle with website/contact information",
                    "audio_dialogue": f"Ready to transform your health? Learn more about {product_name} today.",
                    "text_overlay": "Learn More Now",
                    "director_notes": "Clear, prominent call-to-action"
                }
            ]
        else:
            # Generic fallback structure
            scenes = [
                {
                    "scene_number": 1,
                    "scene_name": "Introduction",
                    "timing": "0:00-0:15",
                    "visual_description": f"Professional presentation of {product_name}",
                    "audio_dialogue": f"Discover the benefits of {product_name} for natural health optimization.",
                    "text_overlay": product_name,
                    "director_notes": "Professional, clean presentation"
                },
                {
                    "scene_number": 2,
                    "scene_name": "Main Content",
                    "timing": "0:15-0:45",
                    "visual_description": "Supporting visuals and graphics",
                    "audio_dialogue": f"{product_name} offers a science-backed approach to liver health and overall wellness through natural ingredients.",
                    "text_overlay": "Science-Backed Results",
                    "director_notes": "Use supporting graphics and testimonials"
                },
                {
                    "scene_number": 3,
                    "scene_name": "Conclusion",
                    "timing": "0:45-1:00",
                    "visual_description": "Call-to-action screen",
                    "audio_dialogue": f"Experience the difference {product_name} can make in your health journey.",
                    "text_overlay": "Get Started Today",
                    "director_notes": "Strong, clear call-to-action"
                }
            ]
        
        visual_notes = [f"Scene {scene['scene_number']}: {scene['visual_description']}" for scene in scenes]
        
        timing_breakdown = {
            "Hook": "5 seconds",
            "Main Content": "35 seconds", 
            "CTA": "10 seconds",
            "Total": "50 seconds"
        }
        
        engagement_elements = [
            f"Strong hook within first 5 seconds for {platform}",
            f"Clear visual storytelling appropriate for {video_type}",
            "Professional product presentation",
            "Compelling call-to-action",
            f"Optimized for {platform} viewing experience"
        ]
        
        script_text = f"""
{video_type.upper()} VIDEO SCRIPT - {product_name}
Platform: {platform}
Duration: {duration}

""" + "\n\n".join([
    f"SCENE {scene['scene_number']}: {scene['scene_name']} ({scene['timing']})\n"
    f"VISUAL: {scene['visual_description']}\n"
    f"AUDIO/DIALOGUE: {scene['audio_dialogue']}\n"
    f"TEXT OVERLAY: {scene['text_overlay']}\n"
    f"NOTES: {scene['director_notes']}"
    for scene in scenes
])
        
        platform_optimization = self._get_platform_optimization_notes(platform, video_type)
        
        return {
            "script_text": script_text,
            "scenes": scenes,
            "visual_notes": visual_notes,
            "timing_breakdown": timing_breakdown,
            "engagement_elements": engagement_elements,
            "platform_optimization": platform_optimization,
            "scene_count": len(scenes),
            "estimated_duration": duration,
            "fallback_generated": True
        }
    
    def _extract_product_name(self, intelligence_data):
        """Extract product name from intelligence"""
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