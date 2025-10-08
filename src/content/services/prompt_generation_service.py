# src/content/services/prompt_generation_service.py
"""
Prompt Generation Service
Intelligence-driven prompt creation for AI content generation
Implements the prompt generation architecture from docs
"""

import logging
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ContentType(str, Enum):
    """Content types supported by the system"""
    EMAIL = "email"
    EMAIL_SEQUENCE = "email_sequence"
    SOCIAL_POST = "social"
    BLOG_ARTICLE = "blog"
    AD_COPY = "ad"
    VIDEO_SCRIPT = "video_script"
    IMAGE = "image"


class SalesPsychologyStage(str, Enum):
    """Sales psychology stages from Universal Sales Framework"""
    PROBLEM_AWARENESS = "problem_awareness"
    PROBLEM_AGITATION = "problem_agitation"
    SOLUTION_REVEAL = "solution_reveal"
    BENEFIT_PROOF = "benefit_proof"
    SOCIAL_VALIDATION = "social_validation"
    URGENCY_CREATION = "urgency_creation"
    OBJECTION_HANDLING = "objection_handling"
    CALL_TO_ACTION = "call_to_action"


class PromptGenerationService:
    """
    Core service for generating optimized AI prompts from campaign intelligence
    Implements the modular architecture from content-generation-implementation-plan.md
    """

    def __init__(self):
        self.name = "PromptGenerationService"
        self.version = "1.0.0"
        logger.info(f"{self.name} v{self.version} initialized")

    async def generate_prompt(
        self,
        content_type: ContentType,
        intelligence_data: Dict[str, Any],
        psychology_stage: SalesPsychologyStage = SalesPsychologyStage.SOLUTION_REVEAL,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate optimized prompt from campaign intelligence
        Main interface for the prompt generation system
        """

        if preferences is None:
            preferences = {}

        try:
            # Step 1: Extract intelligence variables
            variables = self._extract_intelligence_variables(intelligence_data)

            # Step 2: Get content-type specific template
            template = self._get_content_template(content_type, psychology_stage)

            # Step 3: Build prompt from template and variables
            prompt = self._build_prompt(template, variables, preferences)

            # Step 4: Add system message for AI context
            system_message = self._build_system_message(content_type, variables)

            # Step 5: Calculate quality score
            quality_score = self._calculate_prompt_quality(prompt, variables)

            return {
                "success": True,
                "prompt": prompt,
                "system_message": system_message,
                "variables": variables,
                "content_type": content_type.value,
                "psychology_stage": psychology_stage.value,
                "quality_score": quality_score,
                "metadata": {
                    "intelligence_sources": len(intelligence_data.get("intelligence_sources", [])),
                    "variables_extracted": len(variables),
                    "template_used": f"{content_type.value}_{psychology_stage.value}"
                }
            }

        except Exception as e:
            logger.error(f"Prompt generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content_type": content_type.value
            }

    def _extract_intelligence_variables(self, intelligence_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract and map intelligence data to prompt variables
        NOW ENHANCED: Leverages AI-generated intelligence from 6 enhancers for richer content
        """

        variables = {}

        # Extract product name (primary variable)
        variables["PRODUCT_NAME"] = intelligence_data.get("product_name", "this product")

        # Extract from offer intelligence (basic data)
        offer = intelligence_data.get("offer_intelligence", {})
        variables["PRIMARY_BENEFIT"] = self._extract_first(offer, ["key_features", "benefits", "value_proposition"],
                                                          self._extract_from_basic_data(intelligence_data, "benefits"))
        variables["PRICE_POINT"] = offer.get("pricing_info", "competitive pricing")
        variables["GUARANTEE_TERMS"] = offer.get("guarantee_terms", "satisfaction guaranteed")

        # Extract from psychology intelligence (basic data)
        psychology = intelligence_data.get("psychology_intelligence", {})
        variables["PAIN_POINT"] = self._extract_first(psychology, ["pain_points", "challenges", "problems"], "common challenges")
        variables["TARGET_AUDIENCE"] = psychology.get("target_audience", intelligence_data.get("target_audience", "customers"))
        variables["EMOTIONAL_TRIGGER"] = self._extract_first(psychology, ["emotional_triggers", "desires", "aspirations"], "positive results")
        variables["DESIRE_STATE"] = self._extract_first(psychology, ["desire_states", "goals", "outcomes"], "desired outcomes")

        # Extract from competitive intelligence (basic data)
        competitive = intelligence_data.get("competitive_intelligence", {})
        variables["COMPETITIVE_ADVANTAGE"] = self._extract_first(competitive, ["differentiation_factors", "unique_selling_points", "advantages"],
                                                                 self._extract_from_basic_data(intelligence_data, "competitive_advantages"))
        variables["MARKET_POSITIONING"] = competitive.get("market_positioning", intelligence_data.get("positioning", "leading solution"))

        # Extract from brand intelligence (basic data)
        brand = intelligence_data.get("brand_intelligence", {})
        variables["BRAND_VOICE"] = brand.get("brand_voice", "professional")
        variables["TONE"] = brand.get("tone", "conversational")

        # Extract from content intelligence (basic data)
        content = intelligence_data.get("content_intelligence", {})
        variables["KEY_MESSAGES"] = self._extract_first(content, ["key_messages", "talking_points", "highlights"], "important information")

        # 🔥 NEW: Extract from AI-Enhanced Intelligence (6 enhancers)
        # Extract from scientific_enhancement
        scientific = intelligence_data.get("scientific_intelligence", {})
        if scientific:
            variables["SCIENTIFIC_BACKING"] = self._extract_first(scientific, ["validated_claims", "research_support", "scientific_backing"], "")
            variables["RESEARCH_CREDIBILITY"] = self._extract_first(scientific.get("scientific_credibility", {}), ["research_basis", "evidence_level"], "")

        # Extract from emotional_enhancement
        emotional = intelligence_data.get("emotional_transformation_intelligence", {})
        if emotional:
            emotional_journey = self._extract_first(emotional, ["emotional_journey", "amplified_triggers"], "")
            variables["EMOTIONAL_JOURNEY"] = emotional_journey if emotional_journey else ""
            variables["PSYCHOLOGICAL_TRIGGERS"] = self._extract_first(emotional, ["psychological_drivers", "amplified_triggers"], "")

        # Extract from credibility_enhancement
        credibility = intelligence_data.get("credibility_intelligence", {})
        if credibility:
            variables["TRUST_SIGNALS"] = self._extract_first(credibility, ["trust_indicators", "credibility_markers"], "")
            variables["AUTHORITY_MARKERS"] = self._extract_first(credibility, ["authority_signals", "expertise_indicators"], "")
            variables["SOCIAL_PROOF"] = self._extract_first(credibility, ["social_proof_enhancement"], "")

        # Extract from market_enhancement
        market = intelligence_data.get("market_intelligence", {})
        if market:
            variables["MARKET_POSITIONING"] = self._extract_first(market, ["enhanced_positioning", "market_opportunities"], "")
            variables["COMPETITIVE_DIFFERENTIATION"] = self._extract_first(market, ["competitive_differentiation"], "")

        # Extract from authority_enhancement
        authority = intelligence_data.get("scientific_authority_intelligence", {})
        if authority:
            variables["EXPERTISE_MARKERS"] = self._extract_first(authority, ["expertise_markers", "authority_positioning"], "")
            variables["THOUGHT_LEADERSHIP"] = self._extract_first(authority, ["thought_leadership"], "")

        # Extract from content_enhancement
        content_enh = intelligence_data.get("content_intelligence", {})
        if content_enh:
            variables["ENHANCED_MESSAGING"] = self._extract_first(content_enh, ["enhanced_messaging", "optimized_ctas"], "")
            variables["KEY_MESSAGES"] = self._extract_first(content_enh, ["enhanced_messaging", "key_messages"],
                                                           self._extract_first(content, ["key_messages", "talking_points", "highlights"], "important information"))

        logger.info(f"✅ Extracted {len(variables)} intelligence variables (including {len([v for v in variables.values() if v])} with data)")
        logger.info(f"   📊 AI-enhanced variables: {sum(1 for k in variables.keys() if k in ['SCIENTIFIC_BACKING', 'EMOTIONAL_JOURNEY', 'TRUST_SIGNALS', 'MARKET_INSIGHTS', 'RESEARCH_VALIDATION'])}")
        return variables

    def _extract_from_basic_data(self, intelligence_data: Dict[str, Any], key: str) -> str:
        """Helper to extract from basic RAG data arrays"""
        value = intelligence_data.get(key, [])
        if isinstance(value, list) and len(value) > 0:
            return str(value[0])
        elif isinstance(value, str):
            return value
        return ""

    def _extract_first(self, data: Dict, keys: List[str], default: str) -> str:
        """Extract first available value from multiple possible keys"""
        for key in keys:
            value = data.get(key)
            if value:
                if isinstance(value, list) and len(value) > 0:
                    return str(value[0])
                elif isinstance(value, str):
                    return value
        return default

    def _get_content_template(
        self,
        content_type: ContentType,
        psychology_stage: SalesPsychologyStage
    ) -> str:
        """Get content-type specific prompt template"""

        if content_type == ContentType.EMAIL_SEQUENCE:
            return self._get_email_sequence_template(psychology_stage)
        elif content_type == ContentType.EMAIL:
            return self._get_single_email_template(psychology_stage)
        elif content_type == ContentType.SOCIAL_POST:
            return self._get_social_post_template(psychology_stage)
        elif content_type == ContentType.BLOG_ARTICLE:
            return self._get_blog_article_template(psychology_stage)
        elif content_type == ContentType.AD_COPY:
            return self._get_ad_copy_template(psychology_stage)
        elif content_type == ContentType.VIDEO_SCRIPT:
            return self._get_video_script_template(psychology_stage)
        else:
            return self._get_generic_template(psychology_stage)

    def _get_email_sequence_template(self, psychology_stage: SalesPsychologyStage) -> str:
        """
        Get 7-email sales psychology sequence template
        Implements framework from universal-sales-content-framework.md
        """

        return """
Generate a 7-email sales psychology sequence for {PRODUCT_NAME}.

=== CORE INTELLIGENCE ===
TARGET AUDIENCE: {TARGET_AUDIENCE}
PRIMARY BENEFIT: {PRIMARY_BENEFIT}
PAIN POINT: {PAIN_POINT}
EMOTIONAL TRIGGER: {EMOTIONAL_TRIGGER}
COMPETITIVE ADVANTAGE: {COMPETITIVE_ADVANTAGE}

=== AI-ENHANCED INTELLIGENCE (Use to add depth and variation) ===
SCIENTIFIC BACKING: {SCIENTIFIC_BACKING}
RESEARCH CREDIBILITY: {RESEARCH_CREDIBILITY}
EMOTIONAL JOURNEY: {EMOTIONAL_JOURNEY}
PSYCHOLOGICAL TRIGGERS: {PSYCHOLOGICAL_TRIGGERS}
TRUST SIGNALS: {TRUST_SIGNALS}
AUTHORITY MARKERS: {AUTHORITY_MARKERS}
SOCIAL PROOF: {SOCIAL_PROOF}
MARKET POSITIONING: {MARKET_POSITIONING}
COMPETITIVE DIFFERENTIATION: {COMPETITIVE_DIFFERENTIATION}
EXPERTISE MARKERS: {EXPERTISE_MARKERS}
THOUGHT LEADERSHIP: {THOUGHT_LEADERSHIP}
ENHANCED MESSAGING: {ENHANCED_MESSAGING}

IMPORTANT: Use the AI-enhanced intelligence above to create unique, data-driven emails that go beyond generic marketing copy. Incorporate scientific research, emotional insights, trust indicators, and market intelligence throughout the sequence.

CREATE 7 EMAILS FOLLOWING THIS PROVEN PSYCHOLOGY SEQUENCE:

**Email 1: Problem Agitation (Day 1)**
- Make the pain unbearable
- Amplify {PAIN_POINT} emotionally
- NO solution mentioned - pure problem agitation
- Subject: Create urgency around the problem
- CTA: "Click to discover the hidden cause..."

**Email 2: Problem Revelation (Day 3)**
- The "aha moment" - explain the real cause
- Reveal root cause of {PAIN_POINT}
- Position existing solutions as band-aids
- Build authority with {COMPETITIVE_ADVANTAGE}
- CTA: "Learn about the real solution..."

**Email 3: Solution Introduction (Day 5)**
- Hope and possibility
- Introduce {PRODUCT_NAME} as the missing piece
- Use {PRIMARY_BENEFIT} as the value proposition
- Share transformation story framework
- CTA: "See how {PRODUCT_NAME} works..."

**Email 4: Social Proof Explosion (Day 7)**
- Others like me are succeeding
- Multiple customer stories/testimonials
- Address specific objections
- Use credibility signals
- CTA: "Join thousands who chose {PRODUCT_NAME}..."

**Email 5: Urgency & Scarcity (Day 10)**
- Fear of missing out
- Limited time offer or bonus
- Emphasize consequences of inaction
- Use loss aversion triggers
- CTA: "Claim your {PRODUCT_NAME} before it's gone..."

**Email 6: Objection Crusher (Day 12)**
- Remove final barriers
- Address top 3 objections logically
- Use {GUARANTEE_TERMS} as risk reversal
- Provide emotional and logical rebuttals
- CTA: "Try {PRODUCT_NAME} risk-free today..."

**Email 7: Final Call (Day 14)**
- Now or never
- Recap the journey and transformation possible
- Final urgency push
- Paint picture of regret if they don't act
- CTA: "Get {PRODUCT_NAME} now - doors close at midnight..."

FORMAT: Return each email as:
EMAIL_1
SUBJECT: [compelling subject line]
BODY: [300-500 word email body]
SEND_DELAY: [timing]
PSYCHOLOGY_STAGE: [stage name]
---

REQUIREMENTS:
- Use {PRODUCT_NAME} consistently throughout - NEVER use placeholders
- Each email must follow its psychology stage precisely
- Include specific CTAs that match the stage
- Maintain {TONE} tone and {BRAND_VOICE} voice
- Focus on {EMOTIONAL_TRIGGER} to drive engagement
"""

    def _get_single_email_template(self, psychology_stage: SalesPsychologyStage) -> str:
        """Get template for single email"""

        stage_focus = {
            SalesPsychologyStage.PROBLEM_AWARENESS: "identifying and amplifying the problem",
            SalesPsychologyStage.PROBLEM_AGITATION: "making the pain unbearable",
            SalesPsychologyStage.SOLUTION_REVEAL: "introducing the solution",
            SalesPsychologyStage.BENEFIT_PROOF: "proving the benefits work",
            SalesPsychologyStage.SOCIAL_VALIDATION: "showing social proof",
            SalesPsychologyStage.URGENCY_CREATION: "creating urgency to act",
            SalesPsychologyStage.OBJECTION_HANDLING: "addressing objections",
            SalesPsychologyStage.CALL_TO_ACTION: "driving immediate action"
        }

        focus = stage_focus.get(psychology_stage, "engaging the reader")

        return f"""
Write a compelling marketing email for {{PRODUCT_NAME}} focused on {focus}.

PRODUCT: {{PRODUCT_NAME}}
TARGET AUDIENCE: {{TARGET_AUDIENCE}}
PRIMARY BENEFIT: {{PRIMARY_BENEFIT}}
PAIN POINT: {{PAIN_POINT}}
EMOTIONAL TRIGGER: {{EMOTIONAL_TRIGGER}}
COMPETITIVE ADVANTAGE: {{COMPETITIVE_ADVANTAGE}}

PSYCHOLOGY STAGE: {psychology_stage.value.replace('_', ' ').title()}

Create an email with:
1. Attention-grabbing subject line (under 60 characters)
2. Compelling opening hook
3. Body focused on {focus}
4. Strong call-to-action
5. Tone: {{TONE}}, Voice: {{BRAND_VOICE}}

The email should be 250-400 words, highly engaging, and drive the reader to take action.
"""

    def _get_social_post_template(self, psychology_stage: SalesPsychologyStage) -> str:
        """Get template for social media post"""

        return """
Create a high-engagement social media post for {PRODUCT_NAME}.

PRODUCT: {PRODUCT_NAME}
PRIMARY BENEFIT: {PRIMARY_BENEFIT}
TARGET AUDIENCE: {TARGET_AUDIENCE}
EMOTIONAL TRIGGER: {EMOTIONAL_TRIGGER}
TONE: {TONE}

PSYCHOLOGY STAGE: """ + psychology_stage.value.replace('_', ' ').title() + """

Create a post with:
1. Hook (first line must grab attention)
2. Value/benefit statement
3. Social proof or credibility element
4. Clear call-to-action
5. 3-5 relevant hashtags

Length: 100-150 words
Style: {BRAND_VOICE}
Goal: Drive engagement and clicks
"""

    def _get_blog_article_template(self, psychology_stage: SalesPsychologyStage) -> str:
        """Get template for blog article"""

        return """
Write an SEO-optimized blog article about {PRODUCT_NAME}.

PRODUCT: {PRODUCT_NAME}
PRIMARY BENEFIT: {PRIMARY_BENEFIT}
TARGET AUDIENCE: {TARGET_AUDIENCE}
PAIN POINT: {PAIN_POINT}
COMPETITIVE ADVANTAGE: {COMPETITIVE_ADVANTAGE}
KEY MESSAGES: {KEY_MESSAGES}

Create a comprehensive article with:
1. SEO-optimized title (H1)
2. Compelling introduction
3. Problem identification (using {PAIN_POINT})
4. Solution presentation ({PRODUCT_NAME})
5. Benefits and proof points
6. Social proof/testimonials
7. Strong conclusion with CTA

Length: 800-1200 words
Tone: {TONE}
Style: {BRAND_VOICE}
Include: Subheadings (H2, H3), bullet points, actionable insights
"""

    def _get_ad_copy_template(self, psychology_stage: SalesPsychologyStage) -> str:
        """Get template for ad copy - optimized for Google Ads responsive search ads"""

        return """
Create high-converting ad copy variations for {PRODUCT_NAME}.

=== PRODUCT INTELLIGENCE ===
PRODUCT: {PRODUCT_NAME}
PRIMARY BENEFIT: {PRIMARY_BENEFIT}
TARGET AUDIENCE: {TARGET_AUDIENCE}
PAIN POINT: {PAIN_POINT}
EMOTIONAL_TRIGGER: {EMOTIONAL_TRIGGER}
COMPETITIVE_ADVANTAGE: {COMPETITIVE_ADVANTAGE}
TONE: {TONE}
BRAND VOICE: {BRAND_VOICE}

=== AI-ENHANCED INTELLIGENCE ===
Scientific Backing: {SCIENTIFIC_BACKING}
Credibility Signals: {CREDIBILITY_SIGNALS}
Market Position: {MARKET_POSITIONING}
Emotional Journey: {EMOTIONAL_JOURNEY}
Authority Markers: {AUTHORITY_MARKERS}

=== AD COPY REQUIREMENTS ===
Generate {variation_count} complete ad variations. Each variation must include:

1. HEADLINES (3-5 per variation):
   - Each headline: 25-30 characters max
   - Use different angles: benefit-focused, curiosity-driven, urgency-based, social proof
   - Format: "Headline: [your headline text]"

2. DESCRIPTIONS (2-3 per variation):
   - Each description: 60-90 characters max
   - Expand on benefits, overcome objections, create desire
   - Format: "Description: [your description text]"

3. PRIMARY TEXT (1 per variation):
   - 100-125 characters
   - Compelling hook that combines {EMOTIONAL_TRIGGER} with {PRIMARY_BENEFIT}
   - Format: "Primary Text: [your primary text]"

4. CALL TO ACTION (1 per variation):
   - 10-15 characters max
   - Action-oriented and urgent
   - Format: "CTA: [your call to action]"

=== OUTPUT FORMAT ===
AD_1:
Headline: [25-30 chars]
Headline: [25-30 chars]
Headline: [25-30 chars]
Description: [60-90 chars]
Description: [60-90 chars]
Primary Text: [100-125 chars]
CTA: [10-15 chars]

AD_2:
[... same format ...]

=== CRITICAL REQUIREMENTS ===
- ALWAYS use "{PRODUCT_NAME}" exactly as shown - NEVER use placeholders
- All headlines MUST be under 30 characters
- All descriptions MUST be under 90 characters
- Focus on {TARGET_AUDIENCE} pain points and desires
- Leverage {COMPETITIVE_ADVANTAGE} to differentiate
- Use {TONE} tone consistently
- Drive action with urgency and benefit clarity
"""

    def _get_video_script_template(self, psychology_stage: SalesPsychologyStage) -> str:
        """Get template for video script"""

        return """
Write a video script for {PRODUCT_NAME}.

PRODUCT: {PRODUCT_NAME}
PRIMARY BENEFIT: {PRIMARY_BENEFIT}
TARGET AUDIENCE: {TARGET_AUDIENCE}
PAIN_POINT: {PAIN_POINT}
EMOTIONAL_TRIGGER: {EMOTIONAL_TRIGGER}

Create a 60-90 second video script with:
- 0-10s: Hook with surprising statistic or question
- 10-30s: Agitate {PAIN_POINT} using {EMOTIONAL_TRIGGER}
- 30-50s: Reveal {COMPETITIVE_ADVANTAGE}
- 50-70s: Introduce {PRODUCT_NAME} and {PRIMARY_BENEFIT}
- 70-90s: Strong CTA

Include: Visual cues, tone guidance, pacing notes
Style: {BRAND_VOICE}
"""

    def _get_generic_template(self, psychology_stage: SalesPsychologyStage) -> str:
        """Fallback generic template"""

        return """
Create marketing content for {PRODUCT_NAME}.

PRODUCT: {PRODUCT_NAME}
PRIMARY BENEFIT: {PRIMARY_BENEFIT}
TARGET AUDIENCE: {TARGET_AUDIENCE}
TONE: {TONE}
BRAND VOICE: {BRAND_VOICE}

Create compelling content that highlights {PRODUCT_NAME} benefits for {TARGET_AUDIENCE}.
Focus on {PRIMARY_BENEFIT} and maintain {TONE} tone.
"""

    def _build_prompt(
        self,
        template: str,
        variables: Dict[str, str],
        preferences: Dict[str, Any]
    ) -> str:
        """Build final prompt by substituting variables into template"""

        prompt = template

        # Substitute all variables
        for key, value in variables.items():
            placeholder = "{" + key + "}"
            prompt = prompt.replace(placeholder, str(value))

        # Substitute preference-based placeholders (like variation_count)
        if "{variation_count}" in prompt:
            variation_count = preferences.get("variation_count", 3)
            prompt = prompt.replace("{variation_count}", str(variation_count))

        # Add strong variation instructions to prevent repetitive content
        import time
        import random

        variation_seed = int(time.time() * 1000) % 10000  # More granular seed
        random.seed(variation_seed)

        # Randomly select different creative approaches
        opening_styles = [
            "Start with a compelling question",
            "Begin with a surprising statistic or fact",
            "Open with a relatable story or scenario",
            "Lead with a bold statement or declaration",
            "Start with a vivid sensory description",
            "Begin with a paradox or contradiction",
            "Open with a provocative 'what if' scenario"
        ]

        narrative_approaches = [
            "Use a problem-solution narrative arc",
            "Follow a before-after-bridge structure",
            "Use a storytelling approach with character journey",
            "Employ a data-driven logical progression",
            "Use emotional escalation and release pattern",
            "Follow a challenge-insight-transformation flow",
            "Use comparative contrast (old way vs new way)"
        ]

        selected_opening = random.choice(opening_styles)
        selected_narrative = random.choice(narrative_approaches)

        prompt += f"\n\n=== CRITICAL UNIQUENESS REQUIREMENTS (Seed: {variation_seed}) ==="
        prompt += f"\n\nOPENING STYLE FOR THIS SEQUENCE: {selected_opening}"
        prompt += f"\nNARRATIVE APPROACH FOR THIS SEQUENCE: {selected_narrative}"
        prompt += "\n\nMANDATORY VARIATION RULES:"
        prompt += "\n1. NEVER start emails with 'Have you ever...' - use completely different opening patterns"
        prompt += "\n2. Vary sentence structure dramatically - mix short punchy sentences with longer flowing ones"
        prompt += "\n3. Use different rhetorical devices: metaphors, analogies, questions, statements, stories"
        prompt += "\n4. Change the emotional tone between emails: urgent, hopeful, analytical, empathetic, confident"
        prompt += "\n5. Vary paragraph length and rhythm throughout the sequence"
        prompt += "\n6. Use different vocabulary and avoid repeating the same descriptive words"
        prompt += "\n7. Each email should feel like it was written by a different expert with a unique voice"
        prompt += f"\n8. Make this sequence COMPLETELY DIFFERENT from any previous generation (variation #{variation_seed})"

        # Add any additional preferences
        if preferences.get("additional_instructions"):
            prompt += f"\n\nADDITIONAL INSTRUCTIONS:\n{preferences['additional_instructions']}"

        if preferences.get("length"):
            prompt += f"\n\nTARGET LENGTH: {preferences['length']}"

        if preferences.get("style"):
            prompt += f"\n\nSTYLE REQUIREMENTS: {preferences['style']}"

        return prompt.strip()

    def _build_system_message(self, content_type: ContentType, variables: Dict[str, str]) -> str:
        """Build system message to guide AI behavior"""

        product_name = variables.get("PRODUCT_NAME", "the product")
        brand_voice = variables.get("BRAND_VOICE", "professional")
        tone = variables.get("TONE", "conversational")

        return f"""You are an expert marketing copywriter specializing in {content_type.value} content.

CRITICAL RULES:
1. ALWAYS use the exact product name "{product_name}" - NEVER use placeholders like "Your Product", "[Product]", or generic terms
2. Maintain {brand_voice} brand voice and {tone} tone throughout
3. Focus on benefits and emotional triggers, not just features
4. Use proven sales psychology and persuasion principles
5. Create content that drives specific actions
6. Be authentic, credible, and value-focused

Your goal is to create high-converting content that resonates with the target audience and drives measurable results."""

    def _calculate_prompt_quality(self, prompt: str, variables: Dict[str, str]) -> int:
        """Calculate prompt quality score (0-100)"""

        score = 0

        # Check prompt length (should be substantial)
        if len(prompt) > 500:
            score += 20
        elif len(prompt) > 200:
            score += 10

        # Check variable utilization
        variables_used = sum(1 for var in variables.values() if var in prompt)
        utilization_ratio = variables_used / len(variables) if variables else 0
        score += int(utilization_ratio * 30)

        # Check for key elements
        if "TARGET AUDIENCE" in prompt or "target audience" in prompt.lower():
            score += 10
        if "PRIMARY BENEFIT" in prompt or "benefit" in prompt.lower():
            score += 10
        if "PAIN POINT" in prompt or "pain" in prompt.lower():
            score += 10
        if "EMOTIONAL" in prompt or "emotional" in prompt.lower():
            score += 10
        if "CTA" in prompt or "call-to-action" in prompt.lower() or "call to action" in prompt.lower():
            score += 10

        return min(score, 100)

    def get_supported_content_types(self) -> List[str]:
        """Get list of supported content types"""
        return [ct.value for ct in ContentType]

    def get_psychology_stages(self) -> List[str]:
        """Get list of psychology stages"""
        return [stage.value for stage in SalesPsychologyStage]
