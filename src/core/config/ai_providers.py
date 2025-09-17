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
        """Initialize all AI providers from environment variables."""
        return {
            # Ultra Cheap Tier
            "deepseek": AIProviderConfig(
                name="deepseek",
                api_key=settings.DEEPSEEK_API_KEY,
                tier=AIProviderTier.ULTRA_CHEAP,
                cost_per_1k_tokens=0.0001,
                max_tokens=8192,
                fallback_priority=1
            ),
            "groq": AIProviderConfig(
                name="groq",
                api_key=settings.GROQ_API_KEY,
                tier=AIProviderTier.ULTRA_CHEAP,
                cost_per_1k_tokens=0.0002,
                max_tokens=8192,
                fallback_priority=2
            ),
            
            # Budget Tier
            "together": AIProviderConfig(
                name="together",
                api_key=settings.TOGETHER_API_KEY,
                tier=AIProviderTier.BUDGET,
                cost_per_1k_tokens=0.0008,
                max_tokens=32768,
                fallback_priority=3
            ),
            "aimlapi": AIProviderConfig(
                name="aimlapi",
                api_key=settings.AIMLAPI_API_KEY,
                tier=AIProviderTier.BUDGET,
                cost_per_1k_tokens=0.001,
                max_tokens=16384,
                fallback_priority=4
            ),
            
            # Standard Tier
            "cohere": AIProviderConfig(
                name="cohere",
                api_key=settings.COHERE_API_KEY,
                tier=AIProviderTier.STANDARD,
                cost_per_1k_tokens=0.002,
                max_tokens=4096,
                fallback_priority=5
            ),
            "minimax": AIProviderConfig(
                name="minimax",
                api_key=settings.MINIMAX_API_KEY,
                tier=AIProviderTier.STANDARD,
                cost_per_1k_tokens=0.003,
                max_tokens=8192,
                fallback_priority=6
            ),
            
            # Premium Tier
            "openai": AIProviderConfig(
                name="openai",
                api_key=settings.OPENAI_API_KEY,
                tier=AIProviderTier.PREMIUM,
                cost_per_1k_tokens=0.01,
                max_tokens=16384,
                fallback_priority=7
            ),
            "anthropic": AIProviderConfig(
                name="anthropic",
                api_key=settings.ANTHROPIC_API_KEY,
                tier=AIProviderTier.PREMIUM,
                cost_per_1k_tokens=0.015,
                max_tokens=32768,
                fallback_priority=8
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


# Global AI provider manager instance
ai_provider_config = AIProviderManager()