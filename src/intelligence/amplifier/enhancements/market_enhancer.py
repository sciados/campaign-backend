# src/intelligence/amplifier/enhancements/market_enhancer.py
"""
Generates comprehensive market analysis and competitive intelligence using ULTRA-CHEAP AI providers
UPDATED: Integrated with tiered AI provider system for 95-99% cost savings
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re

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
            
            # Generate market size and trends using ultra-cheap AI
            market_analysis = await self._generate_market_analysis(product_name, offer_intel)
            
            # Generate competitive landscape using ultra-cheap AI
            competitive_landscape = await self._generate_competitive_landscape(product_name, competitive_intel)
            
            # Generate pricing analysis using ultra-cheap AI
            pricing_analysis = await self._generate_pricing_analysis(product_name, offer_intel)
            
            # Generate target market insights using ultra-cheap AI
            target_market = await self._generate_target_market_insights(product_name, offer_intel)
            
            # Generate market opportunities using ultra-cheap AI
            market_opportunities = await self._generate_market_opportunities(product_name, competitive_intel)
            
            # Generate market positioning using ultra-cheap AI
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
                len(market_analysis) + 
                len(competitive_landscape) + 
                len(pricing_analysis) +
                len(target_market) +
                len(market_opportunities) +
                len(market_positioning)
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