# src/intelligence/generators/social_media_generator.py
"""
SOCIAL MEDIA POSTS GENERATOR
✅ Platform-specific content (Facebook, Instagram, Twitter, LinkedIn)
✅ Multiple post variations
✅ Hashtag optimization
✅ Engagement-focused copy
🔥 FIXED: Enum serialization issues resolved
"""

import os
import logging
import re
import uuid
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.models.base import EnumSerializerMixin

logger = logging.getLogger(__name__)

class SocialMediaGenerator(EnumSerializerMixin):
    """Generate platform-specific social media posts"""
    
    def __init__(self):
        self.ai_providers = self._initialize_ai_providers()
        self.platforms = ["facebook", "instagram", "twitter", "linkedin", "tiktok"]
        
    def _initialize_ai_providers(self):
        """Initialize AI providers for social media"""
        providers = []
        
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                import openai
                providers.append({
                    "name": "openai",
                    "client": openai.AsyncOpenAI(api_key=api_key),
                    "models": ["gpt-4", "gpt-3.5-turbo"],
                    "strengths": ["social_creativity", "hashtags", "engagement"]
                })
                logger.info("✅ OpenAI provider initialized for social media")
        except Exception as e:
            logger.warning(f"OpenAI not available for social media: {str(e)}")
        
        return providers
    
    async def generate_social_posts(
        self, 
        intelligence_data: Dict[str, Any], 
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate social media posts for multiple platforms"""
        
        if preferences is None:
            preferences = {}
            
        platform = preferences.get("platform", "all")
        post_count = preferences.get("count", 5)
        
        product_name = self._extract_product_name(intelligence_data)
        # 🔥 FIXED: Use enum serialization for angle system
        angle_system = self._serialize_enum_field(intelligence_data.get("angle_selection_system", {}))
        
        posts = []
        
        for provider in self.ai_providers:
            try:
                if platform == "all":
                    # Generate for all platforms
                    for p in self.platforms:
                        platform_posts = await self._generate_platform_posts(
                            provider, p, product_name, intelligence_data, post_count // len(self.platforms) + 1
                        )
                        posts.extend(platform_posts)
                else:
                    # Generate for specific platform
                    platform_posts = await self._generate_platform_posts(
                        provider, platform, product_name, intelligence_data, post_count
                    )
                    posts.extend(platform_posts)
                
                if posts:
                    break
                    
            except Exception as e:
                logger.error(f"Social media generation failed with {provider['name']}: {str(e)}")
                continue
        
        # Fallback generation
        if not posts:
            posts = self._generate_fallback_social_posts(product_name, platform, post_count)
        
        return {
            "content_type": "SOCIAL_POSTS",
            "title": f"{product_name} Social Media Content",
            "content": {
                "posts": posts,
                "total_posts": len(posts),
                "platforms_covered": len(set(post["platform"] for post in posts))
            },
            "metadata": {
                "generated_by": "social_media_ai",
                "product_name": product_name,
                "content_type": "SOCIAL_POSTS",
                "post_count": len(posts),
                "platform_optimization": True
            }
        }
    
    async def _generate_platform_posts(self, provider, platform, product_name, intelligence_data, count):
        """Generate posts for specific platform"""
        
        platform_specs = {
            "facebook": {"max_length": 500, "tone": "conversational", "hashtags": 5},
            "instagram": {"max_length": 200, "tone": "visual", "hashtags": 15},
            "twitter": {"max_length": 280, "tone": "concise", "hashtags": 3},
            "linkedin": {"max_length": 300, "tone": "professional", "hashtags": 5},
            "tiktok": {"max_length": 150, "tone": "trendy", "hashtags": 8}
        }
        
        spec = platform_specs.get(platform, platform_specs["facebook"])
        
        prompt = f"""
Create {count} different {platform} posts for {product_name}.

Platform Requirements:
- Max length: {spec['max_length']} characters
- Tone: {spec['tone']}
- Include {spec['hashtags']} relevant hashtags
- Focus on engagement

Product: {product_name}
Benefits: Health optimization, natural wellness

Create posts with different angles:
1. Educational/informational
2. Customer success story
3. Behind the scenes
4. Question/engagement
5. Inspirational/motivational

Format each post as:
POST 1:
[Content with hashtags]
---
POST 2:
[Content with hashtags]
---
"""
        
        try:
            if provider["name"] == "openai":
                response = await provider["client"].chat.completions.create(
                    model=provider["models"][0],
                    messages=[
                        {"role": "system", "content": f"Create engaging {platform} posts that drive engagement"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.9,
                    max_tokens=1500
                )
                
                content = response.choices[0].message.content
                return self._parse_social_posts(content, platform, product_name)
        
        except Exception as e:
            logger.error(f"Platform post generation failed: {str(e)}")
            return []
    
    def _parse_social_posts(self, content, platform, product_name):
        """Parse social media posts from AI response"""
        
        posts = []
        post_blocks = content.split("---")
        
        for i, block in enumerate(post_blocks):
            block = block.strip()
            if len(block) < 20:
                continue
                
            # Extract hashtags
            hashtags = []
            hashtag_matches = re.findall(r'#\w+', block)
            hashtags.extend(hashtag_matches)
            
            # Clean content (remove POST 1:, POST 2: etc.)
            clean_content = re.sub(r'^POST \d+:\s*', '', block, flags=re.MULTILINE)
            clean_content = clean_content.strip()
            
            if clean_content:
                posts.append({
                    "post_number": len(posts) + 1,
                    "platform": platform,
                    "content": clean_content,
                    "hashtags": hashtags,
                    "character_count": len(clean_content),
                    "engagement_elements": self._identify_engagement_elements(clean_content),
                    "post_type": self._classify_post_type(clean_content),
                    "product_mentions": product_name.lower() in clean_content.lower()
                })
        
        return posts[:5]  # Limit to 5 posts per platform
    
    def _identify_engagement_elements(self, content):
        """Identify engagement elements in post"""
        elements = []
        
        if "?" in content:
            elements.append("question")
        if any(word in content.lower() for word in ["comment", "share", "like", "thoughts"]):
            elements.append("call_to_action")
        if any(word in content.lower() for word in ["story", "journey", "experience"]):
            elements.append("storytelling")
        if "!" in content:
            elements.append("excitement")
            
        return elements
    
    def _classify_post_type(self, content):
        """Classify the type of social media post"""
        
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["tip", "fact", "learn", "research"]):
            return "educational"
        elif any(word in content_lower for word in ["success", "result", "transformation"]):
            return "testimonial"
        elif "?" in content:
            return "engagement"
        elif any(word in content_lower for word in ["inspire", "motivate", "believe"]):
            return "inspirational"
        else:
            return "promotional"
    
    def _generate_fallback_social_posts(self, product_name, platform, count):
        """Generate fallback social media posts"""
        
        fallback_posts = [
            {
                "content": f"Discover the natural benefits of {product_name} for your wellness journey! 🌿 #health #wellness #natural",
                "post_type": "promotional"
            },
            {
                "content": f"What's your biggest health goal this month? {product_name} might be the support you need! 💪 #goals #health",
                "post_type": "engagement"
            },
            {
                "content": f"Did you know? Liver health is crucial for overall wellness. That's why {product_name} focuses on optimization! 🧠 #facts #health",
                "post_type": "educational"
            },
            {
                "content": f"Real results, real people. See why thousands choose {product_name} for their health journey! ⭐ #testimonials #results",
                "post_type": "testimonial"
            },
            {
                "content": f"Your health transformation starts with one decision. Choose {product_name}, choose better health! ✨ #motivation #transform",
                "post_type": "inspirational"
            }
        ]
        
        posts = []
        for i in range(min(count, len(fallback_posts))):
            post_data = fallback_posts[i]
            posts.append({
                "post_number": i + 1,
                "platform": platform if platform != "all" else "facebook",
                "content": post_data["content"],
                "hashtags": re.findall(r'#\w+', post_data["content"]),
                "character_count": len(post_data["content"]),
                "post_type": post_data["post_type"],
                "product_mentions": True,
                "fallback_generated": True
            })
        
        return posts
    
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


# ============================================================================
# AD COPY GENERATOR (separate class in same file)
# ============================================================================

class AdCopyGenerator(EnumSerializerMixin):
    """Generate paid advertising copy for different platforms"""
    
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
            
        platform = preferences.get("platform", "facebook")
        objective = preferences.get("objective", "conversions")
        ad_count = preferences.get("count", 5)
        
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
            }
        }
        
        spec = platform_specs.get(platform, platform_specs["facebook"])
        
        # 🔥 FIXED: Extract angle intelligence with proper enum serialization
        angle_system = self._serialize_enum_field(intelligence_data.get("angle_selection_system", {}))
        angles = angle_system.get("available_angles", [])

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


# ============================================================================
# BLOG POST GENERATOR (separate class in same file)  
# ============================================================================

class BlogPostGenerator(EnumSerializerMixin):
    """Generate long-form blog posts and articles"""
    
    def __init__(self):
        self.ai_providers = self._initialize_ai_providers()
        
    def _initialize_ai_providers(self):
        """Initialize AI providers for blog posts"""
        providers = []
        
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                import anthropic
                providers.append({
                    "name": "anthropic",
                    "client": anthropic.AsyncAnthropic(api_key=api_key),
                    "models": ["claude-3-5-sonnet-20241022"],
                    "strengths": ["long_form", "research", "depth"]
                })
                logger.info("✅ Anthropic provider initialized for blog posts")
        except Exception as e:
            logger.warning(f"Anthropic not available for blog posts: {str(e)}")
            
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                import openai
                providers.append({
                    "name": "openai",
                    "client": openai.AsyncOpenAI(api_key=api_key),
                    "models": ["gpt-4"],
                    "strengths": ["creativity", "engagement"]
                })
                logger.info("✅ OpenAI provider initialized for blog posts")
        except Exception as e:
            logger.warning(f"OpenAI not available for blog posts: {str(e)}")
            
        return providers
    
    async def generate_blog_post(
        self, 
        intelligence_data: Dict[str, Any], 
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive blog post"""
        
        if preferences is None:
            preferences = {}
            
        topic = preferences.get("topic", "health_benefits")
        length = preferences.get("length", "medium")  # short, medium, long
        tone = preferences.get("tone", "informative")
        
        product_name = self._extract_product_name(intelligence_data)
        
        blog_post = None
        
        for provider in self.ai_providers:
            try:
                blog_post = await self._generate_blog_content(
                    provider, topic, length, tone, product_name, intelligence_data
                )
                
                if blog_post:
                    break
                    
            except Exception as e:
                logger.error(f"Blog generation failed with {provider['name']}: {str(e)}")
                continue
        
        if not blog_post:
            blog_post = self._generate_fallback_blog_post(product_name, topic)
        
        return {
            "content_type": "blog_post",
            "title": blog_post.get("title", f"{product_name} Health Benefits"),
            "content": {
                "title": blog_post.get("title"),
                "introduction": blog_post.get("introduction"),
                "main_content": blog_post.get("main_content"),
                "conclusion": blog_post.get("conclusion"),
                "full_text": blog_post.get("full_text"),
                "word_count": blog_post.get("word_count", 0),
                "sections": blog_post.get("sections", [])
            },
            "metadata": {
                "generated_by": "blog_ai",
                "product_name": product_name,
                "content_type": "blog_post",
                "topic": topic,
                "length_category": length,
                "tone": tone,
                "seo_optimized": True
            }
        }
    
    async def _generate_blog_content(self, provider, topic, length, tone, product_name, intelligence_data):
        """Generate blog content with AI"""
        
        word_targets = {
            "short": 800,
            "medium": 1500, 
            "long": 2500
        }
        
        target_words = word_targets.get(length, 1500)
        
        # 🔥 FIXED: Extract intelligence with proper enum serialization
        scientific_intel = self._serialize_enum_field(intelligence_data.get("scientific_authority_intelligence", {}))
        emotional_intel = self._serialize_enum_field(intelligence_data.get("emotional_transformation_intelligence", {}))
        
        prompt = f"""
Write a comprehensive {length} blog post about {topic} related to {product_name}.

Requirements:
- Target length: {target_words} words
- Tone: {tone}
- Include scientific backing where relevant
- SEO-optimized structure with clear headers
- Engaging introduction and conclusion
- Actionable insights for readers

Product: {product_name}
Scientific backing: {', '.join(scientific_intel.get('clinical_studies', ['Research-supported'])[:3])}

Structure:
1. Compelling headline (H1)
2. Hook introduction (150-200 words)
3. Main content sections (3-5 sections with H2 headers)
4. Actionable conclusion
5. Call-to-action

Focus on providing value while naturally mentioning {product_name} where relevant.
Use headers like:
# Main Title
## Section 1: [Topic]
## Section 2: [Topic]
etc.
"""
        
        try:
            if provider["name"] == "anthropic":
                response = await provider["client"].messages.create(
                    model=provider["models"][0],
                    max_tokens=4000,
                    temperature=0.7,
                    system=f"You are an expert health and wellness blogger writing about {topic}. Create valuable, informative content with clear structure.",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                content = response.content[0].text
                return self._parse_blog_post(content, product_name)
                
            elif provider["name"] == "openai":
                response = await provider["client"].chat.completions.create(
                    model=provider["models"][0],
                    messages=[
                        {"role": "system", "content": f"Expert health blogger writing about {topic}. Create valuable, structured content."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=4000
                )
                
                content = response.choices[0].message.content
                return self._parse_blog_post(content, product_name)
        
        except Exception as e:
            logger.error(f"Blog content generation failed: {str(e)}")
            return None
    
    def _parse_blog_post(self, content, product_name):
        """Parse blog post from AI response"""
        
        lines = content.split('\n')
        
        # Extract title (usually first line or marked with #)
        title = ""
        for line in lines[:5]:
            if line.strip() and (line.startswith('#') or len(line.strip()) < 100):
                title = line.strip().replace('#', '').strip()
                break
        
        if not title:
            title = f"The Complete Guide to {product_name} Benefits"
        
        # Extract sections
        sections = []
        current_section = None
        section_content = []
        
        for line in lines:
            if line.startswith('##') and not line.startswith('###'):
                # Save previous section
                if current_section:
                    sections.append({
                        "header": current_section,
                        "content": '\n'.join(section_content).strip()
                    })
                
                # Start new section
                current_section = line.replace('##', '').strip()
                section_content = []
            elif current_section:
                section_content.append(line)
        
        # Add last section
        if current_section:
            sections.append({
                "header": current_section,
                "content": '\n'.join(section_content).strip()
            })
        
        # Simple content parsing for introduction, main content, conclusion
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        introduction = paragraphs[1] if len(paragraphs) > 1 else paragraphs[0][:200] + "..."
        main_content = '\n\n'.join(paragraphs[2:-1]) if len(paragraphs) > 3 else content
        conclusion = paragraphs[-1] if paragraphs else "Discover the benefits of natural health optimization."
        
        return {
            "title": title,
            "introduction": introduction,
            "main_content": main_content,
            "conclusion": conclusion,
            "full_text": content,
            "word_count": len(content.split()),
            "sections": sections
        }
    
    def _generate_fallback_blog_post(self, product_name, topic):
        """Generate fallback blog post"""
        
        title = f"Understanding {product_name}: A Comprehensive Guide to Natural Health"
        
        content = f"""
# {title}

## Introduction

Natural health optimization has become increasingly important in our modern world. {product_name} represents a science-backed approach to wellness that addresses the root causes of health challenges rather than just symptoms.

## The Science Behind {product_name}

Research continues to validate the importance of liver health in overall wellness. {product_name} focuses on optimizing liver function through natural, evidence-based methods.

### Key Benefits

1. **Metabolic Enhancement**: Supporting natural metabolic processes
2. **Energy Optimization**: Promoting sustained energy levels
3. **Detoxification Support**: Enhancing natural detox pathways
4. **Overall Wellness**: Contributing to comprehensive health improvement

## How {product_name} Works

{product_name} works by supporting your body's natural processes rather than forcing artificial changes. This approach leads to more sustainable results and better overall health outcomes.

## Getting Started

If you're considering {product_name} as part of your wellness journey, consult with healthcare professionals to ensure it's right for your individual needs.

## Conclusion

Natural health optimization is a journey, not a destination. {product_name} can be a valuable tool in supporting your wellness goals through science-backed, natural methods.
"""
        
        sections = [
            {"header": "The Science Behind " + product_name, "content": "Research-backed approach to health optimization"},
            {"header": "Key Benefits", "content": "Metabolic enhancement, energy optimization, detoxification support"},
            {"header": "How " + product_name + " Works", "content": "Natural process support for sustainable results"},
            {"header": "Getting Started", "content": "Consult healthcare professionals for personalized guidance"}
        ]
        
        return {
            "title": title,
            "introduction": "Natural health optimization has become increasingly important in our modern world.",
            "main_content": content,
            "conclusion": "Natural health optimization is a journey, not a destination.",
            "full_text": content,
            "word_count": len(content.split()),
            "sections": sections
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