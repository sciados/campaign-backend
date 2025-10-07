# src/content/services/ai_provider_service.py
"""
AI Provider Abstraction Layer
Provides unified interface to multiple AI providers with cost optimization
"""

import os
import logging
import time
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class AIProvider(str, Enum):
    """Supported AI providers"""
    DEEPSEEK = "deepseek"
    GPT4O_MINI = "gpt4o_mini"
    CLAUDE = "claude"
    GROQ = "groq"


class TaskComplexity(str, Enum):
    """Task complexity levels for provider selection"""
    SIMPLE = "simple"       # Short text, simple tasks -> DeepSeek
    STANDARD = "standard"   # Medium complexity -> DeepSeek/GPT-4o Mini
    COMPLEX = "complex"     # High quality needed -> Claude


class AIProviderService:
    """
    Unified AI provider service with intelligent routing and cost optimization
    Implements the multi-provider abstraction from architecture docs
    """

    def __init__(self):
        self.providers = {
            AIProvider.DEEPSEEK: {
                "name": "DeepSeek V3",
                "cost_per_1k_tokens": 0.0001,  # Ultra cheap
                "quality_score": 75,
                "speed_score": 85,
                "available": bool(os.getenv("DEEPSEEK_API_KEY"))
            },
            AIProvider.GPT4O_MINI: {
                "name": "GPT-4o Mini",
                "cost_per_1k_tokens": 0.0015,  # Moderate
                "quality_score": 85,
                "speed_score": 90,
                "available": bool(os.getenv("OPENAI_API_KEY"))
            },
            AIProvider.CLAUDE: {
                "name": "Claude 3.5 Sonnet",
                "cost_per_1k_tokens": 0.015,   # Premium
                "quality_score": 95,
                "speed_score": 80,
                "available": bool(os.getenv("ANTHROPIC_API_KEY"))
            },
            AIProvider.GROQ: {
                "name": "Groq (Mixtral)",
                "cost_per_1k_tokens": 0.0002,  # Very cheap
                "quality_score": 70,
                "speed_score": 95,
                "available": bool(os.getenv("GROQ_API_KEY"))
            }
        }

        self.generation_stats = {
            "total_requests": 0,
            "total_cost": 0.0,
            "provider_usage": {},
            "average_latency": 0.0
        }

        logger.info(f"AI Provider Service initialized with {len(self.providers)} providers")

    def select_optimal_provider(
        self,
        task_complexity: TaskComplexity = TaskComplexity.STANDARD,
        max_cost_per_1k: Optional[float] = None,
        min_quality: Optional[int] = None
    ) -> AIProvider:
        """
        Select optimal provider based on task requirements
        Implements cost optimization routing logic from docs
        """

        # Filter available providers
        available_providers = [
            (provider, config)
            for provider, config in self.providers.items()
            if config["available"]
        ]

        if not available_providers:
            raise Exception("No AI providers available - check API keys")

        # Apply filters
        if max_cost_per_1k:
            available_providers = [
                (p, c) for p, c in available_providers
                if c["cost_per_1k_tokens"] <= max_cost_per_1k
            ]

        if min_quality:
            available_providers = [
                (p, c) for p, c in available_providers
                if c["quality_score"] >= min_quality
            ]

        if not available_providers:
            # Fallback to any available provider
            available_providers = [
                (p, c) for p, c in self.providers.items() if c["available"]
            ]

        # Select based on task complexity
        if task_complexity == TaskComplexity.SIMPLE:
            # Prioritize cheapest
            selected = min(available_providers, key=lambda x: x[1]["cost_per_1k_tokens"])
        elif task_complexity == TaskComplexity.COMPLEX:
            # Prioritize quality
            selected = max(available_providers, key=lambda x: x[1]["quality_score"])
        else:
            # Balance cost and quality
            selected = min(
                available_providers,
                key=lambda x: x[1]["cost_per_1k_tokens"] / (x[1]["quality_score"] / 100)
            )

        provider = selected[0]
        logger.info(f"Selected provider: {self.providers[provider]['name']} for {task_complexity.value} task")
        return provider

    async def generate_text(
        self,
        prompt: str,
        system_message: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        task_complexity: TaskComplexity = TaskComplexity.STANDARD,
        preferred_provider: Optional[AIProvider] = None
    ) -> Dict[str, Any]:
        """
        Generate text using optimal AI provider
        Main interface for all AI generation in the system
        """

        start_time = time.time()

        try:
            # Select provider
            if preferred_provider and self.providers[preferred_provider]["available"]:
                provider = preferred_provider
            else:
                provider = self.select_optimal_provider(task_complexity)

            # Generate with selected provider
            result = await self._call_provider(
                provider=provider,
                prompt=prompt,
                system_message=system_message,
                max_tokens=max_tokens,
                temperature=temperature
            )

            # Calculate cost
            estimated_tokens = len(prompt.split()) * 1.3 + max_tokens
            cost = (estimated_tokens / 1000) * self.providers[provider]["cost_per_1k_tokens"]

            # Track statistics
            generation_time = time.time() - start_time
            self._update_stats(provider, cost, generation_time)

            return {
                "success": True,
                "content": result,
                "provider": provider.value,
                "provider_name": self.providers[provider]["name"],
                "cost": cost,
                "generation_time": generation_time,
                "quality_score": self.providers[provider]["quality_score"],
                "estimated_tokens": int(estimated_tokens)
            }

        except Exception as e:
            logger.error(f"AI generation failed: {e}")

            # Try fallback provider
            if not preferred_provider:
                try:
                    fallback_provider = self._get_fallback_provider(provider)
                    logger.warning(f"Attempting fallback to {fallback_provider.value}")

                    result = await self._call_provider(
                        provider=fallback_provider,
                        prompt=prompt,
                        system_message=system_message,
                        max_tokens=max_tokens,
                        temperature=temperature
                    )

                    generation_time = time.time() - start_time
                    estimated_tokens = len(prompt.split()) * 1.3 + max_tokens
                    cost = (estimated_tokens / 1000) * self.providers[fallback_provider]["cost_per_1k_tokens"]

                    self._update_stats(fallback_provider, cost, generation_time)

                    return {
                        "success": True,
                        "content": result,
                        "provider": fallback_provider.value,
                        "provider_name": self.providers[fallback_provider]["name"],
                        "cost": cost,
                        "generation_time": generation_time,
                        "quality_score": self.providers[fallback_provider]["quality_score"],
                        "fallback_used": True
                    }
                except Exception as fallback_error:
                    logger.error(f"Fallback provider also failed: {fallback_error}")

            return {
                "success": False,
                "error": str(e),
                "provider": provider.value if 'provider' in locals() else "unknown"
            }

    async def _call_provider(
        self,
        provider: AIProvider,
        prompt: str,
        system_message: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Call specific AI provider"""

        if provider == AIProvider.DEEPSEEK:
            return await self._call_deepseek(prompt, system_message, max_tokens, temperature)
        elif provider == AIProvider.GPT4O_MINI:
            return await self._call_openai(prompt, system_message, max_tokens, temperature)
        elif provider == AIProvider.CLAUDE:
            return await self._call_anthropic(prompt, system_message, max_tokens, temperature)
        elif provider == AIProvider.GROQ:
            return await self._call_groq(prompt, system_message, max_tokens, temperature)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def _call_deepseek(
        self,
        prompt: str,
        system_message: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Call DeepSeek API"""
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )

        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        return response.choices[0].message.content

    async def _call_openai(
        self,
        prompt: str,
        system_message: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Call OpenAI API"""
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        return response.choices[0].message.content

    async def _call_anthropic(
        self,
        prompt: str,
        system_message: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Call Anthropic API"""
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        response = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message if system_message else None,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    async def _call_groq(
        self,
        prompt: str,
        system_message: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Call Groq API"""
        from groq import AsyncGroq

        client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        response = await client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        return response.choices[0].message.content

    def _get_fallback_provider(self, failed_provider: AIProvider) -> AIProvider:
        """Get fallback provider when primary fails"""

        # Priority fallback chain: DeepSeek -> GPT-4o Mini -> Claude -> Groq
        fallback_chain = [
            AIProvider.DEEPSEEK,
            AIProvider.GPT4O_MINI,
            AIProvider.CLAUDE,
            AIProvider.GROQ
        ]

        # Find next available provider in chain
        for provider in fallback_chain:
            if provider != failed_provider and self.providers[provider]["available"]:
                return provider

        # If all else fails, return any available provider
        for provider, config in self.providers.items():
            if provider != failed_provider and config["available"]:
                return provider

        raise Exception("No fallback provider available")

    def _update_stats(self, provider: AIProvider, cost: float, latency: float):
        """Update generation statistics"""
        self.generation_stats["total_requests"] += 1
        self.generation_stats["total_cost"] += cost

        if provider.value not in self.generation_stats["provider_usage"]:
            self.generation_stats["provider_usage"][provider.value] = 0
        self.generation_stats["provider_usage"][provider.value] += 1

        # Update running average latency
        total = self.generation_stats["total_requests"]
        current_avg = self.generation_stats["average_latency"]
        self.generation_stats["average_latency"] = (
            (current_avg * (total - 1) + latency) / total
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get generation statistics"""
        return {
            **self.generation_stats,
            "available_providers": [
                {
                    "provider": provider.value,
                    "name": config["name"],
                    "available": config["available"],
                    "cost_per_1k": config["cost_per_1k_tokens"],
                    "quality_score": config["quality_score"]
                }
                for provider, config in self.providers.items()
            ]
        }
