# FIXED: src/intelligence/utils/tiered_ai_provider.py
"""
Tiered AI Provider System
Default: Ultra-cheap providers (Groq, Together AI)
Premium: High-quality providers (Claude, OpenAI) for future paid tiers
FIXED: TieredProviderConfig attribute access issue
"""
import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ServiceTier(Enum):
    """Service tiers for AI provider selection"""
    FREE = "free"                    # Ultra-cheap providers only
    STANDARD = "standard"            # Balanced providers  
    PREMIUM = "premium"              # High-quality providers
    ENTERPRISE = "enterprise"        # All providers with priority routing

class ProviderTier(Enum):
    """Provider cost/quality tiers"""
    ULTRA_CHEAP = "ultra_cheap"      # $0.0001-0.001/1K tokens
    BUDGET = "budget"                # $0.001-0.005/1K tokens  
    BALANCED = "balanced"            # $0.005-0.015/1K tokens
    PREMIUM = "premium"              # $0.015+/1K tokens

@dataclass
class TieredProviderConfig:
    """Enhanced provider config with tier information"""
    name: str
    priority: int
    cost_per_1k_tokens: float
    quality_score: float
    speed_rating: int
    provider_tier: ProviderTier
    available_in_tiers: List[ServiceTier]
    api_key_env: str
    client_class: str
    model_name: str
    max_tokens: int
    rate_limit_rpm: int
    available: bool = False
    client: Any = None
    
    # 🔥 FIXED: Add 'tier' property to fix attribute access
    @property
    def tier(self) -> ProviderTier:
        """Alias for provider_tier to maintain compatibility"""
        return self.provider_tier

