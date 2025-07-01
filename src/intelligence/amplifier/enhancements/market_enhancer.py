# src/intelligence/amplifier/enhancements/market_enhancer.py
"""
Generates comprehensive market analysis and competitive intelligence using AI
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re

logger = logging.getLogger(__name__)

class MarketIntelligenceEnhancer:
    """Generate comprehensive market intelligence and competitive analysis"""
    
    def __init__(self, ai_providers: List[Dict]):
        self.ai_providers = ai_providers
        self.available_provider = self._get_best_provider()
        
    def _get_best_provider(self) -> Optional[Dict]:
        """Get the best available AI provider - prefer OpenAI for stability"""
    
    # Prefer OpenAI first (working perfectly)
        for provider in self.ai_providers:
            if provider.get("name") == "openai" and provider.get("available"):
                logger.info("🚀 Using OpenAI for enhancement")
            return provider
    
    # Fallback to Cohere second
        for provider in self.ai_providers:
            if provider.get("name") == "cohere" and provider.get("available"):
                logger.info("💫 Using Cohere for enhancement") 
            return provider
    
    # Fallback to Claude third (has API issues currently)
        for provider in self.ai_providers:
            if provider.get("name") == "anthropic" and provider.get("available"):
                logger.info("🤖 Using Claude for enhancement")
            return provider
    
        logger.warning("⚠️ No AI providers available for enhancement")
        return None
        
        # Prefer OpenAI for content and messaging
        for provider in self.ai_providers:
            if provider.get("name") == "openai" and provider.get("available"):
                logger.info("📝 Using OpenAI for content enhancement")
                return provider
        
        # Fallback to Anthropic Claude
        for provider in self.ai_providers:
            if provider.get("name") == "anthropic" and provider.get("available"):
                logger.info("📝 Using Anthropic Claude for content enhancement")
                return provider
        
        logger.warning("⚠️ No AI providers available for content enhancement")
        return None
        
        # Prefer OpenAI for market analysis and competitive intelligence
        for provider in self.ai_providers:
            if provider.get("name") == "openai" and provider.get("available"):
                logger.info("📊 Using OpenAI for market intelligence enhancement")
                return provider
        
        # Fallback to Anthropic Claude
        for provider in self.ai_providers:
            if provider.get("name") == "anthropic" and provider.get("available"):
                logger.info("📊 Using Anthropic Claude for market intelligence enhancement")
                return provider
        
        logger.warning("⚠️ No AI providers available for market intelligence")
        return None
    
    async def generate_market_intelligence(
        self, 
        product_data: Dict[str, Any], 
        base_intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive market intelligence"""
        
        if not self.available_provider:
            return self._generate_fallback_market_intelligence(product_data)
        
        try:
            # Extract product information
            product_name = product_data.get("product_name", "Product")
            offer_intel = base_intelligence.get("offer_intelligence", {})
            competitive_intel = base_intelligence.get("competitive_intelligence", {})
            
            # Generate market size and trends
            market_analysis = await self._generate_market_analysis(product_name, offer_intel)
            
            # Generate competitive landscape
            competitive_landscape = await self._generate_competitive_landscape(product_name, competitive_intel)
            
            # Generate pricing analysis
            pricing_analysis = await self._generate_pricing_analysis(product_name, offer_intel)
            
            # Generate target market insights
            target_market = await self._generate_target_market_insights(product_name, offer_intel)
            
            # Generate market opportunities
            market_opportunities = await self._generate_market_opportunities(product_name, competitive_intel)
            
            # Generate market positioning
            market_positioning = await self._generate_market_positioning(product_name, offer_intel)
            
            # Compile comprehensive market intelligence
            market_intelligence = {
                "market_analysis": market_analysis,
                "competitive_landscape": competitive_landscape,
                "pricing_analysis": pricing_analysis,
                "target_market_insights": target_market,
                "market_opportunities": market_opportunities,
                "market_positioning": market_positioning,
                "market_intelligence_score": self._calculate_market_intelligence_score(
                    market_analysis, competitive_landscape, target_market
                ),
                "generated_at": datetime.utcnow().isoformat(),
                "ai_provider": self.available_provider.get("name"),
                "enhancement_confidence": 0.82
            }
            
            logger.info(f"✅ Generated market intelligence for {product_name}")
            return market_intelligence
            
        except Exception as e:
            logger.error(f"❌ Market intelligence generation failed: {str(e)}")
            return self._generate_fallback_market_intelligence(product_data)
    
    async def _generate_market_analysis(
        self, 
        product_name: str, 
        offer_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate market size and trends analysis"""
        
        # Determine market category
        market_category = self._determine_market_category(product_name, offer_intel)
        
        prompt = f"""
        As a market research analyst, provide comprehensive market analysis for the {market_category} category, specifically for products like "{product_name}".
        
        Product context:
        {json.dumps(offer_intel, indent=2)}
        
        Provide market analysis including:
        1. Market size estimates and growth trends
        2. Key market drivers and challenges
        3. Consumer behavior trends
        4. Market segmentation insights
        5. Future market projections
        
        Format as JSON:
        {{
            "market_size": {{"current_estimate": "text", "growth_rate": "text"}},
            "market_drivers": ["driver1", "driver2", "driver3"],
            "market_challenges": ["challenge1", "challenge2"],
            "consumer_trends": ["trend1", "trend2", "trend3"],
            "market_segments": ["segment1", "segment2"],
            "future_projections": ["projection1", "projection2"]
        }}
        
        Provide realistic market analysis based on industry knowledge:
        """
        
        try:
            market_analysis = await self._call_ai_provider(prompt)
            
            if isinstance(market_analysis, str):
                market_analysis = json.loads(market_analysis)
            
            return market_analysis if isinstance(market_analysis, dict) else {}
            
        except Exception as e:
            logger.error(f"❌ Market analysis generation failed: {str(e)}")
            return self._fallback_market_analysis(market_category)
    
    async def _generate_competitive_landscape(
        self, 
        product_name: str, 
        competitive_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate competitive landscape analysis"""
        
        prompt = f"""
        As a competitive intelligence analyst, analyze the competitive landscape for products like "{product_name}".
        
        Existing competitive intelligence:
        {json.dumps(competitive_intel, indent=2)}
        
        Provide competitive landscape analysis including:
        1. Key competitor categories and types
        2. Competitive advantages in the market
        3. Market differentiation strategies
        4. Competitive gaps and opportunities
        5. Barrier to entry analysis
        
        Format as JSON:
        {{
            "competitor_categories": ["category1", "category2"],
            "competitive_advantages": ["advantage1", "advantage2", "advantage3"],
            "differentiation_strategies": ["strategy1", "strategy2"],
            "competitive_gaps": ["gap1", "gap2", "gap3"],
            "market_barriers": ["barrier1", "barrier2"],
            "opportunity_areas": ["opportunity1", "opportunity2"]
        }}
        
        Focus on actionable competitive insights:
        """
        
        try:
            competitive_landscape = await self._call_ai_provider(prompt)
            
            if isinstance(competitive_landscape, str):
                competitive_landscape = json.loads(competitive_landscape)
            
            return competitive_landscape if isinstance(competitive_landscape, dict) else {}
            
        except Exception as e:
            logger.error(f"❌ Competitive landscape generation failed: {str(e)}")
            return self._fallback_competitive_landscape()
    
    async def _generate_pricing_analysis(
        self, 
        product_name: str, 
        offer_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate pricing strategy analysis"""
        
        existing_pricing = offer_intel.get("pricing", [])
        
        prompt = f"""
        As a pricing strategist, analyze pricing strategies for products like "{product_name}".
        
        Current pricing information:
        {json.dumps(existing_pricing, indent=2)}
        
        Provide pricing analysis including:
        1. Pricing strategy types in this market
        2. Price positioning opportunities
        3. Value-based pricing considerations
        4. Competitive pricing insights
        5. Pricing optimization recommendations
        
        Format as JSON:
        {{
            "pricing_strategies": ["strategy1", "strategy2", "strategy3"],
            "price_positioning": ["premium", "mid-market", "value"],
            "value_propositions": ["value1", "value2"],
            "competitive_pricing": ["insight1", "insight2"],
            "optimization_recommendations": ["rec1", "rec2", "rec3"]
        }}
        
        Focus on actionable pricing insights:
        """
        
        try:
            pricing_analysis = await self._call_ai_provider(prompt)
            
            if isinstance(pricing_analysis, str):
                pricing_analysis = json.loads(pricing_analysis)
            
            return pricing_analysis if isinstance(pricing_analysis, dict) else {}
            
        except Exception as e:
            logger.error(f"❌ Pricing analysis generation failed: {str(e)}")
            return self._fallback_pricing_analysis()
    
    async def _generate_target_market_insights(
        self, 
        product_name: str, 
        offer_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate target market and customer insights"""
        
        prompt = f"""
        As a customer insights analyst, analyze the target market for products like "{product_name}".
        
        Product information:
        {json.dumps(offer_intel, indent=2)}
        
        Provide target market insights including:
        1. Primary customer segments
        2. Customer demographics and psychographics
        3. Customer pain points and motivations
        4. Purchase decision factors
        5. Customer journey insights
        
        Format as JSON:
        {{
            "customer_segments": ["segment1", "segment2", "segment3"],
            "demographics": ["demo1", "demo2"],
            "psychographics": ["psycho1", "psycho2"],
            "pain_points": ["pain1", "pain2", "pain3"],
            "motivations": ["motivation1", "motivation2"],
            "decision_factors": ["factor1", "factor2", "factor3"],
            "customer_journey": ["stage1", "stage2", "stage3"]
        }}
        
        Focus on actionable customer insights:
        """
        
        try:
            target_market = await self._call_ai_provider(prompt)
            
            if isinstance(target_market, str):
                target_market = json.loads(target_market)
            
            return target_market if isinstance(target_market, dict) else {}
            
        except Exception as e:
            logger.error(f"❌ Target market analysis generation failed: {str(e)}")
            return self._fallback_target_market_insights()
    
    async def _generate_market_opportunities(
        self, 
        product_name: str, 
        competitive_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate market opportunities analysis"""
        
        existing_opportunities = competitive_intel.get("opportunities", [])
        
        prompt = f"""
        As a market opportunity analyst, identify market opportunities for products like "{product_name}".
        
        Existing competitive opportunities:
        {json.dumps(existing_opportunities, indent=2)}
        
        Provide market opportunity analysis including:
        1. Emerging market trends and opportunities
        2. Underserved market segments
        3. Product innovation opportunities
        4. Channel and distribution opportunities
        5. Partnership and collaboration opportunities
        
        Format as JSON:
        {{
            "emerging_trends": ["trend1", "trend2", "trend3"],
            "underserved_segments": ["segment1", "segment2"],
            "innovation_opportunities": ["innovation1", "innovation2", "innovation3"],
            "channel_opportunities": ["channel1", "channel2"],
            "partnership_opportunities": ["partnership1", "partnership2"],
            "market_expansion": ["expansion1", "expansion2"]
        }}
        
        Focus on actionable market opportunities:
        """
        
        try:
            market_opportunities = await self._call_ai_provider(prompt)
            
            if isinstance(market_opportunities, str):
                market_opportunities = json.loads(market_opportunities)
            
            return market_opportunities if isinstance(market_opportunities, dict) else {}
            
        except Exception as e:
            logger.error(f"❌ Market opportunities generation failed: {str(e)}")
            return self._fallback_market_opportunities()
    
    async def _generate_market_positioning(
        self, 
        product_name: str, 
        offer_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate market positioning strategy"""
        
        value_props = offer_intel.get("value_propositions", [])
        
        prompt = f"""
        As a brand positioning strategist, develop market positioning strategy for "{product_name}".
        
        Current value propositions:
        {json.dumps(value_props, indent=2)}
        
        Provide positioning strategy including:
        1. Positioning statement options
        2. Unique value proposition development
        3. Brand differentiation strategies
        4. Market positioning pillars
        5. Competitive positioning advantages
        
        Format as JSON:
        {{
            "positioning_statements": ["statement1", "statement2"],
            "unique_value_props": ["uvp1", "uvp2", "uvp3"],
            "differentiation_strategies": ["strategy1", "strategy2"],
            "positioning_pillars": ["pillar1", "pillar2", "pillar3"],
            "competitive_advantages": ["advantage1", "advantage2"],
            "brand_attributes": ["attribute1", "attribute2", "attribute3"]
        }}
        
        Focus on strategic positioning insights:
        """
        
        try:
            market_positioning = await self._call_ai_provider(prompt)
            
            if isinstance(market_positioning, str):
                market_positioning = json.loads(market_positioning)
            
            return market_positioning if isinstance(market_positioning, dict) else {}
            
        except Exception as e:
            logger.error(f"❌ Market positioning generation failed: {str(e)}")
            return self._fallback_market_positioning()
    
    async def _call_ai_provider(self, prompt: str) -> Any:
        """Call the available AI provider"""
        
        if self.available_provider["name"] == "anthropic":
            response = await self.available_provider["client"].messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return response.content[0].text
            
        elif self.available_provider["name"] == "openai":
            response = await self.available_provider["client"].chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a market research analyst providing strategic insights. Always respond with valid JSON when requested."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content
        
        else:
            raise Exception("No supported AI provider available")
    
    def _determine_market_category(self, product_name: str, offer_intel: Dict[str, Any]) -> str:
        """Determine market category for analysis"""
        
        product_name_lower = product_name.lower()
        content = str(offer_intel).lower()
        
        if "liver" in product_name_lower or "hepato" in product_name_lower:
            return "liver health supplements"
        elif "weight" in content or "fat" in content or "burn" in content:
            return "weight management supplements"
        elif "energy" in content or "metabolism" in content:
            return "energy and metabolism supplements"
        elif "detox" in content or "cleanse" in content:
            return "detoxification supplements"
        elif "health" in content or "wellness" in content:
            return "health and wellness supplements"
        else:
            return "dietary supplements"
    
    def _calculate_market_intelligence_score(
        self, 
        market_analysis: Dict[str, Any], 
        competitive_landscape: Dict[str, Any], 
        target_market: Dict[str, Any]
    ) -> float:
        """Calculate market intelligence quality score"""
        
        score = 0.3  # Base score
        
        # Market analysis score
        if market_analysis:
            score += min(len(market_analysis) * 0.08, 0.25)
        
        # Competitive landscape score
        if competitive_landscape:
            score += min(len(competitive_landscape) * 0.06, 0.20)
        
        # Target market score
        if target_market:
            score += min(len(target_market) * 0.05, 0.25)
        
        return min(score, 1.0)
    
    # Fallback methods
    def _generate_fallback_market_intelligence(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback market intelligence"""
        
        product_name = product_data.get("product_name", "Product")
        market_category = self._determine_market_category(product_name, {})
        
        return {
            "market_analysis": self._fallback_market_analysis(market_category),
            "competitive_landscape": self._fallback_competitive_landscape(),
            "pricing_analysis": self._fallback_pricing_analysis(),
            "target_market_insights": self._fallback_target_market_insights(),
            "market_opportunities": self._fallback_market_opportunities(),
            "market_positioning": self._fallback_market_positioning(),
            "market_intelligence_score": 0.65,
            "generated_at": datetime.utcnow().isoformat(),
            "ai_provider": "fallback",
            "enhancement_confidence": 0.65
        }
    
    def _fallback_market_analysis(self, market_category: str) -> Dict[str, Any]:
        """Fallback market analysis"""
        
        return {
            "market_size": {
                "current_estimate": f"Multi-billion dollar {market_category} market",
                "growth_rate": "Steady growth projected at 5-8% annually"
            },
            "market_drivers": [
                "Increasing health consciousness among consumers",
                "Growing awareness of preventive healthcare",
                "Aging population seeking wellness solutions",
                "Rising disposable income for health products"
            ],
            "market_challenges": [
                "Regulatory compliance and scrutiny",
                "Market saturation in some segments",
                "Consumer skepticism about health claims"
            ],
            "consumer_trends": [
                "Preference for natural and organic ingredients",
                "Demand for transparency in product sourcing",
                "Interest in personalized health solutions",
                "Shift towards online purchasing channels"
            ],
            "market_segments": [
                "Health-conscious millennials",
                "Aging baby boomers",
                "Fitness enthusiasts",
                "Preventive health seekers"
            ],
            "future_projections": [
                "Continued growth in personalized nutrition",
                "Expansion of direct-to-consumer channels",
                "Integration of technology in health monitoring"
            ]
        }
    
    def _fallback_competitive_landscape(self) -> Dict[str, Any]:
        """Fallback competitive landscape"""
        
        return {
            "competitor_categories": [
                "Established pharmaceutical companies",
                "Specialized supplement brands",
                "Direct-to-consumer wellness companies",
                "Multi-level marketing health companies"
            ],
            "competitive_advantages": [
                "Scientific research and clinical validation",
                "Premium ingredient sourcing and quality",
                "Strong brand reputation and trust",
                "Innovative product formulations"
            ],
            "differentiation_strategies": [
                "Evidence-based marketing approach",
                "Transparent ingredient disclosure",
                "Personalized customer experience",
                "Professional healthcare partnerships"
            ],
            "competitive_gaps": [
                "Limited scientific backing in mass market",
                "Poor customer education and support",
                "Generic formulations without innovation",
                "Inadequate digital marketing presence"
            ],
            "market_barriers": [
                "High regulatory compliance costs",
                "Significant marketing investment requirements",
                "Established brand loyalty in market"
            ],
            "opportunity_areas": [
                "Evidence-based positioning",
                "Educational content marketing",
                "Professional healthcare channel partnerships"
            ]
        }
    
    def _fallback_pricing_analysis(self) -> Dict[str, Any]:
        """Fallback pricing analysis"""
        
        return {
            "pricing_strategies": [
                "Premium pricing for quality positioning",
                "Value-based pricing tied to health outcomes",
                "Subscription model for customer retention",
                "Bundle pricing for comprehensive solutions"
            ],
            "price_positioning": ["premium", "mid-market", "value"],
            "value_propositions": [
                "Superior ingredient quality justifies premium pricing",
                "Clinical research backing supports higher price point",
                "Comprehensive health solution provides better value"
            ],
            "competitive_pricing": [
                "Premium segment allows for higher margins",
                "Value segment requires cost optimization",
                "Subscription models improve customer lifetime value"
            ],
            "optimization_recommendations": [
                "Test price sensitivity with different customer segments",
                "Implement dynamic pricing based on demand",
                "Develop value-tier product offerings",
                "Consider geographic pricing strategies"
            ]
        }
    
    def _fallback_target_market_insights(self) -> Dict[str, Any]:
        """Fallback target market insights"""
        
        return {
            "customer_segments": [
                "Health-conscious professionals aged 30-50",
                "Fitness enthusiasts and athletes",
                "Individuals with specific health concerns",
                "Preventive health seekers over 40"
            ],
            "demographics": [
                "Higher income households ($50K+ annually)",
                "College-educated consumers",
                "Urban and suburban residents"
            ],
            "psychographics": [
                "Values quality over price",
                "Seeks evidence-based solutions",
                "Proactive about health management",
                "Willing to invest in long-term wellness"
            ],
            "pain_points": [
                "Overwhelmed by supplement choices",
                "Skeptical about health claims",
                "Concerned about ingredient quality",
                "Difficulty tracking health improvements"
            ],
            "motivations": [
                "Desire to maintain optimal health",
                "Prevention of future health issues",
                "Improvement of energy and vitality"
            ],
            "decision_factors": [
                "Scientific evidence and research backing",
                "Product quality and ingredient transparency",
                "Brand reputation and trustworthiness",
                "Healthcare professional recommendations"
            ],
            "customer_journey": [
                "Problem recognition and health concern awareness",
                "Research and information gathering phase",
                "Product comparison and evaluation",
                "Purchase decision and trial period",
                "Usage experience and outcome assessment"
            ]
        }
    
    def _fallback_market_opportunities(self) -> Dict[str, Any]:
        """Fallback market opportunities"""
        
        return {
            "emerging_trends": [
                "Personalized nutrition based on genetic testing",
                "Integration of wearable health technology",
                "Sustainable and eco-friendly packaging",
                "Telehealth and remote health monitoring"
            ],
            "underserved_segments": [
                "Senior citizens seeking age-specific solutions",
                "Athletes requiring specialized performance nutrition",
                "Individuals with specific dietary restrictions"
            ],
            "innovation_opportunities": [
                "Novel delivery methods and formulations",
                "Combination products addressing multiple health areas",
                "Technology-enhanced tracking and monitoring",
                "Personalized dosing and recommendation systems"
            ],
            "channel_opportunities": [
                "Healthcare professional partnerships",
                "Corporate wellness program integrations",
                "Specialized online health platforms",
                "Subscription-based direct delivery models"
            ],
            "partnership_opportunities": [
                "Clinical research institutions",
                "Healthcare providers and clinics",
                "Fitness and wellness centers",
                "Technology companies for health tracking"
            ],
            "market_expansion": [
                "International market penetration",
                "Adjacent health and wellness categories",
                "Professional and clinical market segments"
            ]
        }
    
    def _fallback_market_positioning(self) -> Dict[str, Any]:
        """Fallback market positioning"""
        
        return {
            "positioning_statements": [
                "The science-backed health solution for discerning wellness seekers",
                "Premium quality supplements with clinically validated ingredients"
            ],
            "unique_value_props": [
                "Rigorous scientific research backing all product claims",
                "Premium ingredient sourcing with full transparency",
                "Personalized health solution approach",
                "Healthcare professional recommended formulations"
            ],
            "differentiation_strategies": [
                "Evidence-based marketing and education",
                "Superior ingredient quality and sourcing",
                "Comprehensive customer support and guidance"
            ],
            "positioning_pillars": [
                "Scientific credibility and research validation",
                "Premium quality and ingredient transparency",
                "Customer education and support excellence",
                "Professional healthcare partnerships"
            ],
            "competitive_advantages": [
                "Strong scientific foundation differentiates from competitors",
                "Premium positioning commands higher margins",
                "Educational approach builds customer trust and loyalty"
            ],
            "brand_attributes": [
                "Trustworthy and scientifically credible",
                "Premium quality and effective",
                "Educational and supportive",
                "Innovative and research-driven"
            ]
        }