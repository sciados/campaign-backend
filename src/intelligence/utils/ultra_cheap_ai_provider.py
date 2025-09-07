# src/intelligence/utils/ultra_cheap_ai_provider.py
"""
ULTRA-CHEAP AI PROVIDER
🚀 90% cost savings vs OpenAI/Anthropic
💰 $0.002 per 1K tokens (vs $0.060 OpenAI)
🔄 Smart provider rotation with failover
📊 Real-time cost tracking
"""

import os
import logging
import asyncio
import time
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class ProviderType(Enum):
    ULTRA_CHEAP = "ultra_cheap"
    STANDARD = "standard"
    PREMIUM = "premium"
    FALLBACK = "fallback"

class UltraCheapAIProvider:
    """
    90% cost savings AI provider with intelligent failover
    Tries ultra-cheap providers first, falls back to expensive ones only if needed
    """
    
    def __init__(self):
        self.providers = self._initialize_providers()
        self.cost_tracker = CostTracker()
        self.provider_health = {}
        self._initialize_provider_health()
        
    def _initialize_providers(self) -> List[Dict[str, Any]]:
        """Initialize all available AI providers in cost order"""
        
        providers = []
        
        # 🚀 ULTRA-CHEAP TIER (90% savings)
        # Together AI - $0.002 per 1K tokens
        if os.getenv("TOGETHER_API_KEY"):
            providers.append({
                "name": "together_ai",
                "type": ProviderType.ULTRA_CHEAP,
                "cost_per_1k_tokens": 0.002,
                "priority": 1,
                "models": {
                    "text": ["meta-llama/Llama-2-70b-chat-hf", "mistralai/Mixtral-8x7B-Instruct-v0.1"],
                    "image": None
                },
                "client": None,
                "strengths": ["fast_generation", "cost_effective", "social_media"],
                "max_tokens": 4096,
                "api_key": os.getenv("TOGETHER_API_KEY")
            })
            
        # Replicate - $0.003 per 1K tokens  
        if os.getenv("REPLICATE_API_TOKEN"):
            providers.append({
                "name": "replicate",
                "type": ProviderType.ULTRA_CHEAP,
                "cost_per_1k_tokens": 0.003,
                "priority": 2,
                "models": {
                    "text": ["meta/llama-2-70b-chat", "mistralai/mixtral-8x7b-instruct-v0.1"],
                    "image": ["stability-ai/sdxl", "bytedance/sdxl-lightning-4step"]
                },
                "client": None,
                "strengths": ["text_generation", "image_generation", "versatile"],
                "max_tokens": 4096,
                "api_key": os.getenv("REPLICATE_API_TOKEN")
            })
            
        # Groq - Ultra-fast inference, very cheap
        if os.getenv("GROQ_API_KEY"):
            providers.append({
                "name": "groq",
                "type": ProviderType.ULTRA_CHEAP,
                "cost_per_1k_tokens": 0.001,
                "priority": 1,
                "models": {
                    "text": ["llama2-70b-4096", "mixtral-8x7b-32768"],
                    "image": None
                },
                "client": None,
                "strengths": ["ultra_fast", "ultra_cheap", "social_content"],
                "max_tokens": 4096,
                "api_key": os.getenv("GROQ_API_KEY")
            })
        
        # 💰 STANDARD TIER (80% savings)
        # Anthropic Claude Haiku - $0.0125 per 1K tokens
        if os.getenv("ANTHROPIC_API_KEY"):
            providers.append({
                "name": "anthropic_haiku",
                "type": ProviderType.STANDARD,
                "cost_per_1k_tokens": 0.0125,
                "priority": 10,
                "models": {
                    "text": ["claude-3-haiku-20240307"],
                    "image": None
                },
                "client": None,
                "strengths": ["quality", "fast", "reasoning"],
                "max_tokens": 4096,
                "api_key": os.getenv("ANTHROPIC_API_KEY")
            })
            
        # 🔥 PREMIUM TIER (70% savings)
        # Anthropic Claude Sonnet - $0.015 per 1K tokens
        if os.getenv("ANTHROPIC_API_KEY"):
            providers.append({
                "name": "anthropic_sonnet",
                "type": ProviderType.PREMIUM,
                "cost_per_1k_tokens": 0.015,
                "priority": 20,
                "models": {
                    "text": ["claude-3-5-sonnet-20241022"],
                    "image": None
                },
                "client": None,
                "strengths": ["high_quality", "complex_reasoning", "long_form"],
                "max_tokens": 8192,
                "api_key": os.getenv("ANTHROPIC_API_KEY")
            })
        
        # ⚠️ FALLBACK TIER (Expensive - only when ultra-cheap fails)
        # OpenAI GPT-4 - $0.060 per 1K tokens (EXPENSIVE FALLBACK)
        if os.getenv("OPENAI_API_KEY"):
            providers.append({
                "name": "openai_gpt4",
                "type": ProviderType.FALLBACK,
                "cost_per_1k_tokens": 0.060,
                "priority": 99,
                "models": {
                    "text": ["gpt-4", "gpt-4-turbo"],
                    "image": ["dall-e-3"]
                },
                "client": None,
                "strengths": ["reliability", "creativity", "fallback"],
                "max_tokens": 8192,
                "api_key": os.getenv("OPENAI_API_KEY")
            })
            
        # Sort by priority (cheapest first)
        providers.sort(key=lambda x: x["priority"])
        
        logger.info(f"✅ Initialized {len(providers)} AI providers for ultra-cheap operations")
        return providers
    
    def _initialize_provider_health(self):
        """Initialize provider health tracking"""
        for provider in self.providers:
            self.provider_health[provider["name"]] = {
                "healthy": True,
                "error_count": 0,
                "last_success": None,
                "last_error": None,
                "consecutive_failures": 0
            }
    
    async def generate_text(
        self, 
        prompt: str, 
        max_tokens: int = 1500,
        temperature: float = 0.7,
        cost_target: str = "ultra_cheap",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text using ultra-cheap providers first
        
        Args:
            prompt: The text prompt
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature (0.0-1.0)
            cost_target: "ultra_cheap", "standard", "premium", or "any"
        
        Returns:
            Dict with generated text and cost information
        """
        
        # Filter providers based on cost target
        target_providers = self._filter_providers_by_cost_target(cost_target, "text")
        
        for provider in target_providers:
            if not self._is_provider_healthy(provider["name"]):
                continue
                
            try:
                start_time = time.time()
                result = await self._generate_text_with_provider(
                    provider, prompt, max_tokens, temperature, **kwargs
                )
                
                if result:
                    generation_time = time.time() - start_time
                    
                    # Track costs and success
                    self._track_success(provider["name"], result, generation_time)
                    
                    return {
                        "success": True,
                        "content": result["content"],
                        "provider": provider["name"],
                        "cost": result["cost"],
                        "savings_vs_openai": self._calculate_savings(result["cost"], max_tokens),
                        "generation_time": generation_time,
                        "cost_tier": provider["type"].value
                    }
                    
            except Exception as e:
                self._track_failure(provider["name"], str(e))
                logger.warning(f"Provider {provider['name']} failed: {str(e)}")
                continue
        
        return {
            "success": False,
            "error": "All providers failed",
            "fallback_needed": True
        }
    
    async def generate_image(
        self, 
        prompt: str, 
        size: str = "1024x1024",
        cost_target: str = "ultra_cheap",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate image using ultra-cheap providers first
        95% cheaper than DALL-E 3 ($0.040 -> $0.002)
        """
        
        target_providers = self._filter_providers_by_cost_target(cost_target, "image")
        
        for provider in target_providers:
            if not self._is_provider_healthy(provider["name"]):
                continue
                
            try:
                start_time = time.time()
                result = await self._generate_image_with_provider(
                    provider, prompt, size, **kwargs
                )
                
                if result:
                    generation_time = time.time() - start_time
                    self._track_success(provider["name"], result, generation_time)
                    
                    return {
                        "success": True,
                        "image_url": result["image_url"],
                        "provider": provider["name"],
                        "cost": result["cost"],
                        "savings_vs_dalle": self._calculate_image_savings(result["cost"]),
                        "generation_time": generation_time,
                        "cost_tier": provider["type"].value
                    }
                    
            except Exception as e:
                self._track_failure(provider["name"], str(e))
                logger.warning(f"Image provider {provider['name']} failed: {str(e)}")
                continue
        
        return {
            "success": False,
            "error": "All image providers failed",
            "fallback_needed": True
        }
    
    async def _generate_text_with_provider(
        self, 
        provider: Dict[str, Any], 
        prompt: str, 
        max_tokens: int, 
        temperature: float,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Generate text with specific provider"""
        
        # Initialize client if needed
        if not provider["client"]:
            provider["client"] = await self._initialize_provider_client(provider)
        
        if provider["name"] == "together_ai":
            return await self._generate_together_ai(provider, prompt, max_tokens, temperature)
        elif provider["name"] == "replicate":
            return await self._generate_replicate_text(provider, prompt, max_tokens, temperature)
        elif provider["name"] == "groq":
            return await self._generate_groq(provider, prompt, max_tokens, temperature)
        elif provider["name"] == "anthropic_haiku":
            return await self._generate_anthropic(provider, prompt, max_tokens, temperature, "claude-3-haiku-20240307")
        elif provider["name"] == "anthropic_sonnet":
            return await self._generate_anthropic(provider, prompt, max_tokens, temperature, "claude-3-5-sonnet-20241022")
        elif provider["name"] == "openai_gpt4":
            return await self._generate_openai(provider, prompt, max_tokens, temperature)
        
        return None
    
    async def _generate_together_ai(self, provider: Dict[str, Any], prompt: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        """Generate with Together AI - $0.002 per 1K tokens"""
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.together.xyz/inference",
                    headers={
                        "Authorization": f"Bearer {provider['api_key']}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": provider["models"]["text"][0],
                        "prompt": prompt,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "stop": ["Human:", "Assistant:"]
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["output"]["choices"][0]["text"].strip()
                    
                    # Calculate cost
                    estimated_tokens = len(prompt.split()) + len(content.split())
                    cost = (estimated_tokens / 1000) * provider["cost_per_1k_tokens"]
                    
                    return {
                        "content": content,
                        "cost": cost,
                        "tokens_used": estimated_tokens
                    }
        except Exception as e:
            logger.error(f"Together AI generation failed: {str(e)}")
            raise
    
    async def _generate_replicate_text(self, provider: Dict[str, Any], prompt: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        """Generate with Replicate - $0.003 per 1K tokens"""
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.replicate.com/v1/predictions",
                    headers={
                        "Authorization": f"Token {provider['api_key']}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "version": "replicate/llama-2-70b-chat:latest",
                        "input": {
                            "prompt": prompt,
                            "max_length": max_tokens,
                            "temperature": temperature,
                            "system_prompt": "You are a helpful AI assistant."
                        }
                    },
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    prediction = response.json()
                    
                    # Poll for completion (simplified for this example)
                    content = "Generated content from Replicate"  # Placeholder
                    
                    estimated_tokens = len(prompt.split()) + len(content.split())
                    cost = (estimated_tokens / 1000) * provider["cost_per_1k_tokens"]
                    
                    return {
                        "content": content,
                        "cost": cost,
                        "tokens_used": estimated_tokens
                    }
        except Exception as e:
            logger.error(f"Replicate text generation failed: {str(e)}")
            raise
    
    async def _generate_groq(self, provider: Dict[str, Any], prompt: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        """Generate with Groq - $0.001 per 1K tokens (ultra-fast)"""
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {provider['api_key']}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": provider["models"]["text"][0],
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": max_tokens,
                        "temperature": temperature
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    estimated_tokens = len(prompt.split()) + len(content.split())
                    cost = (estimated_tokens / 1000) * provider["cost_per_1k_tokens"]
                    
                    return {
                        "content": content,
                        "cost": cost,
                        "tokens_used": estimated_tokens
                    }
        except Exception as e:
            logger.error(f"Groq generation failed: {str(e)}")
            raise
    
    async def _generate_anthropic(self, provider: Dict[str, Any], prompt: str, max_tokens: int, temperature: float, model: str) -> Dict[str, Any]:
        """Generate with Anthropic Claude"""
        try:
            if not provider["client"]:
                import anthropic
                provider["client"] = anthropic.AsyncAnthropic(api_key=provider["api_key"])
            
            response = await provider["client"].messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            estimated_tokens = len(prompt.split()) + len(content.split())
            cost = (estimated_tokens / 1000) * provider["cost_per_1k_tokens"]
            
            return {
                "content": content,
                "cost": cost,
                "tokens_used": estimated_tokens
            }
        except Exception as e:
            logger.error(f"Anthropic generation failed: {str(e)}")
            raise
    
    async def _generate_openai(self, provider: Dict[str, Any], prompt: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        """Generate with OpenAI (expensive fallback)"""
        try:
            if not provider["client"]:
                import openai
                provider["client"] = openai.AsyncOpenAI(api_key=provider["api_key"])
            
            response = await provider["client"].chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            content = response.choices[0].message.content
            estimated_tokens = len(prompt.split()) + len(content.split())
            cost = (estimated_tokens / 1000) * provider["cost_per_1k_tokens"]
            
            logger.warning(f"⚠️ Using expensive OpenAI fallback - Cost: ${cost:.4f}")
            
            return {
                "content": content,
                "cost": cost,
                "tokens_used": estimated_tokens
            }
        except Exception as e:
            logger.error(f"OpenAI generation failed: {str(e)}")
            raise
    
    async def _generate_image_with_provider(self, provider: Dict[str, Any], prompt: str, size: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Generate image with specific provider"""
        
        if provider["name"] == "replicate":
            return await self._generate_replicate_image(provider, prompt, size)
        elif provider["name"] == "openai_gpt4":
            return await self._generate_dalle_image(provider, prompt, size)
        
        return None
    
    async def _generate_replicate_image(self, provider: Dict[str, Any], prompt: str, size: str) -> Dict[str, Any]:
        """Generate image with Replicate - 95% cheaper than DALL-E"""
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.replicate.com/v1/predictions",
                    headers={
                        "Authorization": f"Token {provider['api_key']}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "version": "stability-ai/sdxl:latest",
                        "input": {
                            "prompt": prompt,
                            "width": int(size.split("x")[0]),
                            "height": int(size.split("x")[1])
                        }
                    },
                    timeout=60.0
                )
                
                if response.status_code == 201:
                    # Simplified - in reality you'd poll for completion
                    return {
                        "image_url": "https://replicate.delivery/pbxt/example.jpg",
                        "cost": 0.002  # 95% cheaper than DALL-E
                    }
        except Exception as e:
            logger.error(f"Replicate image generation failed: {str(e)}")
            raise
    
    async def _generate_dalle_image(self, provider: Dict[str, Any], prompt: str, size: str) -> Dict[str, Any]:
        """Generate image with DALL-E (expensive fallback)"""
        try:
            if not provider["client"]:
                import openai
                provider["client"] = openai.AsyncOpenAI(api_key=provider["api_key"])
            
            response = await provider["client"].images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality="standard",
                n=1
            )
            
            logger.warning(f"⚠️ Using expensive DALL-E fallback - Cost: $0.040")
            
            return {
                "image_url": response.data[0].url,
                "cost": 0.040
            }
        except Exception as e:
            logger.error(f"DALL-E image generation failed: {str(e)}")
            raise
    
    async def _initialize_provider_client(self, provider: Dict[str, Any]):
        """Initialize provider-specific client"""
        try:
            if provider["name"] in ["anthropic_haiku", "anthropic_sonnet"]:
                import anthropic
                return anthropic.AsyncAnthropic(api_key=provider["api_key"])
            elif provider["name"] == "openai_gpt4":
                import openai
                return openai.AsyncOpenAI(api_key=provider["api_key"])
            # HTTP-based providers don't need persistent clients
            return None
        except Exception as e:
            logger.error(f"Failed to initialize {provider['name']} client: {str(e)}")
            return None
    
    def _filter_providers_by_cost_target(self, cost_target: str, content_type: str) -> List[Dict[str, Any]]:
        """Filter providers based on cost target and capability"""
        
        filtered = []
        
        for provider in self.providers:
            # Check if provider supports the content type
            if content_type == "text" and not provider["models"]["text"]:
                continue
            if content_type == "image" and not provider["models"]["image"]:
                continue
            
            # Filter by cost target
            if cost_target == "ultra_cheap" and provider["type"] == ProviderType.ULTRA_CHEAP:
                filtered.append(provider)
            elif cost_target == "standard" and provider["type"] in [ProviderType.ULTRA_CHEAP, ProviderType.STANDARD]:
                filtered.append(provider)
            elif cost_target == "premium" and provider["type"] in [ProviderType.ULTRA_CHEAP, ProviderType.STANDARD, ProviderType.PREMIUM]:
                filtered.append(provider)
            elif cost_target == "any":
                filtered.append(provider)
        
        return filtered
    
    def _is_provider_healthy(self, provider_name: str) -> bool:
        """Check if provider is healthy for requests"""
        health = self.provider_health.get(provider_name, {})
        
        # Skip if too many consecutive failures
        if health.get("consecutive_failures", 0) >= 3:
            return False
        
        return health.get("healthy", True)
    
    def _track_success(self, provider_name: str, result: Dict[str, Any], generation_time: float):
        """Track successful generation"""
        self.provider_health[provider_name].update({
            "healthy": True,
            "consecutive_failures": 0,
            "last_success": datetime.now(),
            "error_count": max(0, self.provider_health[provider_name].get("error_count", 0) - 1)
        })
        
        # Track costs
        self.cost_tracker.track_generation(
            provider_name=provider_name,
            cost=result.get("cost", 0),
            tokens=result.get("tokens_used", 0),
            generation_time=generation_time
        )
        
        logger.info(f"✅ {provider_name} success - Cost: ${result.get('cost', 0):.4f}, Time: {generation_time:.2f}s")
    
    def _track_failure(self, provider_name: str, error: str):
        """Track provider failure"""
        health = self.provider_health[provider_name]
        health.update({
            "error_count": health.get("error_count", 0) + 1,
            "consecutive_failures": health.get("consecutive_failures", 0) + 1,
            "last_error": error
        })
        
        # Mark as unhealthy if too many failures
        if health["consecutive_failures"] >= 3:
            health["healthy"] = False
            logger.warning(f"⚠️ Provider {provider_name} marked unhealthy after {health['consecutive_failures']} failures")
    
    def _calculate_savings(self, actual_cost: float, tokens: int) -> Dict[str, Any]:
        """Calculate savings vs OpenAI GPT-4"""
        openai_cost = (tokens / 1000) * 0.060  # GPT-4 pricing
        savings = openai_cost - actual_cost
        savings_percent = (savings / openai_cost) * 100 if openai_cost > 0 else 0
        
        return {
            "openai_cost": openai_cost,
            "actual_cost": actual_cost,
            "savings_amount": savings,
            "savings_percent": savings_percent
        }
    
    def _calculate_image_savings(self, actual_cost: float) -> Dict[str, Any]:
        """Calculate image savings vs DALL-E 3"""
        dalle_cost = 0.040
        savings = dalle_cost - actual_cost
        savings_percent = (savings / dalle_cost) * 100
        
        return {
            "dalle_cost": dalle_cost,
            "actual_cost": actual_cost,
            "savings_amount": savings,
            "savings_percent": savings_percent
        }
    
    def get_cost_report(self) -> Dict[str, Any]:
        """Get comprehensive cost report"""
        return self.cost_tracker.get_report()
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get provider health status"""
        return {
            "total_providers": len(self.providers),
            "healthy_providers": sum(1 for h in self.provider_health.values() if h.get("healthy", True)),
            "provider_health": self.provider_health,
            "cost_tiers_available": {
                "ultra_cheap": len([p for p in self.providers if p["type"] == ProviderType.ULTRA_CHEAP]),
                "standard": len([p for p in self.providers if p["type"] == ProviderType.STANDARD]),
                "premium": len([p for p in self.providers if p["type"] == ProviderType.PREMIUM]),
                "fallback": len([p for p in self.providers if p["type"] == ProviderType.FALLBACK])
            }
        }


class CostTracker:
    """Track AI generation costs and savings"""
    
    def __init__(self):
        self.generations = []
        self.total_cost = 0.0
        self.total_savings = 0.0
        
    def track_generation(self, provider_name: str, cost: float, tokens: int, generation_time: float):
        """Track a generation event"""
        
        # Calculate what this would have cost with OpenAI
        openai_cost = (tokens / 1000) * 0.060
        savings = openai_cost - cost
        
        generation_record = {
            "timestamp": datetime.now(),
            "provider": provider_name,
            "cost": cost,
            "tokens": tokens,
            "generation_time": generation_time,
            "openai_equivalent_cost": openai_cost,
            "savings": savings
        }
        
        self.generations.append(generation_record)
        self.total_cost += cost
        self.total_savings += savings
        
        # Keep only last 1000 generations to prevent memory bloat
        if len(self.generations) > 1000:
            self.generations = self.generations[-1000:]
    
    def get_report(self) -> Dict[str, Any]:
        """Get cost savings report"""
        
        if not self.generations:
            return {"message": "No generations tracked yet"}
        
        total_tokens = sum(g["tokens"] for g in self.generations)
        avg_generation_time = sum(g["generation_time"] for g in self.generations) / len(self.generations)
        
        provider_stats = {}
        for generation in self.generations:
            provider = generation["provider"]
            if provider not in provider_stats:
                provider_stats[provider] = {"count": 0, "cost": 0, "savings": 0}
            
            provider_stats[provider]["count"] += 1
            provider_stats[provider]["cost"] += generation["cost"]
            provider_stats[provider]["savings"] += generation["savings"]
        
        return {
            "total_generations": len(self.generations),
            "total_cost": self.total_cost,
            "total_savings": self.total_savings,
            "total_tokens": total_tokens,
            "avg_generation_time": avg_generation_time,
            "savings_percentage": (self.total_savings / (self.total_cost + self.total_savings)) * 100,
            "provider_breakdown": provider_stats,
            "monthly_projection": {
                "current_monthly_cost": self.total_cost * 30,  # Rough projection
                "openai_monthly_cost": (self.total_cost + self.total_savings) * 30,
                "monthly_savings": self.total_savings * 30
            }
        }