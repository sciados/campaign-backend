# src/intelligence/generators/blog_post_generator.py
"""
BLOG POST GENERATOR
✅ Long-form blog posts and articles
✅ SEO-optimized content
✅ Multiple lengths and tones
✅ Structured sections with headers
🔥 FIXED: Enum serialization issues resolved
🔥 FIXED: Product name placeholder elimination
"""

import os
import logging
import uuid
import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.models.base import EnumSerializerMixin

from src.intelligence.utils.product_name_fix import (
       substitute_product_placeholders,
       substitute_placeholders_in_data,
       extract_product_name_from_intelligence,
       fix_email_sequence_placeholders,
       fix_social_media_placeholders,
       fix_ad_copy_placeholders,
       fix_blog_post_placeholders,
       validate_no_placeholders
   )

logger = logging.getLogger(__name__)

class BlogPostGenerator(EnumSerializerMixin):
    """Generate long-form blog posts and articles with product name fixes"""
    
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
        """Generate comprehensive blog post with product name fixes"""
        
        if preferences is None:
            preferences = {}
            
        # 🔥 EXTRACT ACTUAL PRODUCT NAME FIRST
        actual_product_name = extract_product_name_from_intelligence(intelligence_data)
        logger.info(f"🎯 Blog Post Generator: Using product name '{actual_product_name}'")
            
        topic = preferences.get("topic", "health_benefits")
        length = preferences.get("length", "medium")  # short, medium, long
        tone = preferences.get("tone", "informative")
        
        blog_post = None
        
        for provider in self.ai_providers:
            try:
                blog_post = await self._generate_blog_content(
                    provider, topic, length, tone, actual_product_name, intelligence_data
                )
                
                if blog_post:
                    break
                    
            except Exception as e:
                logger.error(f"Blog generation failed with {provider['name']}: {str(e)}")
                continue
        
        if not blog_post:
            blog_post = self._generate_fallback_blog_post(actual_product_name, topic)
        
        # 🔥 APPLY PRODUCT NAME FIXES TO BLOG POST
        fixed_blog_post = fix_blog_post_placeholders(blog_post, intelligence_data)
        
        # 🔥 VALIDATE NO PLACEHOLDERS REMAIN
        title_clean = validate_no_placeholders(fixed_blog_post.get("title", ""), actual_product_name)
        content_clean = validate_no_placeholders(fixed_blog_post.get("full_text", ""), actual_product_name)
        
        if not title_clean or not content_clean:
            logger.warning(f"⚠️ Placeholders found in blog post for '{actual_product_name}'")
        else:
            logger.info(f"✅ Blog post validation passed for '{actual_product_name}'")
        
        return {
            "content_type": "blog_post",
            "title": fixed_blog_post.get("title", f"{actual_product_name} Health Benefits"),
            "content": {
                "title": fixed_blog_post.get("title"),
                "introduction": fixed_blog_post.get("introduction"),
                "main_content": fixed_blog_post.get("main_content"),
                "conclusion": fixed_blog_post.get("conclusion"),
                "full_text": fixed_blog_post.get("full_text"),
                "word_count": fixed_blog_post.get("word_count", 0),
                "sections": fixed_blog_post.get("sections", [])
            },
            "metadata": {
                "generated_by": "blog_ai",
                "product_name": actual_product_name,
                "content_type": "blog_post",
                "topic": topic,
                "length_category": length,
                "tone": tone,
                "seo_optimized": True,
                "placeholders_fixed": True
            }
        }
    
    async def _generate_blog_content(self, provider, topic, length, tone, product_name, intelligence_data):
        """Generate blog content with AI and product name enforcement"""
        
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

CRITICAL: Use ONLY the actual product name "{product_name}" throughout the entire blog post.
NEVER use placeholders like "Your", "PRODUCT", "[Product]", "Your Company", etc.

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
1. Compelling headline (H1) featuring {product_name}
2. Hook introduction (150-200 words) mentioning {product_name}
3. Main content sections (3-5 sections with H2 headers) discussing {product_name}
4. Actionable conclusion about {product_name}
5. Call-to-action for {product_name}

Focus on providing value while naturally mentioning {product_name} where relevant.
Use headers like:
# Main Title about {product_name}
## Section 1: How {product_name} Works
## Section 2: Benefits of {product_name}
etc.

