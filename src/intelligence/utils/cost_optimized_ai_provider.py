# src/intelligence/utils/cost_optimized_ai_provider.py
"""
Cost-Optimized AI Provider Manager
Ensures Claude (Anthropic) is used first for maximum cost savings
"""
import os
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class AIProviderConfig:
    """Configuration for an AI provider"""
    name: str
    priority: int  # 1 = highest priority (cheapest)
    cost_per_1k_tokens: float
    max_tokens: int
    api_key_env: str
    client_class: str
    available: bool = False
    client: Any = None
    rate_limit_rpm: int = 60  # Requests per minute
    rate_limit_tpm: int = 150000  # Tokens per minute

class CostOptimizedAIProvider:
    """
    Manages AI providers with cost optimization priority
    Always uses cheapest available provider first
    """
    
    def __init__(self):
        self.providers = []
        self.current_provider = None
        self.fallback_used = False
        self.cost_tracking = {
            "total_requests": 0,
            "total_tokens_used": 0,
            "estimated_cost": 0.0,
            "cost_savings": 0.0,
            "provider_usage": {}
        }
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize AI providers in cost-optimized order"""
        
        # PRIORITY 1: Claude (Anthropic) - CHEAPEST & HIGH QUALITY
        claude_config = AIProviderConfig(
            name="anthropic",
            priority=1,
            cost_per_1k_tokens=0.006,  # $0.006 per 1K tokens
            max_tokens=100000,
            api_key_env="ANTHROPIC_API_KEY",
            client_class="anthropic.AsyncAnthropic",
            rate_limit_rpm=50,
            rate_limit_tpm=100000
        )
        
        # PRIORITY 2: Cohere - MEDIUM COST & GOOD QUALITY
        cohere_config = AIProviderConfig(
            name="cohere",
            priority=2,
            cost_per_1k_tokens=0.015,  # $0.015 per 1K tokens
            max_tokens=4000,
            api_key_env="COHERE_API_KEY",
            client_class="cohere.AsyncClient",
            rate_limit_rpm=100,
            rate_limit_tpm=10000
        )
        
        # PRIORITY 3: OpenAI - MOST EXPENSIVE (FALLBACK ONLY)
        openai_config = AIProviderConfig(
            name="openai",
            priority=3,
            cost_per_1k_tokens=0.030,  # $0.03 per 1K tokens
            max_tokens=4000,
            api_key_env="OPENAI_API_KEY",
            client_class="openai.AsyncOpenAI",
            rate_limit_rpm=500,
            rate_limit_tpm=10000
        )
        
        self.providers = [claude_config, cohere_config, openai_config]
        
        # Initialize each provider
        for provider in self.providers:
            self._initialize_provider(provider)
        
        # Sort by priority (lowest number = highest priority)
        self.providers.sort(key=lambda x: x.priority)
        
        # Set primary provider
        available_providers = [p for p in self.providers if p.available]
        if available_providers:
            self.current_provider = available_providers[0]
            logger.info(f"🎯 PRIMARY AI PROVIDER: {self.current_provider.name} (${self.current_provider.cost_per_1k_tokens:.3f}/1K tokens)")
        else:
            logger.error("❌ NO AI PROVIDERS AVAILABLE")
    
    def _initialize_provider(self, provider: AIProviderConfig):
        """Initialize a specific AI provider"""
        
        api_key = os.getenv(provider.api_key_env)
        if not api_key:
            logger.warning(f"⚠️ {provider.name}: No API key found in {provider.api_key_env}")
            return
        
        try:
            # Initialize client based on provider
            if provider.name == "anthropic":
                import anthropic
                provider.client = anthropic.AsyncAnthropic(api_key=api_key)
                
            elif provider.name == "cohere":
                import cohere
                provider.client = cohere.AsyncClient(api_key=api_key)
                
            elif provider.name == "openai":
                import openai
                provider.client = openai.AsyncOpenAI(api_key=api_key)
            
            provider.available = True
            logger.info(f"✅ {provider.name}: Initialized (Priority {provider.priority}, ${provider.cost_per_1k_tokens:.3f}/1K tokens)")
            
        except Exception as e:
            logger.error(f"❌ {provider.name}: Failed to initialize - {str(e)}")
            provider.available = False
    
    def get_primary_provider(self) -> Optional[AIProviderConfig]:
        """Get the primary (cheapest available) provider"""
        available_providers = [p for p in self.providers if p.available]
        return available_providers[0] if available_providers else None
    
    def get_provider_by_name(self, name: str) -> Optional[AIProviderConfig]:
        """Get a specific provider by name"""
        for provider in self.providers:
            if provider.name == name and provider.available:
                return provider
        return None
    
    def get_fallback_provider(self, exclude_names: List[str] = None) -> Optional[AIProviderConfig]:
        """Get next available provider, excluding specified ones"""
        exclude_names = exclude_names or []
        
        for provider in self.providers:
            if provider.available and provider.name not in exclude_names:
                return provider
        return None
    
    async def make_ai_request(
        self, 
        prompt: str, 
        max_tokens: int = 1000,
        preferred_provider: str = None,
        fallback_on_error: bool = True
    ) -> Dict[str, Any]:
        """
        Make an AI request using cost-optimized provider selection
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens for response
            preferred_provider: Specific provider to use (optional)
            fallback_on_error: Whether to try fallback providers on error
            
        Returns:
            Dict with response data and metadata
        """
        
        # Determine which provider to use
        if preferred_provider:
            provider = self.get_provider_by_name(preferred_provider)
            if not provider:
                logger.warning(f"⚠️ Preferred provider {preferred_provider} not available, using primary")
                provider = self.get_primary_provider()
        else:
            provider = self.get_primary_provider()
        
        if not provider:
            raise Exception("No AI providers available")
        
        # Estimate cost
        estimated_tokens = len(prompt.split()) * 1.3  # Rough estimation
        estimated_cost = (estimated_tokens / 1000) * provider.cost_per_1k_tokens
        
        logger.info(f"🤖 Using {provider.name} (${provider.cost_per_1k_tokens:.3f}/1K tokens, est. ${estimated_cost:.4f})")
        
        # Track usage
        self._track_usage(provider.name, estimated_tokens, estimated_cost)
        
        # Make the request
        try:
            response = await self._make_provider_request(provider, prompt, max_tokens)
            logger.info(f"✅ {provider.name}: Request successful")
            return {
                "response": response,
                "provider_used": provider.name,
                "estimated_cost": estimated_cost,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ {provider.name}: Request failed - {str(e)}")
            
            if not fallback_on_error:
                raise
            
            # Try fallback provider
            fallback_provider = self.get_fallback_provider(exclude_names=[provider.name])
            if fallback_provider:
                logger.info(f"🔄 Trying fallback provider: {fallback_provider.name}")
                self.fallback_used = True
                
                try:
                    response = await self._make_provider_request(fallback_provider, prompt, max_tokens)
                    
                    # Calculate cost difference
                    fallback_cost = (estimated_tokens / 1000) * fallback_provider.cost_per_1k_tokens
                    cost_difference = fallback_cost - estimated_cost
                    
                    logger.warning(f"⚠️ Fallback cost impact: +${cost_difference:.4f}")
                    
                    return {
                        "response": response,
                        "provider_used": fallback_provider.name,
                        "estimated_cost": fallback_cost,
                        "success": True,
                        "fallback_used": True,
                        "cost_impact": cost_difference
                    }
                    
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback {fallback_provider.name} also failed: {str(fallback_error)}")
                    raise
            else:
                logger.error("❌ No fallback providers available")
                raise
    
    async def _make_provider_request(
        self, 
        provider: AIProviderConfig, 
        prompt: str, 
        max_tokens: int
    ) -> str:
        """Make a request to a specific provider"""
        
        if provider.name == "anthropic":
            return await self._make_anthropic_request(provider, prompt, max_tokens)
        elif provider.name == "cohere":
            return await self._make_cohere_request(provider, prompt, max_tokens)
        elif provider.name == "openai":
            return await self._make_openai_request(provider, prompt, max_tokens)
        else:
            raise Exception(f"Unknown provider: {provider.name}")
    
    async def _make_anthropic_request(
        self, 
        provider: AIProviderConfig, 
        prompt: str, 
        max_tokens: int
    ) -> str:
        """Make request to Anthropic Claude"""
        
        response = await provider.client.messages.create(
            model="claude-3-haiku-20240307",  # Use cheapest Claude model
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    async def _make_cohere_request(
        self, 
        provider: AIProviderConfig, 
        prompt: str, 
        max_tokens: int
    ) -> str:
        """Make request to Cohere"""
        
        response = await provider.client.generate(
            prompt=prompt,
            max_tokens=max_tokens,
            model="command"  # Use standard Cohere model
        )
        
        return response.generations[0].text
    
    async def _make_openai_request(
        self, 
        provider: AIProviderConfig, 
        prompt: str, 
        max_tokens: int
    ) -> str:
        """Make request to OpenAI"""
        
        response = await provider.client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use cheaper model instead of GPT-4
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content
    
    def _track_usage(self, provider_name: str, tokens: float, cost: float):
        """Track usage statistics for cost analysis"""
        
        self.cost_tracking["total_requests"] += 1
        self.cost_tracking["total_tokens_used"] += tokens
        self.cost_tracking["estimated_cost"] += cost
        
        if provider_name not in self.cost_tracking["provider_usage"]:
            self.cost_tracking["provider_usage"][provider_name] = {
                "requests": 0,
                "tokens": 0,
                "cost": 0.0
            }
        
        self.cost_tracking["provider_usage"][provider_name]["requests"] += 1
        self.cost_tracking["provider_usage"][provider_name]["tokens"] += tokens
        self.cost_tracking["provider_usage"][provider_name]["cost"] += cost
        
        # Calculate savings compared to most expensive provider
        most_expensive_cost_per_token = max(p.cost_per_1k_tokens for p in self.providers) / 1000
        max_possible_cost = tokens * most_expensive_cost_per_token
        self.cost_tracking["cost_savings"] = max_possible_cost - self.cost_tracking["estimated_cost"]
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get a summary of cost tracking"""
        
        primary_provider = self.get_primary_provider()
        
        return {
            "primary_provider": primary_provider.name if primary_provider else None,
            "total_requests": self.cost_tracking["total_requests"],
            "total_tokens": self.cost_tracking["total_tokens_used"],
            "estimated_total_cost": self.cost_tracking["estimated_cost"],
            "estimated_savings": self.cost_tracking["cost_savings"],
            "savings_percentage": (self.cost_tracking["cost_savings"] / max(self.cost_tracking["estimated_cost"] + self.cost_tracking["cost_savings"], 0.001)) * 100,
            "fallback_used": self.fallback_used,
            "provider_breakdown": self.cost_tracking["provider_usage"]
        }
    
    def log_cost_summary(self):
        """Log a cost summary"""
        
        summary = self.get_cost_summary()
        
        logger.info("💰 COST OPTIMIZATION SUMMARY:")
        logger.info(f"   Primary Provider: {summary['primary_provider']}")
        logger.info(f"   Total Requests: {summary['total_requests']}")
        logger.info(f"   Estimated Cost: ${summary['estimated_total_cost']:.4f}")
        logger.info(f"   Estimated Savings: ${summary['estimated_savings']:.4f}")
        logger.info(f"   Savings Percentage: {summary['savings_percentage']:.1f}%")
        
        if summary['fallback_used']:
            logger.warning(f"⚠️ Fallback providers were used - may have increased costs")
        
        for provider, usage in summary['provider_breakdown'].items():
            logger.info(f"   {provider}: {usage['requests']} requests, ${usage['cost']:.4f}")