class TieredAIProviderManager:
    """
    Manages AI providers across different service tiers
    Optimizes for cost while allowing premium upgrades
    """
    
    def __init__(self, service_tier: ServiceTier = ServiceTier.FREE):
        self.service_tier = service_tier
        self.providers = []
        self.available_providers = []
        self.current_provider = None
        self.cost_tracking = {
            "total_requests": 0,
            "total_cost": 0.0,
            "cost_savings_vs_openai": 0.0,
            "tier_usage": {}
        }
        self._initialize_tiered_providers()
    
    def _initialize_tiered_providers(self):
        """Initialize providers optimized for ultra-cheap default tier"""

        # TIER 1: ULTRA-CHEAP (DEFAULT for FREE/STANDARD users)
        groq_config = TieredProviderConfig(
            name="groq",
            priority=1,
            cost_per_1k_tokens=0.0002,
            quality_score=78.0,
            speed_rating=10,
            provider_tier=ProviderTier.ULTRA_CHEAP,
            available_in_tiers=[ServiceTier.FREE, ServiceTier.STANDARD, ServiceTier.PREMIUM, ServiceTier.ENTERPRISE],
            api_key_env="GROQ_API_KEY",
            client_class="groq.AsyncGroq",
            # model_name="llama-3.3-70b-specdec",
            model_name="llama-3.3-70b-versatile",  # 🔥 UPDATED: Was llama-3.1-70b-versatile
            max_tokens=32000,
            rate_limit_rpm=30
        )

        # Alternative: Use the ultra-fast speculative decoding version
        # model_name="llama-3.3-70b-specdec",  # 6x faster version

        together_config = TieredProviderConfig(
            name="together",
            priority=2,
            cost_per_1k_tokens=0.0008,
            quality_score=82.0,
            speed_rating=7,
            provider_tier=ProviderTier.ULTRA_CHEAP,
            available_in_tiers=[ServiceTier.FREE, ServiceTier.STANDARD, ServiceTier.PREMIUM, ServiceTier.ENTERPRISE],
            api_key_env="TOGETHER_API_KEY",
            client_class="openai.AsyncOpenAI",
            model_name="meta-llama/Llama-3.1-70B-Instruct-Turbo",  # Together AI model
            max_tokens=32000,
            rate_limit_rpm=100
        )

        deepseek_config = TieredProviderConfig(
            name="deepseek",
            priority=3,
            cost_per_1k_tokens=0.00014,
            quality_score=72.0,
            speed_rating=6,
            provider_tier=ProviderTier.ULTRA_CHEAP,
            available_in_tiers=[ServiceTier.FREE, ServiceTier.STANDARD, ServiceTier.PREMIUM, ServiceTier.ENTERPRISE],
            api_key_env="DEEPSEEK_API_KEY",
            client_class="openai.AsyncOpenAI",
            model_name="deepseek-chat",  # Deepseek model
            max_tokens=16000,
            rate_limit_rpm=60
        )
        # TIER 2: BUDGET (Available for STANDARD+ users)
        fireworks_config = TieredProviderConfig(
            name="fireworks",
            priority=4,
            cost_per_1k_tokens=0.001,
            quality_score=80.0,
            speed_rating=8,
            provider_tier=ProviderTier.BUDGET,
            available_in_tiers=[ServiceTier.STANDARD, ServiceTier.PREMIUM, ServiceTier.ENTERPRISE],
            api_key_env="FIREWORKS_API_KEY",
            client_class="openai.AsyncOpenAI",
            model_name="accounts/fireworks/models/llama-v3-70b-instruct",
            max_tokens=16000,
            rate_limit_rpm=200
        )
        
        # TIER 3: BALANCED (Available for PREMIUM+ users)
        perplexity_config = TieredProviderConfig(
            name="perplexity",
            priority=5,
            cost_per_1k_tokens=0.002,
            quality_score=85.0,
            speed_rating=6,
            provider_tier=ProviderTier.BALANCED,
            available_in_tiers=[ServiceTier.PREMIUM, ServiceTier.ENTERPRISE],
            api_key_env="PERPLEXITY_API_KEY",
            client_class="openai.AsyncOpenAI",
            model_name="llama-3.1-sonar-large-128k-online",
            max_tokens=4000,
            rate_limit_rpm=100
        )
        
        claude_config = TieredProviderConfig(
            name="anthropic",
            priority=6,
            cost_per_1k_tokens=0.006,
            quality_score=92.0,
            speed_rating=5,
            provider_tier=ProviderTier.BALANCED,
            available_in_tiers=[ServiceTier.PREMIUM, ServiceTier.ENTERPRISE],
            api_key_env="ANTHROPIC_API_KEY",
            client_class="anthropic.AsyncAnthropic",
            model_name="claude-3-haiku-20240307",
            max_tokens=100000,
            rate_limit_rpm=50
        )
        
        # TIER 4: PREMIUM (Available for ENTERPRISE users only)
        cohere_config = TieredProviderConfig(
            name="cohere",
            priority=7,
            cost_per_1k_tokens=0.015,
            quality_score=86.0,
            speed_rating=6,
            provider_tier=ProviderTier.PREMIUM,
            available_in_tiers=[ServiceTier.ENTERPRISE],
            api_key_env="COHERE_API_KEY",
            client_class="cohere.AsyncClient",
            model_name="command",
            max_tokens=4000,
            rate_limit_rpm=100
        )
        
        openai_config = TieredProviderConfig(
            name="openai",
            priority=8,
            cost_per_1k_tokens=0.030,
            quality_score=95.0,
            speed_rating=4,
            provider_tier=ProviderTier.PREMIUM,
            available_in_tiers=[ServiceTier.ENTERPRISE],  # Only for paying enterprise customers
            api_key_env="OPENAI_API_KEY",
            client_class="openai.AsyncOpenAI",
            model_name="gpt-3.5-turbo",  # Use cheaper model
            max_tokens=4000,
            rate_limit_rpm=500
        )
        
        self.providers = [
            groq_config, together_config, deepseek_config, fireworks_config,
            perplexity_config, claude_config, cohere_config, openai_config
        ]
        
        # Initialize available providers for current tier
        self._initialize_providers_for_tier()
    
    def _initialize_providers_for_tier(self):
        """Initialize only providers available for current service tier"""
        
        logger.info(f"🎯 Initializing providers for {self.service_tier.value.upper()} tier")
        
        # Filter providers by tier
        available_configs = [
            p for p in self.providers 
            if self.service_tier in p.available_in_tiers
        ]
        
        logger.info(f"📋 Available providers for {self.service_tier.value}: {[p.name for p in available_configs]}")
        
        # Initialize each available provider
        initialized_count = 0
        for provider in available_configs:
            if self._initialize_single_provider(provider):
                self.available_providers.append(provider)
                initialized_count += 1
        
        # Sort by priority (cost optimization)
        self.available_providers.sort(key=lambda x: x.priority)
        
        # Set primary provider
        if self.available_providers:
            self.current_provider = self.available_providers[0]
            
            # Calculate savings
            openai_cost = 0.030
            primary_cost = self.current_provider.cost_per_1k_tokens
            savings_pct = ((openai_cost - primary_cost) / openai_cost) * 100
            
            logger.info(f"✅ {initialized_count} providers initialized for {self.service_tier.value} tier")
            logger.info(f"🎯 PRIMARY PROVIDER: {self.current_provider.name}")
            logger.info(f"💰 COST: ${primary_cost:.5f}/1K tokens ({savings_pct:.1f}% cheaper than OpenAI)")
            logger.info(f"🎯 QUALITY: {self.current_provider.quality_score:.0f}/100")
            logger.info(f"⚡ SPEED: {self.current_provider.speed_rating}/10")
            
        else:
            logger.error(f"❌ No providers available for {self.service_tier.value} tier!")
    
    def _initialize_single_provider(self, provider: TieredProviderConfig) -> bool:
        """Initialize a single provider"""
        
        api_key = os.getenv(provider.api_key_env)
        if not api_key:
            logger.warning(f"⚠️ {provider.name}: No API key found in {provider.api_key_env}")
            return False
        
        try:
            # Initialize based on provider type
            if provider.name == "groq":
                try:
                    import groq
                    provider.client = groq.AsyncGroq(api_key=api_key)
                except ImportError:
                    logger.warning(f"⚠️ {provider.name}: groq package not installed. Run: pip install groq")
                    return False
                    
            elif provider.name in ["together", "deepseek", "fireworks", "perplexity"]:
                try:
                    import openai
                    base_urls = {
                        "together": "https://api.together.xyz/v1",
                        "deepseek": "https://api.deepseek.com",
                        "fireworks": "https://api.fireworks.ai/inference/v1",
                        "perplexity": "https://api.perplexity.ai"
                    }
                    provider.client = openai.AsyncOpenAI(
                        api_key=api_key,
                        base_url=base_urls.get(provider.name)
                    )
                except ImportError:
                    logger.warning(f"⚠️ {provider.name}: openai package required")
                    return False
                    
            elif provider.name == "anthropic":
                try:
                    import anthropic
                    provider.client = anthropic.AsyncAnthropic(api_key=api_key)
                except ImportError:
                    logger.warning(f"⚠️ {provider.name}: anthropic package not installed")
                    return False
                    
            elif provider.name == "cohere":
                try:
                    import cohere
                    provider.client = cohere.AsyncClient(api_key=api_key)
                except ImportError:
                    logger.warning(f"⚠️ {provider.name}: cohere package not installed")
                    return False
                    
            elif provider.name == "openai":
                try:
                    import openai
                    provider.client = openai.AsyncOpenAI(api_key=api_key)
                except ImportError:
                    logger.warning(f"⚠️ {provider.name}: openai package not installed")
                    return False
            
            provider.available = True
            
            # 🔥 FIXED: Use provider.provider_tier instead of provider.tier
            tier_emoji = {
                ProviderTier.ULTRA_CHEAP: "💎",
                ProviderTier.BUDGET: "💰",
                ProviderTier.BALANCED: "⚖️",
                ProviderTier.PREMIUM: "👑"
            }
            
            logger.info(f"✅ {provider.name}: {tier_emoji[provider.provider_tier]} {provider.provider_tier.value} (${provider.cost_per_1k_tokens:.5f}/1K, {provider.quality_score:.0f}/100)")
            return True
            
        except Exception as e:
            logger.error(f"❌ {provider.name}: Failed to initialize - {str(e)}")
            return False
    
    def get_providers_for_tier(self, tier: ServiceTier = None) -> List[TieredProviderConfig]:
        """Get available providers for a specific tier"""
        tier = tier or self.service_tier
        return [p for p in self.available_providers if tier in p.available_in_tiers]
    
    def get_available_providers(self, tier: ServiceTier = None) -> List[Dict[str, Any]]:
        """Get available providers formatted for enhancers"""
        tier = tier or self.service_tier
        providers = self.get_providers_for_tier(tier)
        
        # Convert to format expected by enhancers
        formatted_providers = []
        for provider in providers:
            formatted_providers.append({
                "name": provider.name,
                "available": provider.available,
                "client": provider.client,
                "priority": provider.priority,
                "cost_per_1k_tokens": provider.cost_per_1k_tokens,
                "quality_score": provider.quality_score,
                "provider_tier": provider.provider_tier.value,
                "speed_rating": provider.speed_rating
            })
        
        return formatted_providers
    
    def upgrade_tier(self, new_tier: ServiceTier):
        """Upgrade to a higher service tier"""
        if new_tier.value in ["standard", "premium", "enterprise"]:
            logger.info(f"🚀 Upgrading from {self.service_tier.value} to {new_tier.value}")
            self.service_tier = new_tier
            self.available_providers = []
            self._initialize_providers_for_tier()
        else:
            logger.warning(f"⚠️ Cannot upgrade to {new_tier.value}")
    
    def get_tier_comparison(self) -> Dict[str, Any]:
        """Get comparison of all service tiers"""
        
        tiers_info = {}
        
        for tier in ServiceTier:
            providers = [p for p in self.providers if tier in p.available_in_tiers and p.available]
            
            if providers:
                primary = min(providers, key=lambda x: x.priority)
                cheapest = min(providers, key=lambda x: x.cost_per_1k_tokens)
                highest_quality = max(providers, key=lambda x: x.quality_score)
                
                tiers_info[tier.value] = {
                    "provider_count": len(providers),
                    "providers": [p.name for p in providers],
                    "primary_provider": primary.name,
                    "cheapest_cost": cheapest.cost_per_1k_tokens,
                    "highest_quality": highest_quality.quality_score,
                    "estimated_monthly_cost_1m": (1_000_000 / 1000) * primary.cost_per_1k_tokens
                }
        
        return tiers_info
    
    def get_cost_summary_by_tier(self) -> Dict[str, Any]:
        """Get cost summary including tier comparison"""
        
        base_summary = {
            "current_tier": self.service_tier.value,
            "primary_provider": self.current_provider.name if self.current_provider else None,
            "total_requests": self.cost_tracking["total_requests"],
            "total_cost": self.cost_tracking["total_cost"],
            "cost_savings_vs_openai": self.cost_tracking["cost_savings_vs_openai"],
            "average_quality_score": self.current_provider.quality_score if self.current_provider else 0
        }
        
        # Add tier comparison
        base_summary["tier_comparison"] = self.get_tier_comparison()
        
        return base_summary

