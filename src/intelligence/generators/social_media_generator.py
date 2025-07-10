# src/intelligence/generators/social_media_generator.py
"""
ENHANCED SOCIAL MEDIA GENERATOR WITH ULTRA-CHEAP AI INTEGRATION
✅ 97% cost savings through unified ultra-cheap provider system
✅ Platform-specific content (Facebook, Instagram, Twitter, LinkedIn, TikTok)
✅ Multiple post variations with engagement optimization
✅ Hashtag optimization and viral potential analysis
✅ Real-time cost tracking and performance optimization
"""

import os
import logging
import re
import uuid
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import enhanced base generator with ultra-cheap AI
from .base_generator import BaseContentGenerator
from ..utils.unified_ultra_cheap_provider import get_unified_provider, ultra_cheap_text_generation
from src.models.base import EnumSerializerMixin

logger = logging.getLogger(__name__)

class SocialMediaGenerator(BaseContentGenerator, EnumSerializerMixin):
    """Enhanced social media generator with ultra-cheap AI integration"""
    
    def __init__(self):
        # Initialize with ultra-cheap AI system
        super().__init__("social_media")
        
        # Platform specifications with optimization data
        self.platforms = {
            "facebook": {
                "max_length": 500,
                "optimal_length": 200,
                "tone": "conversational",
                "hashtags": 5,
                "engagement_triggers": ["questions", "polls", "shares"],
                "best_times": "9am-10am, 3pm-4pm",
                "audience": "broad demographic",
                "content_types": ["text", "image", "video", "link"]
            },
            "instagram": {
                "max_length": 200,
                "optimal_length": 125,
                "tone": "visual",
                "hashtags": 15,
                "engagement_triggers": ["stories", "reels", "hashtags"],
                "best_times": "11am-2pm, 5pm-7pm",
                "audience": "visual-focused, younger demographic",
                "content_types": ["image", "reel", "story", "igtv"]
            },
            "twitter": {
                "max_length": 280,
                "optimal_length": 200,
                "tone": "concise",
                "hashtags": 3,
                "engagement_triggers": ["threads", "replies", "retweets"],
                "best_times": "12pm-3pm, 5pm-6pm",
                "audience": "news-focused, professional",
                "content_types": ["text", "image", "thread", "space"]
            },
            "linkedin": {
                "max_length": 300,
                "optimal_length": 200,
                "tone": "professional",
                "hashtags": 5,
                "engagement_triggers": ["industry insights", "thought leadership"],
                "best_times": "8am-10am, 12pm-2pm",
                "audience": "business professionals",
                "content_types": ["text", "article", "video", "document"]
            },
            "tiktok": {
                "max_length": 150,
                "optimal_length": 100,
                "tone": "trendy",
                "hashtags": 8,
                "engagement_triggers": ["challenges", "trends", "sounds"],
                "best_times": "6am-10am, 7pm-9pm",
                "audience": "gen z, millennials",
                "content_types": ["video", "duet", "effect"]
            }
        }
        
        # Content angle strategies for social media
        self.social_angles = [
            {
                "id": "educational_tips",
                "name": "Educational Tips",
                "focus": "Health facts and actionable tips",
                "engagement": "high",
                "virality": "medium"
            },
            {
                "id": "behind_scenes",
                "name": "Behind the Scenes",
                "focus": "Product creation and company insights",
                "engagement": "medium",
                "virality": "high"
            },
            {
                "id": "user_generated",
                "name": "User Generated Content",
                "focus": "Customer stories and testimonials",
                "engagement": "high",
                "virality": "high"
            },
            {
                "id": "trending_topics",
                "name": "Trending Topics",
                "focus": "Current events and health trends",
                "engagement": "medium",
                "virality": "very_high"
            },
            {
                "id": "question_engagement",
                "name": "Question & Engagement",
                "focus": "Community building through questions",
                "engagement": "very_high",
                "virality": "medium"
            }
        ]
        
        logger.info(f"✅ Social Media Generator: Ultra-cheap AI system ready with {len(self.ultra_cheap_providers)} providers")
        logger.info(f"🎯 Platforms: {len(self.platforms)} platforms configured")
    
    async def generate_social_posts(
        self, 
        intelligence_data: Dict[str, Any], 
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate platform-specific social media posts with ultra-cheap AI"""
        
        if preferences is None:
            preferences = {}
        
        # Extract social media generation parameters
        platform = preferences.get("platform", "all")
        post_count = self._safe_int_conversion(preferences.get("count", "5"), 5, 1, 20)
        
        # Extract intelligence for social media generation
        product_details = self._extract_product_details(intelligence_data)
        
        logger.info(f"🎯 Generating {post_count} social media posts for {product_details['name']} (Platform: {platform})")
        
        posts = []
        generation_costs = []
        
        try:
            if platform == "all":
                # Generate for all platforms
                for p in self.platforms.keys():
                    platform_posts, platform_cost = await self._generate_platform_posts_ultra_cheap(
                        p, product_details, intelligence_data, post_count // len(self.platforms) + 1
                    )
                    posts.extend(platform_posts)
                    generation_costs.append(platform_cost)
            else:
                # Generate for specific platform
                platform_posts, platform_cost = await self._generate_platform_posts_ultra_cheap(
                    platform, product_details, intelligence_data, post_count
                )
                posts.extend(platform_posts)
                generation_costs.append(platform_cost)
                
        except Exception as e:
            logger.error(f"❌ Ultra-cheap social media generation failed: {str(e)}")
            # Enhanced fallback with platform optimization
            posts = self._generate_enhanced_fallback_posts(product_details, platform, post_count)
            generation_costs = [{"cost": 0, "fallback": True}]
        
        # Calculate total costs and savings
        total_cost = sum(cost.get("cost", 0) for cost in generation_costs if isinstance(cost, dict))
        total_savings = sum(cost.get("savings_vs_openai", {}).get("savings_amount", 0) for cost in generation_costs if isinstance(cost, dict))
        
        # Apply engagement optimization
        optimized_posts = self._apply_engagement_optimization(posts)
        
        return self._create_standardized_response(
            content={
                "posts": optimized_posts,
                "total_posts": len(optimized_posts),
                "platforms_covered": len(set(post["platform"] for post in optimized_posts)),
                "engagement_optimized": True,
                "viral_potential_analyzed": True
            },
            title=f"{product_details['name']} Social Media Campaign",
            product_name=product_details['name'],
            ai_result={
                "provider_used": "ultra_cheap_social_ai",
                "cost": total_cost,
                "quality_score": 85,
                "generation_time": sum(cost.get("generation_time", 0) for cost in generation_costs if isinstance(cost, dict)),
                "cost_optimization": {
                    "total_cost": total_cost,
                    "total_savings": total_savings,
                    "cost_per_post": total_cost / len(optimized_posts) if optimized_posts else 0,
                    "provider_tier": "ultra_cheap"
                }
            },
            preferences=preferences
        )
    
    async def generate_content(self, intelligence_data: Dict[str, Any], preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate content - main interface for factory integration"""
        return await self.generate_social_posts(intelligence_data, preferences)
    
    async def _generate_platform_posts_ultra_cheap(
        self, 
        platform: str, 
        product_details: Dict[str, str], 
        intelligence_data: Dict[str, Any], 
        count: int
    ) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Generate posts for specific platform using ultra-cheap AI"""
        
        platform_spec = self.platforms.get(platform, self.platforms["facebook"])
        
        # Create platform-optimized social media prompt
        social_prompt = self._create_social_media_prompt(
            product_details, intelligence_data, platform, count, platform_spec
        )
        
        # Generate with ultra-cheap AI system
        ai_result = await self._generate_with_ultra_cheap_ai(
            prompt=social_prompt,
            system_message=f"You are an expert social media manager creating viral, engaging content for {platform}. Focus on high engagement, shareability, and affiliate marketing effectiveness.",
            max_tokens=2500,
            temperature=0.9,  # Higher creativity for social content
            required_strength="creativity"  # Prefer providers good at creative content
        )
        
        if ai_result and ai_result.get("content"):
            posts = self._parse_social_posts(ai_result["content"], platform, product_details['name'])
            
            # Add ultra-cheap AI metadata to each post
            for post in posts:
                post["ultra_cheap_generated"] = True
                post["generation_cost"] = ai_result["cost"] / len(posts) if posts else 0
                post["provider_used"] = ai_result["provider_used"]
            
            logger.info(f"✅ Generated {len(posts)} {platform} posts - Cost: ${ai_result['cost']:.4f}")
            
            return posts, ai_result
        else:
            # Fallback if ultra-cheap fails
            logger.warning(f"Ultra-cheap generation failed for {platform}, using fallback")
            fallback_posts = self._generate_platform_fallback_posts(product_details, platform, count)
            return fallback_posts, {"cost": 0, "fallback": True}
    
    def _create_social_media_prompt(
        self, 
        product_details: Dict[str, str], 
        intelligence_data: Dict[str, Any], 
        platform: str, 
        count: int,
        platform_spec: Dict[str, Any]
    ) -> str:
        """Create platform-optimized social media generation prompt"""
        
        # Extract social media intelligence
        social_intel = self._extract_social_media_intelligence(intelligence_data)
        
        prompt = f"""
VIRAL SOCIAL MEDIA CONTENT GENERATION
Platform: {platform.upper()}

PRODUCT CAMPAIGN: {product_details['name']}
TARGET AUDIENCE: {product_details['audience']}
CORE BENEFITS: {product_details['benefits']}

PLATFORM OPTIMIZATION:
- Max length: {platform_spec['max_length']} characters
- Optimal length: {platform_spec['optimal_length']} characters
- Platform tone: {platform_spec['tone']}
- Hashtag limit: {platform_spec['hashtags']} hashtags
- Best posting times: {platform_spec['best_times']}
- Audience focus: {platform_spec['audience']}
- Content types: {', '.join(platform_spec['content_types'])}

CREATE {count} DIFFERENT {platform.upper()} POSTS USING STRATEGIC ANGLE ROTATION:

Post 1 - EDUCATIONAL TIPS ANGLE:
Focus: Health facts and actionable tips about {product_details['name']}
Style: Informative but engaging, share-worthy health knowledge
Engagement triggers: "Did you know?", "Health tip:", "Save this post"

Post 2 - BEHIND THE SCENES ANGLE:
Focus: Product creation, company story, transparency
Style: Authentic, personal, trustworthy
Engagement triggers: "Behind the scenes", "How it's made", "Our story"

Post 3 - USER GENERATED CONTENT ANGLE:
Focus: Customer success stories and testimonials
Style: Social proof, relatable, inspirational
Engagement triggers: "Customer spotlight", "Real results", "Success story"

Post 4 - TRENDING TOPICS ANGLE:
Focus: Current health trends, news, seasonal content
Style: Timely, relevant, conversation-starting
Engagement triggers: "Trending now", "What's new", "Hot topic"

Post 5 - QUESTION & ENGAGEMENT ANGLE:
Focus: Community building through questions and interaction
Style: Conversational, inclusive, discussion-starting
Engagement triggers: "What do you think?", "Share your experience", "Poll"

OUTPUT FORMAT (EXACT STRUCTURE REQUIRED):
===POST_1===
CONTENT: [Educational tip post - under {platform_spec['optimal_length']} chars]
HASHTAGS: [List of {platform_spec['hashtags']} relevant hashtags]
ANGLE: Educational Tips
ENGAGEMENT_TYPE: [Specific engagement mechanism]
VIRAL_POTENTIAL: [High/Medium/Low with reason]
PLATFORM_OPT: {platform}
===END_POST_1===

===POST_2===
CONTENT: [Behind the scenes post - under {platform_spec['optimal_length']} chars]
HASHTAGS: [List of {platform_spec['hashtags']} relevant hashtags]
ANGLE: Behind the Scenes
ENGAGEMENT_TYPE: [Specific engagement mechanism]
VIRAL_POTENTIAL: [High/Medium/Low with reason]
PLATFORM_OPT: {platform}
===END_POST_2===

[Continue this pattern for all {count} posts]

CRITICAL REQUIREMENTS:
1. Each post must use a completely different content angle
2. Content must be under {platform_spec['optimal_length']} characters for optimal {platform} performance
3. Include exactly {platform_spec['hashtags']} relevant, trending hashtags
4. Optimize for {platform_spec['audience']} audience behavior
5. Include specific engagement triggers for {platform}
6. Use '{product_details['name']}' naturally in content
7. Focus on viral potential and shareability
8. Make each post feel native to {platform}

Generate the complete {count}-post social media campaign now.
"""
        
        return prompt
    
    def _parse_social_posts(self, ai_response: str, platform: str, product_name: str) -> List[Dict]:
        """Parse social media posts from AI response with engagement analysis"""
        
        posts = []
        
        # Try structured parsing first
        try:
            posts = self._parse_structured_social_format(ai_response, platform, product_name)
            if posts and len(posts) >= 3:
                return posts
        except Exception as e:
            logger.warning(f"⚠️ Structured social parsing failed: {str(e)}")
        
        # Try flexible parsing
        try:
            posts = self._parse_flexible_social_format(ai_response, platform, product_name)
            if posts and len(posts) >= 3:
                return posts
        except Exception as e:
            logger.warning(f"⚠️ Flexible social parsing failed: {str(e)}")
        
        # Emergency extraction
        return self._emergency_social_extraction(ai_response, platform, product_name)
    
    def _parse_structured_social_format(self, ai_response: str, platform: str, product_name: str) -> List[Dict]:
        """Parse structured ===POST_X=== format"""
        
        posts = []
        post_blocks = re.split(r'===POST_(\d+)===', ai_response, flags=re.IGNORECASE)
        
        if len(post_blocks) > 1:
            post_blocks = post_blocks[1:]  # Remove content before first post
        
        for i in range(0, len(post_blocks) - 1, 2):
            try:
                post_num = int(post_blocks[i])
                post_content = post_blocks[i + 1] if i + 1 < len(post_blocks) else ""
                
                # Clean up content
                post_content = re.sub(r'===END_POST_\d+===.*$', '', post_content, flags=re.DOTALL | re.IGNORECASE)
                post_content = post_content.strip()
                
                if not post_content:
                    continue
                
                # Parse post components
                post_data = self._extract_social_components(post_content, post_num, platform, product_name)
                
                if post_data and post_data.get("content"):
                    posts.append(post_data)
                
            except (ValueError, IndexError) as e:
                logger.warning(f"⚠️ Error parsing post block {i}: {str(e)}")
                continue
        
        return posts
    
    def _extract_social_components(self, post_content: str, post_num: int, platform: str, product_name: str) -> Dict[str, Any]:
        """Extract individual social media post components"""
        
        post_data = {
            "post_number": post_num,
            "platform": platform,
            "content": "",
            "hashtags": [],
            "angle": "",
            "engagement_type": "",
            "viral_potential": "",
            "product_name": product_name,
            "ultra_cheap_generated": True
        }
        
        lines = post_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Parse structured fields
            if line.upper().startswith('CONTENT:'):
                content_text = line[8:].strip()
                if content_text:
                    post_data["content"] = content_text
            elif line.upper().startswith('HASHTAGS:'):
                hashtags_text = line[9:].strip()
                # Parse hashtags from various formats
                hashtags = []
                if hashtags_text:
                    # Handle different hashtag formats
                    hashtag_candidates = re.findall(r'#\w+', hashtags_text)
                    if not hashtag_candidates:
                        # If no # symbols, split by commas and add #
                        hashtag_candidates = [f"#{tag.strip()}" for tag in hashtags_text.split(',') if tag.strip()]
                    hashtags = hashtag_candidates
                post_data["hashtags"] = hashtags
            elif line.upper().startswith('ANGLE:'):
                angle_text = line[6:].strip()
                if angle_text:
                    post_data["angle"] = angle_text.lower().replace(" ", "_").replace("&", "")
            elif line.upper().startswith('ENGAGEMENT_TYPE:'):
                engagement_text = line[16:].strip()
                if engagement_text:
                    post_data["engagement_type"] = engagement_text
            elif line.upper().startswith('VIRAL_POTENTIAL:'):
                viral_text = line[16:].strip()
                if viral_text:
                    post_data["viral_potential"] = viral_text
        
        # Validate and enhance post data
        platform_spec = self.platforms.get(platform, self.platforms["facebook"])
        
        # Ensure content meets character limits
        if len(post_data["content"]) > platform_spec["optimal_length"]:
            post_data["content"] = post_data["content"][:platform_spec["optimal_length"]-3] + "..."
        
        # Ensure minimum content quality
        if not post_data["content"]:
            post_data["content"] = f"Discover the natural benefits of {product_name} for your wellness journey! 🌿"
        
        # Ensure hashtags are present
        if not post_data["hashtags"]:
            default_hashtags = [
                f"#{product_name.lower()}", "#health", "#wellness", "#natural", "#healthy"
            ]
            post_data["hashtags"] = default_hashtags[:platform_spec["hashtags"]]
        
        # Ensure angle is set
        if not post_data["angle"]:
            post_data["angle"] = "general_health"
        
        # Clean product references
        post_data["content"] = post_data["content"].replace("[product]", product_name)
        post_data["content"] = post_data["content"].replace("Product", product_name)
        
        # Add engagement analysis
        post_data["engagement_analysis"] = self._analyze_engagement_potential(post_data)
        
        return post_data
    
    def _analyze_engagement_potential(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze engagement potential of social media post"""
        
        content = post_data["content"].lower()
        
        engagement_score = 0
        engagement_factors = []
        
        # Question detection
        if "?" in content:
            engagement_score += 20
            engagement_factors.append("contains_question")
        
        # Call to action detection
        cta_keywords = ["comment", "share", "like", "tag", "try", "discover", "learn", "join"]
        if any(keyword in content for keyword in cta_keywords):
            engagement_score += 15
            engagement_factors.append("call_to_action")
        
        # Emotional words detection
        emotional_words = ["amazing", "incredible", "love", "excited", "breakthrough", "transform"]
        if any(word in content for word in emotional_words):
            engagement_score += 10
            engagement_factors.append("emotional_language")
        
        # Hashtag quality
        hashtag_count = len(post_data.get("hashtags", []))
        platform_spec = self.platforms.get(post_data["platform"], self.platforms["facebook"])
        if hashtag_count >= platform_spec["hashtags"] // 2:
            engagement_score += 10
            engagement_factors.append("good_hashtag_usage")
        
        # Content length optimization
        content_length = len(post_data["content"])
        optimal_length = platform_spec["optimal_length"]
        if 0.5 * optimal_length <= content_length <= optimal_length:
            engagement_score += 15
            engagement_factors.append("optimal_length")
        
        # Determine engagement level
        if engagement_score >= 50:
            engagement_level = "high"
        elif engagement_score >= 30:
            engagement_level = "medium"
        else:
            engagement_level = "low"
        
        return {
            "engagement_score": engagement_score,
            "engagement_level": engagement_level,
            "engagement_factors": engagement_factors,
            "viral_indicators": self._identify_viral_indicators(post_data),
            "platform_optimization": engagement_score >= 40
        }
    
    def _identify_viral_indicators(self, post_data: Dict[str, Any]) -> List[str]:
        """Identify viral potential indicators in post"""
        
        content = post_data["content"].lower()
        viral_indicators = []
        
        # Trend-related keywords
        if any(word in content for word in ["trending", "viral", "everyone", "must", "secret"]):
            viral_indicators.append("trend_language")
        
        # Shareability indicators
        if any(word in content for word in ["share", "tag", "show", "tell"]):
            viral_indicators.append("shareability_cues")
        
        # Controversy or strong opinion (moderate level)
        if any(word in content for word in ["believe", "truth", "reality", "fact"]):
            viral_indicators.append("opinion_based")
        
        # Educational value
        if any(word in content for word in ["tip", "learn", "know", "discover", "fact"]):
            viral_indicators.append("educational_value")
        
        # Visual appeal indicators
        if any(word in content for word in ["photo", "video", "see", "look", "watch"]):
            viral_indicators.append("visual_appeal")
        
        return viral_indicators
    
    def _parse_flexible_social_format(self, ai_response: str, platform: str, product_name: str) -> List[Dict]:
        """Parse flexible social format when structured parsing fails"""
        
        posts = []
        
        # Split by common social media separators
        separators = [
            r'Post \d+',
            r'#\d+',
            r'---+',
            r'===+',
            r'\n\n\n+'
        ]
        
        post_sections = [ai_response]
        
        for separator in separators:
            new_sections = []
            for section in post_sections:
                new_sections.extend(re.split(separator, section, flags=re.IGNORECASE | re.MULTILINE))
            post_sections = new_sections
        
        # Process each section
        post_count = 0
        for i, section in enumerate(post_sections):
            section = section.strip()
            if len(section) < 30:  # Too short to be a post
                continue
            
            post_count += 1
            if post_count > 10:  # Reasonable limit
                break
            
            # Extract hashtags
            hashtags = re.findall(r'#\w+', section)
            
            # Clean content (remove hashtags for main content)
            content = re.sub(r'#\w+', '', section).strip()
            content = ' '.join(content.split())  # Clean whitespace
            
            # Apply character limits
            platform_spec = self.platforms.get(platform, self.platforms["facebook"])
            if len(content) > platform_spec["optimal_length"]:
                content = content[:platform_spec["optimal_length"]-3] + "..."
            
            post_data = {
                "post_number": post_count,
                "platform": platform,
                "content": content,
                "hashtags": hashtags[:platform_spec["hashtags"]],
                "angle": f"flexible_parse_{post_count}",
                "engagement_type": "general",
                "viral_potential": "medium",
                "product_name": product_name,
                "ultra_cheap_generated": True
            }
            
            # Add engagement analysis
            post_data["engagement_analysis"] = self._analyze_engagement_potential(post_data)
            
            posts.append(post_data)
        
        return posts
    
    def _emergency_social_extraction(self, ai_response: str, platform: str, product_name: str) -> List[Dict]:
        """Emergency social media extraction when all parsing fails"""
        
        logger.warning("🚨 Using emergency social media extraction")
        
        # Split content into sentences and use best ones
        sentences = [s.strip() for s in ai_response.split('.') if len(s.strip()) > 20]
        
        posts = []
        platform_spec = self.platforms.get(platform, self.platforms["facebook"])
        
        # Create 5 posts from available content or templates
        post_templates = [
            {
                "angle": "educational_tips",
                "content_template": f"Did you know? {product_name} supports natural health optimization through science-backed ingredients! 💡",
                "hashtags": ["#health", "#wellness", "#natural", f"#{product_name.lower()}", "#tips"]
            },
            {
                "angle": "behind_scenes",
                "content_template": f"Behind the scenes: Creating {product_name} with the highest quality standards! 🏭",
                "hashtags": ["#behindthescenes", f"#{product_name.lower()}", "#quality", "#natural", "#health"]
            },
            {
                "angle": "user_generated",
                "content_template": f"Real results from real people! ⭐ {product_name} is changing lives every day.",
                "hashtags": ["#testimonial", "#results", f"#{product_name.lower()}", "#success", "#health"]
            },
            {
                "angle": "trending_topics",
                "content_template": f"Health trend alert! 🚨 Natural wellness with {product_name} is the way forward.",
                "hashtags": ["#trending", "#health", "#wellness", f"#{product_name.lower()}", "#natural"]
            },
            {
                "angle": "question_engagement",
                "content_template": f"What's your biggest health goal this year? 🤔 Let {product_name} support your journey!",
                "hashtags": ["#question", "#goals", "#health", f"#{product_name.lower()}", "#wellness"]
            }
        ]
        
        for i, template in enumerate(post_templates):
            # Use available sentences if we have them
            if i < len(sentences):
                content = sentences[i]
                # Ensure product name is mentioned
                if product_name.lower() not in content.lower():
                    content = f"{content} with {product_name}!"
            else:
                content = template["content_template"]
            
            # Apply character limits
            if len(content) > platform_spec["optimal_length"]:
                content = content[:platform_spec["optimal_length"]-3] + "..."
            
            post_data = {
                "post_number": i + 1,
                "platform": platform,
                "content": content,
                "hashtags": template["hashtags"][:platform_spec["hashtags"]],
                "angle": template["angle"],
                "engagement_type": "general",
                "viral_potential": "medium",
                "product_name": product_name,
                "ultra_cheap_generated": True,
                "emergency_generated": True
            }
            
            # Add engagement analysis
            post_data["engagement_analysis"] = self._analyze_engagement_potential(post_data)
            
            posts.append(post_data)
        
        return posts
    
    def _apply_engagement_optimization(self, posts: List[Dict]) -> List[Dict]:
        """Apply engagement optimization to all posts"""
        
        optimized_posts = []
        
        for post in posts:
            optimized_post = post.copy()
            
            # Add platform-specific engagement metadata
            platform_spec = self.platforms.get(post["platform"], self.platforms["facebook"])
            
            optimized_post["platform_optimization"] = {
                "character_count": len(post["content"]),
                "optimal_range": f"0-{platform_spec['optimal_length']}",
                "hashtag_count": len(post.get("hashtags", [])),
                "hashtag_limit": platform_spec["hashtags"],
                "best_posting_times": platform_spec["best_times"],
                "audience_match": platform_spec["audience"]
            }
            
            # Add viral potential analysis
            optimized_post["viral_analysis"] = {
                "shareability_score": self._calculate_shareability_score(post),
                "trending_potential": self._assess_trending_potential(post),
                "audience_resonance": self._predict_audience_resonance(post),
                "optimal_boost_budget": self._suggest_boost_budget(post)
            }
            
            # Add content performance predictions
            optimized_post["performance_prediction"] = {
                "expected_engagement_rate": self._predict_engagement_rate(post),
                "reach_potential": self._predict_reach_potential(post),
                "conversion_likelihood": self._predict_conversion_likelihood(post),
                "best_posting_time": platform_spec["best_times"].split(",")[0].strip()
            }
            
            optimized_posts.append(optimized_post)
        
        return optimized_posts
    
    def _calculate_shareability_score(self, post: Dict) -> int:
        """Calculate shareability score for post"""
        
        content = post["content"].lower()
        score = 0
        
        # Content factors
        if "tip" in content or "fact" in content:
            score += 20
        if "?" in content:
            score += 15
        if any(word in content for word in ["amazing", "incredible", "must", "secret"]):
            score += 10
        if len(post.get("hashtags", [])) >= 3:
            score += 10
        
        # Length optimization
        platform_spec = self.platforms.get(post["platform"], self.platforms["facebook"])
        content_length = len(post["content"])
        if content_length <= platform_spec["optimal_length"]:
            score += 15
        
        return min(score, 100)
    
    def _assess_trending_potential(self, post: Dict) -> str:
        """Assess trending potential of post"""
        
        content = post["content"].lower()
        
        trending_keywords = ["trend", "viral", "everyone", "new", "breakthrough", "discover"]
        viral_indicators = len([word for word in trending_keywords if word in content])
        
        if viral_indicators >= 2:
            return "high"
        elif viral_indicators >= 1:
            return "medium"
        else:
            return "low"
    
    def _predict_audience_resonance(self, post: Dict) -> str:
        """Predict how well post will resonate with target audience"""
        
        content = post["content"].lower()
        platform = post["platform"]
        
        # Platform-specific resonance factors
        platform_keywords = {
            "facebook": ["family", "community", "share", "together"],
            "instagram": ["beautiful", "aesthetic", "lifestyle", "inspiration"],
            "twitter": ["news", "update", "opinion", "discussion"],
            "linkedin": ["professional", "career", "business", "industry"],
            "tiktok": ["fun", "trend", "challenge", "viral"]
        }
        
        keywords = platform_keywords.get(platform, [])
        matches = sum(1 for keyword in keywords if keyword in content)
        
        if matches >= 2:
            return "high"
        elif matches >= 1:
            return "medium"
        else:
            return "low"
    
    def _suggest_boost_budget(self, post: Dict) -> str:
        """Suggest boost budget for post"""
        
        engagement_analysis = post.get("engagement_analysis", {})
        engagement_level = engagement_analysis.get("engagement_level", "medium")
        
        budget_suggestions = {
            "high": "$20-50 for 3-5 days",
            "medium": "$10-25 for 2-3 days", 
            "low": "$5-15 for 1-2 days"
        }
        
        return budget_suggestions.get(engagement_level, "$10-25 for 2-3 days")
    
    def _predict_engagement_rate(self, post: Dict) -> str:
        """Predict engagement rate based on content analysis"""
        
        engagement_analysis = post.get("engagement_analysis", {})
        engagement_score = engagement_analysis.get("engagement_score", 0)
        
        if engagement_score >= 50:
            return "4-8%"
        elif engagement_score >= 30:
            return "2-4%"
        else:
            return "1-2%"
    
    def _predict_reach_potential(self, post: Dict) -> str:
        """Predict organic reach potential"""
        
        platform = post["platform"]
        viral_indicators = len(post.get("engagement_analysis", {}).get("viral_indicators", []))
        
        # Platform-specific reach factors
        reach_multipliers = {
            "tiktok": 3,
            "instagram": 2,
            "facebook": 1.5,
            "twitter": 2,
            "linkedin": 1
        }
        
        base_reach = 100 + (viral_indicators * 50)
        multiplier = reach_multipliers.get(platform, 1.5)
        estimated_reach = int(base_reach * multiplier)
        
        return f"{estimated_reach}-{estimated_reach * 2} people"
    
    def _predict_conversion_likelihood(self, post: Dict) -> str:
        """Predict conversion likelihood based on content"""
        
        content = post["content"].lower()
        
        # Conversion indicators
        conversion_keywords = ["learn", "discover", "try", "get", "start", "join"]
        has_cta = any(keyword in content for keyword in conversion_keywords)
        
        angle = post.get("angle", "")
        
        # Angle-based conversion rates
        if "user_generated" in angle and has_cta:
            return "high"
        elif "educational" in angle and has_cta:
            return "medium-high"
        elif has_cta:
            return "medium"
        else:
            return "low"
    
    def _generate_enhanced_fallback_posts(self, product_details: Dict[str, str], platform: str, count: int) -> List[Dict]:
        """Generate enhanced fallback social media posts"""
        
        platforms_to_generate = [platform] if platform != "all" else list(self.platforms.keys())
        posts = []
        
        for p in platforms_to_generate:
            platform_posts = self._generate_platform_fallback_posts(product_details, p, count // len(platforms_to_generate) + 1)
            posts.extend(platform_posts)
        
        return posts
    
    def _generate_platform_fallback_posts(self, product_details: Dict[str, str], platform: str, count: int) -> List[Dict]:
        """Generate fallback posts for specific platform"""
        
        platform_spec = self.platforms.get(platform, self.platforms["facebook"])
        product_name = product_details["name"]
        
        fallback_templates = [
            {
                "content": f"Discover the natural benefits of {product_name} for your wellness journey! 🌿 Transform your health naturally.",
                "angle": "educational_tips",
                "hashtags": ["#health", "#wellness", "#natural", f"#{product_name.lower()}", "#transformation"]
            },
            {
                "content": f"What's your biggest health goal this month? 🎯 {product_name} might be the support you need!",
                "angle": "question_engagement", 
                "hashtags": ["#goals", "#health", f"#{product_name.lower()}", "#wellness", "#motivation"]
            },
            {
                "content": f"Real results, real people! ⭐ See why thousands choose {product_name} for their health journey.",
                "angle": "user_generated",
                "hashtags": ["#testimonials", "#results", f"#{product_name.lower()}", "#success", "#health"]
            },
            {
                "content": f"Behind the scenes: How we create {product_name} with the highest quality standards! 🏭",
                "angle": "behind_scenes",
                "hashtags": ["#behindthescenes", "#quality", f"#{product_name.lower()}", "#natural", "#health"]
            },
            {
                "content": f"Health tip: Natural optimization starts with quality ingredients! That's why we created {product_name}. 💡",
                "angle": "educational_tips",
                "hashtags": ["#healthtips", "#natural", f"#{product_name.lower()}", "#wellness", "#quality"]
            }
        ]
        
        posts = []
        for i in range(count):
            template = fallback_templates[i % len(fallback_templates)]
            
            # Apply platform character limits
            content = template["content"]
            if len(content) > platform_spec["optimal_length"]:
                content = content[:platform_spec["optimal_length"]-3] + "..."
            
            post = {
                "post_number": i + 1,
                "platform": platform,
                "content": content,
                "hashtags": template["hashtags"][:platform_spec["hashtags"]],
                "angle": template["angle"],
                "engagement_type": "general",
                "viral_potential": "medium",
                "product_name": product_name,
                "ultra_cheap_generated": False,
                "fallback_generated": True
            }
            
            # Add engagement analysis
            post["engagement_analysis"] = self._analyze_engagement_potential(post)
            
            posts.append(post)
        
        return posts
    
    def _extract_social_media_intelligence(self, intelligence_data: Dict) -> Dict[str, Any]:
        """Extract social media specific intelligence"""
        
        # Get social media intelligence with enum serialization
        social_intel = self._serialize_enum_field(intelligence_data.get("social_media_intelligence", {}))
        emotional_intel = self._serialize_enum_field(intelligence_data.get("emotional_transformation_intelligence", {}))
        community_intel = self._serialize_enum_field(intelligence_data.get("community_social_proof_intelligence", {}))
        
        return {
            "trending_topics": social_intel.get("trending_topics", ["health", "wellness", "natural"]),
            "viral_keywords": social_intel.get("viral_keywords", ["transformation", "results", "breakthrough"]),
            "target_audience": emotional_intel.get("target_audience", "health-conscious adults"),
            "engagement_triggers": community_intel.get("engagement_triggers", ["questions", "polls", "shares"]),
            "platform_preferences": social_intel.get("platform_preferences", {}),
            "optimal_posting_times": social_intel.get("optimal_posting_times", {})
        }
    
    def _safe_int_conversion(self, value: str, default: int, min_val: int, max_val: int) -> int:
        """Safe integer conversion with bounds checking"""
        try:
            result = int(value) if str(value).isdigit() else default
            return max(min_val, min(max_val, result))
        except:
            return default


# Convenience functions for social media generation
async def generate_social_media_with_ultra_cheap_ai(
    intelligence_data: Dict[str, Any],
    platform: str = "all",
    post_count: int = 5,
    preferences: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Generate social media posts using ultra-cheap AI system"""
    
    generator = SocialMediaGenerator()
    if preferences is None:
        preferences = {
            "platform": platform,
            "count": str(post_count)
        }
    else:
        preferences.update({
            "platform": platform,
            "count": str(post_count)
        })
    
    return await generator.generate_social_posts(intelligence_data, preferences)

def get_social_media_generator_cost_summary() -> Dict[str, Any]:
    """Get cost summary from social media generator"""
    generator = SocialMediaGenerator()
    return generator.get_cost_summary()

def get_available_social_platforms() -> List[str]:
    """Get list of available social media platforms"""
    generator = SocialMediaGenerator()
    return list(generator.platforms.keys())

def analyze_social_media_performance(posts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze performance potential of social media posts"""
    
    if not posts:
        return {"error": "No posts to analyze"}
    
    # Calculate overall metrics
    total_posts = len(posts)
    platforms_covered = len(set(post["platform"] for post in posts))
    
    # Engagement analysis
    high_engagement_posts = len([p for p in posts if p.get("engagement_analysis", {}).get("engagement_level") == "high"])
    medium_engagement_posts = len([p for p in posts if p.get("engagement_analysis", {}).get("engagement_level") == "medium"])
    
    # Viral potential analysis
    high_viral_posts = len([p for p in posts if len(p.get("engagement_analysis", {}).get("viral_indicators", [])) >= 2])
    
    # Platform distribution
    platform_distribution = {}
    for post in posts:
        platform = post["platform"]
        platform_distribution[platform] = platform_distribution.get(platform, 0) + 1
    
    return {
        "total_posts": total_posts,
        "platforms_covered": platforms_covered,
        "platform_distribution": platform_distribution,
        "engagement_breakdown": {
            "high_engagement": high_engagement_posts,
            "medium_engagement": medium_engagement_posts,
            "low_engagement": total_posts - high_engagement_posts - medium_engagement_posts
        },
        "viral_potential": {
            "high_viral_potential": high_viral_posts,
            "viral_percentage": (high_viral_posts / total_posts) * 100 if total_posts > 0 else 0
        },
        "overall_quality_score": (
            (high_engagement_posts * 3 + medium_engagement_posts * 2) / total_posts * 100 / 3
        ) if total_posts > 0 else 0,
        "recommendations": _generate_performance_recommendations(posts)
    }

def _generate_performance_recommendations(posts: List[Dict[str, Any]]) -> List[str]:
    """Generate performance improvement recommendations"""
    
    recommendations = []
    
    # Analyze common issues
    low_engagement_count = len([p for p in posts if p.get("engagement_analysis", {}).get("engagement_level") == "low"])
    total_posts = len(posts)
    
    if low_engagement_count / total_posts > 0.5:
        recommendations.append("Consider adding more questions and calls-to-action to increase engagement")
    
    # Check hashtag usage
    poor_hashtag_posts = len([p for p in posts if len(p.get("hashtags", [])) < 3])
    if poor_hashtag_posts / total_posts > 0.3:
        recommendations.append("Improve hashtag strategy - use more relevant, trending hashtags")
    
    # Check content length
    long_posts = len([p for p in posts if len(p.get("content", "")) > 200])
    if long_posts / total_posts > 0.4:
        recommendations.append("Consider shorter, more punchy content for better mobile engagement")
    
    # Platform-specific recommendations
    platforms = set(post["platform"] for post in posts)
    if "tiktok" in platforms:
        recommendations.append("For TikTok, focus on trending sounds and challenges for maximum reach")
    if "linkedin" in platforms:
        recommendations.append("For LinkedIn, emphasize professional benefits and industry insights")
    
    return recommendations if recommendations else ["Content quality looks good! Focus on posting at optimal times for your audience"]