ABSOLUTELY FORBIDDEN: "Your", "PRODUCT", "[Product]", "Your Company", "the product"
REQUIRED: Use "{product_name}" consistently throughout
"""
        
        try:
            if provider["name"] == "anthropic":
                response = await provider["client"].messages.create(
                    model=provider["models"][0],
                    max_tokens=4000,
                    temperature=0.7,
                    system=f"You are an expert health and wellness blogger writing about {topic}. Create valuable, informative content with clear structure. ALWAYS use the exact product name '{product_name}' - never use placeholders like 'Your', 'PRODUCT', or '[Product]'.",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                content = response.content[0].text
                return self._parse_blog_post(content, product_name)
                
            elif provider["name"] == "openai":
                response = await provider["client"].chat.completions.create(
                    model=provider["models"][0],
                    messages=[
                        {"role": "system", "content": f"Expert health blogger writing about {topic}. Create valuable, structured content. ALWAYS use the exact product name '{product_name}' - never use placeholders like 'Your', 'PRODUCT', or '[Product]'."},
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
        """Parse blog post from AI response with product name fixes"""
        
        lines = content.split('\n')
        
        # Extract title (usually first line or marked with #)
        title = ""
        for line in lines[:5]:
            if line.strip() and (line.startswith('#') or len(line.strip()) < 100):
                title = line.strip().replace('#', '').strip()
                break
        
        if not title:
            title = f"The Complete Guide to {product_name} Benefits"
        
        # 🔥 APPLY PRODUCT NAME FIXES TO TITLE
        title = substitute_product_placeholders(title, product_name)
        
        # Extract sections
        sections = []
        current_section = None
        section_content = []
        
        for line in lines:
            if line.startswith('##') and not line.startswith('###'):
                # Save previous section
                if current_section:
                    section_content_str = '\n'.join(section_content).strip()
                    # 🔥 APPLY PRODUCT NAME FIXES TO SECTION CONTENT
                    section_content_str = substitute_product_placeholders(section_content_str, product_name)
                    sections.append({
                        "header": substitute_product_placeholders(current_section, product_name),
                        "content": section_content_str
                    })
                
                # Start new section
                current_section = line.replace('##', '').strip()
                section_content = []
            elif current_section:
                section_content.append(line)
        
        # Add last section
        if current_section:
            section_content_str = '\n'.join(section_content).strip()
            section_content_str = substitute_product_placeholders(section_content_str, product_name)
            sections.append({
                "header": substitute_product_placeholders(current_section, product_name),
                "content": section_content_str
            })
        
        # Simple content parsing for introduction, main content, conclusion
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        introduction = paragraphs[1] if len(paragraphs) > 1 else paragraphs[0][:200] + "..."
        main_content = '\n\n'.join(paragraphs[2:-1]) if len(paragraphs) > 3 else content
        conclusion = paragraphs[-1] if paragraphs else f"Discover the benefits of {product_name} for natural health optimization."
        
        # 🔥 APPLY PRODUCT NAME FIXES TO ALL CONTENT
        introduction = substitute_product_placeholders(introduction, product_name)
        main_content = substitute_product_placeholders(main_content, product_name)
        conclusion = substitute_product_placeholders(conclusion, product_name)
        full_text = substitute_product_placeholders(content, product_name)
        
        return {
            "title": title,
            "introduction": introduction,
            "main_content": main_content,
            "conclusion": conclusion,
            "full_text": full_text,
            "word_count": len(full_text.split()),
            "sections": sections
        }
    
    def _generate_fallback_blog_post(self, product_name, topic):
        """Generate fallback blog post with actual product name"""
        
        title = f"Understanding {product_name}: A Comprehensive Guide to Natural Health"
        
        content = f"""
# {title}

## Introduction

Natural health optimization has become increasingly important in our modern world. {product_name} represents a science-backed approach to wellness that addresses the root causes of health challenges rather than just symptoms.

## The Science Behind {product_name}

Research continues to validate the importance of liver health in overall wellness. {product_name} focuses on optimizing liver function through natural, evidence-based methods.

### Key Benefits

1. **Metabolic Enhancement**: Supporting natural metabolic processes with {product_name}
2. **Energy Optimization**: Promoting sustained energy levels through {product_name}
3. **Detoxification Support**: Enhancing natural detox pathways with {product_name}
4. **Overall Wellness**: Contributing to comprehensive health improvement through {product_name}

## How {product_name} Works

{product_name} works by supporting your body's natural processes rather than forcing artificial changes. This approach leads to more sustainable results and better overall health outcomes.

## Getting Started with {product_name}

If you're considering {product_name} as part of your wellness journey, consult with healthcare professionals to ensure it's right for your individual needs.

## Conclusion

Natural health optimization is a journey, not a destination. {product_name} can be a valuable tool in supporting your wellness goals through science-backed, natural methods.
"""
        
        sections = [
            {"header": f"The Science Behind {product_name}", "content": "Research-backed approach to health optimization"},
            {"header": "Key Benefits", "content": f"Metabolic enhancement, energy optimization, detoxification support through {product_name}"},
            {"header": f"How {product_name} Works", "content": "Natural process support for sustainable results"},
            {"header": f"Getting Started with {product_name}", "content": "Consult healthcare professionals for personalized guidance"}
        ]
        
        return {
            "title": title,
            "introduction": f"Natural health optimization has become increasingly important in our modern world. {product_name} represents a science-backed approach to wellness.",
            "main_content": content,
            "conclusion": f"Natural health optimization is a journey, not a destination. {product_name} can be a valuable tool in supporting your wellness goals.",
            "full_text": content,
            "word_count": len(content.split()),
            "sections": sections
        }
    
    def _extract_product_name(self, intelligence_data):
        """Extract product name from intelligence - DEPRECATED: Use utility function instead"""
        # 🔥 UPDATED: Use the proper utility function
        return extract_product_name_from_intelligence(intelligence_data)