# Global tiered provider manager
_global_tiered_manager = None

def get_tiered_ai_provider(service_tier: ServiceTier = ServiceTier.FREE) -> TieredAIProviderManager:
    """Get the global tiered AI provider manager"""
    global _global_tiered_manager
    
    if _global_tiered_manager is None or _global_tiered_manager.service_tier != service_tier:
        _global_tiered_manager = TieredAIProviderManager(service_tier)
    
    return _global_tiered_manager

def set_default_service_tier(tier: ServiceTier = ServiceTier.FREE):
    """Set the default service tier for your application"""
    global _global_tiered_manager
    _global_tiered_manager = TieredAIProviderManager(tier)
    
    logger.info(f"🎯 Default service tier set to: {tier.value.upper()}")
    
    # Log the impact
    if tier == ServiceTier.FREE:
        logger.info("💎 Using ultra-cheap providers: Groq, Together AI, Deepseek")
        logger.info("💰 Expected savings: 95-99% vs OpenAI")
        logger.info("🎯 Quality range: 72-82/100")
    elif tier == ServiceTier.PREMIUM:
        logger.info("👑 Premium providers available: Claude, Perplexity + ultra-cheap")
        logger.info("💰 Expected cost: Balanced approach")
        logger.info("🎯 Quality range: 72-92/100")

