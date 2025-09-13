# =====================================
# File: src/intelligence/services/intelligence_content_service.py  
# =====================================

"""
Phase 1: 3-Step Intelligence-Driven Content Generation Service

Implements the strategic 3-step process:
1. Extract relevant data from intelligence database
2. Generate optimized prompts using extracted intelligence
3. Route to cost-effective AI providers for content generation

Integrates with existing intelligence schema and factory system.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
from uuid import UUID

from src.core.database.models import IntelligenceCore, ProductData, MarketData
from src.intelligence.repositories.intelligence_repository import IntelligenceRepository
from src.intelligence.models.intelligence_models import AnalysisResult, ProductInfo, MarketInfo
from src.intelligence.generators.factory import ContentGeneratorFactory, get_global_phase2_factory

logger = logging.getLogger(__name__)


class IntelligenceContentService:
    """Phase 1: 3-Step Intelligence-Driven Content Generation"""
    
    def __init__(self):
        self.intelligence_repo = IntelligenceRepository()
        self.factory = None  # Will be initialized on first use
        self._step_metrics = {
            "step1_extractions": 0,
            "step2_optimizations": 0,
            "step3_generations": 0,
            "total_cost": 0.0,
            "intelligence_utilization": 0.0
        }
    
    async def generate_intelligence_driven_content(
        self,
        content_type: str,
        user_id: str,
        company_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
        session = None
    ) -> Dict[str, Any]:
        """
        Main 3-step intelligence-driven content generation
        
        Args:
            content_type: Type of content to generate (email_sequence, social_posts, etc.)
            user_id: User identifier for intelligence lookup
            company_id: Optional company context
            campaign_id: Optional campaign context
            preferences: User preferences for generation
            session: Database session
            
        Returns:
            Enhanced content generation result with intelligence attribution
        """
        try:
            start_time = datetime.now(timezone.utc)
            
            # Initialize factory if needed
            if not self.factory:
                self.factory = await get_global_phase2_factory(db_session=session)
            
            logger.info(f"Starting 3-step intelligence-driven generation for {content_type}")
            
            # === STEP 1: Extract Intelligence Data ===
            logger.info("STEP 1: Extracting intelligence data...")
            intelligence_data = await self._step1_extract_intelligence_data(
                user_id=user_id,
                company_id=company_id,
                content_type=content_type,
                session=session
            )
            
            if not intelligence_data or not intelligence_data.get("intelligence_sources"):
                logger.warning("No intelligence data found, falling back to basic generation")
                return await self._fallback_basic_generation(content_type, preferences, session)
            
            # === STEP 2: Generate Optimized Prompt ===
            logger.info("STEP 2: Generating optimized prompt...")
            optimized_prompt = await self._step2_generate_optimized_prompt(
                intelligence_data=intelligence_data,
                content_type=content_type,
                preferences=preferences or {}
            )
            
            # === STEP 3: Generate Content with Cost Optimization ===
            logger.info("STEP 3: Generating content with cost optimization...")
            content_result = await self._step3_generate_content_optimized(
                prompt_data=optimized_prompt,
                content_type=content_type,
                intelligence_data=intelligence_data,
                user_id=user_id,
                campaign_id=campaign_id,
                session=session
            )
            
            # Track metrics
            generation_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._track_3step_metrics(intelligence_data, optimized_prompt, content_result, generation_time)
            
            # Enhanced response with 3-step traceability
            return {
                "success": True,
                "content_type": content_type,
                "content": content_result.get("content", {}),
                "intelligence_driven": True,
                "three_step_process": {
                    "step1_intelligence_sources": len(intelligence_data.get("intelligence_sources", [])),
                    "step2_prompt_optimization": optimized_prompt.get("optimization_score", 0),
                    "step3_generation_provider": content_result.get("metadata", {}).get("ai_optimization", {}).get("provider_used", "unknown")
                },
                "metadata": {
                    "generated_by": "3_step_intelligence_driven_service",
                    "intelligence_utilization": intelligence_data.get("intelligence_score", 0.0),
                    "prompt_optimization_score": optimized_prompt.get("optimization_score", 0.0),
                    "generation_cost": content_result.get("metadata", {}).get("ai_optimization", {}).get("generation_cost", 0.0),
                    "total_generation_time": generation_time,
                    "intelligence_sources_used": intelligence_data.get("source_count", 0),
                    "product_name": intelligence_data.get("product_name", "Unknown Product"),
                    "campaign_id": campaign_id,
                    "generated_at": start_time.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"3-step intelligence generation failed: {e}")
            return await self._fallback_basic_generation(content_type, preferences, session, error=str(e))
    
    async def _step1_extract_intelligence_data(
        self,
        user_id: str,
        company_id: Optional[str],
        content_type: str,
        session
    ) -> Dict[str, Any]:
        """
        STEP 1: Extract and prepare intelligence data for content generation
        
        Queries the intelligence database to find relevant product intelligence,
        market data, and research that will inform content creation.
        """
        try:
            self._step_metrics["step1_extractions"] += 1
            
            # Build filter criteria
            filters = {"user_id": user_id}
            if company_id:
                filters["company_id"] = company_id
            
            # Get recent high-quality intelligence
            intelligence_records = await self.intelligence_repo.find_all(
                session=session,
                filters=filters,
                limit=10,
                offset=0
            )
            
            if not intelligence_records:
                logger.warning(f"No intelligence found for user {user_id}")
                return {"intelligence_sources": [], "intelligence_score": 0.0}
            
            # Process and score intelligence records
            processed_intelligence = []
            total_confidence = 0.0
            primary_product_name = None
            
            for record in intelligence_records:
                # Extract complete intelligence data
                intelligence_item = {
                    "intelligence_id": record.id,
                    "product_name": record.product_name,
                    "source_url": record.source_url,
                    "confidence_score": record.confidence_score,
                    "analysis_method": record.analysis_method,
                    "created_at": record.created_at,
                    "product_data": self._extract_product_data(record.product_data),
                    "market_data": self._extract_market_data(record.market_data),
                    "research_links": self._extract_research_links(record.research_links)
                }
                
                processed_intelligence.append(intelligence_item)
                total_confidence += record.confidence_score or 0.0
                
                # Use highest confidence record for primary product name
                if not primary_product_name or (record.confidence_score or 0) > 0.7:
                    primary_product_name = record.product_name
            
            # Calculate intelligence utilization score
            avg_confidence = total_confidence / len(processed_intelligence) if processed_intelligence else 0.0
            intelligence_score = min(avg_confidence * (len(processed_intelligence) / 5), 1.0)  # Scale by number of sources
            
            extracted_data = {
                "intelligence_sources": processed_intelligence,
                "product_name": primary_product_name or "this product",
                "source_count": len(processed_intelligence),
                "intelligence_score": intelligence_score,
                "content_type_compatibility": self._assess_content_type_compatibility(processed_intelligence, content_type),
                "extraction_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"STEP 1 Complete: Extracted {len(processed_intelligence)} intelligence sources, score: {intelligence_score:.2f}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Step 1 intelligence extraction failed: {e}")
            return {"intelligence_sources": [], "intelligence_score": 0.0, "error": str(e)}
    
    async def _step2_generate_optimized_prompt(
        self,
        intelligence_data: Dict[str, Any],
        content_type: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        STEP 2: Generate optimized prompts using extracted intelligence
        
        Takes the intelligence data and creates highly targeted prompts that
        incorporate product insights, market positioning, and audience targeting.
        """
        try:
            self._step_metrics["step2_optimizations"] += 1
            
            product_name = intelligence_data.get("product_name", "this product")
            intelligence_sources = intelligence_data.get("intelligence_sources", [])
            
            # Extract key insights from intelligence
            insights = self._extract_key_insights(intelligence_sources)
            
            # Generate content-type specific optimized prompt
            if content_type in ["email_sequence", "email_campaign"]:
                prompt_data = await self._create_email_optimized_prompt(product_name, insights, preferences)
            elif content_type in ["social_posts", "social_media"]:
                prompt_data = await self._create_social_optimized_prompt(product_name, insights, preferences)
            elif content_type in ["ad_copy", "ads"]:
                prompt_data = await self._create_ad_copy_optimized_prompt(product_name, insights, preferences)
            elif content_type in ["blog_post", "article"]:
                prompt_data = await self._create_blog_optimized_prompt(product_name, insights, preferences)
            else:
                prompt_data = await self._create_generic_optimized_prompt(product_name, insights, preferences, content_type)
            
            # Calculate optimization score
            optimization_score = self._calculate_prompt_optimization_score(prompt_data, intelligence_data)
            
            result = {
                "optimized_prompt": prompt_data["prompt"],
                "system_message": prompt_data["system_message"],
                "prompt_strategy": prompt_data["strategy"],
                "intelligence_integration": prompt_data["intelligence_points"],
                "optimization_score": optimization_score,
                "content_type": content_type,
                "product_name": product_name,
                "optimization_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"STEP 2 Complete: Generated optimized prompt, optimization score: {optimization_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Step 2 prompt optimization failed: {e}")
            return {
                "optimized_prompt": f"Generate {content_type} content for {intelligence_data.get('product_name', 'a product')}",
                "system_message": f"You are an expert {content_type} creator.",
                "optimization_score": 0.0,
                "error": str(e)
            }
    
    async def _step3_generate_content_optimized(
        self,
        prompt_data: Dict[str, Any],
        content_type: str,
        intelligence_data: Dict[str, Any],
        user_id: str,
        campaign_id: Optional[str],
        session
    ) -> Dict[str, Any]:
        """
        STEP 3: Generate content using optimized prompts with cost-effective AI routing
        
        Uses the factory system to route to the most cost-effective AI provider
        while maintaining quality through intelligence-optimized prompts.
        """
        try:
            self._step_metrics["step3_generations"] += 1
            
            # Prepare generation parameters
            generation_params = {
                "content_type": content_type,
                "intelligence_data": intelligence_data,
                "preferences": {
                    "optimized_prompt": prompt_data.get("optimized_prompt"),
                    "system_message": prompt_data.get("system_message"),
                    "intelligence_driven": True,
                    "prompt_strategy": prompt_data.get("prompt_strategy"),
                    "optimization_score": prompt_data.get("optimization_score", 0.0)
                },
                "user_id": user_id,
                "campaign_id": campaign_id
            }
            
            # Generate using factory with enhanced routing
            content_result = await self.factory.generate_content(**generation_params)
            
            # Track cost metrics
            generation_cost = content_result.get("metadata", {}).get("ai_optimization", {}).get("generation_cost", 0.0)
            self._step_metrics["total_cost"] += generation_cost
            
            # Enhance result with step 3 metadata
            if "metadata" not in content_result:
                content_result["metadata"] = {}
            
            content_result["metadata"]["step3_optimization"] = {
                "cost_effective_routing": True,
                "prompt_optimization_used": True,
                "intelligence_integration": True,
                "optimization_score": prompt_data.get("optimization_score", 0.0),
                "generation_cost": generation_cost
            }
            
            logger.info(f"STEP 3 Complete: Generated content with cost ${generation_cost:.4f}")
            return content_result
            
        except Exception as e:
            logger.error(f"Step 3 content generation failed: {e}")
            return {
                "success": False,
                "content": {"error": "Content generation failed", "fallback": True},
                "metadata": {"step3_error": str(e), "fallback_used": True}
            }
    
    def _extract_product_data(self, product_data_relations) -> Dict[str, Any]:
        """Extract product data from database relations"""
        if not product_data_relations:
            return {}
        
        # Handle single or multiple product data records
        if isinstance(product_data_relations, list):
            product_data = product_data_relations[0] if product_data_relations else None
        else:
            product_data = product_data_relations
        
        if not product_data:
            return {}
        
        return {
            "features": product_data.features or [],
            "benefits": product_data.benefits or [],
            "ingredients": product_data.ingredients or [],
            "conditions": product_data.conditions or [],
            "usage_instructions": product_data.usage_instructions or []
        }
    
    def _extract_market_data(self, market_data_relations) -> Dict[str, Any]:
        """Extract market data from database relations"""
        if not market_data_relations:
            return {}
        
        # Handle single or multiple market data records
        if isinstance(market_data_relations, list):
            market_data = market_data_relations[0] if market_data_relations else None
        else:
            market_data = market_data_relations
        
        if not market_data:
            return {}
        
        return {
            "category": market_data.category,
            "positioning": market_data.positioning,
            "competitive_advantages": market_data.competitive_advantages or [],
            "target_audience": market_data.target_audience
        }
    
    def _extract_research_links(self, research_relations) -> List[Dict[str, Any]]:
        """Extract research links from database relations"""
        if not research_relations:
            return []
        
        research_items = []
        for relation in research_relations:
            if hasattr(relation, 'research') and relation.research:
                research_items.append({
                    "research_id": relation.research.id,
                    "content": relation.research.content,
                    "research_type": relation.research.research_type,
                    "relevance_score": relation.relevance_score,
                    "source_metadata": relation.research.source_metadata or {}
                })
        
        return research_items
    
    def _extract_key_insights(self, intelligence_sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract key insights from intelligence sources for prompt optimization"""
        insights = {
            "product_features": set(),
            "product_benefits": set(),
            "target_audiences": set(),
            "competitive_advantages": set(),
            "market_positioning": [],
            "usage_contexts": set(),
            "emotional_triggers": set(),
            "scientific_backing": []
        }
        
        for source in intelligence_sources:
            # Extract product insights
            product_data = source.get("product_data", {})
            insights["product_features"].update(product_data.get("features", []))
            insights["product_benefits"].update(product_data.get("benefits", []))
            insights["usage_contexts"].update(product_data.get("usage_instructions", []))
            
            # Extract market insights
            market_data = source.get("market_data", {})
            if market_data.get("target_audience"):
                insights["target_audiences"].add(market_data["target_audience"])
            insights["competitive_advantages"].update(market_data.get("competitive_advantages", []))
            if market_data.get("positioning"):
                insights["market_positioning"].append(market_data["positioning"])
            
            # Extract research insights
            for research in source.get("research_links", []):
                if research.get("research_type") == "scientific":
                    insights["scientific_backing"].append(research.get("content", ""))
                elif research.get("research_type") == "market":
                    # Extract emotional triggers from market research
                    content = research.get("content", "").lower()
                    if "trust" in content or "confidence" in content:
                        insights["emotional_triggers"].add("trust_building")
                    if "fear" in content or "worry" in content:
                        insights["emotional_triggers"].add("fear_based")
                    if "hope" in content or "aspiration" in content:
                        insights["emotional_triggers"].add("aspirational")
        
        # Convert sets to lists for JSON serialization
        return {
            "product_features": list(insights["product_features"])[:10],  # Top 10
            "product_benefits": list(insights["product_benefits"])[:10],
            "target_audiences": list(insights["target_audiences"])[:5],
            "competitive_advantages": list(insights["competitive_advantages"])[:8],
            "market_positioning": insights["market_positioning"][:3],
            "usage_contexts": list(insights["usage_contexts"])[:8],
            "emotional_triggers": list(insights["emotional_triggers"])[:5],
            "scientific_backing": [sb[:200] for sb in insights["scientific_backing"][:3]]  # Truncate for prompts
        }
    
    async def _create_email_optimized_prompt(
        self,
        product_name: str,
        insights: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create optimized prompt for email sequence generation"""
        
        # Build intelligence-informed prompt
        features_str = ", ".join(insights["product_features"][:5])
        benefits_str = ", ".join(insights["product_benefits"][:5])
        audience_str = ", ".join(insights["target_audiences"][:3]) or "health-conscious individuals"
        triggers_str = ", ".join(insights["emotional_triggers"][:3]) or "trust-building, aspirational"
        
        prompt = f"""Generate a comprehensive email sequence for {product_name} using the following intelligence-driven insights:

PRODUCT INTELLIGENCE:
- Key Features: {features_str}
- Primary Benefits: {benefits_str}
- Target Audience: {audience_str}
- Emotional Triggers: {triggers_str}

SEQUENCE REQUIREMENTS:
1. Create 5 strategic emails with diverse angles
2. Use the emotional triggers identified from market intelligence
3. Incorporate the specific features and benefits discovered
4. Tailor messaging to the identified target audience
5. Include compelling subject lines that reflect product insights

INTELLIGENCE-DRIVEN STRATEGY:
- Leverage the competitive advantages discovered in market research
- Reference usage contexts found in product analysis
- Build trust using scientific backing when available
- Address audience pain points identified in intelligence gathering

Create emails that feel personally crafted based on this deep product intelligence."""
        
        system_message = f"""You are an expert email marketing strategist with access to comprehensive product intelligence about {product_name}. 

Your task is to create email sequences that leverage deep insights about the product, its market positioning, target audience, and competitive advantages. Use the intelligence data to create highly targeted, personalized email content that resonates with the specific audience identified.

Focus on intelligence-driven personalization rather than generic email templates."""
        
        return {
            "prompt": prompt,
            "system_message": system_message,
            "strategy": "intelligence_driven_email_sequence",
            "intelligence_points": {
                "features_integrated": len(insights["product_features"][:5]),
                "benefits_integrated": len(insights["product_benefits"][:5]),
                "audience_targeting": len(insights["target_audiences"][:3]),
                "emotional_triggers": len(insights["emotional_triggers"][:3])
            }
        }
    
    async def _create_social_optimized_prompt(
        self,
        product_name: str,
        insights: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create optimized prompt for social media content"""
        
        benefits_str = ", ".join(insights["product_benefits"][:4])
        audience_str = ", ".join(insights["target_audiences"][:2]) or "health-conscious social media users"
        positioning_str = insights["market_positioning"][0] if insights["market_positioning"] else "innovative health solution"
        
        prompt = f"""Create engaging social media content for {product_name} based on intelligence-driven insights:

MARKET INTELLIGENCE:
- Product Positioning: {positioning_str}
- Core Benefits: {benefits_str}
- Target Audience: {audience_str}
- Usage Contexts: {', '.join(insights["usage_contexts"][:3])}

CONTENT STRATEGY:
1. Create 5 diverse social media posts optimized for different platforms
2. Use audience insights to tailor tone and messaging
3. Incorporate specific benefits discovered through intelligence analysis
4. Leverage market positioning insights for competitive differentiation
5. Include platform-specific optimization (hashtags, mentions, etc.)

INTELLIGENCE-DRIVEN APPROACH:
- Reference specific usage contexts identified in product research
- Use competitive advantages as unique selling points
- Create content that resonates with the identified target demographic
- Incorporate emotional triggers that testing has shown to be effective

Generate content that demonstrates deep product knowledge and audience understanding."""
        
        return {
            "prompt": prompt,
            "system_message": f"You are a social media strategist with deep intelligence about {product_name}, its market position, and target audience. Create content that leverages these insights for maximum engagement.",
            "strategy": "intelligence_driven_social_content",
            "intelligence_points": {
                "benefits_integrated": len(insights["product_benefits"][:4]),
                "positioning_used": len(insights["market_positioning"][:1]),
                "audience_targeting": len(insights["target_audiences"][:2]),
                "usage_contexts": len(insights["usage_contexts"][:3])
            }
        }
    
    async def _create_ad_copy_optimized_prompt(
        self,
        product_name: str,
        insights: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create optimized prompt for ad copy generation"""
        
        advantages_str = ", ".join(insights["competitive_advantages"][:4])
        benefits_str = ", ".join(insights["product_benefits"][:3])
        triggers_str = ", ".join(insights["emotional_triggers"][:2])
        
        prompt = f"""Create high-converting ad copy for {product_name} using intelligence-driven market insights:

COMPETITIVE INTELLIGENCE:
- Competitive Advantages: {advantages_str}
- Proven Benefits: {benefits_str}
- Effective Emotional Triggers: {triggers_str}

AD COPY REQUIREMENTS:
1. Create multiple ad variations with different psychological angles
2. Lead with competitive advantages discovered through market analysis
3. Use emotional triggers that intelligence shows are effective for this audience
4. Include compelling headlines that highlight unique positioning
5. Create urgency using insights about customer decision-making patterns

INTELLIGENCE-DRIVEN STRATEGY:
- Differentiate using specific competitive advantages identified
- Appeal to emotions that market research shows resonate with target audience
- Use benefit language that mirrors how customers actually describe the product
- Include social proof elements suggested by market intelligence

Generate ad copy that leverages deep market and competitive intelligence."""
        
        return {
            "prompt": prompt,
            "system_message": f"You are an expert ad copywriter with comprehensive competitive intelligence about {product_name}. Use market insights to create highly targeted, conversion-optimized ad copy.",
            "strategy": "intelligence_driven_ad_copy",
            "intelligence_points": {
                "competitive_advantages": len(insights["competitive_advantages"][:4]),
                "benefits_integrated": len(insights["product_benefits"][:3]),
                "emotional_triggers": len(insights["emotional_triggers"][:2])
            }
        }
    
    async def _create_blog_optimized_prompt(
        self,
        product_name: str,
        insights: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create optimized prompt for blog content"""
        
        scientific_backing = "; ".join(insights["scientific_backing"][:2])
        features_str = ", ".join(insights["product_features"][:6])
        positioning_str = insights["market_positioning"][0] if insights["market_positioning"] else "comprehensive health solution"
        
        prompt = f"""Create an authoritative blog post about {product_name} using intelligence-gathered insights:

RESEARCH INTELLIGENCE:
- Scientific Backing: {scientific_backing}
- Product Features: {features_str}
- Market Positioning: {positioning_str}

CONTENT STRATEGY:
1. Create an informative, authority-building blog post
2. Integrate scientific research discovered through intelligence gathering
3. Reference specific product features with detailed explanations
4. Use market positioning insights to establish credibility
5. Include actionable information that demonstrates product expertise

INTELLIGENCE-DRIVEN APPROACH:
- Lead with scientific credibility when research supports claims
- Explain features in context of their researched benefits
- Use market positioning to establish thought leadership
- Include specific usage contexts identified in product intelligence
- Reference competitive landscape insights for balanced perspective

Create content that showcases deep product knowledge and research-backed authority."""
        
        return {
            "prompt": prompt,
            "system_message": f"You are a content strategist and researcher with comprehensive intelligence about {product_name}, including scientific research, market analysis, and competitive insights. Create authoritative content that demonstrates this expertise.",
            "strategy": "intelligence_driven_blog_content",
            "intelligence_points": {
                "scientific_backing": len(insights["scientific_backing"][:2]),
                "features_detailed": len(insights["product_features"][:6]),
                "market_positioning": len(insights["market_positioning"][:1])
            }
        }
    
    async def _create_generic_optimized_prompt(
        self,
        product_name: str,
        insights: Dict[str, Any],
        preferences: Dict[str, Any],
        content_type: str
    ) -> Dict[str, Any]:
        """Create generic optimized prompt for other content types"""
        
        benefits_str = ", ".join(insights["product_benefits"][:5])
        audience_str = ", ".join(insights["target_audiences"][:2]) or "target audience"
        
        prompt = f"""Create {content_type} content for {product_name} using intelligence-driven insights:

PRODUCT INTELLIGENCE:
- Key Benefits: {benefits_str}
- Target Audience: {audience_str}
- Competitive Advantages: {', '.join(insights["competitive_advantages"][:3])}

Create content that leverages these insights for maximum relevance and impact."""
        
        return {
            "prompt": prompt,
            "system_message": f"You are an expert content creator with intelligence about {product_name}. Use these insights to create targeted {content_type} content.",
            "strategy": f"intelligence_driven_{content_type}",
            "intelligence_points": {
                "benefits_integrated": len(insights["product_benefits"][:5]),
                "audience_targeting": len(insights["target_audiences"][:2])
            }
        }
    
    def _calculate_prompt_optimization_score(
        self,
        prompt_data: Dict[str, Any],
        intelligence_data: Dict[str, Any]
    ) -> float:
        """Calculate optimization score for the generated prompt"""
        
        score = 0.0
        max_score = 100.0
        
        # Intelligence integration score (40 points)
        intelligence_points = prompt_data.get("intelligence_points", {})
        intelligence_score = sum(intelligence_points.values()) * 5  # 5 points per integration
        score += min(intelligence_score, 40)
        
        # Intelligence data quality score (30 points)
        intel_score = intelligence_data.get("intelligence_score", 0.0)
        score += intel_score * 30
        
        # Prompt length and complexity (20 points)
        prompt_length = len(prompt_data.get("optimized_prompt", ""))
        if prompt_length > 500:
            score += 20
        elif prompt_length > 300:
            score += 15
        elif prompt_length > 200:
            score += 10
        
        # Strategy specificity (10 points)
        if prompt_data.get("strategy") and "intelligence_driven" in prompt_data.get("strategy", ""):
            score += 10
        
        return min(score / max_score, 1.0)
    
    def _assess_content_type_compatibility(
        self,
        intelligence_sources: List[Dict[str, Any]],
        content_type: str
    ) -> float:
        """Assess how well the intelligence data matches the content type"""
        
        if not intelligence_sources:
            return 0.0
        
        compatibility_score = 0.0
        
        # Check if intelligence has relevant data for content type
        for source in intelligence_sources:
            product_data = source.get("product_data", {})
            market_data = source.get("market_data", {})
            
            if content_type in ["email_sequence", "email_campaign"]:
                # Email benefits from benefits, features, and audience data
                if product_data.get("benefits"):
                    compatibility_score += 0.3
                if market_data.get("target_audience"):
                    compatibility_score += 0.3
                if product_data.get("features"):
                    compatibility_score += 0.2
            
            elif content_type in ["social_posts", "social_media"]:
                # Social benefits from benefits and positioning
                if product_data.get("benefits"):
                    compatibility_score += 0.4
                if market_data.get("positioning"):
                    compatibility_score += 0.3
                if market_data.get("target_audience"):
                    compatibility_score += 0.2
            
            elif content_type in ["ad_copy", "ads"]:
                # Ads benefit from competitive advantages and benefits
                if market_data.get("competitive_advantages"):
                    compatibility_score += 0.4
                if product_data.get("benefits"):
                    compatibility_score += 0.3
                if market_data.get("target_audience"):
                    compatibility_score += 0.2
            
            else:
                # Generic compatibility
                if product_data.get("benefits") or product_data.get("features"):
                    compatibility_score += 0.5
                if market_data.get("target_audience") or market_data.get("positioning"):
                    compatibility_score += 0.3
        
        return min(compatibility_score / len(intelligence_sources), 1.0)
    
    async def _track_3step_metrics(
        self,
        intelligence_data: Dict[str, Any],
        prompt_data: Dict[str, Any],
        content_result: Dict[str, Any],
        generation_time: float
    ):
        """Track metrics for 3-step process"""
        
        # Update utilization score
        intel_score = intelligence_data.get("intelligence_score", 0.0)
        self._step_metrics["intelligence_utilization"] = (
            self._step_metrics["intelligence_utilization"] * 0.9 + intel_score * 0.1
        )
        
        # Log comprehensive metrics
        logger.info(f"3-Step Process Metrics:")
        logger.info(f"  Step 1 Extractions: {self._step_metrics['step1_extractions']}")
        logger.info(f"  Step 2 Optimizations: {self._step_metrics['step2_optimizations']}")
        logger.info(f"  Step 3 Generations: {self._step_metrics['step3_generations']}")
        logger.info(f"  Total Cost: ${self._step_metrics['total_cost']:.4f}")
        logger.info(f"  Intelligence Utilization: {self._step_metrics['intelligence_utilization']:.2f}")
        logger.info(f"  Generation Time: {generation_time:.2f}s")
    
    async def _fallback_basic_generation(
        self,
        content_type: str,
        preferences: Optional[Dict[str, Any]],
        session,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fallback to basic factory generation when intelligence is unavailable"""
        
        try:
            if not self.factory:
                self.factory = await get_global_phase2_factory(db_session=session)
            
            # Basic intelligence data for fallback
            fallback_intelligence = {
                "product_name": "this product",
                "source_title": "Generic Product",
                "intelligence_score": 0.0,
                "fallback_reason": error or "no_intelligence_available"
            }
            
            result = await self.factory.generate_content(
                content_type=content_type,
                intelligence_data=fallback_intelligence,
                preferences=preferences or {}
            )
            
            # Mark as fallback
            if "metadata" not in result:
                result["metadata"] = {}
            result["metadata"]["intelligence_driven"] = False
            result["metadata"]["fallback_used"] = True
            result["metadata"]["fallback_reason"] = error or "no_intelligence_available"
            
            return {
                "success": True,
                "content_type": content_type,
                "content": result.get("content", {}),
                "intelligence_driven": False,
                "fallback_used": True,
                "metadata": result.get("metadata", {})
            }
            
        except Exception as e:
            logger.error(f"Fallback generation also failed: {e}")
            return {
                "success": False,
                "content_type": content_type,
                "content": {"error": "All generation methods failed"},
                "intelligence_driven": False,
                "fallback_used": True,
                "error": str(e)
            }
    
    def get_service_metrics(self) -> Dict[str, Any]:
        """Get service performance metrics"""
        
        total_operations = (
            self._step_metrics["step1_extractions"] +
            self._step_metrics["step2_optimizations"] + 
            self._step_metrics["step3_generations"]
        )
        
        return {
            "service": "intelligence_content_service",
            "version": "1.0.0",
            "process": "3_step_intelligence_driven_generation",
            "metrics": {
                **self._step_metrics,
                "total_operations": total_operations,
                "avg_cost_per_generation": self._step_metrics["total_cost"] / max(self._step_metrics["step3_generations"], 1),
                "intelligence_utilization_score": self._step_metrics["intelligence_utilization"]
            },
            "process_description": {
                "step1": "Extract relevant intelligence data from database",
                "step2": "Generate optimized prompts using intelligence insights",
                "step3": "Route to cost-effective AI providers for content generation"
            }
        }


# Convenience function for direct usage
async def generate_intelligence_driven_content(
    content_type: str,
    user_id: str,
    company_id: Optional[str] = None,
    campaign_id: Optional[str] = None,
    preferences: Optional[Dict[str, Any]] = None,
    session = None
) -> Dict[str, Any]:
    """
    Direct function for 3-step intelligence-driven content generation
    
    Usage:
        result = await generate_intelligence_driven_content(
            content_type="email_sequence",
            user_id="user123",
            campaign_id="campaign456",
            session=db_session
        )
    """
    service = IntelligenceContentService()
    return await service.generate_intelligence_driven_content(
        content_type=content_type,
        user_id=user_id,
        company_id=company_id,
        campaign_id=campaign_id,
        preferences=preferences,
        session=session
    )