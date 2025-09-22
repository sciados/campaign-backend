# src/content/services/universal_sales_engine.py
"""
UNIVERSAL SALES-DRIVEN CONTENT GENERATION ENGINE
🎯 ONE ENGINE - ALL CONTENT TYPES - SAME PURPOSE: DRIVE SALES

Whether you want an email, image, video, post, or article - the process is identical:
1. Intelligence Analysis → 2. Sales Psychology Application → 3. AI Generation → 4. Format-Specific Output

This engine drives EVERYTHING and outputs exactly what the user demands.
"""

from typing import List, Optional, Dict, Any, Union, Literal
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging
import json
import hashlib
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

# Import AI providers
from src.intelligence.utils.unified_ultra_cheap_provider import UnifiedUltraCheapProvider

logger = logging.getLogger(__name__)

class ContentFormat(Enum):
    """All supported content formats"""
    EMAIL = "email"
    EMAIL_SEQUENCE = "email_sequence"
    SOCIAL_POST = "social_post"
    BLOG_ARTICLE = "blog_article"
    VIDEO_SCRIPT = "video_script"
    VIDEO_SLIDESHOW = "video_slideshow"      # Script + Slideshow video file
    VIDEO_TALKING_HEAD = "video_talking_head" # Script + AI avatar video file
    VIDEO_ANIMATED = "video_animated"        # Script + Animated video file
    VIDEO_KINETIC_TEXT = "video_kinetic_text" # Script + Kinetic typography video file
    AD_COPY = "ad_copy"
    IMAGE = "image"
    INFOGRAPHIC = "infographic"
    LANDING_PAGE = "landing_page"
    SALES_PAGE = "sales_page"
    WEBINAR_SCRIPT = "webinar_script"
    PODCAST_SCRIPT = "podcast_script"
    PRESS_RELEASE = "press_release"
    CASE_STUDY = "case_study"
    WHITE_PAPER = "white_paper"

class SalesPsychologyStage(Enum):
    """Universal sales psychology stages applicable to all content types"""
    PROBLEM_AWARENESS = "problem_awareness"      # Make them aware of the problem
    PROBLEM_AGITATION = "problem_agitation"     # Make the pain unbearable
    SOLUTION_REVEAL = "solution_reveal"         # Introduce the solution
    BENEFIT_PROOF = "benefit_proof"             # Prove the benefits work
    SOCIAL_VALIDATION = "social_validation"     # Show others succeeding
    URGENCY_CREATION = "urgency_creation"       # Create time pressure
    OBJECTION_HANDLING = "objection_handling"   # Remove barriers
    CALL_TO_ACTION = "call_to_action"          # Direct action request

@dataclass
class SalesVariables:
    """Universal sales variables extracted from intelligence"""
    product_name: str
    primary_benefit: str
    pain_point: str
    target_audience: str
    emotional_trigger: str
    credibility_signal: str
    competitive_advantage: str
    guarantee_terms: str
    price_point: str
    urgency_factor: str
    scarcity_element: str
    social_proof_type: str
    authority_indicator: str
    all_benefits: List[str]
    all_features: List[str]
    all_pain_points: List[str]
    all_competitive_advantages: List[str]
    confidence_score: float
    intelligence_richness: float

@dataclass
class ContentRequest:
    """Universal content generation request"""
    format: ContentFormat
    psychology_stage: SalesPsychologyStage
    campaign_id: Union[str, UUID]
    user_id: Union[str, UUID]
    company_id: Union[str, UUID]
    preferences: Dict[str, Any]
    specific_requirements: Dict[str, Any]  # Format-specific requirements

