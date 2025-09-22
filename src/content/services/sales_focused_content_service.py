# src/content/services/sales_focused_content_service.py
"""
Sales-Focused Content Service - Transform Intelligence into Sales-Driving Content
Implements the Universal Sales-Driven Content Framework for conversion optimization
"""

from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging
import json
import hashlib
import random

logger = logging.getLogger(__name__)

class SalesFocusedContentService:
    """
    Content service that generates sales-focused content using the Universal Sales-Driven Content Framework
    Every piece of content has ONE goal: Move prospects closer to purchase
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_sales_content(
        self,
        content_type: str,
        campaign_id: Union[str, UUID],
        user_id: Union[str, UUID],
        company_id: Union[str, UUID],
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate sales-focused content that moves prospects closer to purchase
        Uses Universal Sales-Driven Content Framework
        """
        try:
            # Get intelligence data for this campaign
            intelligence_data = await self._get_campaign_intelligence_data(campaign_id)

            if not intelligence_data:
                return {
                    "success": False,
                    "error": "No intelligence data available for sales content generation",
                    "required_action": "run_campaign_analysis"
                }

            # Extract sales variables from intelligence using our framework
            sales_variables = await self._extract_sales_variables(intelligence_data)

            # Get user context for personalization
            user_context = await self._get_user_context(user_id, company_id)

            # Generate sales-focused content based on type
            if content_type in ["email", "email_sequence"]:
                result = await self._generate_sales_email_sequence(
                    intelligence_data, sales_variables, user_context, preferences or {}
                )
            elif content_type == "social_post":
                result = await self._generate_sales_social_content(
                    intelligence_data, sales_variables, user_context, preferences or {}
                )
            elif content_type == "blog_article":
                result = await self._generate_sales_blog_article(
                    intelligence_data, sales_variables, user_context, preferences or {}
                )
            elif content_type == "video_script":
                result = await self._generate_sales_video_script(
                    intelligence_data, sales_variables, user_context, preferences or {}
                )
            else:
                return {
                    "success": False,
                    "error": f"Unsupported content type: {content_type}"
                }

            # Store content with sales tracking
            content_id = await self._store_sales_content(
                campaign_id=campaign_id,
                user_id=user_id,
                company_id=company_id,
                content_type=content_type,
                content_data=result,
                sales_variables=sales_variables,
                intelligence_used=intelligence_data,
                user_context=user_context,
                generation_settings=preferences or {}
            )

            return {
                "success": True,
                "content_id": str(content_id),
                "content_type": content_type,
                "generated_content": result,
                "sales_framework": result.get("sales_framework"),
                "conversion_focus": result.get("conversion_focus"),
                "intelligence_sources_used": len(intelligence_data)
            }

        except Exception as e:
            logger.error(f"Sales-focused content generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _extract_sales_variables(self, intelligence_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract key sales variables from intelligence data using our framework"""

        if not intelligence_data:
            raise ValueError("No intelligence data to extract sales variables from")

        primary_intel = intelligence_data[0]

        # Extract framework variables
        product_name = primary_intel.get("product_name", "").strip()
        benefits = primary_intel.get("benefits", [])
        features = primary_intel.get("features", [])
        competitive_advantages = primary_intel.get("competitive_advantages", [])
        positioning = primary_intel.get("positioning", "")
        target_audience = primary_intel.get("target_audience", "")

        # Get full analysis data if available
        full_analysis = primary_intel.get("full_analysis_data", {})

        # Extract pain points from research content
        pain_points = self._extract_pain_points_from_intelligence(intelligence_data)

        # Extract emotional triggers
        emotional_triggers = self._extract_emotional_triggers(intelligence_data, full_analysis)

        # Extract credibility signals
        credibility_signals = self._extract_credibility_signals(intelligence_data, full_analysis)

        # Determine pricing/guarantee info
        pricing_info = self._extract_pricing_info(intelligence_data, full_analysis)
        guarantee_terms = self._extract_guarantee_terms(intelligence_data, full_analysis)

        return {
            # Core Framework Variables
            "PRODUCT_NAME": product_name,
            "PRIMARY_BENEFIT": benefits[0] if benefits else "improved results",
            "PAIN_POINT": pain_points[0] if pain_points else "current challenges",
            "TARGET_AUDIENCE": target_audience or "professionals",
            "EMOTIONAL_TRIGGER": emotional_triggers[0] if emotional_triggers else "better outcomes",
            "CREDIBILITY_SIGNAL": credibility_signals[0] if credibility_signals else "proven approach",
            "COMPETITIVE_ADVANTAGE": competitive_advantages[0] if competitive_advantages else "unique methodology",
            "GUARANTEE_TERMS": guarantee_terms or "satisfaction guarantee",
            "PRICE_POINT": pricing_info.get("price", "special pricing"),

            # Extended Variables for Rich Content
            "ALL_BENEFITS": benefits,
            "ALL_FEATURES": features,
            "ALL_PAIN_POINTS": pain_points,
            "ALL_EMOTIONAL_TRIGGERS": emotional_triggers,
            "ALL_CREDIBILITY_SIGNALS": credibility_signals,
            "ALL_COMPETITIVE_ADVANTAGES": competitive_advantages,
            "POSITIONING": positioning,

            # Sales Psychology Elements
            "URGENCY_FACTOR": self._determine_urgency_factor(intelligence_data),
            "SCARCITY_ELEMENT": self._determine_scarcity_element(intelligence_data),
            "SOCIAL_PROOF_TYPE": self._determine_social_proof_type(intelligence_data),
            "AUTHORITY_INDICATOR": self._determine_authority_indicator(intelligence_data),

            # Framework Metadata
            "confidence_score": primary_intel.get("confidence_score", 0),
            "intelligence_richness": self._calculate_intelligence_richness(intelligence_data)
        }

    def _extract_pain_points_from_intelligence(self, intelligence_data: List[Dict[str, Any]]) -> List[str]:
        """Extract pain points that we can agitate in sales content"""

        pain_points = []

        for intel in intelligence_data:
            # Check research content for problems/challenges
            research_content = intel.get("research_content", [])
            for research in research_content:
                content = research.get("content", "").lower()

                # Look for pain point indicators
                pain_indicators = ["problem", "challenge", "struggle", "difficulty", "frustration", "issue", "obstacle"]

                if any(indicator in content for indicator in pain_indicators):
                    sentences = research["content"].split('. ')
                    for sentence in sentences:
                        if any(indicator in sentence.lower() for indicator in pain_indicators):
                            # Clean and extract pain point
                            clean_sentence = sentence.strip().replace('\n', ' ')
                            if len(clean_sentence) > 20 and len(clean_sentence) < 150:
                                pain_points.append(clean_sentence)

            # Also extract from positioning if it mentions problems
            positioning = intel.get("positioning", "").lower()
            if any(word in positioning for word in ["solves", "fixes", "addresses", "eliminates"]):
                pain_points.append(f"traditional {intel.get('category', 'solutions')} limitations")

        # Generic pain points if none found
        if not pain_points:
            category = intelligence_data[0].get("category", "solutions")
            pain_points = [
                f"ineffective {category.lower()}",
                "wasted time and money",
                "lack of results",
                "complicated processes"
            ]

        return pain_points[:5]  # Return top 5 pain points

    def _extract_emotional_triggers(self, intelligence_data: List[Dict[str, Any]], full_analysis: Dict[str, Any]) -> List[str]:
        """Extract emotional triggers for persuasive content"""

        triggers = []
        primary_intel = intelligence_data[0]

        # Extract from benefits (transform to emotional)
        benefits = primary_intel.get("benefits", [])
        for benefit in benefits:
            benefit_lower = benefit.lower()
            if "save" in benefit_lower or "reduce" in benefit_lower:
                triggers.append("relief from current struggles")
            elif "improve" in benefit_lower or "better" in benefit_lower:
                triggers.append("desire for improvement")
            elif "fast" in benefit_lower or "quick" in benefit_lower:
                triggers.append("urgency for immediate results")
            elif "easy" in benefit_lower or "simple" in benefit_lower:
                triggers.append("frustration with complexity")
            else:
                triggers.append(f"excitement about {benefit.lower()}")

        # Extract from positioning
        positioning = primary_intel.get("positioning", "").lower()
        if "premium" in positioning or "advanced" in positioning:
            triggers.append("desire for exclusivity")
        elif "proven" in positioning or "tested" in positioning:
            triggers.append("need for security and assurance")
        elif "innovative" in positioning or "breakthrough" in positioning:
            triggers.append("excitement about innovation")

        # Check full analysis for emotional enhancement data
        emotional_enhancement = full_analysis.get("emotional_enhancement", {})
        if emotional_enhancement:
            enhancement_triggers = emotional_enhancement.get("emotional_triggers", [])
            triggers.extend(enhancement_triggers[:3])

        # Default emotional triggers if none found
        if not triggers:
            triggers = [
                "frustration with current solutions",
                "desire for better results",
                "fear of missing out on improvement",
                "excitement about transformation"
            ]

        return triggers[:6]  # Return top 6 emotional triggers

    def _extract_credibility_signals(self, intelligence_data: List[Dict[str, Any]], full_analysis: Dict[str, Any]) -> List[str]:
        """Extract credibility signals for trust building"""

        signals = []
        primary_intel = intelligence_data[0]

        # Extract from competitive advantages (these build credibility)
        advantages = primary_intel.get("competitive_advantages", [])
        for advantage in advantages:
            if "year" in advantage.lower() or "experience" in advantage.lower():
                signals.append(advantage)
            elif "research" in advantage.lower() or "study" in advantage.lower():
                signals.append(advantage)
            elif "patent" in advantage.lower() or "proprietary" in advantage.lower():
                signals.append(advantage)
            else:
                signals.append(f"proven {advantage.lower()}")

        # Check research content for scientific backing
        for intel in intelligence_data:
            research_content = intel.get("research_content", [])
            for research in research_content:
                research_type = research.get("research_type", "").lower()
                if "scientific" in research_type or "clinical" in research_type:
                    signals.append(f"{research_type} backing")
                elif "market" in research_type:
                    signals.append("market-validated approach")

        # Extract from full analysis credibility enhancement
        credibility_enhancement = full_analysis.get("credibility_enhancement", {})
        if credibility_enhancement:
            enhancement_signals = credibility_enhancement.get("credibility_indicators", [])
            signals.extend(enhancement_signals[:3])

        # Default credibility signals if none found
        if not signals:
            confidence = primary_intel.get("confidence_score", 0)
            if confidence > 0.8:
                signals.append("AI-verified effectiveness")
            signals.extend([
                "systematic methodology",
                "proven framework",
                "measurable results",
                "comprehensive approach"
            ])

        return signals[:5]  # Return top 5 credibility signals

    def _extract_pricing_info(self, intelligence_data: List[Dict[str, Any]], full_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract pricing information from intelligence"""

        pricing = {"price": None, "value": None, "currency": "USD"}

        # Check research content for pricing mentions
        for intel in intelligence_data:
            research_content = intel.get("research_content", [])
            for research in research_content:
                content = research.get("content", "").lower()

                # Look for price indicators
                if "$" in content:
                    # Extract price mentions
                    import re
                    price_matches = re.findall(r'\$\d+(?:,\d{3})*(?:\.\d{2})?', content)
                    if price_matches:
                        pricing["price"] = price_matches[0]

                # Look for value propositions
                if "value" in content or "worth" in content:
                    sentences = research["content"].split('. ')
                    for sentence in sentences:
                        if "value" in sentence.lower() or "worth" in sentence.lower():
                            pricing["value"] = sentence.strip()[:100]
                            break

        # Check full analysis for offer intelligence
        offer_intelligence = full_analysis.get("offer_intelligence", {})
        if offer_intelligence:
            pricing.update({
                "price": offer_intelligence.get("price", pricing["price"]),
                "value_proposition": offer_intelligence.get("value_proposition"),
                "pricing_model": offer_intelligence.get("pricing_model")
            })

        return pricing

    def _extract_guarantee_terms(self, intelligence_data: List[Dict[str, Any]], full_analysis: Dict[str, Any]) -> str:
        """Extract guarantee/risk reversal terms"""

        # Check research content for guarantee mentions
        for intel in intelligence_data:
            research_content = intel.get("research_content", [])
            for research in research_content:
                content = research.get("content", "").lower()

                guarantee_terms = ["guarantee", "refund", "money back", "risk-free", "warranty"]

                if any(term in content for term in guarantee_terms):
                    sentences = research["content"].split('. ')
                    for sentence in sentences:
                        if any(term in sentence.lower() for term in guarantee_terms):
                            return sentence.strip()[:150]

        # Check full analysis for offer intelligence
        offer_intelligence = full_analysis.get("offer_intelligence", {})
        if offer_intelligence:
            guarantee = offer_intelligence.get("guarantee")
            if guarantee:
                return guarantee

        # Default guarantee based on confidence
        confidence = intelligence_data[0].get("confidence_score", 0)
        if confidence > 0.8:
            return "satisfaction guarantee"
        else:
            return "risk-free trial"

    def _determine_urgency_factor(self, intelligence_data: List[Dict[str, Any]]) -> str:
        """Determine urgency factor for sales content"""

        primary_intel = intelligence_data[0]
        positioning = primary_intel.get("positioning", "").lower()

        if "limited" in positioning or "exclusive" in positioning:
            return "limited availability"
        elif "breakthrough" in positioning or "new" in positioning:
            return "early access opportunity"
        elif "proven" in positioning:
            return "limited time proven results"
        else:
            return "special opportunity"

    def _determine_scarcity_element(self, intelligence_data: List[Dict[str, Any]]) -> str:
        """Determine scarcity element for sales content"""

        primary_intel = intelligence_data[0]
        positioning = primary_intel.get("positioning", "").lower()

        if "premium" in positioning or "advanced" in positioning:
            return "exclusive access"
        elif "personalized" in positioning or "custom" in positioning:
            return "limited spots available"
        else:
            return "limited time offer"

    def _determine_social_proof_type(self, intelligence_data: List[Dict[str, Any]]) -> str:
        """Determine type of social proof to emphasize"""

        primary_intel = intelligence_data[0]
        target_audience = primary_intel.get("target_audience", "").lower()

        if "business" in target_audience or "professional" in target_audience:
            return "business case studies"
        elif "individual" in target_audience or "personal" in target_audience:
            return "customer testimonials"
        else:
            return "user success stories"

    def _determine_authority_indicator(self, intelligence_data: List[Dict[str, Any]]) -> str:
        """Determine authority indicator to highlight"""

        primary_intel = intelligence_data[0]
        confidence = primary_intel.get("confidence_score", 0)

        if confidence > 0.9:
            return "industry-leading solution"
        elif confidence > 0.7:
            return "proven methodology"
        else:
            return "systematic approach"

    def _calculate_intelligence_richness(self, intelligence_data: List[Dict[str, Any]]) -> float:
        """Calculate richness of intelligence data for content quality"""

        if not intelligence_data:
            return 0.0

        primary_intel = intelligence_data[0]
        score = 0.0

        # Score different elements that contribute to sales content quality
        score += len(primary_intel.get("benefits", [])) * 0.3  # Benefits are crucial for sales
        score += len(primary_intel.get("features", [])) * 0.2
        score += len(primary_intel.get("competitive_advantages", [])) * 0.25  # Key for differentiation
        score += len(primary_intel.get("research_content", [])) * 0.15
        score += 0.1 if primary_intel.get("positioning") else 0
        score += 0.1 if primary_intel.get("target_audience") else 0
        score += primary_intel.get("confidence_score", 0) * 0.2  # Confidence affects content quality

        return min(score, 10.0)  # Cap at 10

    async def _generate_sales_email_sequence(
        self,
        intelligence_data: List[Dict[str, Any]],
        sales_variables: Dict[str, Any],
        user_context: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate 7-Email Sales Psychology Sequence from our framework"""

        # Determine sequence length based on intelligence richness
        intelligence_richness = sales_variables.get("intelligence_richness", 0)
        if intelligence_richness >= 8:
            sequence_length = 7  # Full framework sequence
        elif intelligence_richness >= 5:
            sequence_length = 5  # Compressed sequence
        else:
            sequence_length = 3  # Minimal sequence

        sequence_length = preferences.get("sequence_length", sequence_length)

        # Define 7-email framework structure
        email_framework = [
            {"type": "problem_agitation", "delay": "immediate", "psychology": "Make the pain unbearable"},
            {"type": "problem_revelation", "delay": "3 days", "psychology": "The 'aha moment' - explain the real cause"},
            {"type": "solution_introduction", "delay": "5 days", "psychology": "Hope and possibility"},
            {"type": "social_proof_explosion", "delay": "7 days", "psychology": "Others like me are succeeding"},
            {"type": "urgency_scarcity", "delay": "10 days", "psychology": "Fear of missing out"},
            {"type": "objection_crusher", "delay": "12 days", "psychology": "Remove final barriers"},
            {"type": "final_call", "delay": "14 days", "psychology": "Now or never"}
        ]

        # Generate emails based on sequence length
        emails = []
        selected_framework = email_framework[:sequence_length]

        for i, email_config in enumerate(selected_framework):
            email = await self._create_sales_email(
                email_number=i + 1,
                email_config=email_config,
                sales_variables=sales_variables,
                user_context=user_context,
                total_in_sequence=sequence_length
            )
            emails.append(email)

        return {
            "content": {"emails": emails},
            "sales_framework": {
                "framework_type": "7_email_sales_psychology_sequence",
                "sequence_length": sequence_length,
                "intelligence_richness": intelligence_richness,
                "conversion_focus": "move_prospects_closer_to_purchase"
            },
            "conversion_focus": {
                "primary_goal": "product_sales",
                "psychological_progression": [email["psychology"] for email in selected_framework],
                "expected_conversion_points": self._identify_conversion_points(selected_framework)
            },
            "personalization_data": {
                "product_name": sales_variables["PRODUCT_NAME"],
                "primary_benefit": sales_variables["PRIMARY_BENEFIT"],
                "target_audience": sales_variables["TARGET_AUDIENCE"],
                "user_customization": user_context.get("uniqueness_seed")
            }
        }

    async def _create_sales_email(
        self,
        email_number: int,
        email_config: Dict[str, Any],
        sales_variables: Dict[str, Any],
        user_context: Dict[str, Any],
        total_in_sequence: int
    ) -> Dict[str, Any]:
        """Create individual sales-focused email using framework templates"""

        email_type = email_config["type"]

        # Generate subject line using sales psychology
        subject = await self._generate_sales_subject(email_type, sales_variables, email_number)

        # Generate body content using sales framework
        body = await self._generate_sales_body(email_type, sales_variables, user_context, email_number)

        # Generate call-to-action based on email type
        cta = self._generate_sales_cta(email_type, sales_variables)

        return {
            "email_number": email_number,
            "subject": subject,
            "body": body,
            "cta": cta,
            "send_delay": email_config["delay"],
            "psychology": email_config["psychology"],
            "email_type": email_type,
            "conversion_intent": self._get_conversion_intent(email_type),
            "sales_variables_used": self._track_sales_variables_usage(email_type, sales_variables)
        }

    async def _generate_sales_subject(self, email_type: str, sales_variables: Dict[str, Any], email_number: int) -> str:
        """Generate sales-focused subject lines using framework patterns"""

        product_name = sales_variables["PRODUCT_NAME"]
        pain_point = sales_variables["PAIN_POINT"]
        primary_benefit = sales_variables["PRIMARY_BENEFIT"]
        emotional_trigger = sales_variables["EMOTIONAL_TRIGGER"]

        if email_type == "problem_agitation":
            subjects = [
                f"Why {pain_point} is sabotaging your {primary_benefit}",
                f"The hidden reason {pain_point} keeps happening",
                f"WARNING: {pain_point} is costing you more than you think"
            ]

        elif email_type == "problem_revelation":
            subjects = [
                f"The shocking truth about {pain_point}",
                f"What nobody tells you about {pain_point}",
                f"The real cause of {pain_point} (revealed)"
            ]

        elif email_type == "solution_introduction":
            subjects = [
                f"What if {primary_benefit} was actually possible?",
                f"The {primary_benefit} breakthrough you've been waiting for",
                f"Finally: A real solution for {primary_benefit}"
            ]

        elif email_type == "social_proof_explosion":
            target_audience = sales_variables["TARGET_AUDIENCE"]
            subjects = [
                f"How {target_audience} are getting {primary_benefit} with {product_name}",
                f"{target_audience} report {primary_benefit} in just days",
                f"Real {primary_benefit} results from {target_audience}"
            ]

        elif email_type == "urgency_scarcity":
            urgency_factor = sales_variables["URGENCY_FACTOR"]
            subjects = [
                f"Last chance: {primary_benefit} opportunity disappearing soon",
                f"{urgency_factor} - doors close at midnight",
                f"Final hours for {primary_benefit} access"
            ]

        elif email_type == "objection_crusher":
            subjects = [
                f"But what if {product_name} doesn't work for me?",
                f"Your biggest concern about {primary_benefit}",
                f"The truth about {product_name} risks"
            ]

        elif email_type == "final_call":
            subjects = [
                f"This is it - final notice for {primary_benefit}",
                f"Last call: {product_name} access ends tonight",
                f"Final chance for {primary_benefit} transformation"
            ]

        else:
            subjects = [f"{product_name}: {primary_benefit} update #{email_number}"]

        return random.choice(subjects)

    async def _generate_sales_body(
        self,
        email_type: str,
        sales_variables: Dict[str, Any],
        user_context: Dict[str, Any],
        email_number: int
    ) -> str:
        """Generate sales-focused email body using framework content strategies"""

        product_name = sales_variables["PRODUCT_NAME"]
        pain_point = sales_variables["PAIN_POINT"]
        primary_benefit = sales_variables["PRIMARY_BENEFIT"]
        emotional_trigger = sales_variables["EMOTIONAL_TRIGGER"]
        credibility_signal = sales_variables["CREDIBILITY_SIGNAL"]

        # Get user name for personalization
        user_name = user_context.get("user_name", "")
        greeting = f"Hi {user_name.split()[0]}," if user_name else "Hi there,"

        if email_type == "problem_agitation":
            body = f"""{greeting}

I need to share something that might be uncomfortable to hear...

{pain_point.capitalize()} isn't just an inconvenience - it's systematically sabotaging your ability to achieve {primary_benefit}.

Here's what's really happening:

Every day you struggle with {pain_point}, you're losing more than just time. You're losing confidence, momentum, and the opportunity for {primary_benefit} that should rightfully be yours.

The worst part? Most people don't even realize how much {pain_point} is truly costing them until it's too late.

I see it happening everywhere - talented people like you being held back by {pain_point}, while others who understand the real problem are pulling ahead.

Tomorrow, I'll reveal exactly what's causing this cycle and why traditional approaches to {pain_point} actually make things worse.

Stay tuned,
{user_context.get('user_name', '[Your Name]')}

P.S. If you're feeling frustrated about {pain_point}, you're not alone. But there IS a way out."""

        elif email_type == "problem_revelation":
            competitive_advantage = sales_variables["COMPETITIVE_ADVANTAGE"]
            body = f"""{greeting}

Yesterday I told you how {pain_point} is sabotaging your {primary_benefit}...

Today, I want to reveal the REAL cause that nobody talks about.

After analyzing thousands of cases, I discovered something shocking:

{pain_point.capitalize()} isn't actually the problem. It's a SYMPTOM.

The real cause? Traditional solutions focus on the surface level while ignoring the underlying system that creates {pain_point} in the first place.

This is why:
• Quick fixes never last
• You keep hitting the same obstacles
• Progress feels impossible despite your best efforts

But here's the breakthrough:

{product_name} addresses this at the root level through {competitive_advantage}.

Instead of treating symptoms, it transforms the entire system that creates {pain_point}.

This is why our {credibility_signal} approach delivers {primary_benefit} where others fail.

Tomorrow, I'll show you exactly how this works and why it changes everything.

Best regards,
{user_context.get('user_name', '[Your Name]')}

P.S. Understanding this difference is the key to everything."""

        elif email_type == "solution_introduction":
            all_benefits = sales_variables["ALL_BENEFITS"][:3]
            body = f"""{greeting}

What if I told you that {primary_benefit} wasn't just possible, but inevitable with the right approach?

You might think I'm overselling, but let me explain...

{product_name} represents a fundamental shift in how we approach {pain_point}.

Instead of fighting symptoms, it creates an environment where {primary_benefit} happens naturally.

Here's what this means for you:

""" + "\n".join(f"✓ {benefit}" for benefit in all_benefits) + f"""

This isn't theory - it's {credibility_signal} methodology that addresses the root cause we discussed yesterday.

The transformation happens because {product_name} works WITH your natural patterns instead of against them.

Want to see how this applies to your specific situation?

[See how {product_name} works →]

More proof coming tomorrow,
{user_context.get('user_name', '[Your Name]')}

P.S. The approach changes everything once you see it in action."""

        elif email_type == "social_proof_explosion":
            target_audience = sales_variables["TARGET_AUDIENCE"]
            social_proof_type = sales_variables["SOCIAL_PROOF_TYPE"]
            body = f"""{greeting}

I want to share some results that might surprise you...

{target_audience.capitalize()} using {product_name} are reporting {primary_benefit} faster than we ever expected.

Here's what real {social_proof_type} are telling us:

"I was skeptical about {primary_benefit}, but {product_name} delivered results I hadn't seen with anything else. The {credibility_signal} approach made all the difference." - Sarah M.

"After struggling with {pain_point} for years, {product_name} gave me {primary_benefit} in weeks, not months. Wish I'd found this sooner." - Michael R.

"The transformation was remarkable. {product_name} didn't just solve {pain_point} - it completely changed how I approach {primary_benefit}." - Jennifer K.

What makes these results possible?

{product_name}'s {competitive_advantage} addresses the core system issues we've been discussing all week.

When you fix the foundation, everything else becomes easier.

These aren't cherry-picked testimonials - they represent the typical experience with our {credibility_signal} methodology.

Ready to join them?

[Learn more about {product_name} →]

More insights tomorrow,
{user_context.get('user_name', '[Your Name]')}

P.S. Results like these are possible because we address the root cause, not just symptoms."""

        elif email_type == "urgency_scarcity":
            urgency_factor = sales_variables["URGENCY_FACTOR"]
            scarcity_element = sales_variables["SCARCITY_ELEMENT"]
            body = f"""{greeting}

This is urgent - I need to tell you about a situation developing with {product_name}.

Due to {urgency_factor}, we have to limit access starting midnight tonight.

Here's what's happening:

The demand for {primary_benefit} solutions has exceeded our capacity to provide the personalized support that makes {product_name} effective.

Rather than compromise quality, we're implementing {scarcity_element} to ensure everyone gets the full benefit of our {credibility_signal} approach.

This means:
• No more waiting lists after tonight
• Current pricing ends at midnight
• {scarcity_element} - first come, first served

I'm not sharing this to pressure you - I'm sharing it because if you've been considering {primary_benefit}, waiting could cost you months of progress.

The {emotional_trigger} you're feeling about {pain_point}? It doesn't get easier with time.

But {product_name} can resolve it quickly IF you have access to our complete system.

[Secure your access before midnight →]

Final update tomorrow,
{user_context.get('user_name', '[Your Name]')}

P.S. After midnight, the next opportunity won't be until {scarcity_element} opens again."""

        elif email_type == "objection_crusher":
            guarantee_terms = sales_variables["GUARANTEE_TERMS"]
            body = f"""{greeting}

I know what you might be thinking about {product_name}...

"What if it doesn't work for me?"
"What if I waste my money?"
"What if I'm different from everyone else?"

These are completely valid concerns. Let me address them directly.

**"What if {product_name} doesn't work for me?"**

Our {credibility_signal} approach has been validated across diverse situations. The methodology adapts to your specific context because it addresses universal principles, not one-size-fits-all tactics.

**"What if I waste my money?"**

That's exactly why we offer {guarantee_terms}. If {product_name} doesn't deliver {primary_benefit}, you get your investment back. No questions, no hassles.

**"What if I'm different from everyone else?"**

The beauty of addressing root causes instead of symptoms is that it works regardless of your starting point. {competitive_advantage} is designed for real-world complexity, not perfect conditions.

The bigger risk isn't trying {product_name} - it's continuing with {pain_point} while {primary_benefit} remains out of reach.

Every day you wait, others are moving ahead with solutions that work.

Try {product_name} completely risk-free:

[Get started with {guarantee_terms} →]

Last chance tomorrow,
{user_context.get('user_name', '[Your Name]')}

P.S. The only way to know for certain is to experience the {credibility_signal} approach yourself."""

        elif email_type == "final_call":
            price_point = sales_variables["PRICE_POINT"]
            body = f"""{greeting}

This is my final message about {product_name}.

In a few hours, access closes and won't reopen for months.

Over the past two weeks, I've shared:
• Why {pain_point} sabotages {primary_benefit}
• The real cause nobody talks about
• How {product_name} addresses the root system
• Proof from {target_audience} getting real results
• Risk-free {guarantee_terms}

Now it's decision time.

You can continue managing {pain_point} with temporary fixes, hoping things improve...

Or you can invest in {product_name} and get the {primary_benefit} transformation you've been wanting.

At {price_point}, this is a fraction of what {pain_point} costs you in lost opportunities, time, and frustration.

But more importantly, this is about finally having {primary_benefit} instead of just hoping for it.

The choice is yours. But after midnight, this choice is gone.

[Get {product_name} now - doors close at midnight →]

To your success,
{user_context.get('user_name', '[Your Name]')}

P.S. Six months from now, you'll either have {primary_benefit} or still be dealing with {pain_point}. This moment determines which."""

        else:
            body = f"""{greeting}

Quick update about {product_name}...

[Content will be generated based on available intelligence data]

Best regards,
{user_context.get('user_name', '[Your Name]')}"""

        return body

    def _generate_sales_cta(self, email_type: str, sales_variables: Dict[str, Any]) -> str:
        """Generate conversion-focused call-to-action for each email type"""

        product_name = sales_variables["PRODUCT_NAME"]
        primary_benefit = sales_variables["PRIMARY_BENEFIT"]

        cta_map = {
            "problem_agitation": f"Discover the hidden cause of {sales_variables['PAIN_POINT']}",
            "problem_revelation": f"Learn about the real solution to {sales_variables['PAIN_POINT']}",
            "solution_introduction": f"See how {product_name} delivers {primary_benefit}",
            "social_proof_explosion": f"Join others achieving {primary_benefit} with {product_name}",
            "urgency_scarcity": f"Secure your {product_name} access before it's gone",
            "objection_crusher": f"Try {product_name} risk-free with {sales_variables['GUARANTEE_TERMS']}",
            "final_call": f"Get {product_name} now - doors close at midnight"
        }

        return cta_map.get(email_type, f"Learn more about {product_name}")

    def _get_conversion_intent(self, email_type: str) -> str:
        """Get the conversion intent for each email type in the sequence"""

        intent_map = {
            "problem_agitation": "awareness",
            "problem_revelation": "interest",
            "solution_introduction": "consideration",
            "social_proof_explosion": "evaluation",
            "urgency_scarcity": "conversion",
            "objection_crusher": "conversion",
            "final_call": "conversion"
        }

        return intent_map.get(email_type, "engagement")

    def _identify_conversion_points(self, email_framework: List[Dict[str, Any]]) -> List[str]:
        """Identify key conversion points in the email sequence"""

        conversion_points = []

        for i, email in enumerate(email_framework):
            email_type = email["type"]

            if email_type == "solution_introduction":
                conversion_points.append(f"Email {i+1}: Initial interest capture")
            elif email_type == "social_proof_explosion":
                conversion_points.append(f"Email {i+1}: Trust building and validation")
            elif email_type in ["urgency_scarcity", "objection_crusher", "final_call"]:
                conversion_points.append(f"Email {i+1}: Direct conversion attempt")

        return conversion_points

    def _track_sales_variables_usage(self, email_type: str, sales_variables: Dict[str, Any]) -> Dict[str, Any]:
        """Track which sales variables were used in this email"""

        usage_map = {
            "problem_agitation": ["PAIN_POINT", "PRIMARY_BENEFIT", "EMOTIONAL_TRIGGER"],
            "problem_revelation": ["PAIN_POINT", "PRODUCT_NAME", "COMPETITIVE_ADVANTAGE", "CREDIBILITY_SIGNAL"],
            "solution_introduction": ["PRODUCT_NAME", "PRIMARY_BENEFIT", "ALL_BENEFITS", "CREDIBILITY_SIGNAL"],
            "social_proof_explosion": ["TARGET_AUDIENCE", "PRODUCT_NAME", "PRIMARY_BENEFIT", "SOCIAL_PROOF_TYPE"],
            "urgency_scarcity": ["URGENCY_FACTOR", "SCARCITY_ELEMENT", "PRIMARY_BENEFIT", "EMOTIONAL_TRIGGER"],
            "objection_crusher": ["PRODUCT_NAME", "GUARANTEE_TERMS", "CREDIBILITY_SIGNAL", "COMPETITIVE_ADVANTAGE"],
            "final_call": ["PRODUCT_NAME", "PRIMARY_BENEFIT", "PRICE_POINT", "TARGET_AUDIENCE"]
        }

        used_variables = usage_map.get(email_type, [])

        return {
            "variables_used": used_variables,
            "variable_count": len(used_variables),
            "personalization_level": "high" if len(used_variables) >= 4 else "medium"
        }

    # Continue with other content type methods...
    # (social_post, blog_article, video_script methods will follow the same sales-focused framework)

    async def _get_campaign_intelligence_data(self, campaign_id: Union[str, UUID]) -> List[Dict[str, Any]]:
        """Get intelligence data from database"""
        try:
            query = text("""
                SELECT
                    ic.id as intelligence_id,
                    ic.product_name,
                    ic.salespage_url,
                    ic.confidence_score,
                    ic.analysis_method,
                    ic.full_analysis_data,
                    pd.features,
                    pd.benefits,
                    pd.ingredients,
                    pd.conditions,
                    pd.usage_instructions,
                    md.category,
                    md.positioning,
                    md.competitive_advantages,
                    md.target_audience,
                    kb.content as research_content,
                    kb.research_type
                FROM intelligence_core ic
                LEFT JOIN product_data pd ON ic.id = pd.intelligence_id
                LEFT JOIN market_data md ON ic.id = md.intelligence_id
                LEFT JOIN intelligence_research ir ON ic.id = ir.intelligence_id
                LEFT JOIN knowledge_base kb ON ir.research_id = kb.id
                WHERE ic.user_id IN (
                    SELECT user_id FROM campaigns WHERE id = :campaign_id
                )
                ORDER BY ic.confidence_score DESC, ic.created_at DESC
            """)

            result = await self.db.execute(query, {"campaign_id": UUID(str(campaign_id))})
            rows = result.fetchall()

            # Group and return intelligence data
            intelligence_map = {}
            for row in rows:
                intel_id = row.intelligence_id

                if intel_id not in intelligence_map:
                    intelligence_map[intel_id] = {
                        "intelligence_id": str(intel_id),
                        "product_name": row.product_name,
                        "salespage_url": row.salespage_url,
                        "confidence_score": float(row.confidence_score) if row.confidence_score else 0.0,
                        "analysis_method": row.analysis_method,
                        "full_analysis_data": row.full_analysis_data if row.full_analysis_data else {},
                        "features": row.features if row.features else [],
                        "benefits": row.benefits if row.benefits else [],
                        "ingredients": row.ingredients if row.ingredients else [],
                        "conditions": row.conditions if row.conditions else [],
                        "usage_instructions": row.usage_instructions if row.usage_instructions else [],
                        "category": row.category,
                        "positioning": row.positioning,
                        "competitive_advantages": row.competitive_advantages if row.competitive_advantages else [],
                        "target_audience": row.target_audience,
                        "research_content": []
                    }

                if row.research_content and row.research_type:
                    intelligence_map[intel_id]["research_content"].append({
                        "content": row.research_content,
                        "research_type": row.research_type
                    })

            return list(intelligence_map.values())

        except Exception as e:
            logger.error(f"Failed to get intelligence data: {e}")
            return []

    async def _get_user_context(self, user_id: Union[str, UUID], company_id: Union[str, UUID]) -> Dict[str, Any]:
        """Get user-specific context for content personalization"""
        try:
            query = text("""
                SELECT
                    u.id as user_id,
                    u.full_name,
                    u.user_type,
                    u.created_at as user_created_at,
                    c.company_name,
                    c.company_slug,
                    c.industry,
                    c.company_size,
                    COUNT(camp.id) as total_campaigns,
                    COUNT(gc.id) as total_content_generated
                FROM users u
                JOIN companies c ON u.company_id = c.id
                LEFT JOIN campaigns camp ON camp.user_id = u.id
                LEFT JOIN generated_content gc ON gc.user_id = u.id
                WHERE u.id = :user_id AND c.id = :company_id
                GROUP BY u.id, c.id
            """)

            result = await self.db.execute(query, {
                "user_id": UUID(str(user_id)),
                "company_id": UUID(str(company_id))
            })
            row = result.fetchone()

            if not row:
                return {"user_id": str(user_id), "uniqueness_seed": str(user_id)[:8]}

            return {
                "user_id": str(row.user_id),
                "user_name": row.full_name,
                "user_type": row.user_type,
                "company_name": row.company_name,
                "company_slug": row.company_slug,
                "industry": row.industry,
                "company_size": row.company_size,
                "experience_level": "experienced" if row.total_campaigns > 5 else "new",
                "content_history": row.total_content_generated,
                "uniqueness_seed": hashlib.md5(f"{user_id}-{company_id}".encode()).hexdigest()[:8]
            }

        except Exception as e:
            logger.error(f"Failed to get user context: {e}")
            return {"user_id": str(user_id), "uniqueness_seed": str(user_id)[:8]}

    async def _store_sales_content(
        self,
        campaign_id: Union[str, UUID],
        user_id: Union[str, UUID],
        company_id: Union[str, UUID],
        content_type: str,
        content_data: Dict[str, Any],
        sales_variables: Dict[str, Any],
        intelligence_used: List[Dict[str, Any]],
        user_context: Dict[str, Any],
        generation_settings: Dict[str, Any]
    ) -> UUID:
        """Store sales-focused content with conversion tracking"""

        content_id = uuid4()

        # Generate sales-focused title
        content_title = await self._generate_sales_title(content_type, sales_variables, content_data)

        # Extract content for storage
        if content_type in ["email", "email_sequence"]:
            emails = content_data.get("content", {}).get("emails", [])
            content_body = json.dumps(emails)
        else:
            content_body = json.dumps(content_data.get("content", {}))

        # Create metadata with sales tracking
        content_metadata = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "sales_framework": content_data.get("sales_framework", {}),
            "conversion_focus": content_data.get("conversion_focus", {}),
            "sales_variables_used": list(sales_variables.keys()),
            "intelligence_sources": len(intelligence_used),
            "user_customization": user_context.get("uniqueness_seed"),
            "generation_method": "sales_focused_framework",
            "framework_version": "universal_sales_driven_v1.0"
        }

        query = text("""
            INSERT INTO generated_content
            (id, user_id, campaign_id, company_id, content_type, content_title, content_body,
             content_metadata, generation_settings, generation_method, content_status, intelligence_id)
            VALUES (:id, :user_id, :campaign_id, :company_id, :content_type, :content_title,
                    :content_body, :content_metadata, :generation_settings, 'sales_focused_ai', 'generated', :intelligence_id)
        """)

        await self.db.execute(query, {
            "id": content_id,
            "user_id": UUID(str(user_id)),
            "campaign_id": UUID(str(campaign_id)),
            "company_id": UUID(str(company_id)),
            "content_type": content_type,
            "content_title": content_title,
            "content_body": content_body,
            "content_metadata": json.dumps(content_metadata),
            "generation_settings": json.dumps(generation_settings),
            "intelligence_id": intelligence_used[0]["intelligence_id"] if intelligence_used else None
        })

        await self.db.commit()
        return content_id

    async def _generate_sales_title(
        self,
        content_type: str,
        sales_variables: Dict[str, Any],
        content_data: Dict[str, Any]
    ) -> str:
        """Generate sales-focused titles that emphasize conversion"""

        product_name = sales_variables["PRODUCT_NAME"]
        primary_benefit = sales_variables["PRIMARY_BENEFIT"]

        if content_type in ["email", "email_sequence"]:
            sequence_length = len(content_data.get("content", {}).get("emails", []))
            return f"{product_name}: {sequence_length}-Email {primary_benefit} Sales Sequence"

        elif content_type == "social_post":
            return f"{product_name} {primary_benefit} - Conversion-Focused Social Campaign"

        elif content_type == "blog_article":
            return f"How to Achieve {primary_benefit} with {product_name}: Sales-Driven Guide"

        elif content_type == "video_script":
            return f"{product_name} {primary_benefit} - Conversion Video Script"

        else:
            return f"{product_name} {primary_benefit} - Sales Content"