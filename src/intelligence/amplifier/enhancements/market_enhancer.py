# src/intelligence/amplifier/enhancements/market_enhancer.py
"""
Generates comprehensive market analysis and competitive intelligence using ULTRA-CHEAP AI providers
FIXED: Removed duplicate AI calling methods, using centralized ai_throttle for consistency
UPDATED: Integrated with tiered AI provider system for 95-99% cost savings
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# FIXED: Import centralized AI throttling system
from ...utils.ai_throttle import safe_ai_call

logger = logging.getLogger(__name__)

class MarketIntelligenceEnhancer:
    """Generate comprehensive market intelligence and competitive analysis using ultra-cheap AI"""
    
    def __init__(self, ai_providers: List[Dict]):
        self.ai_providers = ai_providers
        self.available_provider = self._get_ultra_cheap_provider()
        
        # Log the ultra-cheap optimization status
        if self.available_provider:
            provider_name = self.available_provider.get("name", "unknown")
            cost_per_1k = self.available_provider.get("cost_per_1k_tokens", 0)
            quality_score = self.available_provider.get("quality_score", 0)
            
            logger.info(f"🚀 Market Enhancer using ULTRA-CHEAP provider: {provider_name}")
            logger.info(f"💰 Cost: ${cost_per_1k:.5f}/1K tokens (vs $0.030 OpenAI)")
            logger.info(f"🎯 Quality: {quality_score}/100")
            
            # Calculate savings
            openai_cost = 0.030
            if cost_per_1k > 0:
                savings_pct = ((openai_cost - cost_per_1k) / openai_cost) * 100
                logger.info(f"💎 SAVINGS: {savings_pct:.1f}% cost reduction!")
        else:
            logger.warning("⚠️ No ultra-cheap AI providers available for Market Enhancement")
        
    def _get_ultra_cheap_provider(self) -> Optional[Dict]:
        """Get the best ultra-cheap AI provider using tiered system priority"""
        
        if not self.ai_providers:
            logger.warning("⚠️ No AI providers available for market enhancement")
            return None
        
        # Sort by priority (lowest first = cheapest/fastest)
        sorted_providers = sorted(
            [p for p in self.ai_providers if p.get("available", False)],
            key=lambda x: x.get("priority", 999)
        )
        
        if not sorted_providers:
            logger.warning("⚠️ No available AI providers for market enhancement")
            return None
        
        # Use the highest priority (cheapest) provider
        selected_provider = sorted_providers[0]
        
        provider_name = selected_provider.get("name", "unknown")
        cost = selected_provider.get("cost_per_1k_tokens", 0)
        quality = selected_provider.get("quality_score", 0)
        
        logger.info(f"✅ Selected ultra-cheap provider for market enhancement:")
        logger.info(f"   Provider: {provider_name}")
        logger.info(f"   Cost: ${cost:.5f}/1K tokens")
        logger.info(f"   Quality: {quality}/100")
        logger.info(f"   Priority: {selected_provider.get('priority', 'unknown')}")
        
        return selected_provider
    
    async def _call_ultra_cheap_ai(self, prompt: str) -> Any:
        """
        FIXED: Call the ultra-cheap AI provider using centralized ai_throttle system
        This replaces the duplicate method and ensures consistent error handling
        """
        
        if not self.available_provider:
            raise Exception("No AI provider available")
            
        provider_name = self.available_provider["name"]
        client = self.available_provider["client"]
        
        # Create messages for the AI call
        messages = [
            {
                "role": "system",
                "content": "You are a market research expert providing strategic insights. Always respond with valid JSON when requested. Be thorough and analytical."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ]
        
        # Get the model name for this provider
        model_map = {
            "groq": "llama-3.3-70b-versatile",
            "together": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            "deepseek": "deepseek-chat",
            "anthropic": "claude-3-haiku-20240307",
            "cohere": "command-r-plus",
            "openai": "gpt-3.5-turbo"
        }
        
        model = model_map.get(provider_name, "gpt-3.5-turbo")
        
        # Make the safe AI call with automatic throttling and JSON validation
        result = await safe_ai_call(
            client=client,
            provider_name=provider_name,
            model=model,
            messages=messages,
            temperature=0.2,
            max_tokens=2000
        )
        
        # Handle fallback responses
        if isinstance(result, dict) and result.get("fallback"):
            logger.warning(f"⚠️ AI call returned fallback for {provider_name}")
            # Extract any useful fallback data
            if "fallback_data" in result:
                return result["fallback_data"]
            else:
                raise Exception("AI call failed and no fallback data available")
        
        return result
    
    async def generate_market_intelligence(
        self, 
        product_data: Dict[str, Any], 
        base_intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive market intelligence using ultra-cheap AI"""
        
        if not self.available_provider:
            logger.warning("🚨 No ultra-cheap providers available, using fallback")
            return self._generate_fallback_market_intelligence(product_data)
        
        try:
            # Log cost optimization start
            provider_name = self.available_provider.get("name", "unknown")
            logger.info(f"📈 Starting market intelligence generation with {provider_name}")
            
            # Extract product information
            product_name = product_data.get("product_name", "Product")
            offer_intel = base_intelligence.get("offer_intelligence", {})
            competitive_intel = base_intelligence.get("competitive_intelligence", {})
            
            # Generate market analysis using centralized AI system
            market_analysis = await self._generate_market_analysis(product_name, offer_intel)
            
            # Generate competitive landscape using centralized AI system
            competitive_landscape = await self._generate_competitive_landscape(product_name, competitive_intel)
            
            # Generate pricing analysis using centralized AI system
            pricing_analysis = await self._generate_pricing_analysis(product_name, offer_intel)
            
            # Generate target market insights using centralized AI system
            target_market = await self._generate_target_market_insights(product_name, offer_intel)
            
            # Generate market opportunities using centralized AI system
            market_opportunities = await self._generate_market_opportunities(product_name, competitive_intel)
            
            # Generate market positioning using centralized AI system
            market_positioning = await self._generate_market_positioning(product_name, offer_intel)
            
            # Calculate market intelligence score
            market_intelligence_score = self._calculate_market_intelligence_score(
                market_analysis, competitive_landscape, target_market
            )
            
            # Compile comprehensive market intelligence with ultra-cheap metadata
            market_intelligence = {
                "market_analysis": market_analysis,
                "competitive_landscape": competitive_landscape,
                "pricing_analysis": pricing_analysis,
                "target_market_insights": target_market,
                "market_opportunities": market_opportunities,
                "market_positioning": market_positioning,
                "market_intelligence_score": market_intelligence_score,
                "generated_at": datetime.utcnow().isoformat(),
                "ai_provider": provider_name,
                "enhancement_confidence": 0.82,
                "ultra_cheap_optimization": {
                    "provider_used": provider_name,
                    "cost_per_1k_tokens": self.available_provider.get("cost_per_1k_tokens", 0),
                    "quality_score": self.available_provider.get("quality_score", 0),
                    "provider_tier": self.available_provider.get("provider_tier", "unknown"),
                    "estimated_cost_savings_vs_openai": self._calculate_cost_savings(),
                    "speed_rating": self.available_provider.get("speed_rating", 0)
                }
            }
            
            # Log successful generation with cost data
            total_items = (
                len(market_analysis) if isinstance(market_analysis, dict) else 0 +
                len(competitive_landscape) if isinstance(competitive_landscape, dict) else 0 +
                len(pricing_analysis) if isinstance(pricing_analysis, dict) else 0 +
                len(target_market) if isinstance(target_market, dict) else 0 +
                len(market_opportunities) if isinstance(market_opportunities, dict) else 0 +
                len(market_positioning) if isinstance(market_positioning, dict) else 0
            )
            
            logger.info(f"✅ Market intelligence generated using {provider_name}")
            logger.info(f"📊 Generated {total_items} market items")
            logger.info(f"💰 Cost optimization: {self._calculate_cost_savings():.1f}% savings")
            
            return market_intelligence
            
        except Exception as e:
            logger.error(f"❌ Ultra-cheap market intelligence generation failed: {str(e)}")
            logger.info("🔄 Falling back to static market intelligence")
            return self._generate_fallback_market_intelligence(product_data)
    
    def _calculate_cost_savings(self) -> float:
        """Calculate cost savings percentage vs OpenAI"""
        try:
            openai_cost = 0.030  # OpenAI GPT-4 cost per 1K tokens
            provider_cost = self.available_provider.get("cost_per_1k_tokens", openai_cost)
            
            if provider_cost >= openai_cost:
                return 0.0
            
            savings_pct = ((openai_cost - provider_cost) / openai_cost) * 100
            return min(savings_pct, 99.9)  # Cap at 99.9%
            
        except Exception:
            return 0.0
    
    async def _generate_market_analysis(
        self, 
        product_name: str, 
        offer_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate market analysis intelligence using centralized AI system
        """
        
        # Extract relevant data from offer intelligence
        value_props = offer_intel.get("value_propositions", [])
        pricing_info = offer_intel.get("pricing", [])
        
        prompt = f"""
        As a market research analyst, analyze the market for a product called "{product_name}".
        
        Product value propositions: {json.dumps(value_props, indent=2)}
        Pricing information: {json.dumps(pricing_info, indent=2)}
        
        Generate comprehensive market analysis including:
        1. Market size estimation and trends
        2. Growth potential and projections
        3. Market dynamics and drivers
        4. Regulatory environment considerations
        5. Market barriers and challenges
        6. Seasonal patterns and cycles
        
        Format as JSON:
        {{
            "market_size": {{
                "current_estimate": "market size description",
                "growth_rate": "annual growth rate",
                "market_value": "estimated market value"
            }},
            "market_trends": ["trend1", "trend2", "trend3"],
            "growth_drivers": ["driver1", "driver2", "driver3"],
            "market_challenges": ["challenge1", "challenge2"],
            "regulatory_environment": ["regulation1", "regulation2"],
            "seasonal_patterns": ["pattern1", "pattern2"],
            "market_dynamics": ["dynamic1", "dynamic2"]
        }}
        """
        
        try:
            logger.info(f"📊 Generating market analysis with {self.available_provider.get('name')}")
            market_analysis = await self._call_ultra_cheap_ai(prompt)
            
            # Handle string responses
            if isinstance(market_analysis, str):
                try:
                    market_analysis = json.loads(market_analysis)
                except:
                    logger.warning("⚠️ Could not parse market analysis as JSON, using fallback")
                    return self._fallback_market_analysis(product_name)
            
            result = market_analysis if isinstance(market_analysis, dict) else {}
            logger.info(f"✅ Generated market analysis with {len(result)} categories")
            return result
            
        except Exception as e:
            logger.error(f"❌ Market analysis generation failed: {str(e)}")
            return self._fallback_market_analysis(product_name)
    
    async def _generate_competitive_landscape(
        self, 
        product_name: str, 
        competitive_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate competitive landscape analysis using centralized AI system"""
        
        existing_competitors = competitive_intel.get("competitors", [])
        
        prompt = f"""
        As a competitive intelligence analyst, analyze the competitive landscape for "{product_name}".
        
        Existing competitor information: {json.dumps(existing_competitors, indent=2)}
        
        Generate competitive landscape analysis including:
        1. Competitor categories and segments
        2. Market positioning analysis
        3. Competitive advantages and disadvantages
        4. Market share considerations
        5. Competitive threats and opportunities
        
        Format as JSON:
        {{
            "competitor_categories": ["direct", "indirect", "substitute"],
            "market_positioning": ["position1", "position2"],
            "competitive_advantages": ["advantage1", "advantage2"],
            "competitive_threats": ["threat1", "threat2"],
            "market_share_insights": ["insight1", "insight2"],
            "differentiation_opportunities": ["opportunity1", "opportunity2"]
        }}
        """
        
        try:
            logger.info(f"🏁 Generating competitive landscape with {self.available_provider.get('name')}")
            competitive_landscape = await self._call_ultra_cheap_ai(prompt)
            
            # Handle string responses
            if isinstance(competitive_landscape, str):
                try:
                    competitive_landscape = json.loads(competitive_landscape)
                except:
                    logger.warning("⚠️ Could not parse competitive landscape as JSON, using fallback")
                    return self._fallback_competitive_landscape()
            
            result = competitive_landscape if isinstance(competitive_landscape, dict) else {}
            logger.info(f"✅ Generated competitive landscape with {len(result)} categories")
            return result
            
        except Exception as e:
            logger.error(f"❌ Competitive landscape generation failed: {str(e)}")
            return self._fallback_competitive_landscape()
    
    async def _generate_pricing_analysis(
        self, 
        product_name: str, 
        offer_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate pricing analysis using centralized AI system"""
        
        pricing_info = offer_intel.get("pricing", [])
        value_props = offer_intel.get("value_propositions", [])
        
        prompt = f"""
        As a pricing strategist, analyze pricing for "{product_name}".
        
        Current pricing: {json.dumps(pricing_info, indent=2)}
        Value propositions: {json.dumps(value_props, indent=2)}
        
        Generate pricing analysis. Format as JSON:
        {{
            "pricing_strategy": ["strategy1", "strategy2"],
            "value_alignment": ["alignment1", "alignment2"],
            "competitive_pricing": ["comparison1", "comparison2"],
            "optimization_opportunities": ["opportunity1", "opportunity2"],
            "price_sensitivity_factors": ["factor1", "factor2"],
            "pricing_recommendations": ["recommendation1", "recommendation2"]
        }}
        """
        
        try:
            logger.info(f"💰 Generating pricing analysis with {self.available_provider.get('name')}")
            pricing_analysis = await self._call_ultra_cheap_ai(prompt)
            
            # Handle string responses
            if isinstance(pricing_analysis, str):
                try:
                    pricing_analysis = json.loads(pricing_analysis)
                except:
                    logger.warning("⚠️ Could not parse pricing analysis as JSON, using fallback")
                    return self._fallback_pricing_analysis()
            
            result = pricing_analysis if isinstance(pricing_analysis, dict) else {}
            logger.info(f"✅ Generated pricing analysis with {len(result)} categories")
            return result
            
        except Exception as e:
            logger.error(f"❌ Pricing analysis generation failed: {str(e)}")
            return self._fallback_pricing_analysis()
    
    async def _generate_target_market_insights(
        self, 
        product_name: str, 
        offer_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate target market insights using centralized AI system"""
        
        value_props = offer_intel.get("value_propositions", [])
        
        prompt = f"""
        As a market segmentation expert, analyze target market for "{product_name}".
        
        Product benefits: {json.dumps(value_props, indent=2)}
        
        Generate target market insights. Format as JSON:
        {{
            "primary_segments": ["segment1", "segment2", "segment3"],
            "demographics": ["demo1", "demo2"],
            "psychographics": ["psycho1", "psycho2"],
            "segment_sizes": ["size1", "size2"],
            "customer_journey": ["stage1", "stage2", "stage3"],
            "messaging_preferences": ["preference1", "preference2"],
            "market_entry_strategies": ["strategy1", "strategy2"]
        }}
        """