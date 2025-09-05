# =====================================
# File: src/intelligence/providers/ai_provider_router.py
# =====================================

"""
AI provider routing for Intelligence Engine operations.

Handles cost-optimized routing of AI requests across multiple providers
with fallback and load balancing capabilities.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from enum import Enum

from src.core.config import ai_provider_config
from src.core.shared.decorators import retry_on_failure
from src.core.shared.exceptions import AIProviderError, ServiceUnavailableError

logger = logging.getLogger(__name__)


class RequestComplexity(Enum):
    """Request complexity levels for provider selection."""
    SIMPLE = "simple"      # Basic extraction, use cheapest
    MODERATE = "moderate"  # Standard analysis, use budget/standard
    COMPLEX = "complex"    # Advanced analysis, use standard/premium


class AIProviderRouter:
    """Router for optimized AI provider selection and request handling."""
    
    def __init__(self):
        self.provider_config = ai_provider_config
        self.provider_stats = {}  # Track usage statistics
    
    async def route_request(
        self,
        request_type: str,
        content: str,
        complexity: RequestComplexity = RequestComplexity.SIMPLE,
        preferred_provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Route request to optimal AI provider based on complexity and cost.
        
        Args:
            request_type: Type of request (analysis, extraction, etc.)
            content: Content to process
            complexity: Request complexity level
            preferred_provider: Optional preferred provider name
            
        Returns:
            Dict[str, Any]: Provider response
            
        Raises:
            AIProviderError: If all providers fail
            ServiceUnavailableError: If no providers available
        """
        # Select providers based on complexity
        candidate_providers = self._select_providers_by_complexity(complexity)
        
        if preferred_provider and preferred_provider in [p.name for p in candidate_providers]:
            # Move preferred provider to front
            candidate_providers = [p for p in candidate_providers if p.name == preferred_provider] + \
                                 [p for p in candidate_providers if p.name != preferred_provider]
        
        if not candidate_providers:
            raise ServiceUnavailableError("No AI providers available")
        
        # Try providers in order
        last_error = None
        for provider in candidate_providers:
            try:
                logger.info(f"Routing {request_type} request to {provider.name} (tier: {provider.tier.value})")
                
                response = await self._execute_provider_request(
                    provider=provider,
                    request_type=request_type,
                    content=content
                )
                
                # Update success stats
                self._update_provider_stats(provider.name, success=True)
                
                return {
                    "provider": provider.name,
                    "tier": provider.tier.value,
                    "cost_per_1k_tokens": provider.cost_per_1k_tokens,
                    "response": response
                }
                
            except Exception as e:
                logger.warning(f"Provider {provider.name} failed: {e}")
                self._update_provider_stats(provider.name, success=False)
                last_error = e
                continue
        
        # All providers failed
        raise AIProviderError(
            f"All AI providers failed for {request_type} request",
            provider="all"
        )
    
    def _select_providers_by_complexity(self, complexity: RequestComplexity) -> List:
        """Select appropriate providers based on request complexity."""
        if complexity == RequestComplexity.SIMPLE:
            # Use cheapest providers first
            providers = (
                self.provider_config.get_providers_by_tier("ultra_cheap") +
                self.provider_config.get_providers_by_tier("budget")
            )
        elif complexity == RequestComplexity.MODERATE:
            # Use budget to standard providers
            providers = (
                self.provider_config.get_providers_by_tier("budget") +
                self.provider_config.get_providers_by_tier("standard")
            )
        else:  # COMPLEX
            # Use standard to premium providers
            providers = (
                self.provider_config.get_providers_by_tier("standard") +
                self.provider_config.get_providers_by_tier("premium")
            )
        
        # Filter enabled providers and sort by success rate
        enabled_providers = [p for p in providers if p.enabled]
        return sorted(enabled_providers, key=lambda x: self._get_provider_success_rate(x.name), reverse=True)
    
    async def _execute_provider_request(self, provider, request_type: str, content: str) -> str:
        """Execute request against specific provider."""
        # This is a simplified implementation
        # In practice, you'd have specific handlers for each provider
        
        if provider.name == "openai":
            return await self._call_openai(content)
        elif provider.name == "anthropic":
            return await self._call_anthropic(content)
        elif provider.name == "cohere":
            return await self._call_cohere(content)
        else:
            # Generic provider handler
            return await self._call_generic_provider(provider, content)
    
    async def _call_openai(self, content: str) -> str:
        """Call OpenAI API."""
        # Placeholder implementation
        return f"OpenAI response for: {content[:100]}..."
    
    async def _call_anthropic(self, content: str) -> str:
        """Call Anthropic API."""
        # Placeholder implementation
        return f"Anthropic response for: {content[:100]}..."
    
    async def _call_cohere(self, content: str) -> str:
        """Call Cohere API."""
        # Placeholder implementation
        return f"Cohere response for: {content[:100]}..."
    
    async def _call_generic_provider(self, provider, content: str) -> str:
        """Call generic provider API."""
        # Placeholder implementation
        return f"{provider.name} response for: {content[:100]}..."
    
    def _update_provider_stats(self, provider_name: str, success: bool):
        """Update provider performance statistics."""
        if provider_name not in self.provider_stats:
            self.provider_stats[provider_name] = {"success": 0, "failure": 0}
        
        if success:
            self.provider_stats[provider_name]["success"] += 1
        else:
            self.provider_stats[provider_name]["failure"] += 1
    
    def _get_provider_success_rate(self, provider_name: str) -> float:
        """Get provider success rate for routing decisions."""
        if provider_name not in self.provider_stats:
            return 1.0  # Default to high success rate for new providers
        
        stats = self.provider_stats[provider_name]
        total = stats["success"] + stats["failure"]
        
        if total == 0:
            return 1.0
        
        return stats["success"] / total
    
    def get_provider_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive provider performance statistics."""
        stats = {}
        
        for provider_name, provider in self.provider_config.providers.items():
            provider_stats = self.provider_stats.get(provider_name, {"success": 0, "failure": 0})
            total_requests = provider_stats["success"] + provider_stats["failure"]
            success_rate = self._get_provider_success_rate(provider_name)
            
            stats[provider_name] = {
                "tier": provider.tier.value,
                "cost_per_1k_tokens": provider.cost_per_1k_tokens,
                "enabled": provider.enabled,
                "total_requests": total_requests,
                "successful_requests": provider_stats["success"],
                "failed_requests": provider_stats["failure"],
                "success_rate": success_rate,
                "fallback_priority": provider.fallback_priority
            }
        
        return stats