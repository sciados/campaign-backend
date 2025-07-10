# src/intelligence/generators/base_generator.py
"""
ENHANCED BASE GENERATOR CLASS - ULTRA-CHEAP AI INTEGRATION
✅ Unified ultra-cheap AI provider system
✅ 97% cost savings vs OpenAI through smart provider hierarchy
✅ Automatic failover and load balancing
✅ Real-time cost tracking and optimization
✅ Enhanced error handling with multiple fallbacks
"""

import os
import logging
import uuid
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseContentGenerator(ABC):
    """Enhanced base class with ultra-cheap AI integration"""
    
    def __init__(self, generator_type: str):
        self.generator_type = generator_type
        self.generation_id = str(uuid.uuid4())[:8]
        
        # Initialize ultra-cheap AI system
        self.ultra_cheap_providers = self._initialize_ultra_cheap_providers()
        self.fallback_providers = self._initialize_fallback_providers()
        self.all_providers = self.ultra_cheap_providers + self.fallback_providers
        
        # Cost tracking
        self.cost_tracker = {
            "total_requests": 0,
            "total_cost": 0.0,
            "savings_vs_openai": 0.0,
            "provider_usage": {},
            "session_start": datetime.utcnow()
        }
        
        logger.info(f"✅ {generator_type} Generator - Ultra-Cheap AI System Initialized")
        logger.info(f"💰 Ultra-cheap providers: {len(self.ultra_cheap_providers)}")
        logger.info(f"🔄 Fallback providers: {len(self.fallback_providers)}")
        self._log_cost_savings_potential()
    
    def _initialize_ultra_cheap_providers(self) -> List[Dict[str, Any]]:
        """Initialize ultra-cheap providers (97% savings vs OpenAI)"""
        providers = []
        
        # Groq - Ultra-fast and ultra-cheap
        if os.getenv("GROQ_API_KEY"):
            try:
                import groq
                providers.append({
                    "name": "groq",
                    "client": groq.AsyncGroq(api_key=os.getenv("GROQ_API_KEY")),
                    "model": "llama-3.3-70b-versatile",
                    "cost_per_1k_tokens": 0.0002,
                    "quality_score": 78,
                    "speed_rating": 10,
                    "available": True,
                    "strengths": ["speed", "cost", "conversational", "structured_data"],
                    "tier": "ultra_cheap"
                })
                logger.info("💎 Groq initialized: $0.0002/1K tokens (99.3% cheaper than OpenAI)")
            except ImportError:
                logger.warning("⚠️ Groq package not installed. Run: pip install groq")
            except Exception as e:
                logger.warning(f"⚠️ Groq initialization failed: {str(e)}")
        
        # Together AI - High quality, ultra-cheap
        if os.getenv("TOGETHER_API_KEY"):
            try:
                import openai
                providers.append({
                    "name": "together",
                    "client": openai.AsyncOpenAI(
                        api_key=os.getenv("TOGETHER_API_KEY"),
                        base_url="https://api.together.xyz/v1"
                    ),
                    "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                    "cost_per_1k_tokens": 0.0008,
                    "quality_score": 82,
                    "speed_rating": 7,
                    "available": True,
                    "strengths": ["creativity", "long_form", "analysis", "versatility"],
                    "tier": "ultra_cheap"
                })
                logger.info("💎 Together AI initialized: $0.0008/1K tokens (97.3% cheaper than OpenAI)")
            except Exception as e:
                logger.warning(f"⚠️ Together AI initialization failed: {str(e)}")
        
        # DeepSeek - Extremely cheap reasoning
        if os.getenv("DEEPSEEK_API_KEY"):
            try:
                import openai
                providers.append({
                    "name": "deepseek",
                    "client": openai.AsyncOpenAI(
                        api_key=os.getenv("DEEPSEEK_API_KEY"),
                        base_url="https://api.deepseek.com"
                    ),
                    "model": "deepseek-chat",
                    "cost_per_1k_tokens": 0.00014,
                    "quality_score": 72,
                    "speed_rating": 6,
                    "available": True,
                    "strengths": ["reasoning", "math", "structured_content"],
                    "tier": "ultra_cheap"
                })
                logger.info("💎 DeepSeek initialized: $0.00014/1K tokens (99.5% cheaper than OpenAI)")
            except Exception as e:
                logger.warning(f"⚠️ DeepSeek initialization failed: {str(e)}")
        
        # Replicate - Model diversity
        if os.getenv("REPLICATE_API_TOKEN"):
            try:
                import replicate
                providers.append({
                    "name": "replicate",
                    "client": replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN")),
                    "model": "meta/llama-2-70b-chat",
                    "cost_per_1k_tokens": 0.0015,
                    "quality_score": 75,
                    "speed_rating": 5,
                    "available": True,
                    "strengths": ["model_variety", "specialized_tasks"],
                    "tier": "ultra_cheap"
                })
                logger.info("💎 Replicate initialized: $0.0015/1K tokens (95% cheaper than OpenAI)")
            except Exception as e:
                logger.warning(f"⚠️ Replicate initialization failed: {str(e)}")
        
        return providers
    
    def _initialize_fallback_providers(self) -> List[Dict[str, Any]]:
        """Initialize fallback providers (still cheaper than OpenAI)"""
        providers = []
        
        # Anthropic Claude Haiku - Quality fallback
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                import anthropic
                providers.append({
                    "name": "anthropic",
                    "client": anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY")),
                    "model": "claude-3-haiku-20240307",
                    "cost_per_1k_tokens": 0.0025,
                    "quality_score": 85,
                    "speed_rating": 6,
                    "available": True,
                    "strengths": ["long_form", "structured_content", "analysis", "safety"],
                    "tier": "fallback"
                })
                logger.info("🔄 Anthropic fallback: $0.0025/1K tokens (91.7% cheaper than OpenAI)")
            except Exception as e:
                logger.warning(f"⚠️ Anthropic initialization failed: {str(e)}")
        
        # OpenAI - Emergency fallback only
        if os.getenv("OPENAI_API_KEY"):
            try:
                import openai
                providers.append({
                    "name": "openai",
                    "client": openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")),
                    "model": "gpt-3.5-turbo",
                    "cost_per_1k_tokens": 0.0015,  # Using cheaper GPT-3.5
                    "quality_score": 88,
                    "speed_rating": 7,
                    "available": True,
                    "strengths": ["reliability", "conversational", "versatility"],
                    "tier": "emergency_fallback"
                })
                logger.info("🚨 OpenAI emergency fallback: $0.0015/1K tokens (GPT-3.5)")
            except Exception as e:
                logger.warning(f"⚠️ OpenAI initialization failed: {str(e)}")
        
        return providers
    
    def _log_cost_savings_potential(self):
        """Log potential cost savings"""
        if self.ultra_cheap_providers:
            cheapest = min(self.ultra_cheap_providers, key=lambda x: x["cost_per_1k_tokens"])
            openai_cost = 0.030  # GPT-4 baseline
            savings_pct = ((openai_cost - cheapest["cost_per_1k_tokens"]) / openai_cost) * 100
            
            logger.info(f"💰 PRIMARY PROVIDER: {cheapest['name']} (${cheapest['cost_per_1k_tokens']:.5f}/1K)")
            logger.info(f"🎯 COST SAVINGS: {savings_pct:.1f}% vs OpenAI GPT-4")
            logger.info(f"📊 MONTHLY SAVINGS (1M tokens): ${(openai_cost - cheapest['cost_per_1k_tokens']) * 1000:.2f}")
    
    async def _generate_with_ultra_cheap_ai(
        self,
        prompt: str,
        system_message: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.3,
        required_strength: str = None
    ) -> Dict[str, Any]:
        """Generate content using ultra-cheap AI with automatic failover"""
        
        start_time = time.time()
        
        # Select providers based on required strength
        candidate_providers = self._select_providers_by_strength(required_strength)
        
        for provider in candidate_providers:
            try:
                logger.info(f"🤖 Attempting generation with {provider['name']} (${provider['cost_per_1k_tokens']:.5f}/1K)")
                
                # Estimate cost
                estimated_tokens = len(prompt.split()) * 1.3 + max_tokens
                estimated_cost = (estimated_tokens / 1000) * provider["cost_per_1k_tokens"]
                
                # Make API call based on provider type
                if provider["name"] == "groq":
                    result = await self._call_groq(provider, prompt, system_message, max_tokens, temperature)
                elif provider["name"] in ["together", "deepseek", "openai"]:
                    result = await self._call_openai_compatible(provider, prompt, system_message, max_tokens, temperature)
                elif provider["name"] == "anthropic":
                    result = await self._call_anthropic(provider, prompt, system_message, max_tokens, temperature)
                elif provider["name"] == "replicate":
                    result = await self._call_replicate(provider, prompt, system_message, max_tokens, temperature)
                
                if result and result.get("content"):
                    # Track successful usage
                    self._track_usage(provider, estimated_cost, start_time)
                    
                    return {
                        "content": result["content"],
                        "provider_used": provider["name"],
                        "cost": estimated_cost,
                        "quality_score": provider["quality_score"],
                        "generation_time": time.time() - start_time,
                        "cost_optimization": {
                            "provider_tier": provider["tier"],
                            "cost_per_1k": provider["cost_per_1k_tokens"],
                            "savings_vs_openai": 0.030 - provider["cost_per_1k_tokens"],
                            "total_cost": estimated_cost
                        }
                    }
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ {provider['name']} failed: {error_msg}")
                
                # Handle rate limiting
                if "rate limit" in error_msg.lower() or "429" in error_msg:
                    logger.warning(f"🚨 {provider['name']} rate limited, trying next provider")
                    continue
                else:
                    logger.warning(f"⚠️ {provider['name']} error, trying next provider")
                    continue
        
        # All providers failed
        logger.error("❌ All AI providers failed")
        return self._generate_fallback_content()
    
    def _select_providers_by_strength(self, required_strength: str = None) -> List[Dict[str, Any]]:
        """Select providers based on required strength"""
        
        if not required_strength:
            # Return all available providers sorted by cost
            return sorted(self.all_providers, key=lambda x: x["cost_per_1k_tokens"])
        
        # Filter by strength and sort by cost
        suitable_providers = [
            p for p in self.all_providers 
            if required_strength in p.get("strengths", [])
        ]
        
        if suitable_providers:
            return sorted(suitable_providers, key=lambda x: x["cost_per_1k_tokens"])
        else:
            # Fallback to all providers if no specific match
            return sorted(self.all_providers, key=lambda x: x["cost_per_1k_tokens"])
    
    async def _call_groq(self, provider: Dict, prompt: str, system_message: str, max_tokens: int, temperature: float) -> Dict:
        """Call Groq API"""
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        response = await provider["client"].chat.completions.create(
            model=provider["model"],
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return {"content": response.choices[0].message.content}
    
    async def _call_openai_compatible(self, provider: Dict, prompt: str, system_message: str, max_tokens: int, temperature: float) -> Dict:
        """Call OpenAI-compatible API (Together, DeepSeek, OpenAI)"""
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        response = await provider["client"].chat.completions.create(
            model=provider["model"],
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return {"content": response.choices[0].message.content}
    
    async def _call_anthropic(self, provider: Dict, prompt: str, system_message: str, max_tokens: int, temperature: float) -> Dict:
        """Call Anthropic API"""
        full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt
        
        response = await provider["client"].messages.create(
            model=provider["model"],
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": full_prompt}]
        )
        
        return {"content": response.content[0].text}
    
    async def _call_replicate(self, provider: Dict, prompt: str, system_message: str, max_tokens: int, temperature: float) -> Dict:
        """Call Replicate API"""
        full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt
        
        # Replicate has different API pattern
        output = await provider["client"].run(
            provider["model"],
            input={
                "prompt": full_prompt,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
        )
        
        # Handle different response formats
        if isinstance(output, list):
            content = "".join(output)
        else:
            content = str(output)
        
        return {"content": content}
    
    def _track_usage(self, provider: Dict, cost: float, start_time: float):
        """Track provider usage and costs"""
        provider_name = provider["name"]
        
        # Update totals
        self.cost_tracker["total_requests"] += 1
        self.cost_tracker["total_cost"] += cost
        self.cost_tracker["savings_vs_openai"] += (0.030 - provider["cost_per_1k_tokens"]) * (cost / provider["cost_per_1k_tokens"])
        
        # Update provider-specific tracking
        if provider_name not in self.cost_tracker["provider_usage"]:
            self.cost_tracker["provider_usage"][provider_name] = {
                "requests": 0,
                "total_cost": 0.0,
                "avg_response_time": 0.0,
                "success_rate": 100.0
            }
        
        provider_stats = self.cost_tracker["provider_usage"][provider_name]
        provider_stats["requests"] += 1
        provider_stats["total_cost"] += cost
        
        # Update average response time
        response_time = time.time() - start_time
        current_avg = provider_stats["avg_response_time"]
        request_count = provider_stats["requests"]
        provider_stats["avg_response_time"] = ((current_avg * (request_count - 1)) + response_time) / request_count
        
        logger.info(f"💰 Cost tracking: ${cost:.4f} | Total saved: ${self.cost_tracker['savings_vs_openai']:.2f}")
    
    def _generate_fallback_content(self) -> Dict[str, Any]:
        """Generate fallback content when all providers fail"""
        logger.warning("🔄 Generating fallback content")
        
        return {
            "content": f"Fallback content for {self.generator_type} - AI providers temporarily unavailable",
            "provider_used": "fallback",
            "cost": 0.0,
            "quality_score": 50,
            "generation_time": 0.1,
            "cost_optimization": {
                "provider_tier": "fallback",
                "cost_per_1k": 0.0,
                "savings_vs_openai": 0.030,
                "total_cost": 0.0,
                "fallback_reason": "All AI providers failed"
            }
        }
    
    @abstractmethod
    async def generate_content(self, intelligence_data: Dict[str, Any], preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Abstract method for content generation - must be implemented by subclasses"""
        pass
    
    def _extract_product_name(self, intelligence_data: Dict[str, Any]) -> str:
        """Extract product name from intelligence data"""
        try:
            offer_intel = intelligence_data.get("offer_intelligence", {})
            insights = offer_intel.get("insights", [])
            
            for insight in insights:
                if "called" in str(insight).lower():
                    words = str(insight).split()
                    for i, word in enumerate(words):
                        if word.lower() == "called" and i + 1 < len(words):
                            return words[i + 1].upper().replace(",", "").replace(".", "")
            
            # Fallback extraction methods
            products = offer_intel.get("products", [])
            if products:
                return str(products[0]).upper()
            
        except Exception as e:
            logger.warning(f"⚠️ Product name extraction failed: {str(e)}")
        
        return "PRODUCT"
    
    def _create_standardized_response(
        self, 
        content: Dict[str, Any],
        title: str,
        product_name: str,
        ai_result: Dict[str, Any],
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create standardized response format with ultra-cheap AI metadata"""
        
        if preferences is None:
            preferences = {}
        
        return {
            "content_type": self.generator_type,
            "title": title,
            "content": content,
            "metadata": {
                "generated_by": f"{self.generator_type}_generator",
                "product_name": product_name,
                "content_type": self.generator_type,
                "generation_id": self.generation_id,
                "generated_at": datetime.utcnow().isoformat(),
                "preferences_used": preferences,
                "ai_provider_used": ai_result.get("provider_used"),
                "generation_cost": ai_result.get("cost", 0.0),
                "quality_score": ai_result.get("quality_score", 0),
                "generation_time": ai_result.get("generation_time", 0.0),
                "cost_optimization": ai_result.get("cost_optimization", {}),
                "ultra_cheap_ai_enabled": True,
                "generator_version": "2.0.0-ultra-cheap"
            }
        }
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get comprehensive cost summary"""
        session_duration = (datetime.utcnow() - self.cost_tracker["session_start"]).total_seconds()
        
        return {
            "ultra_cheap_system": {
                "enabled": True,
                "version": "2.0.0",
                "primary_providers": [p["name"] for p in self.ultra_cheap_providers],
                "fallback_providers": [p["name"] for p in self.fallback_providers]
            },
            "cost_performance": {
                "total_requests": self.cost_tracker["total_requests"],
                "total_cost": self.cost_tracker["total_cost"],
                "average_cost_per_request": self.cost_tracker["total_cost"] / max(1, self.cost_tracker["total_requests"]),
                "total_savings_vs_openai": self.cost_tracker["savings_vs_openai"],
                "savings_percentage": (self.cost_tracker["savings_vs_openai"] / max(0.001, self.cost_tracker["savings_vs_openai"] + self.cost_tracker["total_cost"])) * 100,
                "session_duration_minutes": session_duration / 60
            },
            "provider_breakdown": self.cost_tracker["provider_usage"],
            "cost_projections": {
                "monthly_cost_1000_users": self.cost_tracker["total_cost"] * 1000 * 30,
                "monthly_savings_1000_users": self.cost_tracker["savings_vs_openai"] * 1000 * 30,
                "roi_percentage": (self.cost_tracker["savings_vs_openai"] / max(0.001, self.cost_tracker["total_cost"])) * 100
            }
        }
    
    def log_cost_performance(self):
        """Log current cost performance"""
        summary = self.get_cost_summary()
        cost_perf = summary["cost_performance"]
        
        logger.info("💰 ULTRA-CHEAP AI COST PERFORMANCE:")
        logger.info(f"   Requests: {cost_perf['total_requests']}")
        logger.info(f"   Total cost: ${cost_perf['total_cost']:.4f}")
        logger.info(f"   Savings vs OpenAI: ${cost_perf['total_savings_vs_openai']:.2f} ({cost_perf['savings_percentage']:.1f}%)")
        logger.info(f"   Avg cost/request: ${cost_perf['average_cost_per_request']:.4f}")
        
        # Log top providers
        provider_usage = summary["provider_breakdown"]
        if provider_usage:
            top_provider = max(provider_usage.items(), key=lambda x: x[1]["requests"])
            logger.info(f"   Most used: {top_provider[0]} ({top_provider[1]['requests']} requests)")


# Enhanced utilities for ultra-cheap system
def estimate_monthly_savings(current_usage: Dict[str, Any], user_count: int = 1000) -> Dict[str, Any]:
    """Estimate monthly savings with ultra-cheap system"""
    
    # Baseline costs (per 1K tokens)
    openai_cost = 0.030
    claude_cost = 0.006
    ultra_cheap_avg = 0.0005  # Average of Groq, Together, DeepSeek
    
    # Monthly estimates (assuming 50 requests per user, 2K tokens per request)
    monthly_tokens = user_count * 50 * 2  # 100K tokens per user/month
    
    openai_monthly = (monthly_tokens / 1000) * openai_cost
    claude_monthly = (monthly_tokens / 1000) * claude_cost
    ultra_cheap_monthly = (monthly_tokens / 1000) * ultra_cheap_avg
    
    return {
        "user_count": user_count,
        "monthly_tokens": monthly_tokens,
        "cost_comparison": {
            "openai_gpt4": openai_monthly,
            "claude_sonnet": claude_monthly,
            "ultra_cheap_system": ultra_cheap_monthly
        },
        "savings": {
            "vs_openai": openai_monthly - ultra_cheap_monthly,
            "vs_claude": claude_monthly - ultra_cheap_monthly,
            "percentage_vs_openai": ((openai_monthly - ultra_cheap_monthly) / openai_monthly) * 100,
            "percentage_vs_claude": ((claude_monthly - ultra_cheap_monthly) / claude_monthly) * 100
        },
        "annual_projections": {
            "ultra_cheap_annual": ultra_cheap_monthly * 12,
            "openai_annual": openai_monthly * 12,
            "annual_savings": (openai_monthly - ultra_cheap_monthly) * 12
        }
    }