# src/intelligence/generators/ad_copy_generator.py
"""
AD COPY GENERATOR
✅ Platform-specific ad copy (Facebook, Google, Instagram, LinkedIn, YouTube)
✅ Multiple ad variations with different angles
✅ Conversion-focused copy
✅ A/B testing variations
"""

import os
import logging
import uuid
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AdCopyGenerator:
    """Generate platform-specific ad copy for paid advertising"""
    
    def __init__(self):
        self.ai_providers = self._initialize_ai_providers()
        self.ad_platforms = ["facebook", "google", "instagram", "linkedin", "youtube"]
        
    def _initialize_ai_providers(self):
        """Initialize AI providers for ad copy"""
        providers = []
        
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                import openai
                providers.append({
                    "name": "openai",
                    "client": openai.AsyncOpenAI(api_key=api_key),
                    "models": ["gpt-4"],
                    "strengths": ["ad_copy", "conversion", "persuasion"]
                })
                logger.info("✅ OpenAI provider initialized for ad copy")
        except Exception as e:
            logger.warning(f"OpenAI not available for ad copy: {str(e)}")
            
        return providers
    
    async def generate_ad_copy(
        self, 
        intelligence_data: Dict[str, Any], 
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate ad copy for different platforms and objectives"""
        
        if preferences is None:
            preferences = {}
            
        platform = self._serialize_enum_field(intelligence_data.get("platform","facebook"))
        objective = self._serialize_enum_field(intelligence_data.get("objective", "conversions"))
        ad_count = self._serialize_enum_field(intelligence_data.get("count", 5))
        # platform = preferences.get("platform", "facebook")
        # objective = preferences.get("objective", "conversions")
        # ad_count = preferences.get("count", 5)
        
        product_name = self._extract_product_name(intelligence_data)
        
        ads = []
        
        for provider in self.ai_providers:
            try:
                generated_ads = await self._generate_platform_ads(
                    provider, platform, objective, product_name, intelligence_data, ad_count
                )
                ads.extend(generated_ads)
                
                if ads:
                    break
                    
            except Exception as e:
                logger.error(f"Ad generation failed with {provider['name']}: {str(e)}")
                continue
        
        if not ads:
            ads = self._generate_fallback_ads(product_name, platform, ad_count)
        
        return {
            "content_type": "ad_copy",
            "title": f"{product_name} Ad Copy - {platform.title()}",
            "content": {
                "ads": ads,
                "total_ads": len(ads),
                "platform": platform,
                "objective": objective
            },
            "metadata": {
                "generated_by": "ad_copy_ai",
                "product_name": product_name,
                "content_type": "ad_copy",
                "platform_optimized": True,
                "conversion_focused": True
            }
        }
    
    async def _generate_platform_ads(self, provider, platform, objective, product_name, intelligence_data, count):
        """Generate ads for specific platform and objective"""
        
        platform_specs = {
            "facebook": {
                "headline_length": 40,
                "description_length": 125,
                "features": ["video", "carousel", "single_image"]
            },
            "google": {
                "headline_length": 30,
                "description_length": 90,
                "features": ["search", "display", "shopping"]
            },
            "instagram": {
                "headline_length": 40,
                "description_length": 125,
                "features": ["stories", "feed", "reels"]
            },
            "linkedin": {
                "headline_length": 50,
                "description_length": 150,
                "features": ["sponsored_content", "message_ads"]
            },
            "youtube": {
                "headline_length": 60,
                "description_length": 200,
                "features": ["video", "discovery", "bumper"]
            }
        }
        
        #spec = platform_specs.get(platform, platform_specs["facebook"])
        spec = self._serialize_enum_field(platform_specs.get(platform, platform_specs["facebook"]))
        
        # Extract angle intelligence for ad copy
        # angles = intelligence_data.get("angle_selection_system", {}).get("available_angles", [])
        angles = self._serialize_enum_field(intelligence_data.get("angle_selection_system", {}).get("available_angles", []))

        prompt = f"""
Create {count} high-converting {platform} ads for {product_name}.

Platform: {platform}
Objective: {objective}
Headline limit: {spec['headline_length']} characters
Description limit: {spec['description_length']} characters

Product: {product_name}
Focus: Health optimization, liver support, natural wellness

Create ads using different angles:
1. Scientific authority (research-backed)
2. Emotional transformation (personal stories)
3. Social proof (testimonials)
4. Urgency/scarcity (limited time)
5. Lifestyle benefits (confidence, energy)

For each ad, provide:
- Headline (under {spec['headline_length']} chars)
- Description (under {spec['description_length']} chars)
- Call-to-action
- Target audience

Format:
AD 1:
Headline: [headline]
Description: [description]
CTA: [call to action]
Angle: [angle used]
---
"""
        
        try:
            if provider["name"] == "openai":
                response = await provider["client"].chat.completions.create(
                    model=provider["models"][0],
                    messages=[
                        {"role": "system", "content": f"Create high-converting {platform} ads focused on {objective}"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=2000
                )
                
                content = response.choices[0].message.content
                return self._parse_ad_copy(content, platform, product_name)
        
        except Exception as e:
            logger.error(f"Ad generation failed: {str(e)}")
            return []
    
    def _parse_ad_copy(self, content, platform, product_name):
        """Parse ad copy from AI response"""
        
        ads = []
        ad_blocks = content.split("---")
        
        for i, block in enumerate(ad_blocks):
            block = block.strip()
            if len(block) < 20:
                continue
            
            ad_data = {
                "ad_number": len(ads) + 1,
                "platform": platform,
                "headline": "",
                "description": "",
                "cta": "",
                "angle": "",
                "product_name": product_name
            }
            
            # Parse ad components
            lines = block.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith("Headline:"):
                    ad_data["headline"] = line[9:].strip()
                elif line.startswith("Description:"):
                    ad_data["description"] = line[12:].strip()
                elif line.startswith("CTA:"):
                    ad_data["cta"] = line[4:].strip()
                elif line.startswith("Angle:"):
                    ad_data["angle"] = line[6:].strip()
            
            # Validate ad has minimum components
            if ad_data["headline"] and ad_data["description"]:
                ads.append(ad_data)
        
        return ads[:5]
    
    def _generate_fallback_ads(self, product_name, platform, count):
        """Generate fallback ad copy"""
        
        fallback_ads = [
            {
                "headline": f"Discover {product_name} Benefits",
                "description": f"Natural health optimization with {product_name}. Science-backed approach to wellness.",
                "cta": "Learn More",
                "angle": "Scientific Authority"
            },
            {
                "headline": f"Transform Your Health with {product_name}",
                "description": f"Real results, real people. See why thousands choose {product_name} for better health.",
                "cta": "Get Started",
                "angle": "Emotional Transformation"
            },
            {
                "headline": f"Join 10K+ {product_name} Users",
                "description": f"Thousands of satisfied customers can't be wrong. Experience {product_name} benefits yourself.",
                "cta": "Join Now",
                "angle": "Social Proof"
            }
        ]
        
        ads = []
        for i in range(min(count, len(fallback_ads))):
            ad_data = fallback_ads[i].copy()
            ad_data.update({
                "ad_number": i + 1,
                "platform": platform,
                "product_name": product_name,
                "fallback_generated": True
            })
            ads.append(ad_data)
        
        return ads
    
    def _extract_product_name(self, intelligence_data):
        """Extract product name from intelligence"""
        #offer_intel = intelligence_data.get("offer_intelligence", {})
        offer_intel = self._serialize_enum_field(intelligence_data.get("offer_intelligence", {}))
        # insights = offer_intel.get("insights", [])
        insights = self._serialize_enum_field(offer_intel.get("insights", []))
        for insight in insights:
            if "called" in str(insight).lower():
                words = str(insight).split()
                for i, word in enumerate(words):
                    if word.lower() == "called" and i + 1 < len(words):
                        return words[i + 1].upper().replace(",", "").replace(".", "")
        
        return "PRODUCT"