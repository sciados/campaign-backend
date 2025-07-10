# src/intelligence/generators/ad_copy_generator.py
"""
ENHANCED AD COPY GENERATOR WITH ULTRA-CHEAP AI INTEGRATION
✅ 97% cost savings through unified ultra-cheap provider system
✅ Platform-specific ad copy (Facebook, Google, Instagram, LinkedIn, YouTube)
✅ Multiple ad variations with different angles for A/B testing
✅ Conversion-focused copy with automatic failover
✅ Real-time cost tracking and optimization
"""

import os
import logging
import uuid
import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import enhanced base generator with ultra-cheap AI
from .base_generator import BaseContentGenerator
from src.models.base import EnumSerializerMixin

logger = logging.getLogger(__name__)

class AdCopyGenerator(BaseContentGenerator, EnumSerializerMixin):
    """Enhanced ad copy generator with ultra-cheap AI integration"""
    
    def __init__(self):
        # Initialize with ultra-cheap AI system
        super().__init__("ad_copy")
        
        # Ad platform specifications
        self.ad_platforms = {
            "facebook": {
                "headline_length": 40,
                "description_length": 125,
                "features": ["video", "carousel", "single_image"],
                "audience": "social",
                "style": "conversational"
            },
            "google": {
                "headline_length": 30,
                "description_length": 90,
                "features": ["search", "display", "shopping"],
                "audience": "intent-driven",
                "style": "direct"
            },
            "instagram": {
                "headline_length": 40,
                "description_length": 125,
                "features": ["stories", "feed", "reels"],
                "audience": "visual",
                "style": "aesthetic"
            },
            "linkedin": {
                "headline_length": 50,
                "description_length": 150,
                "features": ["sponsored_content", "message_ads"],
                "audience": "professional",
                "style": "business"
            },
            "youtube": {
                "headline_length": 60,
                "description_length": 200,
                "features": ["video", "discovery", "bumper"],
                "audience": "video",
                "style": "engaging"
            }
        }
        
        # Ad objectives and their optimization strategies
        self.ad_objectives = {
            "conversions": {
                "focus": "direct action",
                "cta_strength": "high",
                "urgency": "medium",
                "social_proof": "high"
            },
            "traffic": {
                "focus": "click-through",
                "cta_strength": "medium",
                "urgency": "low",
                "social_proof": "medium"
            },
            "awareness": {
                "focus": "brand recognition",
                "cta_strength": "low",
                "urgency": "low",
                "social_proof": "high"
            },
            "engagement": {
                "focus": "interaction",
                "cta_strength": "medium",
                "urgency": "low",
                "social_proof": "medium"
            }
        }
        
        logger.info(f"✅ Ad Copy Generator: Ultra-cheap AI system ready with {len(self.ultra_cheap_providers)} providers")
        logger.info(f"🎯 Ad Platforms: {len(self.ad_platforms)} platforms configured")
    
    async def generate_ad_copy(
        self, 
        intelligence_data: Dict[str, Any], 
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate platform-specific ad copy with ultra-cheap AI"""
        
        if preferences is None:
            preferences = {}
        
        # Extract ad generation parameters
        platform = preferences.get("platform", "facebook")
        objective = preferences.get("objective", "conversions")
        ad_count = self._safe_int_conversion(preferences.get("count", "5"), 5, 1, 15)
        
        # Extract intelligence for ad generation
        product_details = self._extract_product_details(intelligence_data)
        platform_spec = self.ad_platforms.get(platform, self.ad_platforms["facebook"])
        objective_spec = self.ad_objectives.get(objective, self.ad_objectives["conversions"])
        
        logger.info(f"🎯 Generating {ad_count} {platform} ads for {product_details['name']} (Objective: {objective})")
        
        # Create comprehensive ad generation prompt
        ad_prompt = self._create_ad_generation_prompt(
            product_details, intelligence_data, platform, objective, ad_count, platform_spec, objective_spec
        )
        
        # Generate with ultra-cheap AI system
        try:
            ai_result = await self._generate_with_ultra_cheap_ai(
                prompt=ad_prompt,
                system_message="You are an expert paid advertising copywriter creating high-converting ad copy for affiliate campaigns. Focus on conversion optimization and A/B testing variations.",
                max_tokens=3000,
                temperature=0.9,  # Higher creativity for ad variations
                required_strength="creativity"  # Prefer providers good at creative content
            )
            
            if ai_result and ai_result.get("content"):
                # Parse ads from AI response
                ads = self._parse_ad_copy(ai_result["content"], platform, product_details['name'], objective)
                
                if ads and len(ads) >= ad_count:
                    # Apply platform and objective optimization
                    optimized_ads = self._optimize_ads_for_platform(ads, platform_spec, objective_spec)
                    
                    logger.info(f"✅ SUCCESS: Generated {len(optimized_ads)} conversion-optimized ads with ultra-cheap AI")
                    
                    return self._create_standardized_response(
                        content={
                            "ads": optimized_ads,
                            "total_ads": len(optimized_ads),
                            "platform": platform,
                            "objective": objective,
                            "campaign_focus": "High-converting affiliate ad copy with A/B testing variations"
                        },
                        title=f"{product_details['name']} Ad Copy - {platform.title()} {objective.title()}",
                        product_name=product_details['name'],
                        ai_result=ai_result,
                        preferences=preferences
                    )
        
        except Exception as e:
            logger.error(f"❌ Ultra-cheap AI ad generation failed: {str(e)}")
        
        # Enhanced fallback with platform optimization
        logger.warning("🔄 Using enhanced ad copy fallback with platform optimization")
        return self._guaranteed_ad_copy_fallback(product_details, platform, objective, ad_count)
    
    async def generate_content(self, intelligence_data: Dict[str, Any], preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate content - main interface for factory integration"""
        return await self.generate_ad_copy(intelligence_data, preferences)
    
    def _create_ad_generation_prompt(
        self, 
        product_details: Dict[str, str], 
        intelligence_data: Dict[str, Any], 
        platform: str, 
        objective: str,
        ad_count: int,
        platform_spec: Dict[str, Any],
        objective_spec: Dict[str, Any]
    ) -> str:
        """Create comprehensive ad generation prompt"""
        
        # Extract angle-specific intelligence
        angles_intel = self._extract_ad_angles_intelligence(intelligence_data)
        
        # Build platform-optimized ad prompt
        prompt = f"""
CONVERSION-OPTIMIZED AD COPY GENERATION
Platform: {platform.upper()}
Objective: {objective.upper()}

PRODUCT CAMPAIGN: {product_details['name']}
TARGET AUDIENCE: {product_details['audience']}
CORE BENEFITS: {product_details['benefits']}

PLATFORM REQUIREMENTS:
- Headline limit: {platform_spec['headline_length']} characters
- Description limit: {platform_spec['description_length']} characters
- Audience style: {platform_spec['audience']}
- Platform tone: {platform_spec['style']}

OBJECTIVE OPTIMIZATION:
- Campaign focus: {objective_spec['focus']}
- CTA strength: {objective_spec['cta_strength']}
- Urgency level: {objective_spec['urgency']}
- Social proof: {objective_spec['social_proof']}

CREATE {ad_count} DIFFERENT ADS USING STRATEGIC ANGLE ROTATION:

Ad 1 - SCIENTIFIC AUTHORITY ANGLE:
Focus: {angles_intel['scientific']['focus']}
Approach: Research-backed credibility, clinical validation, proven results
Triggers: "proven", "clinical", "research", "validated", "studies"

Ad 2 - EMOTIONAL TRANSFORMATION ANGLE:
Focus: {angles_intel['emotional']['focus']}
Approach: Personal transformation stories, breakthrough moments
Triggers: "breakthrough", "transformation", "finally", "freedom", "life-changing"

Ad 3 - SOCIAL PROOF ANGLE:
Focus: {angles_intel['community']['focus']}
Approach: Community validation, customer success stories
Triggers: "thousands trust", "customers love", "testimonials", "proven by users"

Ad 4 - URGENCY/SCARCITY ANGLE:
Focus: {angles_intel['urgency']['focus']}
Approach: Time-sensitive offers, limited availability
Triggers: "limited time", "exclusive", "act now", "before it's gone"

Ad 5 - LIFESTYLE/ASPIRATIONAL ANGLE:
Focus: {angles_intel['lifestyle']['focus']}
Approach: Aspirational lifestyle, confidence building
Triggers: "confident", "attractive", "energetic", "vibrant", "successful"

OUTPUT FORMAT (EXACT STRUCTURE REQUIRED):
===AD_1===
HEADLINE: [Scientific authority headline - under {platform_spec['headline_length']} chars]
DESCRIPTION: [Research-focused description - under {platform_spec['description_length']} chars]
CTA: [Strong call-to-action for {objective}]
ANGLE: Scientific Authority
TARGET: [Specific audience segment]
PLATFORM_OPT: {platform}
===END_AD_1===

===AD_2===
HEADLINE: [Emotional transformation headline - under {platform_spec['headline_length']} chars]
DESCRIPTION: [Story-driven description - under {platform_spec['description_length']} chars]
CTA: [Strong call-to-action for {objective}]
ANGLE: Emotional Transformation
TARGET: [Specific audience segment]
PLATFORM_OPT: {platform}
===END_AD_2===

[Continue this pattern for all {ad_count} ads]

CRITICAL REQUIREMENTS:
1. Each ad must use a completely different strategic angle
2. Headlines must be under {platform_spec['headline_length']} characters
3. Descriptions must be under {platform_spec['description_length']} characters
4. Optimize specifically for {platform} audience behavior
5. Focus on {objective} optimization with strong CTAs
6. Use '{product_details['name']}' consistently in all ads
7. Create clear A/B testing variations for affiliate campaigns

Generate the complete {ad_count}-ad campaign sequence now.
"""
        
        return prompt
    
    def _parse_ad_copy(self, ai_response: str, platform: str, product_name: str, objective: str) -> List[Dict]:
        """Parse ad copy from AI response with enhanced validation"""
        
        ads = []
        
        # Try structured parsing first
        try:
            ads = self._parse_structured_ad_format(ai_response, platform, product_name, objective)
            if ads and len(ads) >= 3:
                return ads
        except Exception as e:
            logger.warning(f"⚠️ Structured ad parsing failed: {str(e)}")
        
        # Try flexible parsing
        try:
            ads = self._parse_flexible_ad_format(ai_response, platform, product_name, objective)
            if ads and len(ads) >= 3:
                return ads
        except Exception as e:
            logger.warning(f"⚠️ Flexible ad parsing failed: {str(e)}")
        
        # Emergency extraction
        return self._emergency_ad_extraction(ai_response, platform, product_name, objective)
    
    def _parse_structured_ad_format(self, ai_response: str, platform: str, product_name: str, objective: str) -> List[Dict]:
        """Parse structured ===AD_X=== format"""
        
        ads = []
        ad_blocks = re.split(r'===AD_(\d+)===', ai_response, flags=re.IGNORECASE)
        
        if len(ad_blocks) > 1:
            ad_blocks = ad_blocks[1:]  # Remove content before first ad
        
        for i in range(0, len(ad_blocks) - 1, 2):
            try:
                ad_num = int(ad_blocks[i])
                ad_content = ad_blocks[i + 1] if i + 1 < len(ad_blocks) else ""
                
                # Clean up content
                ad_content = re.sub(r'===END_AD_\d+===.*$', '', ad_content, flags=re.DOTALL | re.IGNORECASE)
                ad_content = ad_content.strip()
                
                if not ad_content:
                    continue
                
                # Parse ad components
                ad_data = self._extract_ad_components(ad_content, ad_num, platform, product_name, objective)
                
                if ad_data and ad_data.get("headline") and ad_data.get("description"):
                    ads.append(ad_data)
                
            except (ValueError, IndexError) as e:
                logger.warning(f"⚠️ Error parsing ad block {i}: {str(e)}")
                continue
        
        return ads
    
    def _extract_ad_components(self, ad_content: str, ad_num: int, platform: str, product_name: str, objective: str) -> Dict[str, Any]:
        """Extract individual ad components from content"""
        
        ad_data = {
            "ad_number": ad_num,
            "platform": platform,
            "objective": objective,
            "headline": "",
            "description": "",
            "cta": "",
            "angle": "",
            "target_audience": "",
            "product_name": product_name,
            "ultra_cheap_generated": True
        }
        
        lines = ad_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Parse structured fields
            if line.upper().startswith('HEADLINE:'):
                headline_text = line[9:].strip()
                if headline_text:
                    ad_data["headline"] = headline_text
            elif line.upper().startswith('DESCRIPTION:'):
                desc_text = line[12:].strip()
                if desc_text:
                    ad_data["description"] = desc_text
            elif line.upper().startswith('CTA:'):
                cta_text = line[4:].strip()
                if cta_text:
                    ad_data["cta"] = cta_text
            elif line.upper().startswith('ANGLE:'):
                angle_text = line[6:].strip()
                if angle_text:
                    ad_data["angle"] = angle_text.lower().replace(" ", "_").replace("&", "")
            elif line.upper().startswith('TARGET:'):
                target_text = line[7:].strip()
                if target_text:
                    ad_data["target_audience"] = target_text
        
        # Validate and enhance ad data
        platform_spec = self.ad_platforms.get(platform, self.ad_platforms["facebook"])
        
        # Ensure headline meets character limits
        if len(ad_data["headline"]) > platform_spec["headline_length"]:
            ad_data["headline"] = ad_data["headline"][:platform_spec["headline_length"]-3] + "..."
        
        # Ensure description meets character limits
        if len(ad_data["description"]) > platform_spec["description_length"]:
            ad_data["description"] = ad_data["description"][:platform_spec["description_length"]-3] + "..."
        
        # Ensure minimum content quality
        if not ad_data["headline"]:
            ad_data["headline"] = f"Discover {product_name} Benefits"
        
        if not ad_data["description"]:
            ad_data["description"] = f"Transform your health naturally with {product_name}. Science-backed results you can trust."
        
        if not ad_data["cta"]:
            objective_ctas = {
                "conversions": "Get Started Now",
                "traffic": "Learn More",
                "awareness": "Discover More",
                "engagement": "Join the Community"
            }
            ad_data["cta"] = objective_ctas.get(objective, "Learn More")
        
        if not ad_data["angle"]:
            ad_data["angle"] = f"campaign_ad_{ad_num}"
        
        # Clean product references
        for field in ["headline", "description", "cta"]:
            ad_data[field] = ad_data[field].replace("[product]", product_name)
            ad_data[field] = ad_data[field].replace("Product", product_name)
            ad_data[field] = ad_data[field].replace("PRODUCT", product_name)
        
        return ad_data
    
    def _parse_flexible_ad_format(self, ai_response: str, platform: str, product_name: str, objective: str) -> List[Dict]:
        """Parse flexible ad format when structured parsing fails"""
        
        ads = []
        
        # Split by common ad separators
        separators = [
            r'Ad \d+',
            r'Advertisement \d+',
            r'Headline:',
            r'---+',
            r'===+'
        ]
        
        ad_sections = [ai_response]
        
        for separator in separators:
            new_sections = []
            for section in ad_sections:
                new_sections.extend(re.split(separator, section, flags=re.IGNORECASE | re.MULTILINE))
            ad_sections = new_sections
        
        # Process each section
        ad_count = 0
        for i, section in enumerate(ad_sections):
            section = section.strip()
            if len(section) < 50:  # Too short to be an ad
                continue
            
            ad_count += 1
            if ad_count > 10:  # Reasonable limit
                break
            
            # Extract headline and description
            lines = [line.strip() for line in section.split('\n') if line.strip()]
            
            headline = ""
            description = ""
            cta = ""
            
            # Find headline (usually first short line or marked with "Headline:")
            for j, line in enumerate(lines):
                if len(line) < 100 and not headline:
                    headline = line
                    lines = lines[j+1:]  # Remove headline from lines
                    break
            
            # Find CTA (usually contains action words)
            cta_keywords = ["learn more", "get started", "shop now", "discover", "try now", "sign up"]
            for line in lines:
                if any(keyword in line.lower() for keyword in cta_keywords):
                    cta = line
                    break
            
            # Remaining content is description
            description_lines = [line for line in lines if line != cta]
            description = " ".join(description_lines)
            
            # Create ad data
            ad_data = {
                "ad_number": ad_count,
                "platform": platform,
                "objective": objective,
                "headline": headline or f"Discover {product_name} Benefits",
                "description": description or f"Transform your health with {product_name}. Natural, effective, trusted.",
                "cta": cta or "Learn More",
                "angle": f"flexible_parse_{ad_count}",
                "target_audience": "health-conscious adults",
                "product_name": product_name,
                "ultra_cheap_generated": True
            }
            
            # Apply character limits
            platform_spec = self.ad_platforms.get(platform, self.ad_platforms["facebook"])
            
            if len(ad_data["headline"]) > platform_spec["headline_length"]:
                ad_data["headline"] = ad_data["headline"][:platform_spec["headline_length"]-3] + "..."
            
            if len(ad_data["description"]) > platform_spec["description_length"]:
                ad_data["description"] = ad_data["description"][:platform_spec["description_length"]-3] + "..."
            
            ads.append(ad_data)
        
        return ads
    
    def _emergency_ad_extraction(self, ai_response: str, platform: str, product_name: str, objective: str) -> List[Dict]:
        """Emergency ad extraction when all parsing fails"""
        
        logger.warning("🚨 Using emergency ad extraction")
        
        # Split content into sentences and use best ones
        sentences = [s.strip() for s in ai_response.split('.') if len(s.strip()) > 20]
        
        ads = []
        platform_spec = self.ad_platforms.get(platform, self.ad_platforms["facebook"])
        
        # Create 5 basic ads from available content
        ad_templates = [
            {
                "angle": "scientific_authority",
                "headline_template": f"Discover {product_name} Benefits",
                "desc_template": f"Science-backed {product_name} for natural health optimization."
            },
            {
                "angle": "emotional_transformation", 
                "headline_template": f"Transform Your Health with {product_name}",
                "desc_template": f"Real people, real results. Experience {product_name} transformation."
            },
            {
                "angle": "social_proof",
                "headline_template": f"Join Thousands Using {product_name}",
                "desc_template": f"Thousands trust {product_name} for their health journey."
            },
            {
                "angle": "urgency_scarcity",
                "headline_template": f"Limited Time: {product_name} Special Offer",
                "desc_template": f"Don't miss out on {product_name} - limited time opportunity."
            },
            {
                "angle": "lifestyle_confidence",
                "headline_template": f"Feel Amazing with {product_name}",
                "desc_template": f"Boost your confidence and energy with {product_name}."
            }
        ]
        
        for i, template in enumerate(ad_templates):
            # Use available sentences if we have them
            if i < len(sentences):
                content = sentences[i]
                # Try to split into headline and description
                words = content.split()
                if len(words) > 10:
                    headline = " ".join(words[:6])
                    description = " ".join(words[6:])
                else:
                    headline = template["headline_template"]
                    description = content
            else:
                headline = template["headline_template"]
                description = template["desc_template"]
            
            # Apply character limits
            if len(headline) > platform_spec["headline_length"]:
                headline = headline[:platform_spec["headline_length"]-3] + "..."
            
            if len(description) > platform_spec["description_length"]:
                description = description[:platform_spec["description_length"]-3] + "..."
            
            ad_data = {
                "ad_number": i + 1,
                "platform": platform,
                "objective": objective,
                "headline": headline,
                "description": description,
                "cta": "Learn More",
                "angle": template["angle"],
                "target_audience": "health-conscious adults",
                "product_name": product_name,
                "ultra_cheap_generated": True,
                "emergency_generated": True
            }
            
            ads.append(ad_data)
        
        return ads
    
    def _optimize_ads_for_platform(self, ads: List[Dict], platform_spec: Dict[str, Any], objective_spec: Dict[str, Any]) -> List[Dict]:
        """Apply platform and objective-specific optimizations"""
        
        optimized_ads = []
        
        for ad in ads:
            optimized_ad = ad.copy()
            
            # Add platform-specific metadata
            optimized_ad["platform_optimization"] = {
                "character_limits_applied": True,
                "audience_style": platform_spec["audience"],
                "platform_tone": platform_spec["style"],
                "features_available": platform_spec["features"]
            }
            
            # Add objective-specific metadata
            optimized_ad["objective_optimization"] = {
                "campaign_focus": objective_spec["focus"],
                "cta_strength": objective_spec["cta_strength"],
                "urgency_level": objective_spec["urgency"],
                "social_proof_level": objective_spec["social_proof"]
            }
            
            # Add A/B testing metadata
            optimized_ad["ab_testing"] = {
                "variation_type": ad.get("angle", "unknown"),
                "test_focus": self._get_ab_test_focus(ad.get("angle", "")),
                "recommended_split": "20% traffic allocation for testing"
            }
            
            # Add conversion optimization metadata
            optimized_ad["conversion_optimization"] = {
                "headline_length": len(ad["headline"]),
                "description_length": len(ad["description"]),
                "cta_present": bool(ad.get("cta")),
                "product_mention": ad["product_name"].lower() in ad["headline"].lower() or ad["product_name"].lower() in ad["description"].lower()
            }
            
            optimized_ads.append(optimized_ad)
        
        return optimized_ads
    
    def _get_ab_test_focus(self, angle: str) -> str:
        """Get A/B testing focus for angle"""
        
        test_focuses = {
            "scientific_authority": "Test credibility vs emotional appeal",
            "emotional_transformation": "Test story-driven vs benefit-focused",
            "social_proof": "Test testimonials vs statistics",
            "urgency_scarcity": "Test time pressure vs availability",
            "lifestyle_confidence": "Test aspirational vs practical benefits"
        }
        
        return test_focuses.get(angle, "Test headline variations")
    
    def _guaranteed_ad_copy_fallback(self, product_details: Dict[str, str], platform: str, objective: str, ad_count: int) -> Dict[str, Any]:
        """Guaranteed ad copy generation with platform optimization"""
        
        logger.info("🔄 Generating guaranteed ad copy with platform optimization")
        
        platform_spec = self.ad_platforms.get(platform, self.ad_platforms["facebook"])
        objective_spec = self.ad_objectives.get(objective, self.ad_objectives["conversions"])
        
        # Platform-specific ad templates
        ad_templates = [
            {
                "angle": "scientific_authority",
                "headline": f"Science-Backed {product_details['name']} Results",
                "description": f"Clinical research validates {product_details['name']} for {product_details['benefits']}. Experience proven health optimization.",
                "cta": "See Research"
            },
            {
                "angle": "emotional_transformation",
                "headline": f"Transform Your Life with {product_details['name']}",
                "description": f"Real people achieving real results. Join thousands who trust {product_details['name']} for natural transformation.",
                "cta": "Start Today"
            },
            {
                "angle": "social_proof",
                "headline": f"10,000+ Trust {product_details['name']}",
                "description": f"Thousands of satisfied customers choose {product_details['name']} for natural health support.",
                "cta": "Join Them"
            },
            {
                "angle": "urgency_scarcity",
                "headline": f"Limited: {product_details['name']} Special Offer",
                "description": f"Don't miss your chance to experience {product_details['name']} benefits. Limited time opportunity.",
                "cta": "Act Now"
            },
            {
                "angle": "lifestyle_confidence",
                "headline": f"Feel Confident with {product_details['name']}",
                "description": f"Boost your energy and confidence naturally. {product_details['name']} supports your wellness goals.",
                "cta": "Feel Amazing"
            }
        ]
        
        ads = []
        
        for i in range(ad_count):
            template = ad_templates[i % len(ad_templates)]
            
            # Apply character limits
            headline = template["headline"]
            if len(headline) > platform_spec["headline_length"]:
                headline = headline[:platform_spec["headline_length"]-3] + "..."
            
            description = template["description"]
            if len(description) > platform_spec["description_length"]:
                description = description[:platform_spec["description_length"]-3] + "..."
            
            # Adapt CTA for objective
            objective_ctas = {
                "conversions": template["cta"],
                "traffic": "Learn More",
                "awareness": "Discover",
                "engagement": "Share"
            }
            
            ad = {
                "ad_number": i + 1,
                "platform": platform,
                "objective": objective,
                "headline": headline,
                "description": description,
                "cta": objective_ctas.get(objective, template["cta"]),
                "angle": template["angle"],
                "target_audience": product_details["audience"],
                "product_name": product_details["name"],
                "ultra_cheap_generated": False,
                "guaranteed_generation": True,
                "platform_optimization": {
                    "character_limits_applied": True,
                    "audience_style": platform_spec["audience"],
                    "platform_tone": platform_spec["style"]
                },
                "objective_optimization": {
                    "campaign_focus": objective_spec["focus"],
                    "cta_strength": objective_spec["cta_strength"]
                }
            }
            ads.append(ad)
        
        # Create response with ultra-cheap AI metadata
        fallback_ai_result = {
            "content": "Guaranteed ad copy generated",
            "provider_used": "guaranteed_fallback",
            "cost": 0.0,
            "quality_score": 75,
            "generation_time": 0.3,
            "cost_optimization": {
                "provider_tier": "guaranteed",
                "cost_per_1k": 0.0,
                "savings_vs_openai": 0.030,
                "total_cost": 0.0,
                "fallback_reason": "Ultra-cheap AI system unavailable"
            }
        }
        
        return self._create_standardized_response(
            content={
                "ads": ads,
                "total_ads": len(ads),
                "platform": platform,
                "objective": objective,
                "campaign_focus": "Guaranteed high-converting affiliate ad copy with platform optimization",
                "reliability": "guaranteed",
                "generation_method": "fallback_with_optimization"
            },
            title=f"Guaranteed {ad_count}-Ad Campaign for {product_details['name']} - {platform.title()} {objective.title()}",
            product_name=product_details['name'],
            ai_result=fallback_ai_result,
            preferences={"platform": platform, "objective": objective, "count": str(ad_count)}
        )
    
    def _extract_ad_angles_intelligence(self, intelligence_data: Dict) -> Dict[str, Dict]:
        """Extract angle-specific intelligence for ad generation"""
        
        # Get angle-specific intelligence sections with enum serialization
        scientific_intel = self._serialize_enum_field(intelligence_data.get("scientific_authority_intelligence", {}))
        emotional_intel = self._serialize_enum_field(intelligence_data.get("emotional_transformation_intelligence", {}))
        community_intel = self._serialize_enum_field(intelligence_data.get("community_social_proof_intelligence", {}))
        urgency_intel = self._serialize_enum_field(intelligence_data.get("urgency_scarcity_intelligence", {}))
        lifestyle_intel = self._serialize_enum_field(intelligence_data.get("lifestyle_confidence_intelligence", {}))
        
        return {
            "scientific": {
                "focus": ", ".join(scientific_intel.get("clinical_studies", ["Research validation", "Clinical evidence"])[:2]),
                "credibility": scientific_intel.get("credibility_score", 0.87)
            },
            "emotional": {
                "focus": ", ".join(emotional_intel.get("transformation_stories", ["Personal transformation", "Life-changing results"])[:2]),
                "credibility": 0.84
            },
            "community": {
                "focus": ", ".join(community_intel.get("social_proof_elements", ["Customer testimonials", "Community success"])[:2]),
                "credibility": 0.81
            },
            "urgency": {
                "focus": ", ".join(urgency_intel.get("urgency_messages", ["Time-sensitive offers", "Limited availability"])[:2]),
                "credibility": 0.78
            },
            "lifestyle": {
                "focus": ", ".join(lifestyle_intel.get("lifestyle_benefits", ["Confidence boost", "Energy enhancement"])[:2]),
                "credibility": 0.80
            }
        }
    
    def _safe_int_conversion(self, value: str, default: int, min_val: int, max_val: int) -> int:
        """Safe integer conversion with bounds checking"""
        try:
            result = int(value) if str(value).isdigit() else default
            return max(min_val, min(max_val, result))
        except:
            return default


# Convenience functions for ad copy generation
async def generate_ad_copy_with_ultra_cheap_ai(
    intelligence_data: Dict[str, Any],
    platform: str = "facebook",
    objective: str = "conversions",
    ad_count: int = 5,
    preferences: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Generate ad copy using ultra-cheap AI system"""
    
    generator = AdCopyGenerator()
    if preferences is None:
        preferences = {
            "platform": platform,
            "objective": objective,
            "count": str(ad_count)
        }
    else:
        preferences.update({
            "platform": platform,
            "objective": objective,
            "count": str(ad_count)
        })
    
    return await generator.generate_ad_copy(intelligence_data, preferences)

def get_ad_copy_generator_cost_summary() -> Dict[str, Any]:
    """Get cost summary from ad copy generator"""
    generator = AdCopyGenerator()
    return generator.get_cost_summary()

def get_available_ad_platforms() -> List[str]:
    """Get list of available ad platforms"""
    generator = AdCopyGenerator()
    return list(generator.ad_platforms.keys())

def get_available_ad_objectives() -> List[str]:
    """Get list of available ad objectives"""
    generator = AdCopyGenerator()
    return list(generator.ad_objectives.keys())

# A/B Testing helper functions
def generate_ad_copy_ab_test_plan(
    ads: List[Dict[str, Any]], 
    budget_allocation: Dict[str, float] = None
) -> Dict[str, Any]:
    """Generate A/B testing plan for ad copy"""
    
    if budget_allocation is None:
        # Equal split by default
        budget_per_ad = 100 / len(ads) if ads else 0
        budget_allocation = {f"ad_{i+1}": budget_per_ad for i in range(len(ads))}
    
    test_plan = {
        "test_type": "multi_variant_ad_copy",
        "total_variants": len(ads),
        "budget_allocation": budget_allocation,
        "recommended_duration": "7-14 days",
        "success_metrics": [
            "click_through_rate",
            "conversion_rate", 
            "cost_per_acquisition",
            "return_on_ad_spend"
        ],
        "variants": []
    }
    
    for i, ad in enumerate(ads):
        variant = {
            "variant_id": f"ad_{i+1}",
            "angle": ad.get("angle", "unknown"),
            "headline": ad.get("headline", ""),
            "description": ad.get("description", ""),
            "test_hypothesis": f"Testing {ad.get('angle', 'unknown')} angle effectiveness",
            "budget_percentage": budget_allocation.get(f"ad_{i+1}", 0),
            "expected_performance": _predict_ad_performance(ad)
        }
        test_plan["variants"].append(variant)
    
    return test_plan

def _predict_ad_performance(ad: Dict[str, Any]) -> Dict[str, str]:
    """Predict ad performance based on angle and content"""
    
    angle = ad.get("angle", "")
    
    performance_predictions = {
        "scientific_authority": {
            "ctr_prediction": "Medium-High",
            "conversion_prediction": "High",
            "audience_fit": "Health-conscious, research-oriented users"
        },
        "emotional_transformation": {
            "ctr_prediction": "High", 
            "conversion_prediction": "High",
            "audience_fit": "Users seeking life changes"
        },
        "social_proof": {
            "ctr_prediction": "Medium",
            "conversion_prediction": "Medium-High",
            "audience_fit": "Social validation seekers"
        },
        "urgency_scarcity": {
            "ctr_prediction": "High",
            "conversion_prediction": "Medium",
            "audience_fit": "Deal-seeking, action-oriented users"
        },
        "lifestyle_confidence": {
            "ctr_prediction": "Medium-High",
            "conversion_prediction": "Medium-High", 
            "audience_fit": "Aspiration-driven users"
        }
    }
    
    return performance_predictions.get(angle, {
        "ctr_prediction": "Medium",
        "conversion_prediction": "Medium",
        "audience_fit": "General audience"
    })