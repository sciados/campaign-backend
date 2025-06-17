# src/intelligence/generators.py
"""
Content generation from intelligence - Transform competitive analysis into marketing materials
"""
import openai
import json
import asyncio
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ContentGenerator:
    """Generate marketing content from intelligence data"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI()
        
        # Content type generators
        self.generators = {
            "email_sequence": self._generate_email_sequence,
            "social_posts": self._generate_social_posts,
            "ad_copy": self._generate_ad_copy,
            "blog_post": self._generate_blog_post,
            "landing_page": self._generate_landing_page,
            "product_description": self._generate_product_description,
            "video_script": self._generate_video_script,
            "sales_page": self._generate_sales_page
        }
    
    async def generate_content(
        self, 
        intelligence_data: Dict[str, Any], 
        content_type: str, 
        preferences: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        """Generate specific content type using intelligence"""
        
        if content_type not in self.generators:
            raise ValueError(f"Unsupported content type: {content_type}")
        
        try:
            # Generate content using specific generator
            generator = self.generators[content_type]
            content_result = await generator(intelligence_data, preferences)
            
            # Add performance predictions
            performance_predictions = await self._predict_performance(
                content_result, intelligence_data, content_type
            )
            
            content_result["performance_predictions"] = performance_predictions
            
            return content_result
            
        except Exception as e:
            logger.error(f"Content generation failed for {content_type}: {str(e)}")
            raise e
    
    async def _generate_email_sequence(
        self, 
        intelligence: Dict[str, Any], 
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate email sequence from intelligence"""
        
        # Extract intelligence for email generation
        pain_points = intelligence.get("psychology_intelligence", {}).get("pain_points", [])
        benefits = intelligence.get("offer_intelligence", {}).get("products", [])
        emotional_triggers = intelligence.get("psychology_intelligence", {}).get("emotional_triggers", [])
        success_stories = intelligence.get("content_intelligence", {}).get("success_stories", [])
        
        # Get user preferences
        tone = preferences.get("tone", "conversational")
        sequence_length = preferences.get("length", 5)
        target_audience = preferences.get("audience", "general")
        
        prompt = f"""
        Create a {sequence_length}-email sequence using this competitive intelligence:

        PSYCHOLOGY INSIGHTS:
        - Pain points: {pain_points[:3]}
        - Emotional triggers: {emotional_triggers[:3]}
        
        OFFER INSIGHTS:
        - Products/benefits: {benefits[:3]}
        - Success stories: {success_stories[:2]}
        
        REQUIREMENTS:
        - Tone: {tone}
        - Target audience: {target_audience}
        - Each email should be 150-300 words
        - Include compelling subject lines
        - Build toward a soft/medium call-to-action
        
        SEQUENCE STRUCTURE:
        1. Hook and relate (address pain point)
        2. Agitate problem (consequences of inaction)  
        3. Introduce solution (present benefits)
        4. Social proof (success stories/testimonials)
        5. Handle objections (address concerns)
        {f"6. Urgency and close (final push)" if sequence_length > 5 else ""}
        
        Return as structured JSON with emails array.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert email marketer who creates high-converting email sequences. Use competitive intelligence to create compelling, psychology-driven content."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2500
            )
            
            ai_response = response.choices[0].message.content
            
            # Parse response into structured format
            emails = self._parse_email_sequence_response(ai_response, sequence_length)
            
            return {
                "content_type": "email_sequence",
                "title": f"{sequence_length}-Email Sequence from Competitive Intelligence",
                "content": emails,
                "metadata": {
                    "sequence_length": len(emails),
                    "total_words": sum(len(email["body"].split()) for email in emails),
                    "intelligence_sources": 1,
                    "tone": tone,
                    "target_audience": target_audience
                },
                "usage_tips": [
                    "Customize sender name and signature",
                    "Test subject lines with A/B testing",
                    "Monitor open and click rates",
                    "Adjust timing based on audience engagement"
                ]
            }
            
        except Exception as e:
            return self._fallback_email_sequence(intelligence, preferences)
    
    async def _generate_social_posts(
        self, 
        intelligence: Dict[str, Any], 
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate social media posts from intelligence"""
        
        key_messages = intelligence.get("content_intelligence", {}).get("key_messages", [])
        emotional_triggers = intelligence.get("psychology_intelligence", {}).get("emotional_triggers", [])
        opportunities = intelligence.get("competitive_intelligence", {}).get("opportunities", [])
        
        platform = preferences.get("platform", "general")
        post_count = preferences.get("count", 10)
        style = preferences.get("style", "engaging")
        
        prompt = f"""
        Create {post_count} social media posts for {platform} using this intelligence:

        KEY MESSAGES: {key_messages[:5]}
        EMOTIONAL TRIGGERS: {emotional_triggers[:3]}
        OPPORTUNITIES: {opportunities[:3]}
        
        REQUIREMENTS:
        - Style: {style}
        - Platform: {platform}
        - Include relevant hashtags
        - Mix of educational, promotional, and engaging content
        - Character limits: Instagram (2200), Twitter (280), LinkedIn (3000)
        
        POST TYPES TO INCLUDE:
        - Question posts (engagement)
        - Tip/advice posts (value)
        - Behind-the-scenes (authenticity)
        - User-generated content ideas
        - Promotional posts (soft sell)
        
        Return as JSON array with post objects.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a social media expert who creates viral, engaging content. Use psychology and competitive insights to drive engagement."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            ai_response = response.choices[0].message.content
            posts = self._parse_social_posts_response(ai_response, post_count)
            
            return {
                "content_type": "social_posts",
                "title": f"{post_count} {platform.title()} Posts from Competitive Intelligence",
                "content": posts,
                "metadata": {
                    "post_count": len(posts),
                    "platform": platform,
                    "style": style,
                    "avg_length": sum(len(post["text"]) for post in posts) // len(posts) if posts else 0
                },
                "usage_tips": [
                    "Post at optimal times for your audience",
                    "Engage with comments and replies",
                    "Track hashtag performance",
                    "Repurpose top-performing posts"
                ]
            }
            
        except Exception as e:
            return self._fallback_social_posts(intelligence, preferences)
    
    async def _generate_ad_copy(
        self, 
        intelligence: Dict[str, Any], 
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate ad copy from intelligence"""
        
        emotional_triggers = intelligence.get("psychology_intelligence", {}).get("emotional_triggers", [])
        benefits = intelligence.get("offer_intelligence", {}).get("products", [])
        pain_points = intelligence.get("psychology_intelligence", {}).get("pain_points", [])
        
        ad_platform = preferences.get("platform", "facebook")
        ad_objective = preferences.get("objective", "conversions")
        target_audience = preferences.get("audience", "general")
        
        prompt = f"""
        Create high-converting ad copy for {ad_platform} using this intelligence:

        EMOTIONAL TRIGGERS: {emotional_triggers[:3]}
        BENEFITS: {benefits[:3]}
        PAIN POINTS: {pain_points[:3]}
        
        AD SPECIFICATIONS:
        - Platform: {ad_platform}
        - Objective: {ad_objective}
        - Target audience: {target_audience}
        
        CREATE MULTIPLE VARIATIONS:
        - 3 headline options (attention-grabbing)
        - 3 primary text options (benefit-focused)
        - 3 call-to-action options
        - 2 description options
        
        PSYCHOLOGY PRINCIPLES TO USE:
        - Urgency and scarcity
        - Social proof elements
        - Problem/solution framework
        - Benefit-driven messaging
        
        Return as structured JSON with variations.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a direct response copywriter who creates high-converting ads. Use psychology and competitive intelligence to maximize conversions."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1800
            )
            
            ai_response = response.choices[0].message.content
            ad_variations = self._parse_ad_copy_response(ai_response)
            
            return {
                "content_type": "ad_copy",
                "title": f"{ad_platform.title()} Ad Copy from Competitive Intelligence",
                "content": ad_variations,
                "metadata": {
                    "platform": ad_platform,
                    "objective": ad_objective,
                    "target_audience": target_audience,
                    "variations_count": len(ad_variations.get("headlines", []))
                },
                "usage_tips": [
                    "A/B test different headline variations",
                    "Monitor cost per acquisition (CPA)",
                    "Test different audience segments",
                    "Optimize based on conversion data"
                ]
            }
            
        except Exception as e:
            return self._fallback_ad_copy(intelligence, preferences)
    
    async def _generate_blog_post(
        self, 
        intelligence: Dict[str, Any], 
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate blog post from intelligence"""
        
        key_insights = intelligence.get("content_intelligence", {}).get("key_insights", [])
        opportunities = intelligence.get("competitive_intelligence", {}).get("opportunities", [])
        data_points = intelligence.get("content_intelligence", {}).get("data_points", [])
        
        topic = preferences.get("topic", "industry insights")
        length = preferences.get("length", "medium")  # short, medium, long
        seo_focus = preferences.get("seo_keywords", [])
        
        word_targets = {"short": 800, "medium": 1500, "long": 2500}
        target_words = word_targets.get(length, 1500)
        
        prompt = f"""
        Write a {target_words}-word blog post about {topic} using this competitive intelligence:

        KEY INSIGHTS: {key_insights[:5]}
        MARKET OPPORTUNITIES: {opportunities[:3]}
        DATA POINTS: {data_points[:3]}
        SEO KEYWORDS: {seo_focus[:5]}
        
        BLOG POST STRUCTURE:
        1. Compelling headline (SEO-optimized)
        2. Introduction hook (problem/opportunity)
        3. Main content sections (3-5 sections)
        4. Data-driven insights and examples
        5. Actionable takeaways
        6. Conclusion with call-to-action
        
        REQUIREMENTS:
        - Authority-building tone
        - Include competitive insights naturally
        - Add internal linking opportunities
        - SEO-optimized headings
        - Include meta description
        
        Return as structured JSON with sections.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert content marketer who creates authority-building blog posts. Use competitive intelligence to provide unique insights and establish thought leadership."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=3500
            )
            
            ai_response = response.choices[0].message.content
            blog_content = self._parse_blog_post_response(ai_response)
            
            return {
                "content_type": "blog_post",
                "title": blog_content.get("headline", f"Blog Post: {topic}"),
                "content": blog_content,
                "metadata": {
                    "word_count": len(blog_content.get("body", "").split()),
                    "estimated_read_time": len(blog_content.get("body", "").split()) // 200,
                    "seo_keywords": seo_focus,
                    "sections": len(blog_content.get("sections", []))
                },
                "usage_tips": [
                    "Optimize images with alt text",
                    "Add internal and external links",
                    "Promote on social media",
                    "Update with fresh data regularly"
                ]
            }
            
        except Exception as e:
            return self._fallback_blog_post(intelligence, preferences)
    
    async def _generate_landing_page(
        self, 
        intelligence: Dict[str, Any], 
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate landing page copy from intelligence"""
        
        offer_details = intelligence.get("offer_intelligence", {})
        psychology_insights = intelligence.get("psychology_intelligence", {})
        competitive_advantages = intelligence.get("competitive_intelligence", {}).get("opportunities", [])
        
        page_goal = preferences.get("goal", "lead_generation")
        target_audience = preferences.get("audience", "general")
        
        prompt = f"""
        Create a high-converting landing page for {page_goal} using this intelligence:

        OFFER INSIGHTS: {offer_details}
        PSYCHOLOGY INSIGHTS: {psychology_insights}
        COMPETITIVE ADVANTAGES: {competitive_advantages[:3]}
        
        TARGET AUDIENCE: {target_audience}
        
        LANDING PAGE SECTIONS:
        1. Compelling headline and subheadline
        2. Hero section with value proposition
        3. Benefits section (not features)
        4. Social proof section
        5. Objection handling
        6. Strong call-to-action
        7. Urgency/scarcity elements
        
        CONVERSION OPTIMIZATION:
        - Use emotional triggers from intelligence
        - Address specific pain points
        - Highlight competitive advantages
        - Include trust signals
        - Clear, prominent CTA buttons
        
        Return as structured JSON with sections.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a conversion optimization expert who creates high-converting landing pages. Use competitive intelligence and psychology to maximize conversions."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=2500
            )
            
            ai_response = response.choices[0].message.content
            landing_page = self._parse_landing_page_response(ai_response)
            
            return {
                "content_type": "landing_page",
                "title": landing_page.get("headline", "High-Converting Landing Page"),
                "content": landing_page,
                "metadata": {
                    "goal": page_goal,
                    "target_audience": target_audience,
                    "sections": len(landing_page.get("sections", [])),
                    "cta_count": landing_page.get("cta_count", 0)
                },
                "needs_tracking": True,
                "target_url": preferences.get("redirect_url", ""),
                "usage_tips": [
                    "A/B test different headlines",
                    "Monitor conversion rates",
                    "Optimize page load speed",
                    "Track user behavior with heatmaps"
                ]
            }
            
        except Exception as e:
            return self._fallback_landing_page(intelligence, preferences)
    
    async def _generate_product_description(self, intelligence: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Generate product description from intelligence"""
        
        products = intelligence.get("offer_intelligence", {}).get("products", [])
        benefits = intelligence.get("psychology_intelligence", {}).get("benefits", [])
        emotional_triggers = intelligence.get("psychology_intelligence", {}).get("emotional_triggers", [])
        
        product_type = preferences.get("product_type", "general")
        length = preferences.get("length", "medium")
        
        prompt = f"""
        Create a compelling product description for a {product_type} using this intelligence:

        PRODUCT INSIGHTS: {products[:3]}
        BENEFITS: {benefits[:5]}
        EMOTIONAL TRIGGERS: {emotional_triggers[:3]}
        
        REQUIREMENTS:
        - Length: {length}
        - Focus on benefits over features
        - Use emotional triggers effectively
        - Include clear value proposition
        - End with strong call-to-action
        
        Return as structured content.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert product copywriter who creates compelling descriptions that convert browsers into buyers."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            ai_response = response.choices[0].message.content
            
            return {
                "content_type": "product_description",
                "title": f"Product Description - {product_type}",
                "content": {
                    "description": ai_response,
                    "key_benefits": benefits[:5],
                    "emotional_hooks": emotional_triggers[:3]
                },
                "metadata": {
                    "product_type": product_type,
                    "length": length,
                    "word_count": len(ai_response.split())
                },
                "usage_tips": [
                    "Use in product listings",
                    "Adapt for different platforms",
                    "A/B test different versions",
                    "Include in email campaigns"
                ]
            }
            
        except Exception as e:
            return {
                "content_type": "product_description",
                "title": "Product Description",
                "content": {"description": "High-quality product description based on competitive intelligence."},
                "metadata": {"fallback": True}
            }
    
    async def _generate_video_script(self, intelligence: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Generate video script from intelligence"""
        
        key_messages = intelligence.get("content_intelligence", {}).get("key_messages", [])
        emotional_triggers = intelligence.get("psychology_intelligence", {}).get("emotional_triggers", [])
        success_stories = intelligence.get("content_intelligence", {}).get("success_stories", [])
        
        video_type = preferences.get("video_type", "educational")
        duration = preferences.get("duration", "3-5 minutes")
        
        prompt = f"""
        Create a {duration} {video_type} video script using this intelligence:

        KEY MESSAGES: {key_messages[:5]}
        EMOTIONAL TRIGGERS: {emotional_triggers[:3]}
        SUCCESS STORIES: {success_stories[:2]}
        
        SCRIPT STRUCTURE:
        1. Hook (first 10 seconds)
        2. Problem identification
        3. Solution presentation
        4. Social proof/examples
        5. Call-to-action
        
        Include:
        - Visual cues and directions
        - Timing suggestions
        - Engagement elements
        - Clear call-to-action
        
        Return as structured script format.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert video script writer who creates engaging, conversion-focused video content."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            ai_response = response.choices[0].message.content
            
            return {
                "content_type": "video_script",
                "title": f"{video_type.title()} Video Script - {duration}",
                "content": {
                    "script": ai_response,
                    "duration": duration,
                    "video_type": video_type
                },
                "metadata": {
                    "video_type": video_type,
                    "duration": duration,
                    "estimated_words": len(ai_response.split())
                },
                "usage_tips": [
                    "Practice delivery before recording",
                    "Use teleprompter for longer scripts",
                    "Add engaging visuals and graphics",
                    "Include captions for accessibility"
                ]
            }
            
        except Exception as e:
            return {
                "content_type": "video_script",
                "title": "Video Script",
                "content": {"script": "Engaging video script based on competitive intelligence."},
                "metadata": {"fallback": True}
            }
    
    async def _generate_sales_page(self, intelligence: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete sales page from intelligence"""
        
        offer_details = intelligence.get("offer_intelligence", {})
        psychology_insights = intelligence.get("psychology_intelligence", {})
        competitive_advantages = intelligence.get("competitive_intelligence", {}).get("opportunities", [])
        
        page_type = preferences.get("page_type", "long_form")
        target_audience = preferences.get("audience", "general")
        
        prompt = f"""
        Create a complete {page_type} sales page using this intelligence:

        OFFER DETAILS: {offer_details}
        PSYCHOLOGY INSIGHTS: {psychology_insights}
        COMPETITIVE ADVANTAGES: {competitive_advantages[:5]}
        
        TARGET AUDIENCE: {target_audience}
        
        SALES PAGE STRUCTURE:
        1. Compelling headline and subheadline
        2. Problem agitation
        3. Solution introduction
        4. Benefits and features
        5. Social proof section
        6. Objection handling
        7. Urgency and scarcity
        8. Strong call-to-action
        9. Guarantee and risk reversal
        10. Final call-to-action
        
        Include:
        - Psychological triggers throughout
        - Multiple CTA buttons
        - Trust signals and testimonials
        - Competitive differentiation
        
        Return as structured sales page sections.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert sales copywriter who creates high-converting sales pages using psychological principles and competitive intelligence."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=4000
            )
            
            ai_response = response.choices[0].message.content
            
            return {
                "content_type": "sales_page",
                "title": f"{page_type.title()} Sales Page",
                "content": {
                    "full_page": ai_response,
                    "page_type": page_type,
                    "target_audience": target_audience
                },
                "metadata": {
                    "page_type": page_type,
                    "target_audience": target_audience,
                    "word_count": len(ai_response.split()),
                    "estimated_read_time": len(ai_response.split()) // 200
                },
                "needs_tracking": True,
                "usage_tips": [
                    "Test different headlines",
                    "Monitor conversion rates",
                    "Add exit-intent popups",
                    "Implement scroll tracking"
                ]
            }
            
        except Exception as e:
            return {
                "content_type": "sales_page",
                "title": "Sales Page",
                "content": {"full_page": "Complete sales page based on competitive intelligence."},
                "metadata": {"fallback": True}
            }
    
    # Helper methods for parsing AI responses
    
    def _parse_email_sequence_response(self, ai_response: str, sequence_length: int) -> List[Dict[str, str]]:
        """Parse AI response into email sequence format"""
        
        emails = []
        
        try:
            # Try to parse JSON response
            if '{' in ai_response and '}' in ai_response:
                import re
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    parsed_data = json.loads(json_match.group())
                    return parsed_data.get("emails", [])
            
            # Fallback: Parse text format
            lines = ai_response.split('\n')
            current_email = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for email indicators
                if 'email' in line.lower() and ('1' in line or '2' in line or '3' in line):
                    if current_email:
                        emails.append(current_email)
                    current_email = {"email_number": len(emails) + 1}
                
                elif 'subject' in line.lower():
                    current_email["subject"] = line.split(':', 1)[-1].strip()
                
                elif len(line) > 50 and 'subject' not in line.lower():
                    # Likely email body content
                    if "body" not in current_email:
                        current_email["body"] = line
                    else:
                        current_email["body"] += "\n" + line
            
            # Add last email
            if current_email:
                emails.append(current_email)
            
            # Ensure we have the requested number of emails
            while len(emails) < sequence_length:
                emails.append({
                    "email_number": len(emails) + 1,
                    "subject": f"Follow-up Email #{len(emails) + 1}",
                    "body": "Continue building relationship and providing value..."
                })
            
            return emails[:sequence_length]
            
        except Exception as e:
            logger.error(f"Failed to parse email sequence: {str(e)}")
            return self._generate_fallback_emails(sequence_length)
    
    def _parse_social_posts_response(self, ai_response: str, post_count: int) -> List[Dict[str, Any]]:
        """Parse AI response into social posts format"""
        
        posts = []
        
        try:
            # Try JSON parsing first
            if '{' in ai_response and '[' in ai_response:
                import re
                json_match = re.search(r'\[.*\]', ai_response, re.DOTALL)
                if json_match:
                    parsed_data = json.loads(json_match.group())
                    return parsed_data[:post_count]
            
            # Fallback: Parse text format
            lines = ai_response.split('\n')
            current_post = ""
            
            for line in lines:
                line = line.strip()
                if not line:
                    if current_post:
                        posts.append({
                            "text": current_post.strip(),
                            "hashtags": self._extract_hashtags(current_post),
                            "type": "general"
                        })
                        current_post = ""
                    continue
                
                if line.startswith(('Post', 'Tweet', '#')):
                    if current_post:
                        posts.append({
                            "text": current_post.strip(),
                            "hashtags": self._extract_hashtags(current_post),
                            "type": "general"
                        })
                    current_post = line
                else:
                    current_post += "\n" + line
            
            # Add last post
            if current_post:
                posts.append({
                    "text": current_post.strip(),
                    "hashtags": self._extract_hashtags(current_post),
                    "type": "general"
                })
            
            return posts[:post_count]
            
        except Exception as e:
            logger.error(f"Failed to parse social posts: {str(e)}")
            return self._generate_fallback_posts(post_count)
    
    def _parse_ad_copy_response(self, ai_response: str) -> Dict[str, List[str]]:
        """Parse AI response into ad copy variations"""
        
        variations = {
            "headlines": [],
            "primary_text": [],
            "descriptions": [],
            "call_to_actions": []
        }
        
        try:
            lines = ai_response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Identify sections
                if 'headline' in line.lower():
                    current_section = "headlines"
                elif 'primary' in line.lower() or 'body' in line.lower():
                    current_section = "primary_text"
                elif 'description' in line.lower():
                    current_section = "descriptions"
                elif 'call' in line.lower() or 'cta' in line.lower():
                    current_section = "call_to_actions"
                
                # Extract variations
                elif line.startswith(('-', '•', '*', '1.', '2.', '3.')):
                    variation = line[1:].strip() if line.startswith(('-', '•', '*')) else line[2:].strip()
                    if current_section and variation:
                        variations[current_section].append(variation)
            
            return variations
            
        except Exception as e:
            logger.error(f"Failed to parse ad copy: {str(e)}")
            return {
                "headlines": ["Get Results Fast", "Transform Your Business", "Limited Time Offer"],
                "primary_text": ["Discover the secret to success", "Join thousands of satisfied customers", "Don't miss this opportunity"],
                "descriptions": ["Learn more about our solution", "Start your journey today"],
                "call_to_actions": ["Learn More", "Get Started", "Sign Up Now"]
            }
    
    def _parse_blog_post_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response into blog post format"""
        
        blog_post = {
            "headline": "",
            "meta_description": "",
            "introduction": "",
            "sections": [],
            "conclusion": "",
            "body": ai_response
        }
        
        try:
            lines = ai_response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Identify headline
                if line.startswith('#') or ('headline' in line.lower() and len(line) < 100):
                    blog_post["headline"] = line.replace('#', '').strip()
                
                # Identify sections
                elif line.startswith('##') or ('section' in line.lower() and ':' in line):
                    section_title = line.replace('##', '').strip()
                    blog_post["sections"].append({"title": section_title, "content": ""})
                    current_section = len(blog_post["sections"]) - 1
                
                # Add content to current section
                elif current_section is not None and len(line) > 20:
                    blog_post["sections"][current_section]["content"] += line + "\n"
            
            return blog_post
            
        except Exception as e:
            logger.error(f"Failed to parse blog post: {str(e)}")
            return {
                "headline": "Industry Insights from Competitive Analysis",
                "meta_description": "Discover key insights and opportunities in your industry",
                "body": ai_response,
                "sections": [{"title": "Key Insights", "content": ai_response[:500]}]
            }
    
    def _parse_landing_page_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response into landing page sections"""
        
        landing_page = {
            "headline": "",
            "subheadline": "",
            "sections": [],
            "cta_count": 0
        }
        
        try:
            lines = ai_response.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Count CTAs
                if any(cta in line.lower() for cta in ['call to action', 'cta', 'button', 'sign up', 'get started']):
                    landing_page["cta_count"] += 1
                
                # Extract headline
                if ('headline' in line.lower() or line.startswith('#')) and not landing_page["headline"]:
                    landing_page["headline"] = line.replace('#', '').strip()
                
                # Extract sections
                elif line.startswith('##') or any(section in line.lower() for section in ['hero', 'benefits', 'proof']):
                    landing_page["sections"].append(line.strip())
            
            return landing_page
            
        except Exception as e:
            logger.error(f"Failed to parse landing page: {str(e)}")
            return {
                "headline": "Transform Your Results Today",
                "subheadline": "Join thousands who have already succeeded",
                "sections": ["Hero Section", "Benefits", "Social Proof", "Call to Action"],
                "cta_count": 2
            }
    
    # Performance prediction methods
    
    async def _predict_performance(
        self, 
        content_result: Dict[str, Any], 
        intelligence: Dict[str, Any], 
        content_type: str
    ) -> Dict[str, Any]:
        """Predict content performance based on intelligence and best practices"""
        
        confidence_score = intelligence.get("confidence_score", 0.5)
        
        # Base predictions on content type and intelligence quality
        base_predictions = {
            "email_sequence": {
                "estimated_open_rate": 0.15 + (confidence_score * 0.1),
                "estimated_click_rate": 0.02 + (confidence_score * 0.02),
                "estimated_conversion_rate": 0.01 + (confidence_score * 0.015)
            },
            "social_posts": {
                "estimated_engagement_rate": 0.03 + (confidence_score * 0.02),
                "estimated_reach": "medium" if confidence_score > 0.7 else "low",
                "viral_potential": "high" if confidence_score > 0.8 else "medium"
            },
            "ad_copy": {
                "estimated_ctr": 0.01 + (confidence_score * 0.02),
                "estimated_conversion_rate": 0.02 + (confidence_score * 0.03),
                "estimated_cpa": "low" if confidence_score > 0.7 else "medium"
            },
            "blog_post": {
                "estimated_traffic": "high" if confidence_score > 0.8 else "medium",
                "seo_potential": "strong" if confidence_score > 0.7 else "good",
                "share_potential": "high" if confidence_score > 0.75 else "medium"
            },
            "landing_page": {
                "estimated_conversion_rate": 0.02 + (confidence_score * 0.05),
                "bounce_rate": 0.4 - (confidence_score * 0.1),
                "optimization_score": confidence_score * 10
            },
            "product_description": {
                "estimated_conversion_rate": 0.03 + (confidence_score * 0.04),
                "click_through_rate": 0.05 + (confidence_score * 0.03),
                "engagement_score": confidence_score * 8
            },
            "video_script": {
                "estimated_watch_time": "high" if confidence_score > 0.7 else "medium",
                "engagement_rate": 0.04 + (confidence_score * 0.03),
                "conversion_potential": "strong" if confidence_score > 0.75 else "good"
            },
            "sales_page": {
                "estimated_conversion_rate": 0.01 + (confidence_score * 0.06),
                "time_on_page": "high" if confidence_score > 0.8 else "medium",
                "optimization_score": confidence_score * 9
            }
        }
        
        predictions = base_predictions.get(content_type, {})
        
        # Add general predictions
        predictions.update({
            "confidence_level": "high" if confidence_score > 0.8 else "medium" if confidence_score > 0.6 else "low",
            "optimization_suggestions": [
                "A/B test different variations",
                "Monitor performance metrics closely",
                "Optimize based on early results"
            ],
            "success_factors": [
                "Based on competitive intelligence",
                "Uses proven psychology principles",
                "Addresses identified market gaps"
            ]
        })
        
        return predictions
    
    # Fallback methods
    
    def _generate_fallback_emails(self, count: int) -> List[Dict[str, str]]:
        """Generate fallback email sequence when AI fails"""
        
        fallback_emails = [
            {
                "email_number": 1,
                "subject": "Welcome! Here's what you need to know...",
                "body": "Thank you for your interest. Let me share some valuable insights with you..."
            },
            {
                "email_number": 2,
                "subject": "The #1 mistake most people make",
                "body": "I've noticed a common pattern that prevents success. Here's how to avoid it..."
            },
            {
                "email_number": 3,
                "subject": "Here's proof it actually works",
                "body": "I want to share a success story that demonstrates the power of this approach..."
            },
            {
                "email_number": 4,
                "subject": "What's holding you back?",
                "body": "Let's address the common concerns and objections people have..."
            },
            {
                "email_number": 5,
                "subject": "Last chance to transform your results",
                "body": "This is your final opportunity to take action and see real change..."
            }
        ]
        
        return fallback_emails[:count]
    
    def _generate_fallback_posts(self, count: int) -> List[Dict[str, Any]]:
        """Generate fallback social posts when AI fails"""
        
        fallback_posts = [
            {
                "text": "What's the biggest challenge you're facing right now? Let me know in the comments!",
                "hashtags": ["#motivation", "#success", "#entrepreneur"],
                "type": "engagement"
            },
            {
                "text": "Here's a quick tip that can transform your results: Focus on progress, not perfection.",
                "hashtags": ["#tip", "#mindset", "#growth"],
                "type": "educational"
            },
            {
                "text": "Success isn't about being the best. It's about being better than you were yesterday.",
                "hashtags": ["#inspiration", "#success", "#mindset"],
                "type": "motivational"
            },
            {
                "text": "The difference between successful people and everyone else? They take action despite fear.",
                "hashtags": ["#action", "#courage", "#success"],
                "type": "motivational"
            },
            {
                "text": "Stop waiting for the perfect moment. Start with what you have, where you are.",
                "hashtags": ["#start", "#action", "#motivation"],
                "type": "inspirational"
            }
        ]
        
        return (fallback_posts * (count // len(fallback_posts) + 1))[:count]
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        import re
        hashtags = re.findall(r'#\w+', text)
        return hashtags
    
    # Additional fallback methods for other content types
    def _fallback_email_sequence(self, intelligence: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "content_type": "email_sequence",
            "title": "Email Sequence from Intelligence",
            "content": self._generate_fallback_emails(preferences.get("length", 5)),
            "metadata": {"fallback": True}
        }
    
    def _fallback_social_posts(self, intelligence: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "content_type": "social_posts", 
            "title": "Social Media Posts",
            "content": self._generate_fallback_posts(preferences.get("count", 10)),
            "metadata": {"fallback": True}
        }
    
    def _fallback_ad_copy(self, intelligence: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "content_type": "ad_copy",
            "title": "Ad Copy Variations",
            "content": {
                "headlines": ["Transform Your Results", "Get Started Today", "Limited Time Offer"],
                "primary_text": ["Discover the solution you've been looking for"],
                "call_to_actions": ["Learn More", "Get Started", "Sign Up"]
            },
            "metadata": {"fallback": True}
        }
    
    def _fallback_blog_post(self, intelligence: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "content_type": "blog_post",
            "title": "Industry Insights Blog Post",
            "content": {
                "headline": "Key Industry Insights You Need to Know",
                "body": "Based on our competitive analysis, here are the key trends and opportunities...",
                "sections": [{"title": "Key Insights", "content": "Important industry developments..."}]
            },
            "metadata": {"fallback": True}
        }
    
    def _fallback_landing_page(self, intelligence: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "content_type": "landing_page",
            "title": "High-Converting Landing Page",
            "content": {
                "headline": "Transform Your Business Today",
                "sections": ["Hero", "Benefits", "Social Proof", "Call to Action"],
                "cta_count": 2
            },
            "metadata": {"fallback": True}
        }