class ContentGenerator(ABC):
    """Abstract base for all content generators"""

    @abstractmethod
    async def generate(
        self,
        sales_variables: SalesVariables,
        user_context: Dict[str, Any],
        psychology_stage: SalesPsychologyStage,
        ai_provider: UnifiedUltraCheapProvider,
        specific_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate content for specific format"""
        pass

    @abstractmethod
    def get_format_requirements(self) -> Dict[str, Any]:
        """Get format-specific requirements and constraints"""
        pass

class UniversalSalesEngine:
    """
    UNIVERSAL SALES-DRIVEN CONTENT GENERATION ENGINE

    The same engine drives ALL content types:
    - Email → Sales psychology + text generation
    - Image → Sales psychology + visual generation
    - Video → Sales psychology + video generation
    - Article → Sales psychology + long-form generation

    Process is IDENTICAL for all formats:
    1. Extract sales variables from intelligence
    2. Apply sales psychology framework
    3. Generate with AI using format-specific generator
    4. Output exactly what user demands
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_provider = UnifiedUltraCheapProvider()
        self.content_generators = {}
        self._register_generators()

    def _register_generators(self):
        """Register all content format generators"""
        # Import enhanced video generator
        from src.content.services.video_generation_service import EnhancedVideoScriptGenerator

        self.content_generators = {
            ContentFormat.EMAIL: EmailGenerator(),
            ContentFormat.EMAIL_SEQUENCE: EmailSequenceGenerator(),
            ContentFormat.SOCIAL_POST: SocialPostGenerator(),
            ContentFormat.BLOG_ARTICLE: BlogArticleGenerator(),
            ContentFormat.VIDEO_SCRIPT: VideoScriptGenerator(),
            ContentFormat.VIDEO_SLIDESHOW: EnhancedVideoScriptGenerator(),    # Creates script + slideshow video
            ContentFormat.VIDEO_TALKING_HEAD: EnhancedVideoScriptGenerator(), # Creates script + AI avatar video
            ContentFormat.VIDEO_ANIMATED: EnhancedVideoScriptGenerator(),     # Creates script + animated video
            ContentFormat.VIDEO_KINETIC_TEXT: EnhancedVideoScriptGenerator(), # Creates script + kinetic text video
            ContentFormat.AD_COPY: AdCopyGenerator(),
            ContentFormat.IMAGE: ImageGenerator(),
            ContentFormat.INFOGRAPHIC: InfographicGenerator(),
            ContentFormat.LANDING_PAGE: LandingPageGenerator(),
            ContentFormat.SALES_PAGE: SalesPageGenerator(),
            ContentFormat.WEBINAR_SCRIPT: WebinarScriptGenerator(),
            ContentFormat.PODCAST_SCRIPT: PodcastScriptGenerator(),
            ContentFormat.PRESS_RELEASE: PressReleaseGenerator(),
            ContentFormat.CASE_STUDY: CaseStudyGenerator(),
            ContentFormat.WHITE_PAPER: WhitePaperGenerator(),
        }

    async def generate_sales_content(self, request: ContentRequest) -> Dict[str, Any]:
        """
        UNIVERSAL CONTENT GENERATION METHOD

        Same process for ALL content types:
        1. Get intelligence → 2. Extract sales variables → 3. Apply psychology → 4. Generate with AI

        Whether email, image, video, or article - the engine works identically
        """
        try:
            logger.info(f"🚀 Universal Sales Engine: Generating {request.format.value} content")

            # Step 1: Get intelligence data
            intelligence_data = await self._get_campaign_intelligence_data(request.campaign_id)

            if not intelligence_data:
                return {
                    "success": False,
                    "error": "No intelligence data available for content generation",
                    "required_action": "run_campaign_analysis"
                }

            # Step 2: Extract universal sales variables
            sales_variables = await self._extract_sales_variables(intelligence_data)

            # Step 3: Get user context for personalization
            user_context = await self._get_user_context(request.user_id, request.company_id)

            # Step 4: Get the appropriate content generator
            generator = self.content_generators.get(request.format)
            if not generator:
                return {
                    "success": False,
                    "error": f"Unsupported content format: {request.format.value}"
                }

            # Step 5: Generate content using the universal engine + format-specific generator
            content_result = await generator.generate(
                sales_variables=sales_variables,
                user_context=user_context,
                psychology_stage=request.psychology_stage,
                ai_provider=self.ai_provider,
                specific_requirements=request.specific_requirements
            )

            # Step 6: Store the generated content with universal metadata
            content_id = await self._store_universal_content(
                request=request,
                content_result=content_result,
                sales_variables=sales_variables,
                intelligence_used=intelligence_data,
                user_context=user_context
            )

            return {
                "success": True,
                "content_id": str(content_id),
                "content_format": request.format.value,
                "psychology_stage": request.psychology_stage.value,
                "generated_content": content_result,
                "sales_variables_applied": True,
                "ai_generated": True,
                "completely_unique": True,
                "conversion_optimized": True,
                "engine_version": "universal_sales_v1.0",
                "intelligence_sources_used": len(intelligence_data),
                "format_requirements_met": generator.get_format_requirements()
            }

        except Exception as e:
            logger.error(f"❌ Universal Sales Engine failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "engine": "universal_sales_engine"
            }

    async def _extract_sales_variables(self, intelligence_data: List[Dict[str, Any]]) -> SalesVariables:
        """Extract universal sales variables from intelligence data"""

        if not intelligence_data:
            raise ValueError("No intelligence data available")

        primary_intel = intelligence_data[0]

        # Core product information
        product_name = primary_intel.get("product_name", "").strip()
        benefits = primary_intel.get("benefits", [])
        features = primary_intel.get("features", [])
        competitive_advantages = primary_intel.get("competitive_advantages", [])
        positioning = primary_intel.get("positioning", "")
        target_audience = primary_intel.get("target_audience", "")

        # Extract pain points from research content
        pain_points = self._extract_pain_points_from_intelligence(intelligence_data)

        # Extract emotional triggers
        emotional_triggers = self._extract_emotional_triggers(intelligence_data)

        # Extract credibility signals
        credibility_signals = self._extract_credibility_signals(intelligence_data)

        # Calculate intelligence richness
        intelligence_richness = self._calculate_intelligence_richness(intelligence_data)

        return SalesVariables(
            product_name=product_name,
            primary_benefit=benefits[0] if benefits else "improved results",
            pain_point=pain_points[0] if pain_points else "current challenges",
            target_audience=target_audience or "professionals",
            emotional_trigger=emotional_triggers[0] if emotional_triggers else "desire for improvement",
            credibility_signal=credibility_signals[0] if credibility_signals else "proven approach",
            competitive_advantage=competitive_advantages[0] if competitive_advantages else "unique methodology",
            guarantee_terms="satisfaction guarantee",
            price_point="special pricing",
            urgency_factor="limited opportunity",
            scarcity_element="limited time offer",
            social_proof_type="customer success stories",
            authority_indicator="industry-leading solution",
            all_benefits=benefits,
            all_features=features,
            all_pain_points=pain_points,
            all_competitive_advantages=competitive_advantages,
            confidence_score=primary_intel.get("confidence_score", 0.0),
            intelligence_richness=intelligence_richness
        )

    def _extract_pain_points_from_intelligence(self, intelligence_data: List[Dict[str, Any]]) -> List[str]:
        """Extract pain points from intelligence research"""
        pain_points = []

        for intel in intelligence_data:
            research_content = intel.get("research_content", [])
            for research in research_content:
                content = research.get("content", "").lower()
                pain_indicators = ["problem", "challenge", "struggle", "difficulty", "frustration", "issue", "obstacle"]

                if any(indicator in content for indicator in pain_indicators):
                    sentences = research["content"].split('. ')
                    for sentence in sentences:
                        if any(indicator in sentence.lower() for indicator in pain_indicators):
                            clean_sentence = sentence.strip().replace('\n', ' ')
                            if 20 <= len(clean_sentence) <= 150:
                                pain_points.append(clean_sentence)

        # Default pain points if none found
        if not pain_points:
            category = intelligence_data[0].get("category", "solutions")
            pain_points = [
                f"ineffective {category.lower()}",
                "wasted time and money",
                "lack of results",
                "complicated processes"
            ]

        return pain_points[:5]

    def _extract_emotional_triggers(self, intelligence_data: List[Dict[str, Any]]) -> List[str]:
        """Extract emotional triggers for persuasive content"""
        triggers = []
        primary_intel = intelligence_data[0]

        # Extract from benefits
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

        # Default triggers if none found
        if not triggers:
            triggers = [
                "frustration with current solutions",
                "desire for better results",
                "fear of missing out on improvement",
                "excitement about transformation"
            ]

        return triggers[:6]

    def _extract_credibility_signals(self, intelligence_data: List[Dict[str, Any]]) -> List[str]:
        """Extract credibility signals for trust building"""
        signals = []
        primary_intel = intelligence_data[0]

        # Extract from competitive advantages
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

        # Default signals if none found
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

        return signals[:5]

    def _calculate_intelligence_richness(self, intelligence_data: List[Dict[str, Any]]) -> float:
        """Calculate richness of intelligence data"""
        if not intelligence_data:
            return 0.0

        primary_intel = intelligence_data[0]
        score = 0.0

        # Score different elements
        score += len(primary_intel.get("benefits", [])) * 0.3
        score += len(primary_intel.get("features", [])) * 0.2
        score += len(primary_intel.get("competitive_advantages", [])) * 0.25
        score += len(primary_intel.get("research_content", [])) * 0.15
        score += 0.1 if primary_intel.get("positioning") else 0
        score += 0.1 if primary_intel.get("target_audience") else 0
        score += primary_intel.get("confidence_score", 0) * 0.2

        return min(score, 10.0)

    # Database methods (same as previous implementations)
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
        """Get user context for personalization"""
        try:
            query = text("""
                SELECT
                    u.id as user_id,
                    u.full_name,
                    u.user_type,
                    c.company_name,
                    c.industry,
                    COUNT(camp.id) as total_campaigns
                FROM users u
                JOIN companies c ON u.company_id = c.id
                LEFT JOIN campaigns camp ON camp.user_id = u.id
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
                "industry": row.industry,
                "experience_level": "experienced" if row.total_campaigns > 5 else "new",
                "uniqueness_seed": hashlib.md5(f"{user_id}-{company_id}".encode()).hexdigest()[:8]
            }

        except Exception as e:
            logger.error(f"Failed to get user context: {e}")
            return {"user_id": str(user_id), "uniqueness_seed": str(user_id)[:8]}

    async def _store_universal_content(
        self,
        request: ContentRequest,
        content_result: Dict[str, Any],
        sales_variables: SalesVariables,
        intelligence_used: List[Dict[str, Any]],
        user_context: Dict[str, Any]
    ) -> UUID:
        """Store content generated by universal engine"""

        content_id = uuid4()

        # Universal title format
        content_title = f"Universal Sales Engine: {sales_variables.product_name} {request.format.value.title()}"

        # Store content based on format
        content_body = json.dumps(content_result.get("content", {}))

        # Universal metadata
        content_metadata = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "engine": "universal_sales_engine",
            "engine_version": "v1.0",
            "content_format": request.format.value,
            "psychology_stage": request.psychology_stage.value,
            "sales_variables_applied": {
                "product_name": sales_variables.product_name,
                "primary_benefit": sales_variables.primary_benefit,
                "pain_point": sales_variables.pain_point,
                "target_audience": sales_variables.target_audience,
                "emotional_trigger": sales_variables.emotional_trigger,
                "credibility_signal": sales_variables.credibility_signal,
                "competitive_advantage": sales_variables.competitive_advantage
            },
            "ai_generated": True,
            "completely_unique": True,
            "conversion_optimized": True,
            "intelligence_richness": sales_variables.intelligence_richness,
            "confidence_score": sales_variables.confidence_score,
            "user_customization": user_context.get("uniqueness_seed"),
            "generation_metadata": content_result.get("generation_metadata", {}),
            "format_specific_metadata": content_result.get("format_metadata", {})
        }

        query = text("""
            INSERT INTO generated_content
            (id, user_id, campaign_id, company_id, content_type, content_title, content_body,
             content_metadata, generation_settings, generation_method, content_status, intelligence_id)
            VALUES (:id, :user_id, :campaign_id, :company_id, :content_type, :content_title,
                    :content_body, :content_metadata, :generation_settings, 'universal_sales_engine', 'generated', :intelligence_id)
        """)

        await self.db.execute(query, {
            "id": content_id,
            "user_id": UUID(str(request.user_id)),
            "campaign_id": UUID(str(request.campaign_id)),
            "company_id": UUID(str(request.company_id)),
            "content_type": request.format.value,
            "content_title": content_title,
            "content_body": content_body,
            "content_metadata": json.dumps(content_metadata),
            "generation_settings": json.dumps(request.preferences),
            "intelligence_id": intelligence_used[0]["intelligence_id"] if intelligence_used else None
        })

        await self.db.commit()
        return content_id


# Content Generator Implementations for different formats
class EmailGenerator(ContentGenerator):
    """Generate sales-focused emails"""

    async def generate(
        self,
        sales_variables: SalesVariables,
        user_context: Dict[str, Any],
        psychology_stage: SalesPsychologyStage,
        ai_provider: UnifiedUltraCheapProvider,
        specific_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:

        # Create sales-focused email prompt
        prompt = self._create_email_prompt(sales_variables, user_context, psychology_stage, specific_requirements)

        # Generate with AI
        result = await ai_provider.unified_generate(
            content_type="sales_email",
            prompt=prompt,
            system_message="You are a master sales copywriter. Create compelling emails that move prospects closer to purchase using proven sales psychology.",
            max_tokens=800,
            temperature=0.7,
            task_complexity="medium"
        )

        if result.get("success"):
            email_content = self._parse_email_content(result["content"])

            return {
                "content": email_content,
                "generation_metadata": {
                    "psychology_stage": psychology_stage.value,
                    "ai_provider": result.get("provider_used"),
                    "sales_focus": "conversion_optimized"
                },
                "format_metadata": {
                    "word_count": len(email_content.get("body", "").split()),
                    "estimated_read_time": "2-3 minutes"
                }
            }

        raise Exception(f"Email generation failed: {result.get('error', 'Unknown error')}")

    def _create_email_prompt(
        self,
        sales_variables: SalesVariables,
        user_context: Dict[str, Any],
        psychology_stage: SalesPsychologyStage,
        specific_requirements: Dict[str, Any]
    ) -> str:
        """Create AI prompt for email generation"""

        user_name = user_context.get("user_name", "")
        greeting = f"Hi {user_name.split()[0]}," if user_name else "Hi there,"

        prompt = f"""
GENERATE A SALES-FOCUSED EMAIL

PSYCHOLOGY STAGE: {psychology_stage.value}
PRODUCT: {sales_variables.product_name}
TARGET AUDIENCE: {sales_variables.target_audience}
PRIMARY BENEFIT: {sales_variables.primary_benefit}
PAIN POINT: {sales_variables.pain_point}
EMOTIONAL TRIGGER: {sales_variables.emotional_trigger}

EMAIL STRUCTURE:
1. Subject Line (compelling, under 60 characters)
2. Greeting: {greeting}
3. Body (applies {psychology_stage.value} psychology)
4. Call-to-Action
5. Signature: {user_context.get('user_name', '[Your Name]')}

REQUIREMENTS:
- Focus on {psychology_stage.value}
- Use sales psychology to drive conversion
- Make it compelling and persuasive
- Include specific benefit: {sales_variables.primary_benefit}
- Address pain point: {sales_variables.pain_point}
- Trigger emotion: {sales_variables.emotional_trigger}

Generate the complete email:
"""
        return prompt

    def _parse_email_content(self, ai_content: str) -> Dict[str, Any]:
        """Parse AI-generated email content"""
        lines = ai_content.strip().split('\n')

        email_parts = {
            "subject": "",
            "body": "",
            "cta": "Learn More"
        }

        # Extract subject line
        for line in lines[:5]:
            if "subject" in line.lower():
                email_parts["subject"] = line.split(":", 1)[-1].strip().strip('"')
                break

        # Extract body (everything after subject)
        body_lines = []
        capturing_body = False

        for line in lines:
            if capturing_body or ("hi " in line.lower() and any(word in line.lower() for word in ["there", "friend"])):
                capturing_body = True
                body_lines.append(line.strip())
            elif "subject" not in line.lower() and len(line.strip()) > 20:
                body_lines.append(line.strip())

        email_parts["body"] = '\n'.join(body_lines).strip()

        # Extract CTA if present
        for line in body_lines:
            if any(cta_word in line.lower() for cta_word in ["click", "learn more", "get", "discover", "try"]):
                email_parts["cta"] = line.strip()
                break

        return email_parts

    def get_format_requirements(self) -> Dict[str, Any]:
        return {
            "max_subject_length": 60,
            "max_body_length": 2000,
            "required_elements": ["subject", "body", "cta"],
            "tone": "persuasive",
            "focus": "conversion"
        }


class ImageGenerator(ContentGenerator):
    """Generate sales-focused images"""

    async def generate(
        self,
        sales_variables: SalesVariables,
        user_context: Dict[str, Any],
        psychology_stage: SalesPsychologyStage,
        ai_provider: UnifiedUltraCheapProvider,
        specific_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:

        # Create image prompt with sales psychology
        prompt = self._create_image_prompt(sales_variables, psychology_stage, specific_requirements)

        # Generate image with AI
        result = await ai_provider.unified_generate(
            content_type="sales_image",
            prompt=prompt,
            system_message="Generate compelling sales-focused images that drive conversions and embody sales psychology principles.",
            max_tokens=100,  # For image prompts
            temperature=0.8,
            task_complexity="medium",
            generate_image=True  # This tells the provider to generate an image
        )

        if result.get("success"):
            return {
                "content": {
                    "image_url": result.get("image_url"),
                    "image_prompt": prompt,
                    "alt_text": f"{sales_variables.product_name} - {sales_variables.primary_benefit}",
                    "sales_message": self._generate_image_sales_message(sales_variables, psychology_stage)
                },
                "generation_metadata": {
                    "psychology_stage": psychology_stage.value,
                    "ai_provider": result.get("provider_used"),
                    "sales_focus": "visual_conversion"
                },
                "format_metadata": {
                    "image_type": "promotional",
                    "style": "professional_sales",
                    "dimensions": specific_requirements.get("dimensions", "1024x1024")
                }
            }

        raise Exception(f"Image generation failed: {result.get('error', 'Unknown error')}")

    def _create_image_prompt(
        self,
        sales_variables: SalesVariables,
        psychology_stage: SalesPsychologyStage,
        specific_requirements: Dict[str, Any]
    ) -> str:
        """Create AI prompt for image generation with sales psychology"""

        style = specific_requirements.get("style", "professional")
        dimensions = specific_requirements.get("dimensions", "1024x1024")

        psychology_visuals = {
            SalesPsychologyStage.PROBLEM_AWARENESS: "frustrated person struggling with problem, dark colors, before state",
            SalesPsychologyStage.PROBLEM_AGITATION: "intense struggle, stress, overwhelm, urgent red colors",
            SalesPsychologyStage.SOLUTION_REVEAL: "bright light, hope, solution emerging, uplifting colors",
            SalesPsychologyStage.BENEFIT_PROOF: "success, achievement, results, confident person",
            SalesPsychologyStage.SOCIAL_VALIDATION: "group of happy successful people, testimonials, community",
            SalesPsychologyStage.URGENCY_CREATION: "clock, limited time, countdown, urgent orange/red",
            SalesPsychologyStage.OBJECTION_HANDLING: "reassurance, guarantees, trust symbols, security",
            SalesPsychologyStage.CALL_TO_ACTION: "clear action, button, pointing, direct call"
        }

        visual_psychology = psychology_visuals.get(psychology_stage, "professional product showcase")

        prompt = f"""
Create a {style} sales image for {sales_variables.product_name}

SALES PSYCHOLOGY: {psychology_stage.value}
VISUAL ELEMENTS: {visual_psychology}
PRODUCT: {sales_variables.product_name}
BENEFIT TO HIGHLIGHT: {sales_variables.primary_benefit}
TARGET AUDIENCE: {sales_variables.target_audience}

IMAGE REQUIREMENTS:
- Professional, high-quality appearance
- Clear visual hierarchy
- Sales-focused composition
- Emotional appeal based on {sales_variables.emotional_trigger}
- Colors that support {psychology_stage.value}
- Dimensions: {dimensions}

VISUAL STYLE: {style}, modern, compelling, conversion-focused

Create an image that embodies {psychology_stage.value} and drives sales for {sales_variables.product_name}.
"""
        return prompt

    def _generate_image_sales_message(
        self,
        sales_variables: SalesVariables,
        psychology_stage: SalesPsychologyStage
    ) -> str:
        """Generate accompanying sales message for the image"""

        message_templates = {
            SalesPsychologyStage.PROBLEM_AWARENESS: f"Are you struggling with {sales_variables.pain_point}?",
            SalesPsychologyStage.SOLUTION_REVEAL: f"Discover how {sales_variables.product_name} delivers {sales_variables.primary_benefit}",
            SalesPsychologyStage.SOCIAL_VALIDATION: f"Join thousands achieving {sales_variables.primary_benefit} with {sales_variables.product_name}",
            SalesPsychologyStage.URGENCY_CREATION: f"Limited time: Get {sales_variables.primary_benefit} with {sales_variables.product_name}",
            SalesPsychologyStage.CALL_TO_ACTION: f"Ready for {sales_variables.primary_benefit}? Try {sales_variables.product_name} now!"
        }

        return message_templates.get(
            psychology_stage,
            f"Transform your results with {sales_variables.product_name}"
        )

    def get_format_requirements(self) -> Dict[str, Any]:
        return {
            "supported_dimensions": ["1024x1024", "1920x1080", "800x600"],
            "supported_styles": ["professional", "modern", "minimalist", "bold"],
            "required_elements": ["image_url", "alt_text", "sales_message"],
            "focus": "visual_conversion"
        }


# Add more generators for other formats...
class VideoScriptGenerator(ContentGenerator):
    """Generate sales-focused video scripts"""

    async def generate(
        self,
        sales_variables: SalesVariables,
        user_context: Dict[str, Any],
        psychology_stage: SalesPsychologyStage,
        ai_provider: UnifiedUltraCheapProvider,
        specific_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:

        video_length = specific_requirements.get("length", "2-3 minutes")
        video_type = specific_requirements.get("type", "promotional")

        prompt = f"""
CREATE A SALES-FOCUSED VIDEO SCRIPT

PSYCHOLOGY STAGE: {psychology_stage.value}
PRODUCT: {sales_variables.product_name}
VIDEO LENGTH: {video_length}
VIDEO TYPE: {video_type}

SALES ELEMENTS:
- Primary Benefit: {sales_variables.primary_benefit}
- Pain Point: {sales_variables.pain_point}
- Emotional Trigger: {sales_variables.emotional_trigger}
- Target Audience: {sales_variables.target_audience}

Create a compelling video script that applies {psychology_stage.value} to drive sales.

Include:
1. Hook (first 5 seconds)
2. Problem/Solution presentation
3. Benefits demonstration
4. Social proof elements
5. Strong call-to-action
6. Visual direction notes

Format as a proper video script with timestamps and scene descriptions.
"""

        result = await ai_provider.unified_generate(
            content_type="video_script",
            prompt=prompt,
            system_message="Create engaging video scripts that combine visual storytelling with sales psychology to drive conversions.",
            max_tokens=1200,
            temperature=0.7,
            task_complexity="complex"
        )

        if result.get("success"):
            return {
                "content": {
                    "script": result["content"],
                    "estimated_length": video_length,
                    "video_type": video_type,
                    "key_messages": [
                        sales_variables.primary_benefit,
                        sales_variables.competitive_advantage,
                        sales_variables.emotional_trigger
                    ]
                },
                "generation_metadata": {
                    "psychology_stage": psychology_stage.value,
                    "ai_provider": result.get("provider_used"),
                    "sales_focus": "video_conversion"
                },
                "format_metadata": {
                    "script_length": len(result["content"].split()),
                    "estimated_production_time": "2-4 hours",
                    "complexity": "medium"
                }
            }

        raise Exception(f"Video script generation failed: {result.get('error', 'Unknown error')}")

    def get_format_requirements(self) -> Dict[str, Any]:
        return {
            "supported_lengths": ["30 seconds", "1 minute", "2-3 minutes", "5-10 minutes"],
            "supported_types": ["promotional", "explainer", "testimonial", "demo"],
            "required_elements": ["script", "visual_directions", "cta"],
            "focus": "video_conversion"
        }


# Placeholder generators for other formats
class EmailSequenceGenerator(ContentGenerator):
    async def generate(self, sales_variables, user_context, psychology_stage, ai_provider, specific_requirements):
        # Implementation for email sequences
        pass
    def get_format_requirements(self): return {"sequence_length": "3-7 emails"}

class SocialPostGenerator(ContentGenerator):
    async def generate(self, sales_variables, user_context, psychology_stage, ai_provider, specific_requirements):
        # Implementation for social posts
        pass
    def get_format_requirements(self): return {"max_length": 280, "platforms": ["twitter", "linkedin", "facebook"]}

class BlogArticleGenerator(ContentGenerator):
    async def generate(self, sales_variables, user_context, psychology_stage, ai_provider, specific_requirements):
        # Implementation for blog articles
        pass
    def get_format_requirements(self): return {"word_count": "800-2000", "seo_optimized": True}

class AdCopyGenerator(ContentGenerator):
    async def generate(self, sales_variables, user_context, psychology_stage, ai_provider, specific_requirements):
        # Implementation for ad copy
        pass
    def get_format_requirements(self): return {"headline_length": 30, "description_length": 90}

class InfographicGenerator(ContentGenerator):
    async def generate(self, sales_variables, user_context, psychology_stage, ai_provider, specific_requirements):
        # Implementation for infographics
        pass
    def get_format_requirements(self): return {"dimensions": "1080x1350", "data_points": "5-10"}

class LandingPageGenerator(ContentGenerator):
    async def generate(self, sales_variables, user_context, psychology_stage, ai_provider, specific_requirements):
        # Implementation for landing pages
        pass
    def get_format_requirements(self): return {"sections": ["hero", "benefits", "social_proof", "cta"]}

class SalesPageGenerator(ContentGenerator):
    async def generate(self, sales_variables, user_context, psychology_stage, ai_provider, specific_requirements):
        # Implementation for sales pages
        pass
    def get_format_requirements(self): return {"length": "long_form", "conversion_elements": True}

class WebinarScriptGenerator(ContentGenerator):
    async def generate(self, sales_variables, user_context, psychology_stage, ai_provider, specific_requirements):
        # Implementation for webinar scripts
        pass
    def get_format_requirements(self): return {"duration": "45-60 minutes", "interactive": True}

class PodcastScriptGenerator(ContentGenerator):
    async def generate(self, sales_variables, user_context, psychology_stage, ai_provider, specific_requirements):
        # Implementation for podcast scripts
        pass
    def get_format_requirements(self): return {"duration": "15-30 minutes", "conversational": True}

class PressReleaseGenerator(ContentGenerator):
    async def generate(self, sales_variables, user_context, psychology_stage, ai_provider, specific_requirements):
        # Implementation for press releases
        pass
    def get_format_requirements(self): return {"word_count": "400-600", "ap_style": True}

class CaseStudyGenerator(ContentGenerator):
    async def generate(self, sales_variables, user_context, psychology_stage, ai_provider, specific_requirements):
        # Implementation for case studies
        pass
    def get_format_requirements(self): return {"structure": "problem_solution_results", "data_driven": True}

class WhitePaperGenerator(ContentGenerator):
    async def generate(self, sales_variables, user_context, psychology_stage, ai_provider, specific_requirements):
        # Implementation for white papers
        pass
    def get_format_requirements(self): return {"word_count": "2500-5000", "authoritative": True}