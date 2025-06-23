# src/intelligence/generators.py - FIXED VERSION
"""
Content generation from intelligence - Transform competitive analysis into marketing materials
"""
import os
import json
import asyncio
from typing import Dict, List, Any, Optional
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class ContentGenerator:
    """Generate marketing content from intelligence data"""
    
    def __init__(self):
        # ✅ FIXED: Safe OpenAI initialization with error handling
        try:
            import openai
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = openai.AsyncOpenAI(api_key=api_key)
                self.ai_available = True
                logger.info("✅ OpenAI client initialized successfully")
            else:
                self.openai_client = None
                self.ai_available = False
                logger.warning("⚠️ OpenAI API key not found. Using template-based generation.")
        except ImportError:
            self.openai_client = None
            self.ai_available = False
            logger.warning("⚠️ OpenAI not available. Using template-based generation.")
        except Exception as e:
            self.openai_client = None
            self.ai_available = False
            logger.error(f"❌ OpenAI initialization failed: {str(e)}")
        
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
        
        logger.info(f"🎯 Starting content generation: {content_type}")
        
        # ✅ FIXED: Ensure preferences is properly handled
        if preferences is None:
            preferences = {}
        
        # ✅ FIXED: Convert all preference values to strings to avoid type comparison errors
        safe_preferences = {}
        for key, value in preferences.items():
            try:
                if isinstance(value, (int, float)):
                    safe_preferences[key] = str(value)
                elif isinstance(value, bool):
                    safe_preferences[key] = "true" if value else "false"
                elif isinstance(value, list):
                    safe_preferences[key] = ", ".join(str(item) for item in value)
                elif value is None:
                    safe_preferences[key] = ""
                else:
                    safe_preferences[key] = str(value)
            except Exception as e:
                logger.warning(f"⚠️ Error processing preference {key}: {str(e)}")
                safe_preferences[key] = ""
        
        logger.info(f"📋 Safe preferences: {safe_preferences}")
        
        if content_type not in self.generators:
            logger.error(f"❌ Unsupported content type: {content_type}")
            return self._generate_fallback_content(content_type, f"Unsupported content type: {content_type}")
        
        try:
            # Generate content using specific generator
            generator = self.generators[content_type]
            logger.info(f"🔧 Using generator: {generator.__name__}")
            
            content_result = await generator(intelligence_data, safe_preferences)
            
            # Add performance predictions
            performance_predictions = self._predict_performance(
                content_result, intelligence_data, content_type
            )
            
            content_result["performance_predictions"] = performance_predictions
            
            logger.info(f"✅ Content generation completed: {content_type}")
            return content_result
            
        except Exception as e:
            logger.error(f"❌ Content generation failed for {content_type}: {str(e)}")
            import traceback
            logger.error(f"📍 Traceback: {traceback.format_exc()}")
            return self._generate_fallback_content(content_type, str(e))
    
    async def _generate_email_sequence(
        self, 
        intelligence: Dict[str, Any], 
        preferences: Dict[str, str]
    ) -> Dict[str, Any]:
        """Generate email sequence from intelligence"""
        
        logger.info("📧 Generating email sequence")
        
        # Extract intelligence for email generation
        psych_intel = intelligence.get("psychology_intelligence", {})
        offer_intel = intelligence.get("offer_intelligence", {})
        content_intel = intelligence.get("content_intelligence", {})
        
        pain_points = psych_intel.get("pain_points", [])
        benefits = offer_intel.get("products", [])
        emotional_triggers = psych_intel.get("emotional_triggers", [])
        success_stories = content_intel.get("success_stories", [])
        
        # Get user preferences with safe defaults
        tone = preferences.get("tone", "conversational")
        sequence_length_str = preferences.get("length", "5")
        target_audience = preferences.get("audience", "general")
        
        # ✅ FIXED: Safe integer conversion
        try:
            sequence_length = int(sequence_length_str) if sequence_length_str.isdigit() else 5
        except (ValueError, AttributeError):
            sequence_length = 5
        
        # Ensure sequence length is reasonable
        sequence_length = max(3, min(10, sequence_length))
        
        logger.info(f"📊 Email sequence params: length={sequence_length}, tone={tone}, audience={target_audience}")
        
        if self.ai_available and self.openai_client:
            try:
                return await self._generate_ai_email_sequence(
                    pain_points, benefits, emotional_triggers, success_stories,
                    tone, sequence_length, target_audience
                )
            except Exception as e:
                logger.error(f"❌ AI email generation failed: {str(e)}")
                return self._generate_template_email_sequence(sequence_length, tone, target_audience)
        else:
            return self._generate_template_email_sequence(sequence_length, tone, target_audience)
    
    async def _generate_ai_email_sequence(
        self, pain_points, benefits, emotional_triggers, success_stories,
        tone, sequence_length, target_audience
    ) -> Dict[str, Any]:
        """Generate email sequence using OpenAI"""
        
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
        
        Return as JSON with this exact structure:
        {{
          "sequence_title": "Email Sequence Title",
          "emails": [
            {{
              "email_number": 1,
              "subject": "Subject line here",
              "body": "Email body content here",
              "send_delay": "Day 1"
            }}
          ]
        }}
        """
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert email marketer. Return only valid JSON format with the exact structure requested."
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
            "content": {
                "sequence_title": f"{sequence_length}-Email Marketing Sequence",
                "emails": emails
            },
            "metadata": {
                "sequence_length": len(emails),
                "total_words": sum(len(email.get("body", "").split()) for email in emails),
                "intelligence_sources": 1,
                "tone": tone,
                "target_audience": target_audience,
                "generated_by": "openai"
            },
            "usage_tips": [
                "Customize sender name and signature",
                "Test subject lines with A/B testing", 
                "Monitor open and click rates",
                "Adjust timing based on audience engagement"
            ]
        }
    
    def _generate_template_email_sequence(
        self, sequence_length: int, tone: str, target_audience: str
    ) -> Dict[str, Any]:
        """Generate template-based email sequence"""
        
        logger.info(f"📧 Generating template email sequence: {sequence_length} emails")
        
        template_emails = [
            {
                "email_number": 1,
                "subject": f"Welcome to {target_audience} success",
                "body": f"Hi there,\n\nWelcome! We're excited to help you achieve your goals with our proven approach.\n\nBest regards,\nThe Team",
                "send_delay": "Day 1"
            },
            {
                "email_number": 2,
                "subject": "The challenge most people face",
                "body": f"Many {target_audience} struggle with common challenges. Our research shows what works best.\n\nLet us show you how.",
                "send_delay": "Day 3"
            },
            {
                "email_number": 3,
                "subject": "Here's how we solve it",
                "body": f"Our solution uses proven methods to deliver results for {target_audience}.\n\nSee how it works.",
                "send_delay": "Day 5"
            },
            {
                "email_number": 4,
                "subject": "What others are saying",
                "body": f"Don't just take our word for it. See what other {target_audience} are saying about our approach.",
                "send_delay": "Day 7"
            },
            {
                "email_number": 5,
                "subject": "Ready to get started?",
                "body": f"Join thousands of satisfied {target_audience} who've experienced our results.\n\nGet started today!",
                "send_delay": "Day 10"
            }
        ]
        
        # Extend or trim to match requested length
        while len(template_emails) < sequence_length:
            template_emails.append({
                "email_number": len(template_emails) + 1,
                "subject": f"Follow-up #{len(template_emails) + 1}",
                "body": f"Continuing our conversation about {target_audience} success...",
                "send_delay": f"Day {(len(template_emails) + 1) * 2 + 1}"
            })
        
        emails = template_emails[:sequence_length]
        
        return {
            "content_type": "email_sequence",
            "title": f"{sequence_length}-Email Sequence (Template)",
            "content": {
                "sequence_title": f"{sequence_length}-Email Marketing Sequence",
                "emails": emails
            },
            "metadata": {
                "sequence_length": len(emails),
                "total_words": sum(len(email.get("body", "").split()) for email in emails),
                "tone": tone,
                "target_audience": target_audience,
                "generated_by": "template"
            },
            "usage_tips": [
                "Customize the content for your specific brand voice",
                "Add personalization tokens where appropriate",
                "Test subject lines with your audience"
            ]
        }
    
    async def _generate_social_posts(
        self, 
        intelligence: Dict[str, Any], 
        preferences: Dict[str, str]
    ) -> Dict[str, Any]:
        """Generate social media posts from intelligence"""
        
        logger.info("📱 Generating social media posts")
        
        content_intel = intelligence.get("content_intelligence", {})
        psych_intel = intelligence.get("psychology_intelligence", {})
        comp_intel = intelligence.get("competitive_intelligence", {})
        
        key_messages = content_intel.get("key_messages", [])
        emotional_triggers = psych_intel.get("emotional_triggers", [])
        opportunities = comp_intel.get("opportunities", [])
        
        platform = preferences.get("platform", "general")
        post_count_str = preferences.get("count", "5")
        style = preferences.get("style", "engaging")
        
        # ✅ FIXED: Safe integer conversion
        try:
            post_count = int(post_count_str) if post_count_str.isdigit() else 5
        except (ValueError, AttributeError):
            post_count = 5
        
        post_count = max(3, min(20, post_count))
        
        logger.info(f"📊 Social posts params: platform={platform}, count={post_count}, style={style}")
        
        # Generate template posts (simpler and more reliable)
        posts = self._generate_template_social_posts(
            key_messages, emotional_triggers, opportunities,
            platform, post_count, style
        )
        
        return {
            "content_type": "social_posts",
            "title": f"{post_count} {platform.title()} Posts from Competitive Intelligence",
            "content": posts,
            "metadata": {
                "post_count": len(posts),
                "platform": platform,
                "style": style,
                "avg_length": sum(len(post.get("text", "")) for post in posts) // len(posts) if posts else 0,
                "generated_by": "template"
            },
            "usage_tips": [
                "Post at optimal times for your audience",
                "Engage with comments and replies",
                "Track hashtag performance",
                "Repurpose top-performing posts"
            ]
        }
    
    def _generate_template_social_posts(
        self, key_messages, emotional_triggers, opportunities, 
        platform, post_count, style
    ) -> List[Dict[str, Any]]:
        """Generate template social media posts"""
        
        triggers = emotional_triggers[:3] if emotional_triggers else ["proven", "effective", "simple"]
        messages = key_messages[:3] if key_messages else ["Transform your results", "Achieve success", "Get started today"]
        
        template_posts = [
            {
                "text": f"Discover how {triggers[0] if triggers else 'proven'} strategies help you achieve amazing results! 🚀",
                "hashtags": ["#success", "#growth", "#results"],
                "type": "motivational",
                "platform": platform
            },
            {
                "text": f"The secret to {triggers[1] if len(triggers) > 1 else 'effective'} results? Understanding what actually works. 💡",
                "hashtags": ["#tips", "#strategy", "#insight"],
                "type": "educational",
                "platform": platform
            },
            {
                "text": f"Why choose our approach? Because {triggers[2] if len(triggers) > 2 else 'simple'} methods get real results! ✅",
                "hashtags": ["#proof", "#testimonials", "#success"],
                "type": "social_proof",
                "platform": platform
            },
            {
                "text": f"Ready to transform your approach? Here's what {messages[0] if messages else 'success'} looks like... 🎯",
                "hashtags": ["#transformation", "#results", "#action"],
                "type": "call_to_action",
                "platform": platform
            },
            {
                "text": f"The difference between success and struggle? Having the right {triggers[0] if triggers else 'proven'} strategy. 💪",
                "hashtags": ["#strategy", "#mindset", "#success"],
                "type": "inspirational",
                "platform": platform
            }
        ]
        
        # Extend if needed
        while len(template_posts) < post_count:
            template_posts.append({
                "text": f"Continue your journey to success with {triggers[0] if triggers else 'proven'} methods that work!",
                "hashtags": ["#success", "#journey", "#growth"],
                "type": "general",
                "platform": platform
            })
        
        return template_posts[:post_count]
    
    async def _generate_ad_copy(
        self, 
        intelligence: Dict[str, Any], 
        preferences: Dict[str, str]
    ) -> Dict[str, Any]:
        """Generate ad copy from intelligence"""
        
        logger.info("📢 Generating ad copy")
        
        return {
            "content_type": "ad_copy",
            "title": "Ad Copy Variations from Intelligence",
            "content": {
                "headlines": [
                    "Transform Your Results Today",
                    "Get the Competitive Edge",
                    "Proven Strategies That Work"
                ],
                "primary_text": [
                    "Discover the strategies your competitors don't want you to know",
                    "Join thousands who've transformed their results",
                    "Get started with proven methods today"
                ],
                "descriptions": [
                    "Learn more about our proven approach",
                    "Start your transformation journey today"
                ],
                "call_to_actions": ["Learn More", "Get Started", "Sign Up Now"]
            },
            "metadata": {
                "platform": preferences.get("platform", "facebook"),
                "objective": preferences.get("objective", "conversions"),
                "generated_by": "template"
            },
            "usage_tips": [
                "A/B test different headline variations",
                "Monitor cost per acquisition",
                "Test different audience segments"
            ]
        }
    
    async def _generate_blog_post(
        self, 
        intelligence: Dict[str, Any], 
        preferences: Dict[str, str]
    ) -> Dict[str, Any]:
        """Generate blog post from intelligence"""
        
        logger.info("📝 Generating blog post")
        
        topic = preferences.get("topic", "industry insights")
        
        return {
            "content_type": "blog_post",
            "title": f"Blog Post: {topic}",
            "content": {
                "headline": f"Key {topic.title()} You Need to Know",
                "introduction": f"Based on our competitive analysis, here are the key trends and opportunities in {topic}.",
                "body": f"Our research reveals important insights about {topic} that can transform your approach...",
                "conclusion": "These insights provide a roadmap for success in today's competitive landscape.",
                "sections": [
                    {"title": "Key Insights", "content": f"Important developments in {topic}..."},
                    {"title": "Opportunities", "content": f"Market gaps and opportunities in {topic}..."},
                    {"title": "Action Steps", "content": f"How to implement these {topic} insights..."}
                ]
            },
            "metadata": {
                "topic": topic,
                "word_count": 500,
                "generated_by": "template"
            },
            "usage_tips": [
                "Add relevant images and charts",
                "Include internal and external links",
                "Promote on social media"
            ]
        }
    
    async def _generate_landing_page(
        self, 
        intelligence: Dict[str, Any], 
        preferences: Dict[str, str]
    ) -> Dict[str, Any]:
        """Generate landing page copy from intelligence"""
        
        logger.info("🎯 Generating landing page")
        
        return {
            "content_type": "landing_page",
            "title": "High-Converting Landing Page",
            "content": {
                "headline": "Transform Your Business Today",
                "subheadline": "Join thousands who have already succeeded",
                "sections": [
                    "Hero Section with compelling value proposition",
                    "Benefits section highlighting key advantages",
                    "Social proof with testimonials and success stories",
                    "Call-to-action with clear next steps"
                ],
                "cta_count": 3
            },
            "metadata": {
                "goal": preferences.get("goal", "lead_generation"),
                "generated_by": "template"
            },
            "usage_tips": [
                "A/B test different headlines",
                "Monitor conversion rates",
                "Optimize page load speed"
            ]
        }
    
    async def _generate_product_description(self, intelligence: Dict[str, Any], preferences: Dict[str, str]) -> Dict[str, Any]:
        """Generate product description from intelligence"""
        
        logger.info("🛍️ Generating product description")
        
        return {
            "content_type": "product_description",
            "title": "Product Description",
            "content": {
                "description": "High-quality product description based on competitive intelligence and market insights.",
                "key_benefits": ["Proven results", "Easy to use", "Professional quality"],
                "features": ["Feature 1", "Feature 2", "Feature 3"]
            },
            "metadata": {"generated_by": "template"},
            "usage_tips": ["Customize for your brand", "Add specific details", "Include customer reviews"]
        }
    
    async def _generate_video_script(self, intelligence: Dict[str, Any], preferences: Dict[str, str]) -> Dict[str, Any]:
        """Generate video script from intelligence"""
        
        logger.info("🎥 Generating video script")
        
        return {
            "content_type": "video_script",
            "title": "Video Script",
            "content": {
                "script": "Engaging video script based on competitive intelligence and proven storytelling techniques.",
                "duration": preferences.get("duration", "3-5 minutes"),
                "style": preferences.get("style", "educational")
            },
            "metadata": {"generated_by": "template"},
            "usage_tips": ["Practice delivery", "Add visual cues", "Include captions"]
        }
    
    async def _generate_sales_page(self, intelligence: Dict[str, Any], preferences: Dict[str, str]) -> Dict[str, Any]:
        """Generate sales page from intelligence"""
        
        logger.info("💰 Generating sales page")
        
        return {
            "content_type": "sales_page",
            "title": "Sales Page",
            "content": {
                "headline": "Transform Your Results with Proven Strategies",
                "sections": [
                    "Problem identification and agitation",
                    "Solution presentation with benefits",
                    "Social proof and testimonials",
                    "Urgency and call-to-action"
                ]
            },
            "metadata": {"generated_by": "template"},
            "usage_tips": ["Test different headlines", "Monitor conversions", "Add exit-intent popups"]
        }
    
    def _parse_email_sequence_response(self, ai_response: str, sequence_length: int) -> List[Dict[str, str]]:
        """Parse AI response into email sequence format"""
        
        try:
            # Try to parse JSON response
            if '{' in ai_response and 'emails' in ai_response:
                import re
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    parsed_data = json.loads(json_match.group())
                    emails = parsed_data.get("emails", [])
                    if emails:
                        return emails[:sequence_length]
            
            # Fallback: return template emails
            return self._generate_fallback_emails(sequence_length)
            
        except Exception as e:
            logger.error(f"Failed to parse email sequence: {str(e)}")
            return self._generate_fallback_emails(sequence_length)
    
    def _generate_fallback_emails(self, count: int) -> List[Dict[str, str]]:
        """Generate fallback email sequence"""
        
        fallback_emails = [
            {
                "email_number": 1,
                "subject": "Welcome! Here's what you need to know...",
                "body": "Thank you for your interest. Let me share some valuable insights with you...",
                "send_delay": "Day 1"
            },
            {
                "email_number": 2,
                "subject": "The #1 mistake most people make",
                "body": "I've noticed a common pattern that prevents success. Here's how to avoid it...",
                "send_delay": "Day 3"
            },
            {
                "email_number": 3,
                "subject": "Here's proof it actually works",
                "body": "I want to share a success story that demonstrates the power of this approach...",
                "send_delay": "Day 5"
            },
            {
                "email_number": 4,
                "subject": "What's holding you back?",
                "body": "Let's address the common concerns and objections people have...",
                "send_delay": "Day 7"
            },
            {
                "email_number": 5,
                "subject": "Last chance to transform your results",
                "body": "This is your final opportunity to take action and see real change...",
                "send_delay": "Day 10"
            }
        ]
        
        # Extend if needed
        while len(fallback_emails) < count:
            fallback_emails.append({
                "email_number": len(fallback_emails) + 1,
                "subject": f"Follow-up Email #{len(fallback_emails) + 1}",
                "body": "Continue building relationship and providing value...",
                "send_delay": f"Day {(len(fallback_emails) + 1) * 2 + 1}"
            })
        
        return fallback_emails[:count]
    
    def _predict_performance(
        self, 
        content_result: Dict[str, Any], 
        intelligence: Dict[str, Any], 
        content_type: str
    ) -> Dict[str, Any]:
        """Predict content performance based on intelligence"""
        
        confidence_score = intelligence.get("confidence_score", 0.5)
        
        return {
            "estimated_engagement": "Medium to High" if confidence_score > 0.7 else "Medium",
            "conversion_potential": "Good" if confidence_score > 0.6 else "Fair",
            "optimization_suggestions": [
                "A/B test different variations",
                "Monitor performance metrics",
                "Optimize based on results"
            ],
            "confidence_level": "High" if confidence_score > 0.8 else "Medium"
        }
    
    def _generate_fallback_content(self, content_type: str, error_msg: str) -> Dict[str, Any]:
        """Generate fallback content when everything else fails"""
        
        logger.warning(f"⚠️ Generating fallback content for {content_type}: {error_msg}")
        
        return {
            "title": f"Template {content_type.replace('_', ' ').title()}",
            "content": f"Template-based {content_type} content. Error: {error_msg}",
            "metadata": {
                "generated_by": "fallback",
                "content_type": content_type,
                "generated_at": datetime.utcnow().isoformat(),
                "error": error_msg
            },
            "usage_tips": [
                "Check server logs for detailed error information",
                "Verify all dependencies are installed",
                "Try again with different preferences"
            ],
            "performance_predictions": {
                "estimated_engagement": "N/A",
                "conversion_potential": "N/A"
            }
        }


class CampaignAngleGenerator:
    """Generate campaign angles from intelligence data"""
    
    def __init__(self):
        # ✅ FIXED: Safe initialization with error handling
        try:
            import openai
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = openai.AsyncOpenAI(api_key=api_key)
                self.ai_available = True
            else:
                self.openai_client = None
                self.ai_available = False
        except Exception as e:
            self.openai_client = None
            self.ai_available = False
            logger.error(f"❌ CampaignAngleGenerator initialization failed: {str(e)}")
    
    async def generate_angles(
        self,
        intelligence_sources: List[Any],
        target_audience: Optional[str] = None,
        industry: Optional[str] = None,
        tone_preferences: Optional[List[str]] = None,
        unique_value_props: Optional[List[str]] = None,
        avoid_angles: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate campaign angles from intelligence sources"""
        
        logger.info("🎯 Generating campaign angles")
        
        # ✅ FIXED: Safe parameter handling
        target_audience = target_audience or "business professionals"
        industry = industry or "general business"
        tone_preferences = tone_preferences or ["professional", "authoritative"]
        unique_value_props = unique_value_props or ["proven results", "expert guidance"]
        avoid_angles = avoid_angles or ["price competition"]
        
        try:
            if self.ai_available and self.openai_client:
                return await self._generate_ai_angles(
                    intelligence_sources, target_audience, industry, 
                    tone_preferences, unique_value_props, avoid_angles
                )
            else:
                return self._generate_template_angles(
                    target_audience, industry, tone_preferences, unique_value_props
                )
        except Exception as e:
            logger.error(f"❌ Campaign angle generation failed: {str(e)}")
            return self._generate_template_angles(
                target_audience, industry, tone_preferences, unique_value_props
            )
    
    async def _generate_ai_angles(
        self, intelligence_sources, target_audience, industry,
        tone_preferences, unique_value_props, avoid_angles
    ) -> Dict[str, Any]:
        """Generate angles using AI"""
        
        prompt = f"""
        Generate unique campaign angles for a {industry} business targeting {target_audience}.
        
        Context:
        - Target Audience: {target_audience}
        - Industry: {industry}
        - Tone Preferences: {tone_preferences}
        - Unique Value Props: {unique_value_props}
        - Avoid These Angles: {avoid_angles}
        
        Create 1 primary angle and 3 alternative angles that are compelling and unique.
        Focus on differentiation and avoid direct competition.
        
        Return as JSON with primary_angle and alternative_angles arrays.
        """
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert campaign strategist. Return only valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        ai_response = response.choices[0].message.content
        
        try:
            import re
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                return self._format_angle_response(parsed, target_audience, industry)
        except:
            pass
        
        # Fallback if parsing fails
        return self._generate_template_angles(target_audience, industry, tone_preferences, unique_value_props)
    
    def _generate_template_angles(
        self, target_audience: str, industry: str, 
        tone_preferences: List[str], unique_value_props: List[str]
    ) -> Dict[str, Any]:
        """Generate template campaign angles"""
        
        return {
            "primary_angle": {
                "angle": f"The strategic intelligence advantage for {target_audience}",
                "reasoning": "Positions as insider knowledge with competitive edge",
                "target_audience": target_audience,
                "key_messages": [
                    "Exclusive strategic insights",
                    "Proven competitive advantages",
                    "Actionable intelligence for immediate results",
                    "Clear roadmap from analysis to success"
                ],
                "differentiation_points": [
                    "Intelligence-driven methodology vs gut-feeling approaches",
                    "Proven systematic approach vs trial-and-error methods",
                    "Data-driven insights vs common knowledge",
                    "Competitive analysis expertise vs generic consulting"
                ]
            },
            "alternative_angles": [
                {
                    "angle": f"From struggling in {industry} to leading with insider knowledge",
                    "reasoning": "Empowerment narrative transforming challenge into advantage",
                    "strength_score": 0.85,
                    "use_case": f"{target_audience} competing against larger competitors"
                },
                {
                    "angle": "Why 90% of competitive analysis fails (and the 10% that transforms businesses)",
                    "reasoning": "Statistical exclusivity creating urgency and positioning as rare solution",
                    "strength_score": 0.82,
                    "use_case": "Data-driven decision makers and analytical professionals"
                },
                {
                    "angle": f"The ethical competitive edge that builds sustainable {industry} dominance",
                    "reasoning": "Focus on ethical advantage and long-term sustainability",
                    "strength_score": 0.80,
                    "use_case": "Ethical businesses focused on sustainable growth"
                }
            ],
            "positioning_strategy": {
                "market_position": f"Premium strategic intelligence partner for {industry}",
                "competitive_advantage": "Comprehensive intelligence-driven approach with proven methodology",
                "value_proposition": f"Transform {industry} performance through competitive intelligence and strategic insights",
                "messaging_framework": [
                    "Problem identification: Current competitive disadvantages",
                    "Solution demonstration: Intelligence-driven approach with proof",
                    "Unique methodology: Systematic analysis and implementation",
                    "Results showcase: Documented success stories and outcomes",
                    "Implementation guidance: Clear action steps and support",
                    "Future vision: Long-term competitive advantage and leadership"
                ]
            },
            "implementation_guide": {
                "content_priorities": [
                    "Case study development showcasing transformation results",
                    "Authority building through proprietary industry insights",
                    "Social proof collection and strategic presentation",
                    "Educational content demonstrating methodology",
                    "Thought leadership positioning in competitive intelligence"
                ],
                "channel_recommendations": [
                    "LinkedIn for B2B professional targeting",
                    "Email nurture sequences for relationship building",
                    "Content marketing for authority establishment",
                    "Webinars for methodology demonstration",
                    "Strategic partnerships with complementary providers"
                ],
                "testing_suggestions": [
                    "A/B test different angle variations in headlines",
                    "Test social proof elements and case studies",
                    "Optimize call-to-action messaging variations",
                    "Test different value proposition presentations",
                    "Experiment with urgency vs authority positioning"
                ]
            }
        }
    
    def _format_angle_response(
        self, parsed_data: Dict[str, Any], target_audience: str, industry: str
    ) -> Dict[str, Any]:
        """Format AI response into standard angle structure"""
        
        return {
            "primary_angle": {
                "angle": parsed_data.get("primary_angle", {}).get("angle", f"Strategic advantage for {target_audience}"),
                "reasoning": parsed_data.get("primary_angle", {}).get("reasoning", "Creates competitive advantage"),
                "target_audience": target_audience,
                "key_messages": parsed_data.get("primary_angle", {}).get("key_messages", [
                    "Strategic insights", "Competitive advantage", "Proven results"
                ]),
                "differentiation_points": parsed_data.get("primary_angle", {}).get("differentiation_points", [
                    "Data-driven approach", "Proven methodology", "Expert guidance"
                ])
            },
            "alternative_angles": parsed_data.get("alternative_angles", [
                {
                    "angle": f"Transform your {industry} approach with proven intelligence",
                    "reasoning": "Focus on transformation and proven results",
                    "strength_score": 0.8,
                    "use_case": f"{target_audience} seeking competitive advantage"
                }
            ]),
            "positioning_strategy": {
                "market_position": f"Premium strategic intelligence partner for {industry}",
                "competitive_advantage": "Intelligence-driven methodology with proven results",
                "value_proposition": f"Transform {industry} performance through strategic insights",
                "messaging_framework": [
                    "Problem identification", "Solution demonstration", 
                    "Methodology explanation", "Results showcase", "Action steps"
                ]
            },
            "implementation_guide": {
                "content_priorities": [
                    "Case studies and success stories",
                    "Authority building content",
                    "Educational methodology content",
                    "Social proof and testimonials"
                ],
                "channel_recommendations": [
                    "LinkedIn for professional targeting",
                    "Email marketing for nurture",
                    "Content marketing for authority",
                    "Webinars for engagement"
                ],
                "testing_suggestions": [
                    "A/B test messaging variations",
                    "Test different audience segments",
                    "Optimize conversion elements",
                    "Test social proof presentations"
                ]
            }
        }