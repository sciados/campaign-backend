# =====================================
# File: src/core/config/ai_providers.py
# =====================================

"""
AI Provider configuration management for CampaignForge.

Manages the extensive collection of AI providers with cost optimization,
tiered routing, and fallback configurations.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

from src.core.config.settings import settings


class AIProviderTier(Enum):
    """AI Provider cost and performance tiers."""
    ULTRA_CHEAP = "ultra_cheap"
    BUDGET = "budget"
    STANDARD = "standard"
    PREMIUM = "premium"


@dataclass
class AIProviderConfig:
    """Configuration for individual AI providers."""
    name: str
    api_key: str
    tier: AIProviderTier
    cost_per_1k_tokens: float
    max_tokens: int
    supports_streaming: bool = True
    enabled: bool = True
    fallback_priority: int = 0  # Lower number = higher priority


class AIProviderManager:
    """Manages AI provider configurations and routing."""
    
    def __init__(self):
        self.providers = self._initialize_providers()
    
    def _initialize_providers(self) -> Dict[str, AIProviderConfig]:
        """
        Initialize all AI providers from environment variables.

        Updated 2025: Optimized pricing, priorities, and token limits based on latest benchmarks.
        Providers ordered by cost-efficiency and quality for marketing content generation.
        """
        return {
            # ========================================
            # ULTRA CHEAP TIER - Bulk & High-Volume
            # Best for: Social media, product descriptions, high-volume campaigns
            # ========================================

            "groq": AIProviderConfig(
                name="groq",
                api_key=settings.GROQ_API_KEY,
                tier=AIProviderTier.ULTRA_CHEAP,
                cost_per_1k_tokens=0.00059,  # Updated: Llama 3.1 70B - $0.59/$0.79 per 1M
                max_tokens=128000,  # Updated: Llama 3.1 supports 128K context
                fallback_priority=1,  # PRIORITY 1: Fastest (249 tok/s), cheapest quality option
                supports_streaming=True
            ),
            "deepseek": AIProviderConfig(
                name="deepseek",
                api_key=settings.DEEPSEEK_API_KEY,
                tier=AIProviderTier.ULTRA_CHEAP,
                cost_per_1k_tokens=0.00014,  # Updated: V3 - $0.14/$0.28 per 1M (cache hits 74% cheaper)
                max_tokens=64000,  # DeepSeek V3 context
                fallback_priority=2,  # PRIORITY 2: Extremely cheap, excellent cache optimization
                supports_streaming=True
            ),
            "together": AIProviderConfig(
                name="together",
                api_key=settings.TOGETHER_API_KEY,
                tier=AIProviderTier.ULTRA_CHEAP,
                cost_per_1k_tokens=0.0001,  # Updated: Llama 3 8B Lite - $0.10 per 1M
                max_tokens=32768,  # Llama 3 context
                fallback_priority=3,  # PRIORITY 3: 6x cheaper than GPT-4o-mini
                supports_streaming=True
            ),

            # ========================================
            # BUDGET TIER - Quality Balance
            # Best for: Blog posts, newsletters, B2B content
            # ========================================

            "aimlapi": AIProviderConfig(
                name="aimlapi",
                api_key=settings.AIMLAPI_API_KEY,
                tier=AIProviderTier.BUDGET,
                cost_per_1k_tokens=0.001,  # Updated: $1.00/$2.00 per 1M (80% cheaper than OpenAI)
                max_tokens=16384,
                fallback_priority=4,  # PRIORITY 4: 300+ models access, great value
                supports_streaming=True
            ),
            "cohere": AIProviderConfig(
                name="cohere",
                api_key=settings.COHERE_API_KEY,
                tier=AIProviderTier.BUDGET,
                cost_per_1k_tokens=0.0015,  # Updated: Command R+ - ~$1.50/$6 per 1M
                max_tokens=128000,  # Command R+ supports 128K
                fallback_priority=5,  # PRIORITY 5: Excellent for RAG, business content
                supports_streaming=True
            ),

            # ========================================
            # STANDARD TIER - High Quality
            # Best for: Important content, customer-facing materials
            # ========================================

            "openai": AIProviderConfig(
                name="openai",
                api_key=settings.OPENAI_API_KEY,
                tier=AIProviderTier.STANDARD,
                cost_per_1k_tokens=0.0025,  # Updated: GPT-4o - $2.50/$10 per 1M (75% cheaper than GPT-4 Turbo)
                max_tokens=128000,  # GPT-4o supports 128K
                fallback_priority=6,  # PRIORITY 6: Best quality/cost balance, multimodal
                supports_streaming=True
            ),
            "minimax": AIProviderConfig(
                name="minimax",
                api_key=settings.MINIMAX_API_KEY,
                tier=AIProviderTier.STANDARD,
                cost_per_1k_tokens=0.002,  # Updated: ~$2/$8 per 1M (estimate)
                max_tokens=8192,
                fallback_priority=7,  # PRIORITY 7: #1 for Chinese, 32 languages
                supports_streaming=True
            ),

            # ========================================
            # PREMIUM TIER - Best Quality
            # Best for: Brand content, creative campaigns, executive communications
            # ========================================

            "anthropic": AIProviderConfig(
                name="anthropic",
                api_key=settings.ANTHROPIC_API_KEY,
                tier=AIProviderTier.PREMIUM,
                cost_per_1k_tokens=0.003,  # Updated: Claude Sonnet 4.5 - $3/$15 per 1M
                max_tokens=200000,  # Claude supports 200K context
                fallback_priority=8,  # PRIORITY 8: BEST QUALITY - exceptional writing, nuance, tone
                supports_streaming=True
            ),
            "xai": AIProviderConfig(
                name="xai",
                api_key=settings.XAI_API_KEY,
                tier=AIProviderTier.PREMIUM,
                cost_per_1k_tokens=0.003,  # Updated: Grok 4 - $3/$15 per 1M
                max_tokens=128000,  # Grok 4 context
                fallback_priority=9,  # PRIORITY 9: Real-time X data, unique perspectives
                supports_streaming=True
            ),
        }
    
    def get_providers_by_tier(self, tier: AIProviderTier) -> List[AIProviderConfig]:
        """Get all providers in a specific tier, sorted by fallback priority."""
        providers = [
            p for p in self.providers.values()
            if p.tier == tier and p.enabled and p.api_key and len(p.api_key.strip()) > 10
        ]
        return sorted(providers, key=lambda x: x.fallback_priority)
    
    def get_cheapest_provider(self) -> Optional[AIProviderConfig]:
        """Get the cheapest available provider."""
        enabled_providers = [p for p in self.providers.values() if p.enabled]
        if not enabled_providers:
            return None
        return min(enabled_providers, key=lambda x: x.cost_per_1k_tokens)
    
    def get_fallback_chain(self) -> List[AIProviderConfig]:
        """Get providers in fallback order."""
        enabled_providers = [p for p in self.providers.values() if p.enabled]
        return sorted(enabled_providers, key=lambda x: x.fallback_priority)
    
    def get_provider(self, name: str) -> Optional[AIProviderConfig]:
        """Get a specific provider by name."""
        return self.providers.get(name)

    def get_provider_for_content_type(self, content_type: str, quality_tier: str = "balanced") -> Optional[AIProviderConfig]:
        """
        Get optimal provider for specific content type and quality tier.

        Args:
            content_type: Type of content (social, blog, email, product_desc, creative, technical, multilingual)
            quality_tier: Quality tier (ultra_cheap, balanced, premium)

        Returns:
            Optimal provider configuration or None
        """
        content_routing = {
            # Short-form marketing (social, ads, headlines)
            "social": {
                "ultra_cheap": "groq",      # Best: Speed + Cost
                "balanced": "deepseek",      # Good balance
                "premium": "openai"          # When quality matters
            },
            # Long-form content (blogs, articles, whitepapers)
            "blog": {
                "ultra_cheap": "groq",       # Budget option
                "balanced": "openai",        # Best balance
                "premium": "anthropic"       # Best quality
            },
            # Email campaigns
            "email": {
                "ultra_cheap": "deepseek",   # Bulk campaigns
                "balanced": "openai",        # Standard campaigns
                "premium": "anthropic"       # High-value sequences
            },
            # Product descriptions (e-commerce)
            "product_desc": {
                "ultra_cheap": "groq",       # Volume production
                "balanced": "together",      # Good consistency
                "premium": "openai"          # Premium products
            },
            # Creative/brand content
            "creative": {
                "ultra_cheap": "openai",     # No ultra-cheap for brand
                "balanced": "openai",        # Good option
                "premium": "anthropic"       # Best for brand voice
            },
            # Technical/B2B content
            "technical": {
                "ultra_cheap": "cohere",     # Budget B2B
                "balanced": "openai",        # Standard technical
                "premium": "anthropic"       # Complex reasoning
            },
            # Multilingual content
            "multilingual": {
                "ultra_cheap": "deepseek",   # Basic multilingual
                "balanced": "openai",        # Best overall
                "premium": "anthropic"       # Cultural nuance
            },
        }

        provider_name = content_routing.get(content_type, {}).get(quality_tier)
        if provider_name:
            return self.get_provider(provider_name)
        return None

    def get_cost_estimate(self, provider_name: str, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for a provider given token counts.

        Args:
            provider_name: Name of the provider
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        provider = self.get_provider(provider_name)
        if not provider:
            return 0.0

        # Simplified: using same rate for input/output (actual would differ)
        total_tokens = input_tokens + output_tokens
        cost_per_token = provider.cost_per_1k_tokens / 1000
        return total_tokens * cost_per_token


# Global AI provider manager instance
ai_provider_config = AIProviderManager()