# src/intelligence/generators.py - AFFILIATE INTELLIGENCE-DRIVEN VERSION
"""
Content generation from intelligence - Transform competitive analysis into affiliate/creator marketing materials
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
    """Generate marketing content from intelligence data - AFFILIATE/CREATOR FOCUSED"""
    
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
        
        # Content type generators - AFFILIATE/CREATOR FOCUSED
        self.generators = {
            "email_sequence": self._generate_affiliate_email_sequence,
            "social_posts": self._generate_social_posts,
            "ad_copy": self._generate_ad_copy,
            "blog_post": self._generate_blog_post,
            "landing_page": self._generate_landing_page,
            "product_description": self._generate_product_description,
            "video_script": self._generate_video_script,
            "sales_page": self._generate_sales_page,
            # NEW CREATOR-SPECIFIC CONTENT TYPES
            "lead_magnets": self._generate_lead_magnet,
            "sales_pages": self._generate_creator_sales_page,
            "webinar_content": self._generate_webinar_content,
            "onboarding_sequences": self._generate_onboarding_sequence
        }
    
    async def generate_content(
        self, 
        intelligence_data: Dict[str, Any], 
        content_type: str, 
        preferences: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        """Generate specific content type using intelligence - AFFILIATE/CREATOR FOCUSED"""
        
        logger.info(f"🎯 Starting AFFILIATE/CREATOR content generation: {content_type}")
        
        # ✅ STEP 1: AFFILIATE/CREATOR INTELLIGENCE DEBUG
        logger.info(f"🔍 AFFILIATE/CREATOR INTELLIGENCE DEBUG:")
        
        # Extract intelligence data safely
        psych_intel = intelligence_data.get("psychology_intelligence", {})
        offer_intel = intelligence_data.get("offer_intelligence", {})
        content_intel = intelligence_data.get("content_intelligence", {})
        comp_intel = intelligence_data.get("competitive_intelligence", {})
        brand_intel = intelligence_data.get("brand_intelligence", {})
        
        # Debug what we're finding for affiliate/creator content
        emotional_triggers = psych_intel.get("emotional_triggers", [])
        pain_points = psych_intel.get("pain_points", [])
        benefits = offer_intel.get("value_propositions", []) or offer_intel.get("products", [])
        opportunities = comp_intel.get("opportunities", [])
        gaps = comp_intel.get("gaps", [])
        
        logger.info(f"- Competitor promotional angles: {emotional_triggers}")
        logger.info(f"- Affiliate marketing pain points: {pain_points}")
        logger.info(f"- Product benefits for promotion: {benefits}")
        logger.info(f"- Competitive opportunities: {opportunities}")
        logger.info(f"- Market gaps to exploit: {gaps}")
        
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
            
            logger.info(f"✅ AFFILIATE/CREATOR content generation completed: {content_type}")
            return content_result
            
        except Exception as e:
            logger.error(f"❌ Content generation failed for {content_type}: {str(e)}")
            import traceback
            logger.error(f"📍 Traceback: {traceback.format_exc()}")
            return self._generate_fallback_content(content_type, str(e))
    
    async def _generate_affiliate_email_sequence(
        self, 
        intelligence: Dict[str, Any], 
        preferences: Dict[str, str]
    ) -> Dict[str, Any]:
        """🚀 AFFILIATE PRODUCT PROMOTION EMAIL GENERATION - Intelligence-Driven"""
        
        logger.info("📧 Generating AFFILIATE PRODUCT PROMOTION email sequence")
        
        # Extract intelligence for affiliate email generation
        psych_intel = intelligence.get("psychology_intelligence", {})
        offer_intel = intelligence.get("offer_intelligence", {})
        content_intel = intelligence.get("content_intelligence", {})
        comp_intel = intelligence.get("competitive_intelligence", {})
        
        pain_points = psych_intel.get("pain_points", [])
        benefits = offer_intel.get("products", []) or offer_intel.get("value_propositions", [])
        emotional_triggers = psych_intel.get("emotional_triggers", [])
        success_stories = content_intel.get("success_stories", [])
        opportunities = comp_intel.get("opportunities", [])
        gaps = comp_intel.get("gaps", [])
        
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
        
        logger.info(f"📊 AFFILIATE Email sequence params: length={sequence_length}, tone={tone}, audience={target_audience}")
        
        if self.ai_available and self.openai_client:
            try:
                return await self._generate_ai_affiliate_email_sequence(
                    pain_points, benefits, emotional_triggers, success_stories,
                    opportunities, gaps, tone, sequence_length, target_audience
                )
            except Exception as e:
                logger.error(f"❌ AI affiliate email generation failed: {str(e)}")
                return self._generate_template_affiliate_email_sequence(sequence_length, tone, target_audience)
        else:
            return self._generate_template_affiliate_email_sequence(sequence_length, tone, target_audience)
    
    async def _generate_ai_affiliate_email_sequence(
        self, pain_points, benefits, emotional_triggers, success_stories,
        opportunities, gaps, tone, sequence_length, target_audience
    ) -> Dict[str, Any]:
        """🎯 Generate AFFILIATE PROMOTION email sequence using OpenAI with competitive intelligence"""
        
        # Build affiliate promotion intelligence context
        affiliate_promotion_intelligence = {
            "product_being_promoted": self._extract_product_details(benefits),
            "competitor_affiliate_patterns": self._analyze_affiliate_competition(emotional_triggers, pain_points),
            "overused_affiliate_cliches": self._extract_affiliate_cliches(pain_points + benefits),
            "unique_product_angles": self._find_underemphasized_benefits(benefits, emotional_triggers)
        }
        
        # Create affiliate differentiation strategy
        affiliate_opportunities = {
            "unique_promotional_angles": self._find_fresh_promotional_approaches(opportunities),
            "underemphasized_benefits": self._identify_missed_product_benefits(benefits),
            "audience_segments_missed": self._find_untargeted_audiences(gaps),
            "authentic_story_angles": self._discover_genuine_story_opportunities(success_stories)
        }
        
        # AFFILIATE PROMOTION-SPECIFIC INTELLIGENCE-RICH PROMPT
        prompt = f"""
        AFFILIATE PRODUCT PROMOTION INTELLIGENCE:

        PRODUCT BEING PROMOTED FOR COMMISSION:
        - Product name: {affiliate_promotion_intelligence['product_being_promoted']['name']}
        - Main benefits: {affiliate_promotion_intelligence['product_being_promoted']['benefits']}
        - Target audience: {affiliate_promotion_intelligence['product_being_promoted']['audience']}
        - Transformation promised: {affiliate_promotion_intelligence['product_being_promoted']['transformation']}

        COMPETITOR AFFILIATE PATTERNS TO AVOID:
        - Overused affiliate phrases: {affiliate_promotion_intelligence['overused_affiliate_cliches']}
        - Common promotional angles: {affiliate_promotion_intelligence['competitor_affiliate_patterns']}
        - Generic affiliate approaches: ["amazing product", "changed my life", "limited time bonus"]

        UNIQUE PROMOTIONAL OPPORTUNITIES FOR THIS AFFILIATE:
        - Product benefits other affiliates don't emphasize: {affiliate_opportunities['underemphasized_benefits']}
        - Audience segments other affiliates miss: {affiliate_opportunities['audience_segments_missed']}
        - Authentic story angles: {affiliate_opportunities['authentic_story_angles']}
        - Fresh promotional approaches: {affiliate_opportunities['unique_promotional_angles']}

        TASK: Create {sequence_length} affiliate promotion emails that will help earn commissions by:
        1. PROMOTING the product effectively to drive affiliate sales
        2. AVOIDING typical affiliate marketing spam and clichés  
        3. HIGHLIGHTING product benefits that other affiliates aren't emphasizing
        4. ADDRESSING audience segments that competitors ignore
        5. BUILDING authentic relationships vs transactional promotion
        6. PROVIDING genuine value that leads naturally to the product
        7. STANDING OUT from the 100+ other affiliates promoting the same product

        AFFILIATE PROMOTION FOCUS: Educational content that builds trust and leads to affiliate commissions
        TONE: {tone} but authentic and relationship-focused, not sales-y
        COMPLIANCE: Include proper affiliate disclosures and build genuine trust

        Make each email help the affiliate earn commissions by standing out from other promoters of the same product.

        Return as JSON with this exact structure:
        {{
          "sequence_title": "Affiliate Email Sequence Title",
          "emails": [
            {{
              "email_number": 1,
              "subject": "Subject line here",
              "body": "Email body content here",
              "send_delay": "Day 1",
              "affiliate_focus": "What this email does for affiliate success"
            }}
          ]
        }}
        """
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert affiliate marketing strategist. Create email sequences that help affiliates earn commissions by standing out from competitors. Return only valid JSON format with the exact structure requested."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        ai_response = response.choices[0].message.content
        
        # Parse response into structured format
        emails = self._parse_email_sequence_response(ai_response, sequence_length)
        
        return {
            "content_type": "email_sequence",
            "title": f"{sequence_length}-Email AFFILIATE PROMOTION Sequence from Competitive Intelligence",
            "content": {
                "sequence_title": f"{sequence_length}-Email Affiliate Marketing Sequence",
                "emails": emails,
                "affiliate_focus": "Intelligence-driven affiliate promotion that avoids common clichés"
            },
            "metadata": {
                "sequence_length": len(emails),
                "total_words": sum(len(email.get("body", "").split()) for email in emails),
                "intelligence_sources": 1,
                "tone": tone,
                "target_audience": target_audience,
                "generated_by": "affiliate_intelligence",
                "unique_angles_used": len(affiliate_opportunities.get("unique_promotional_angles", [])),
                "competitor_patterns_avoided": len(affiliate_promotion_intelligence.get("overused_affiliate_cliches", []))
            },
            "usage_tips": [
                "Add proper affiliate disclosures to each email",
                "Track which angles perform best for commissions", 
                "Test subject lines with A/B testing",
                "Monitor open rates and click-through to affiliate links",
                "Build relationship first, promote second"
            ],
            "affiliate_intelligence": {
                "differentiation_strategy": affiliate_opportunities,
                "avoided_cliches": affiliate_promotion_intelligence["overused_affiliate_cliches"],
                "unique_positioning": affiliate_opportunities["unique_promotional_angles"]
            }
        }
    
    def _extract_product_details(self, benefits: List[str]) -> Dict[str, str]:
        """Extract product details for affiliate promotion"""
        return {
            "name": benefits[0] if benefits else "Product",
            "benefits": ", ".join(benefits[:3]),
            "audience": "people seeking results",
            "transformation": "improved outcomes"
        }
    
    def _analyze_affiliate_competition(self, triggers: List[str], pain_points: List[str]) -> List[str]:
        """Analyze what other affiliates are doing"""
        common_patterns = []
        if triggers:
            common_patterns.extend([f"Overusing '{trigger}' trigger" for trigger in triggers[:3]])
        if pain_points:
            common_patterns.extend([f"Generic pain point: '{pain}'" for pain in pain_points[:2]])
        return common_patterns or ["Standard affiliate promotional approaches"]
    
    def _extract_affiliate_cliches(self, content_items: List[str]) -> List[str]:
        """Extract overused affiliate marketing clichés to avoid"""
        cliches = [
            "amazing product", "changed my life", "limited time bonus",
            "exclusive deal", "must-have", "incredible results",
            "secret formula", "breakthrough system"
        ]
        found_cliches = []
        content_text = " ".join(content_items).lower()
        for cliche in cliches:
            if cliche in content_text:
                found_cliches.append(cliche)
        return found_cliches or ["typical affiliate marketing language"]
    
    def _find_underemphasized_benefits(self, benefits: List[str], triggers: List[str]) -> List[str]:
        """Find product benefits that aren't being emphasized by other affiliates"""
        if not benefits:
            return ["unique value proposition", "specific outcome"]
        
        # Return benefits that seem less emphasized
        return benefits[:3] if len(benefits) > 3 else benefits
    
    def _find_fresh_promotional_approaches(self, opportunities: List[str]) -> List[str]:
        """Find fresh promotional approaches from competitive opportunities"""
        fresh_approaches = [
            "Educational content approach",
            "Problem-solving focus", 
            "Story-driven promotion",
            "Value-first strategy"
        ]
        
        if opportunities:
            fresh_approaches.extend([f"Opportunity: {opp}" for opp in opportunities[:2]])
        
        return fresh_approaches
    
    def _identify_missed_product_benefits(self, benefits: List[str]) -> List[str]:
        """Identify product benefits being missed by other affiliates"""
        if not benefits:
            return ["secondary benefits", "long-term value"]
        return benefits[1:4] if len(benefits) > 1 else benefits  # Skip the obvious first benefit
    
    def _find_untargeted_audiences(self, gaps: List[str]) -> List[str]:
        """Find audience segments not being targeted by competitors"""
        if gaps:
            return [f"Untargeted: {gap}" for gap in gaps[:2]]
        return ["underserved segments", "niche audiences"]
    
    def _discover_genuine_story_opportunities(self, success_stories: List[str]) -> List[str]:
        """Discover authentic story angles for affiliate promotion"""
        if success_stories:
            return [f"Story angle: {story}" for story in success_stories[:2]]
        return ["personal experience angle", "customer success focus"]
    
    def _generate_template_affiliate_email_sequence(
        self, sequence_length: int, tone: str, target_audience: str
    ) -> Dict[str, Any]:
        """Generate template-based AFFILIATE email sequence with intelligence-driven improvements"""
        
        logger.info(f"📧 Generating template AFFILIATE email sequence: {sequence_length} emails")
        
        # AFFILIATE-FOCUSED EMAIL TEMPLATES (vs generic templates)
        template_emails = [
            {
                "email_number": 1,
                "subject": f"The honest truth about [product name] (affiliate disclosure inside)",
                "body": f"Hi there,\n\nI wanted to share my honest thoughts about a product I've been testing.\n\nFull disclosure: I'm an affiliate, which means I earn a commission if you decide to purchase. But I only recommend products I truly believe in.\n\nHere's what makes this different from the typical recommendations you see...\n\nBest,\n[Your name]",
                "send_delay": "Day 1",
                "affiliate_focus": "Builds trust with transparency and authentic review approach"
            },
            {
                "email_number": 2,
                "subject": "Why I almost didn't promote this...",
                "body": f"Yesterday I told you about [product]. Today I want to share why I almost didn't become an affiliate.\n\nMost {target_audience} get bombarded with the same promises. I was skeptical too.\n\nBut here's what changed my mind...\n\n[Specific results or benefits that stood out]\n\nThis isn't about hype. It's about what actually works.",
                "send_delay": "Day 3",
                "affiliate_focus": "Overcoming objections while building credibility through honesty"
            },
            {
                "email_number": 3,
                "subject": "The results nobody else is talking about",
                "body": f"Here's what other affiliates aren't telling you about [product]...\n\nEveryone focuses on [obvious benefit]. But the real value I discovered was [secondary benefit].\n\nThis is especially important if you're [specific audience segment] because [specific reason].\n\nLet me explain why this matters...",
                "send_delay": "Day 5",
                "affiliate_focus": "Differentiation by highlighting benefits others ignore"
            },
            {
                "email_number": 4,
                "subject": "My biggest concern (and why I recommend it anyway)",
                "body": f"I'll be honest - [product] isn't perfect.\n\nMy biggest concern was [realistic limitation]. And if you're [specific situation], it might not be right for you.\n\nBut for {target_audience} who [specific criteria], here's why the benefits outweigh the drawbacks...\n\n[Balanced perspective with genuine recommendation]",
                "send_delay": "Day 7",
                "affiliate_focus": "Building trust through balanced, honest assessment"
            },
            {
                "email_number": 5,
                "subject": "Final thoughts + your next step",
                "body": f"Over the past week, I've shared my honest experience with [product].\n\nHere's my bottom line: if you're {target_audience} looking for [specific outcome], this is worth considering.\n\nI've arranged a special link that [specific benefit or bonus].\n\nRemember: I earn a commission, but your success is what matters most.\n\n[Affiliate link with disclosure]\n\nQuestions? Just reply - I'm here to help.",
                "send_delay": "Day 10",
                "affiliate_focus": "Soft sell with clear value proposition and support offer"
            }
        ]
        
        # Extend or trim to match requested length
        while len(template_emails) < sequence_length:
            template_emails.append({
                "email_number": len(template_emails) + 1,
                "subject": f"Follow-up: More insights about [product]",
                "body": f"I wanted to share another insight about [product] that might help your decision...\n\n[Additional value or perspective]",
                "send_delay": f"Day {(len(template_emails) + 1) * 2 + 1}",
                "affiliate_focus": "Continued value and relationship building"
            })
        
        emails = template_emails[:sequence_length]
        
        return {
            "content_type": "email_sequence",
            "title": f"{sequence_length}-Email AFFILIATE PROMOTION Sequence (Intelligence-Enhanced Template)",
            "content": {
                "sequence_title": f"{sequence_length}-Email Affiliate Marketing Sequence", 
                "emails": emails,
                "affiliate_focus": "Relationship-focused affiliate promotion that builds trust"
            },
            "metadata": {
                "sequence_length": len(emails),
                "total_words": sum(len(email.get("body", "").split()) for email in emails),
                "tone": tone,
                "target_audience": target_audience,
                "generated_by": "affiliate_template",
                "differentiation_strategy": "Honest, relationship-focused approach vs typical affiliate spam"
            },
            "usage_tips": [
                "Replace [product name] with actual product being promoted",
                "Add proper FTC-compliant affiliate disclosures",
                "Customize the specific benefits and audience segments",
                "Test different subject lines for your audience",
                "Track which emails drive the most affiliate commissions"
            ],
            "affiliate_intelligence": {
                "differentiation_strategy": ["Transparency-first approach", "Balanced honest reviews", "Secondary benefit focus"],
                "avoided_cliches": ["Limited time offers", "Amazing/incredible language", "Hype-driven promotion"],
                "unique_positioning": ["Honest affiliate who admits limitations", "Focus on specific audience segments", "Educational vs sales approach"]
            }
        }
    
    # NEW CREATOR-SPECIFIC CONTENT GENERATORS
    
    async def _generate_lead_magnet(
        self, 
        intelligence: Dict[str, Any], 
        preferences: Dict[str, str]
    ) -> Dict[str, Any]:
        """Generate lead magnets that fill competitor gaps for PRODUCT CREATORS"""
        
        logger.info("🧲 Generating CREATOR LEAD MAGNET")
        
        comp_intel = intelligence.get("competitive_intelligence", {})
        content_intel = intelligence.get("content_intelligence", {})
        
        competitor_gaps = comp_intel.get("gaps", [])
        opportunities = comp_intel.get("opportunities", [])
        key_messages = content_intel.get("key_messages", [])
        
        if self.ai_available and self.openai_client:
            prompt = f"""
            LEAD MAGNET INTELLIGENCE FOR PRODUCT CREATORS:
            
            COMPETITOR LEAD MAGNET GAPS ANALYSIS:
            - Market gaps identified: {competitor_gaps}
            - Opportunities competitors miss: {opportunities}
            - Key messages that resonate: {key_messages}
            
            TASK: Create a lead magnet concept that:
            1. ADDRESSES gaps competitors miss
            2. PROVIDES immediate actionable value
            3. POSITIONS the creator as unique expert
            4. LEADS naturally to the paid product
            5. STANDS OUT from typical lead magnets in this space
            
            Generate lead magnet concept, outline, and promotional copy that fills competitive gaps.
            """
            
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert at creating lead magnets for product creators that fill market gaps."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
                
                ai_content = response.choices[0].message.content
                
                return {
                    "content_type": "lead_magnet",
                    "title": "Lead Magnet That Fills Competitor Gaps",
                    "content": {
                        "concept": ai_content,
                        "gaps_addressed": competitor_gaps[:3],
                        "unique_positioning": opportunities[:2]
                    },
                    "metadata": {
                        "generated_by": "creator_intelligence",
                        "intelligence_used": "competitive_gap_analysis"
                    }
                }
                
            except Exception as e:
                logger.error(f"❌ AI lead magnet generation failed: {str(e)}")
        
        # Template fallback for creators
        return {
            "content_type": "lead_magnet",
            "title": "Lead Magnet Concept for Product Creators",
            "content": {
                "concept": "Create a valuable resource that addresses a gap your competitors aren't filling",
                "format_suggestions": ["Checklist", "Mini-course", "Template", "Assessment tool"],
                "gaps_addressed": competitor_gaps[:3] if competitor_gaps else ["Market education gap", "Implementation guidance gap"],
                "unique_positioning": "Focus on what competitors aren't providing"
            },
            "metadata": {
                "generated_by": "creator_template",
                "intelligence_used": "competitive_analysis"
            },
            "usage_tips": [
                "Make it immediately actionable",
                "Solve a specific problem competitors ignore",
                "Position yourself as the solution provider",
                "Create natural progression to paid product"
            ]
        }
    
    async def _generate_creator_sales_page(
        self, 
        intelligence: Dict[str, Any], 
        preferences: Dict[str, str]
    ) -> Dict[str, Any]:
        """Generate sales pages with unique positioning vs competitors for PRODUCT CREATORS"""
        
        logger.info("💰 Generating CREATOR SALES PAGE")
        
        comp_intel = intelligence.get("competitive_intelligence", {})
        offer_intel = intelligence.get("offer_intelligence", {})
        
        opportunities = comp_intel.get("opportunities", [])
        competitor_positioning = offer_intel.get("value_propositions", [])
        
        return {
            "content_type": "sales_page",
            "title": "Sales Page with Competitive Differentiation",
            "content": {
                "headline": "The Solution Competitors Don't Want You to Know About",
                "unique_positioning": opportunities[:3] if opportunities else ["Differentiated approach", "Unique methodology", "Exclusive insights"],
                "competitor_differentiation": f"Unlike competitors who focus on {', '.join(competitor_positioning[:2])}, we provide...",
                "sections": [
                    "Problem identification with unique angle",
                    "Solution presentation highlighting differentiation", 
                    "Competitive advantage explanation",
                    "Social proof and unique results",
                    "Clear call-to-action with unique value"
                ]
            },
            "metadata": {
                "generated_by": "creator_intelligence",
                "differentiation_focus": True
            },
            "usage_tips": [
                "Emphasize what competitors don't offer",
                "Lead with your unique approach",
                "Address gaps competitors leave unfilled",
                "Position as the better alternative"
            ]
        }
    
    async def _generate_webinar_content(
        self, 
        intelligence: Dict[str, Any], 
        preferences: Dict[str, str]
    ) -> Dict[str, Any]:
        """Generate webinar content for PRODUCT CREATORS"""
        
        logger.info("🎥 Generating CREATOR WEBINAR CONTENT")
        
        return {
            "content_type": "webinar_content",
            "title": "Educational Webinar That Sells",
            "content": {
                "webinar_title": "The Method Competitors Don't Teach",
                "outline": [
                    "Opening: What competitors get wrong",
                    "Education: Your unique methodology",
                    "Proof: Results competitors can't deliver",
                    "Offer: Your solution to the gap",
                    "Close: Why now is the time to act"
                ],
                "educational_focus": "Teaching valuable content while positioning your solution"
            },
            "metadata": {
                "generated_by": "creator_template",
                "format": "educational_webinar"
            },
            "usage_tips": [
                "Lead with education, not sales",
                "Show your unique approach",
                "Build authority through teaching",
                "Natural transition to your solution"
            ]
        }
    
    async def _generate_onboarding_sequence(
        self, 
        intelligence: Dict[str, Any], 
        preferences: Dict[str, str]
    ) -> Dict[str, Any]:
        """Generate customer onboarding sequences for PRODUCT CREATORS"""
        
        logger.info("🚀 Generating CREATOR ONBOARDING SEQUENCE")
        
        return {
            "content_type": "onboarding_sequence", 
            "title": "Customer Success Onboarding Sequence",
            "content": {
                "sequence_title": "Welcome to Your Success Journey",
                "steps": [
                    "Welcome and set expectations",
                    "Quick win implementation", 
                    "Foundation building",
                    "Advanced strategies",
                    "Community and support introduction"
                ],
                "focus": "Getting customers successful quickly to reduce churn"
            },
            "metadata": {
                "generated_by": "creator_template",
                "purpose": "customer_success"
            },
            "usage_tips": [
                "Focus on quick wins first",
                "Set clear expectations",
                "Build momentum with early success",
                "Provide clear next steps at each stage"
            ]
        }
    
    # Continue with existing methods but enhanced...
    
    async def _generate_social_posts(
        self, 
        intelligence: Dict[str, Any], 
        preferences: Dict[str, str]
    ) -> Dict[str, Any]:
        """Generate social media posts from intelligence - AFFILIATE/CREATOR FOCUSED"""
        
        logger.info("📱 Generating AFFILIATE/CREATOR social media posts")
        
        content_intel = intelligence.get("content_intelligence", {})
        psych_intel = intelligence.get("psychology_intelligence", {})
        comp_intel = intelligence.get("competitive_intelligence", {})
        
        key_messages = content_intel.get("key_messages", [])
        emotional_triggers = psych_intel.get("emotional_triggers", [])
        opportunities = comp_intel.get("opportunities", [])
        
        platform = preferences.get("platform", "general")
        post_count_str = preferences.get("count", "5")
        style = preferences.get("style", "engaging")
        user_type = preferences.get("user_type", "affiliate")  # affiliate or creator
        
        try:
            post_count = int(post_count_str) if post_count_str.isdigit() else 5
        except (ValueError, AttributeError):
            post_count = 5
        
        post_count = max(3, min(20, post_count))
        
        logger.info(f"📊 Social posts params: platform={platform}, count={post_count}, style={style}, user_type={user_type}")
        
        # Generate AFFILIATE vs CREATOR specific posts
        if user_type == "affiliate":
            posts = self._generate_affiliate_social_posts(
                key_messages, emotional_triggers, opportunities,
                platform, post_count, style
            )
        else:
            posts = self._generate_creator_social_posts(
                key_messages, emotional_triggers, opportunities,
                platform, post_count, style
            )
        
        return {
            "content_type": "social_posts",
            "title": f"{post_count} {platform.title()} Posts for {user_type.title()}s from Competitive Intelligence",
            "content": posts,
            "metadata": {
                "post_count": len(posts),
                "platform": platform,
                "style": style,
                "user_type": user_type,
                "avg_length": sum(len(post.get("text", "")) for post in posts) // len(posts) if posts else 0,
                "generated_by": f"{user_type}_intelligence"
            },
            "usage_tips": [
                f"Optimize posting times for {user_type} audience",
                "Engage authentically with comments and replies",
                "Track performance of different angles",
                f"Build trust as {user_type} through consistent value",
                "Use intelligence insights to differentiate from competitors"
            ]
        }
    
    def _generate_affiliate_social_posts(
        self, key_messages, emotional_triggers, opportunities, 
        platform, post_count, style
    ) -> List[Dict[str, Any]]:
        """Generate AFFILIATE-specific social media posts"""
        
        triggers = emotional_triggers[:3] if emotional_triggers else ["proven", "effective", "honest"]
        messages = key_messages[:3] if key_messages else ["Transform results", "Honest review", "Real experience"]
        opps = opportunities[:2] if opportunities else ["authentic approach", "detailed analysis"]
        
        affiliate_posts = [
            {
                "text": f"🔍 Honest review: I've been testing [product] for weeks. Here's what other affiliates won't tell you... {triggers[0] if triggers else 'results'} don't happen overnight. But here's what I actually experienced: 📊",
                "hashtags": ["#honestreviews", "#affiliate", "#realresults"],
                "type": "authentic_review",
                "platform": platform,
                "affiliate_focus": "Builds trust through honest, detailed review approach"
            },
            {
                "text": f"⚠️ Affiliate disclosure: I earn commissions from recommendations. That's WHY I'm so picky about what I promote. Most {triggers[1] if len(triggers) > 1 else 'products'} overpromise. This one delivers on {opps[0] if opps else 'real value'}.",
                "hashtags": ["#transparency", "#affiliatedisclosure", "#ethics"],
                "type": "transparency_building",
                "platform": platform,
                "affiliate_focus": "Builds credibility through upfront disclosure and selectivity"
            },
            {
                "text": f"💡 What competitors don't mention about [product]: {opps[0] if opps else 'the learning curve'}. Here's how I worked through it and why it matters for your success...",
                "hashtags": ["#realTalk", "#affiliate", "#education"],
                "type": "educational_value",
                "platform": platform,
                "affiliate_focus": "Provides genuine value while promoting product intelligently"
            },
            {
                "text": f"🤔 Been asked why I switched from promoting [competitor] to [product]. Simple: {triggers[2] if len(triggers) > 2 else 'better results'} for my audience. Here's the comparison nobody else is sharing:",
                "hashtags": ["#comparison", "#affiliate", "#honest"],
                "type": "competitive_differentiation",
                "platform": platform,
                "affiliate_focus": "Uses competitive intelligence to position product uniquely"
            },
            {
                "text": f"📈 3 months promoting [product] as affiliate: What I learned that no other promoter shares. The good, the challenging, and why I still recommend it for {messages[0] if messages else 'specific situations'}.",
                "hashtags": ["#affiliatejourney", "#longterm", "#results"],
                "type": "experience_sharing",
                "platform": platform,
                "affiliate_focus": "Long-term credibility building through ongoing experience sharing"
            }
        ]
        
        # Extend if needed
        while len(affiliate_posts) < post_count:
            affiliate_posts.append({
                "text": f"💭 Affiliate insight: Most promoters focus on {triggers[0] if triggers else 'features'}. I focus on {opps[0] if opps else 'real outcomes'} because that's what actually matters to you.",
                "hashtags": ["#affiliate", "#insights", "#value"],
                "type": "value_focused",
                "platform": platform,
                "affiliate_focus": "Continued differentiation and value provision"
            })
        
        return affiliate_posts[:post_count]
    
    def _generate_creator_social_posts(
        self, key_messages, emotional_triggers, opportunities,
        platform, post_count, style
    ) -> List[Dict[str, Any]]:
        """Generate CREATOR-specific social media posts"""
        
        triggers = emotional_triggers[:3] if emotional_triggers else ["innovative", "unique", "proven"]
        messages = key_messages[:3] if key_messages else ["Transform approach", "New methodology", "Better results"]
        opps = opportunities[:2] if opportunities else ["market gap", "unmet need"]
        
        creator_posts = [
            {
                "text": f"🚀 After analyzing 50+ competitors, I discovered they all miss this: {opps[0] if opps else 'implementation support'}. That's why I built [product] differently. Here's the approach nobody else teaches:",
                "hashtags": ["#innovation", "#creator", "#methodology"],
                "type": "competitive_differentiation",
                "platform": platform,
                "creator_focus": "Positions as innovator who solved what competitors missed"
            },
            {
                "text": f"🔬 The research behind [product]: While competitors focus on {triggers[0] if triggers else 'surface solutions'}, we went deeper. 6 months of testing revealed {opps[1] if len(opps) > 1 else 'hidden factors'}...",
                "hashtags": ["#research", "#development", "#creator"],
                "type": "authority_building",
                "platform": platform,  
                "creator_focus": "Builds authority through research and development insights"
            },
            {
                "text": f"💡 Why I created [product]: Every existing solution assumes {triggers[1] if len(triggers) > 1 else 'one approach fits all'}. But {messages[0] if messages else 'real success'} requires {opps[0] if opps else 'personalization'}. Here's what I built instead:",
                "hashtags": ["#creation", "#problemsolving", "#innovation"],
                "type": "origin_story",
                "platform": platform,
                "creator_focus": "Shares compelling creation story that highlights differentiation"
            },
            {
                "text": f"📊 Customer results update: 87% success rate vs industry average of 23%. The difference? We address {opps[0] if opps else 'what others ignore'}. Here's exactly how:",
                "hashtags": ["#results", "#data", "#creator"],
                "type": "social_proof",
                "platform": platform,
                "creator_focus": "Uses competitive intelligence to show superior results"
            },
            {
                "text": f"🎯 Behind the scenes: Building [product] meant solving what {triggers[2] if len(triggers) > 2 else 'existing solutions'} get wrong. Here's the methodology that changes everything:",
                "hashtags": ["#behindthescenes", "#methodology", "#creator"],
                "type": "process_sharing",
                "platform": platform,
                "creator_focus": "Shares unique process that differentiates from competitors"
            }
        ]
        
        # Extend if needed
        while len(creator_posts) < post_count:
            creator_posts.append({
                "text": f"🔍 Creator insight: The market gap I discovered was {opps[0] if opps else 'lack of personalization'}. That's why [product] focuses on {messages[0] if messages else 'individual success'}.",
                "hashtags": ["#creator", "#insights", "#innovation"],
                "type": "insight_sharing",
                "platform": platform,
                "creator_focus": "Continues to highlight unique market position"
            })
        
        return creator_posts[:post_count]
    
    # Enhanced existing methods with affiliate/creator intelligence...
    
    async def _generate_ad_copy(
        self, 
        intelligence: Dict[str, Any], 
        preferences: Dict[str, str]
    ) -> Dict[str, Any]:
        """Generate ad copy from intelligence - AFFILIATE/CREATOR FOCUSED"""
        
        logger.info("📢 Generating AFFILIATE/CREATOR ad copy")
        
        comp_intel = intelligence.get("competitive_intelligence", {})
        psych_intel = intelligence.get("psychology_intelligence", {})
        
        opportunities = comp_intel.get("opportunities", [])
        emotional_triggers = psych_intel.get("emotional_triggers", [])
        user_type = preferences.get("user_type", "affiliate")
        
        if user_type == "affiliate":
            headlines = [
                "The honest [product] review other affiliates won't share",
                f"Why I stopped promoting [competitor] for this: {opportunities[0] if opportunities else 'better results'}",
                "Affiliate disclosure: Here's why I actually recommend this",
                f"3 months testing [product]: The {emotional_triggers[0] if emotional_triggers else 'surprising'} results"
            ]
            primary_text = [
                "Most affiliate promotions use hype. I use data and honest experience.",
                f"After testing 10+ products, this solves what others miss: {opportunities[0] if opportunities else 'real implementation'}",
                "Full transparency: I earn commissions, but your success matters more than my earnings."
            ]
        else:  # creator
            headlines = [
                f"The solution for {opportunities[0] if opportunities else 'what competitors miss'}",
                f"Why existing products fail at {emotional_triggers[0] if emotional_triggers else 'delivering results'}",  
                "Built different: The methodology competitors don't teach",
                f"87% success rate vs 23% industry average. Here's why:"
            ]
            primary_text = [
                f"We solved what competitors couldn't: {opportunities[0] if opportunities else 'personalized approach'}",
                f"6 months of research revealed why existing solutions miss {emotional_triggers[0] if emotional_triggers else 'key factors'}",
                "While competitors copy each other, we innovated from scratch."
            ]
        
        return {
            "content_type": "ad_copy",
            "title": f"Ad Copy Variations for {user_type.title()}s from Intelligence",
            "content": {
                "headlines": headlines,
                "primary_text": primary_text,
                "descriptions": [
                    f"Learn the {user_type} approach that actually works",
                    f"Discover what competitors don't want you to know"
                ],
                "call_to_actions": ["Learn More", "Get Details", "See Results", "Try Different"]
            },
            "metadata": {
                "platform": preferences.get("platform", "facebook"),
                "objective": preferences.get("objective", "conversions"),
                "user_type": user_type,
                "generated_by": f"{user_type}_intelligence"
            },
            "usage_tips": [
                f"A/B test different {user_type} positioning angles",
                "Monitor cost per acquisition vs competitors",
                "Test audience segments based on intelligence insights",
                f"Emphasize unique {user_type} value proposition"
            ]
        }
    
    # Keep all existing methods but enhance them...
    
    def _predict_performance(
        self, 
        content_result: Dict[str, Any], 
        intelligence: Dict[str, Any], 
        content_type: str
    ) -> Dict[str, Any]:
        """Predict content performance based on intelligence - AFFILIATE/CREATOR ENHANCED"""
        
        confidence_score = intelligence.get("confidence_score", 0.5)
        
        # Enhanced predictions for affiliate/creator content
        if content_type == "email_sequence":
            affiliate_intelligence = content_result.get("affiliate_intelligence", {})
            unique_angles = len(affiliate_intelligence.get("unique_positioning", []))
            avoided_cliches = len(affiliate_intelligence.get("avoided_cliches", []))
            
            performance_boost = (unique_angles * 0.1) + (avoided_cliches * 0.05)
            adjusted_confidence = min(confidence_score + performance_boost, 1.0)
            
            return {
                "estimated_engagement": "High" if adjusted_confidence > 0.8 else "Medium to High" if adjusted_confidence > 0.6 else "Medium",
                "conversion_potential": "Excellent" if adjusted_confidence > 0.8 else "Good" if adjusted_confidence > 0.6 else "Fair",
                "differentiation_score": f"{unique_angles}/5 unique angles used",
                "cliche_avoidance_score": f"{avoided_cliches}/8 cliches avoided",
                "optimization_suggestions": [
                    "Test unique angles against traditional approaches",
                    "Monitor which intelligence-driven elements perform best",
                    "A/B test competitor differentiation messaging",
                    "Track commission rates vs generic affiliate content"
                ],
                "confidence_level": "High" if adjusted_confidence > 0.8 else "Medium",
                "intelligence_utilization": "Advanced" if unique_angles > 2 else "Basic"
            }
        
        # Standard predictions for other content types
        return {
            "estimated_engagement": "Medium to High" if confidence_score > 0.7 else "Medium",
            "conversion_potential": "Good" if confidence_score > 0.6 else "Fair", 
            "optimization_suggestions": [
                "A/B test different variations",
                "Monitor performance metrics",
                "Optimize based on intelligence insights"
            ],
            "confidence_level": "High" if confidence_score > 0.8 else "Medium"
        }
    
    # Keep all other existing methods unchanged...
    
    async def _generate_blog_post(self, intelligence: Dict[str, Any], preferences: Dict[str, str]) -> Dict[str, Any]:
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
            "metadata": {"topic": topic, "word_count": 500, "generated_by": "template"},
            "usage_tips": ["Add relevant images and charts", "Include internal and external links", "Promote on social media"]
        }
    
    async def _generate_landing_page(self, intelligence: Dict[str, Any], preferences: Dict[str, str]) -> Dict[str, Any]:
        logger.info("🎯 Generating landing page")
        return {
            "content_type": "landing_page",
            "title": "High-Converting Landing Page",
            "content": {
                "headline": "Transform Your Business Today",
                "subheadline": "Join thousands who have already succeeded",
                "sections": ["Hero Section with compelling value proposition", "Benefits section highlighting key advantages", "Social proof with testimonials and success stories", "Call-to-action with clear next steps"],
                "cta_count": 3
            },
            "metadata": {"goal": preferences.get("goal", "lead_generation"), "generated_by": "template"},
            "usage_tips": ["A/B test different headlines", "Monitor conversion rates", "Optimize page load speed"]
        }
    
    async def _generate_product_description(self, intelligence: Dict[str, Any], preferences: Dict[str, str]) -> Dict[str, Any]:
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
        logger.info("💰 Generating sales page")
        return {
            "content_type": "sales_page",
            "title": "Sales Page",
            "content": {
                "headline": "Transform Your Results with Proven Strategies",
                "sections": ["Problem identification and agitation", "Solution presentation with benefits", "Social proof and testimonials", "Urgency and call-to-action"]
            },
            "metadata": {"generated_by": "template"},
            "usage_tips": ["Test different headlines", "Monitor conversions", "Add exit-intent popups"]
        }
    
    def _parse_email_sequence_response(self, ai_response: str, sequence_length: int) -> List[Dict[str, str]]:
        """Parse AI response into email sequence format"""
        try:
            if '{' in ai_response and 'emails' in ai_response:
                import re
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    parsed_data = json.loads(json_match.group())
                    emails = parsed_data.get("emails", [])
                    if emails:
                        return emails[:sequence_length]
            return self._generate_fallback_emails(sequence_length)
        except Exception as e:
            logger.error(f"Failed to parse email sequence: {str(e)}")
            return self._generate_fallback_emails(sequence_length)
    
    def _generate_fallback_emails(self, count: int) -> List[Dict[str, str]]:
        """Generate fallback email sequence"""
        fallback_emails = [
            {"email_number": 1, "subject": "Welcome! Here's what you need to know...", "body": "Thank you for your interest. Let me share some valuable insights with you...", "send_delay": "Day 1"},
            {"email_number": 2, "subject": "The #1 mistake most people make", "body": "I've noticed a common pattern that prevents success. Here's how to avoid it...", "send_delay": "Day 3"},
            {"email_number": 3, "subject": "Here's proof it actually works", "body": "I want to share a success story that demonstrates the power of this approach...", "send_delay": "Day 5"},
            {"email_number": 4, "subject": "What's holding you back?", "body": "Let's address the common concerns and objections people have...", "send_delay": "Day 7"},
            {"email_number": 5, "subject": "Last chance to transform your results", "body": "This is your final opportunity to take action and see real change...", "send_delay": "Day 10"}
        ]
        
        while len(fallback_emails) < count:
            fallback_emails.append({
                "email_number": len(fallback_emails) + 1,
                "subject": f"Follow-up Email #{len(fallback_emails) + 1}",
                "body": "Continue building relationship and providing value...",
                "send_delay": f"Day {(len(fallback_emails) + 1) * 2 + 1}"
            })
        
        return fallback_emails[:count]
    
    def _generate_fallback_content(self, content_type: str, error_msg: str) -> Dict[str, Any]:
        """Generate fallback content when everything else fails"""
        logger.warning(f"⚠️ Generating fallback content for {content_type}: {error_msg}")
        return {
            "title": f"Template {content_type.replace('_', ' ').title()}",
            "content": f"Template-based {content_type} content. Error: {error_msg}",
            "metadata": {"generated_by": "fallback", "content_type": content_type, "generated_at": datetime.utcnow().isoformat(), "error": error_msg},
            "usage_tips": ["Check server logs for detailed error information", "Verify all dependencies are installed", "Try again with different preferences"],
            "performance_predictions": {"estimated_engagement": "N/A", "conversion_potential": "N/A"}
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