# src/intelligence/generators/blog_post_generator.py
"""
BLOG POST GENERATOR
✅ Long-form blog posts and articles
✅ SEO-optimized content
✅ Multiple lengths and tones
✅ Structured sections with headers
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