# Convenience functions for easy integration
async def make_tiered_ai_request(
    prompt: str,
    max_tokens: int = 1000,
    service_tier: ServiceTier = ServiceTier.FREE,
    temperature: float = 0.3
) -> Dict[str, Any]:
    """Make AI request using tiered provider system"""
    
    manager = get_tiered_ai_provider(service_tier)
    
    if not manager.current_provider:
        raise Exception(f"No providers available for {service_tier.value} tier")
    
    provider = manager.current_provider
    
    # Track usage
    estimated_tokens = len(prompt.split()) * 1.3
    estimated_cost = (estimated_tokens / 1000) * provider.cost_per_1k_tokens
    
    manager.cost_tracking["total_requests"] += 1
    manager.cost_tracking["total_cost"] += estimated_cost
    manager.cost_tracking["cost_savings_vs_openai"] += (estimated_tokens / 1000) * (0.030 - provider.cost_per_1k_tokens)
    
    logger.info(f"🤖 Using {provider.name} ({service_tier.value} tier) - ${estimated_cost:.4f}")
    
    try:
        # Make request based on provider type
        if provider.name == "groq":
            response = await provider.client.chat.completions.create(
                model=provider.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content
            
        elif provider.name in ["together", "deepseek", "fireworks", "perplexity", "openai"]:
            response = await provider.client.chat.completions.create(
                model=provider.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content
            
        elif provider.name == "anthropic":
            response = await provider.client.messages.create(
                model=provider.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.content[0].text
            
        elif provider.name == "cohere":
            response = await provider.client.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                model=provider.model_name
            )
            content = response.generations[0].text
        
        return {
            "response": content,
            "provider_used": provider.name,
            "service_tier": service_tier.value,
            "estimated_cost": estimated_cost,
            "quality_score": provider.quality_score,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"❌ {provider.name} request failed: {str(e)}")
        
        # Try fallback provider in same tier
        fallback_providers = [p for p in manager.available_providers if p != provider]
        if fallback_providers:
            logger.info(f"🔄 Trying fallback: {fallback_providers[0].name}")
            # Update current provider to fallback
            manager.current_provider = fallback_providers[0]
            # Recursive call with fallback
            return await make_tiered_ai_request(prompt, max_tokens, service_tier, temperature)
        
        raise

def get_cost_summary() -> Dict[str, Any]:
    """Get cost summary from global manager"""
    global _global_tiered_manager
    
    if _global_tiered_manager:
        return _global_tiered_manager.get_cost_summary_by_tier()
    else:
        return {
            "error": "No tiered manager initialized",
            "estimated_savings": 0.0,
            "savings_percentage": 0.0
        }

def log_tier_comparison():
    """Log a comparison of all service tiers"""
    
    logger.info("🎯 SERVICE TIER COMPARISON:")
    logger.info("=" * 60)
    
    tiers = [ServiceTier.FREE, ServiceTier.STANDARD, ServiceTier.PREMIUM, ServiceTier.ENTERPRISE]
    
    for tier in tiers:
        manager = TieredAIProviderManager(tier)
        if manager.available_providers:
            primary = manager.current_provider
            monthly_cost = (1_000_000 / 1000) * primary.cost_per_1k_tokens
            
            logger.info(f"\n{tier.value.upper()} TIER:")
            logger.info(f"  Primary: {primary.name} (${primary.cost_per_1k_tokens:.5f}/1K)")
            logger.info(f"  Quality: {primary.quality_score:.0f}/100")
            logger.info(f"  Monthly cost (1M tokens): ${monthly_cost:.2f}")
            logger.info(f"  Available providers: {len(manager.available_providers)}")

if __name__ == "__main__":
    # Set ultra-cheap as default for your application
    set_default_service_tier(ServiceTier.FREE)
    
    # Show tier comparison
    log_tier_comparison()