# Global instance for easy access
_global_provider_manager = None

def get_cost_optimized_provider() -> CostOptimizedAIProvider:
    """Get the global cost-optimized provider instance"""
    global _global_provider_manager
    
    if _global_provider_manager is None:
        _global_provider_manager = CostOptimizedAIProvider()
    
    return _global_provider_manager

# Convenience functions for easy integration

async def make_cost_optimized_ai_request(
    prompt: str,
    max_tokens: int = 1000,
    preferred_provider: str = None
) -> Dict[str, Any]:
    """
    Make a cost-optimized AI request
    
    Usage:
        response = await make_cost_optimized_ai_request(
            prompt="Analyze this sales page...",
            max_tokens=2000,
            preferred_provider="anthropic"  # Optional
        )
    """
    
    provider_manager = get_cost_optimized_provider()
    return await provider_manager.make_ai_request(prompt, max_tokens, preferred_provider)

def get_cost_optimization_summary() -> Dict[str, Any]:
    """Get cost optimization summary"""
    
    provider_manager = get_cost_optimized_provider()
    return provider_manager.get_cost_summary()

def log_cost_optimization_summary():
    """Log cost optimization summary"""
    
    provider_manager = get_cost_optimized_provider()
    provider_manager.log_cost_summary()

def force_primary_provider(provider_name: str = "anthropic"):
    """Force a specific provider as primary (for testing)"""
    
    provider_manager = get_cost_optimized_provider()
    provider = provider_manager.get_provider_by_name(provider_name)
    
    if provider:
        provider_manager.current_provider = provider
        logger.info(f"🔧 Forced primary provider to: {provider_name}")
    else:
        logger.error(f"❌ Cannot force provider {provider_name} - not available")