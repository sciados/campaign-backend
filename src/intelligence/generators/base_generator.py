# src/intelligence/generators/base_generator.py
"""
ENHANCED BASE GENERATOR - CIRCULAR IMPORT FREE
🚀 Clean architecture with lazy loading to prevent circular imports
💰 Maximizes cost savings while maintaining quality
🔄 Dynamic routing through lazy imports and dependency injection
⚡ Intelligent fallback and error handling
"""

import os
import logging
import uuid
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timezone
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseContentGenerator(ABC):
    """Enhanced base class with clean dependency management (no circular imports)"""
    
    def __init__(self, generator_type: str):
        self.generator_type = generator_type
        self.generation_id = str(uuid.uuid4())[:8]
        
        # Lazy-loaded dependencies (prevents circular imports)
        self._dynamic_router = None
        self._smart_router = None
        self._ultra_cheap_provider = None
        
        # Cost tracking enhanced with real-time optimization
        self.cost_tracker = {
            "total_requests": 0,
            "total_cost": 0.0,
            "savings_vs_expensive": 0.0,
            "provider_distribution": {},
            "optimization_decisions": [],
            "session_start": datetime.datetime.now()
        }
        
        logger.info(f"✅ {generator_type} Generator - Enhanced Base Initialized (Circular Import Free)")
    
    async def _get_dynamic_router(self):
        """Lazy load dynamic router to prevent circular imports"""
        if self._dynamic_router is None:
            try:
                # Import only when needed
                from ..adapters.dynamic_router import get_dynamic_router
                self._dynamic_router = await get_dynamic_router()
                logger.debug(f"🔄 Dynamic router loaded for {self.generator_type}")
            except ImportError as e:
                logger.warning(f"⚠️ Dynamic router not available: {e}")
                self._dynamic_router = False  # Mark as unavailable
        return self._dynamic_router if self._dynamic_router is not False else None
    
    async def _get_smart_router(self):
        """Lazy load smart router to prevent circular imports"""
        if self._smart_router is None:
            try:
                # Import only when needed
                from ..utils.smart_router import get_smart_router
                self._smart_router = get_smart_router()
                logger.debug(f"🔄 Smart router loaded for {self.generator_type}")
            except ImportError as e:
                logger.warning(f"⚠️ Smart router not available: {e}")
                self._smart_router = False  # Mark as unavailable
        return self._smart_router if self._smart_router is not False else None
    
    async def _get_ultra_cheap_provider(self):
        """Lazy load ultra cheap provider to prevent circular imports"""
        if self._ultra_cheap_provider is None:
            try:
                # Import only when needed
                from ..utils.ultra_cheap_ai_provider import UltraCheapAIProvider
                self._ultra_cheap_provider = UltraCheapAIProvider()
                logger.debug(f"🔄 Ultra cheap provider loaded for {self.generator_type}")
            except ImportError as e:
                logger.warning(f"⚠️ Ultra cheap provider not available: {e}")
                self._ultra_cheap_provider = False  # Mark as unavailable
        return self._ultra_cheap_provider if self._ultra_cheap_provider is not False else None
    
    async def _generate_with_dynamic_ai(
        self,
        content_type: str,
        prompt: str,
        system_message: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.3,
        task_complexity: str = "standard"
    ) -> Dict[str, Any]:
        """Generate content using dynamic AI routing with lazy loading"""
        
        start_time = time.time()
        
        # Try dynamic router first
        dynamic_router = await self._get_dynamic_router()
        if dynamic_router:
            try:
                result = await self._generate_with_dynamic_router(
                    dynamic_router, content_type, prompt, system_message, 
                    max_tokens, temperature, task_complexity
                )
                
                if result.get("success"):
                    generation_time = time.time() - start_time
                    self._track_generation_metrics(result, generation_time)
                    return result
                    
            except Exception as e:
                logger.warning(f"⚠️ Dynamic router failed: {e}")
        
        # Try smart router fallback
        smart_router = await self._get_smart_router()
        if smart_router:
            try:
                result = await self._generate_with_smart_router(
                    smart_router, prompt, system_message, max_tokens, temperature
                )
                
                if result.get("success"):
                    generation_time = time.time() - start_time
                    self._track_generation_metrics(result, generation_time)
                    return result
                    
            except Exception as e:
                logger.warning(f"⚠️ Smart router failed: {e}")
        
        # Try ultra cheap provider fallback
        ultra_cheap = await self._get_ultra_cheap_provider()
        if ultra_cheap:
            try:
                result = await self._generate_with_ultra_cheap(
                    ultra_cheap, prompt, system_message, max_tokens, temperature
                )
                
                if result.get("success"):
                    generation_time = time.time() - start_time
                    self._track_generation_metrics(result, generation_time)
                    return result
                    
            except Exception as e:
                logger.warning(f"⚠️ Ultra cheap provider failed: {e}")
        
        # Final fallback to static generation
        return await self._fallback_static_generation(prompt, system_message, max_tokens, temperature)
    
    async def _generate_with_dynamic_router(
        self, 
        router, 
        content_type: str, 
        prompt: str, 
        system_message: str,
        max_tokens: int,
        temperature: float,
        task_complexity: str
    ) -> Dict[str, Any]:
        """Generate using dynamic router"""
        
        # Define generation function for the router
        async def generation_function(provider_context: Dict[str, Any], **kwargs) -> str:
            client = provider_context["client"]
            model = provider_context["model"]
            provider_name = provider_context["provider_name"]
            
            # Route to appropriate provider implementation
            return await self._call_provider(provider_name, client, model, prompt, system_message, max_tokens, temperature)
        
        # Execute with optimal provider
        result, metadata = await router.execute_with_optimal_provider(
            content_type=content_type,
            generation_function=generation_function,
            task_complexity=task_complexity,
            prompt=prompt,
            system_message=system_message,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        estimated_cost = self._estimate_cost(result, metadata["provider_used"])
        
        return {
            "success": True,
            "content": result,
            "provider_used": metadata["provider_used"],
            "cost": estimated_cost,
            "quality_score": 85,
            "generation_time": 0,
            "optimization_metadata": {
                "selection_reason": metadata["selection_reason"],
                "fallback_used": metadata["fallback_used"],
                "dynamic_routing": True,
                "content_type": content_type,
                "task_complexity": task_complexity
            }
        }
    
    async def _generate_with_smart_router(
        self, 
        router, 
        prompt: str, 
        system_message: str,
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Generate using smart router"""
        
        try:
            result = await router.route_request(
                prompt=prompt,
                system_message=system_message,
                max_tokens=max_tokens,
                temperature=temperature,
                routing_params={
                    "content_type": "text",
                    "cost_priority": 0.9,
                    "quality_threshold": 0.75,
                    "speed_priority": 0.8
                }
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "content": result["content"],
                    "provider_used": result.get("provider_used", "smart_router"),
                    "cost": result.get("cost", 0.001),
                    "quality_score": 80,
                    "optimization_metadata": {
                        "smart_routing": True,
                        "routing_optimization": result.get("routing_optimization", {})
                    }
                }
        except Exception as e:
            logger.error(f"Smart router error: {e}")
        
        return {"success": False, "error": "Smart router failed"}
    
    async def _generate_with_ultra_cheap(
        self, 
        provider, 
        prompt: str, 
        system_message: str,
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Generate using ultra cheap provider"""
        
        try:
            result = await provider.generate_text(
                prompt=prompt,
                system_message=system_message,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "content": result["content"],
                    "provider_used": result.get("provider", "ultra_cheap"),
                    "cost": result.get("cost", 0.001),
                    "quality_score": 75,
                    "optimization_metadata": {
                        "ultra_cheap": True,
                        "cost_optimization": result.get("cost_optimization", {})
                    }
                }
        except Exception as e:
            logger.error(f"Ultra cheap provider error: {e}")
        
        return {"success": False, "error": "Ultra cheap provider failed"}
    
    async def _call_provider(
        self, 
        provider_name: str, 
        client, 
        model: str, 
        prompt: str, 
        system_message: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Call specific provider (implement specific logic per provider)"""
        
        if provider_name == "groq":
            return await self._call_groq(client, model, prompt, system_message, max_tokens, temperature)
        elif provider_name == "deepseek":
            return await self._call_openai_compatible(client, model, prompt, system_message, max_tokens, temperature)
        elif provider_name == "together":
            return await self._call_openai_compatible(client, model, prompt, system_message, max_tokens, temperature)
        elif provider_name == "anthropic":
            return await self._call_anthropic(client, model, prompt, system_message, max_tokens, temperature)
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")
    
    async def _call_groq(self, client, model: str, prompt: str, system_message: str, max_tokens: int, temperature: float) -> str:
        """Call Groq API"""
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
    
    async def _call_openai_compatible(self, client, model: str, prompt: str, system_message: str, max_tokens: int, temperature: float) -> str:
        """Call OpenAI-compatible APIs (DeepSeek, Together)"""
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
    
    async def _call_anthropic(self, client, model: str, prompt: str, system_message: str, max_tokens: int, temperature: float) -> str:
        """Call Anthropic API"""
        full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt
        
        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": full_prompt}]
        )
        
        return response.content[0].text
    
    async def _fallback_static_generation(self, prompt: str, system_message: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        """Fallback to static provider selection when all routing fails"""
        logger.warning("🔄 Using static fallback generation")
        
        # Try providers in order of preference from Railway environment
        fallback_providers = [
            ("groq", "GROQ_API_KEY"),
            ("deepseek", "DEEPSEEK_API_KEY"),
            ("together", "TOGETHER_API_KEY"),
            ("anthropic", "ANTHROPIC_API_KEY")
        ]
        
        for provider_name, env_key in fallback_providers:
            api_key = os.getenv(env_key)
            if api_key:
                try:
                    # Basic provider call without circular imports
                    result_content = await self._basic_provider_call(provider_name, api_key, prompt, system_message, max_tokens, temperature)
                    
                    if result_content:
                        return {
                            "success": True,
                            "content": result_content,
                            "provider_used": provider_name,
                            "cost": 0.001,
                            "quality_score": 70,
                            "generation_time": 2.0,
                            "optimization_metadata": {
                                "fallback_used": True,
                                "fallback_reason": "All dynamic routing failed"
                            }
                        }
                        
                except Exception as e:
                    logger.warning(f"⚠️ Fallback provider {provider_name} failed: {e}")
                    continue
        
        # Final emergency fallback
        return {
            "success": False,
            "content": f"Emergency fallback content for {self.generator_type} - all providers failed",
            "provider_used": "emergency_fallback",
            "cost": 0.0,
            "quality_score": 30,
            "generation_time": 0.1,
            "optimization_metadata": {
                "fallback_used": True,
                "fallback_reason": "All providers failed"
            }
        }
    
    async def _basic_provider_call(self, provider_name: str, api_key: str, prompt: str, system_message: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Basic provider call without any dependencies"""
        
        if provider_name == "groq":
            try:
                import groq
                client = groq.AsyncGroq(api_key=api_key)
                return await self._call_groq(client, "llama-3.3-70b-versatile", prompt, system_message, max_tokens, temperature)
            except ImportError:
                logger.warning("Groq not available")
                
        elif provider_name == "deepseek":
            try:
                import openai
                client = openai.AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")
                return await self._call_openai_compatible(client, "deepseek-chat", prompt, system_message, max_tokens, temperature)
            except ImportError:
                logger.warning("OpenAI client not available for DeepSeek")
        
        elif provider_name == "together":
            try:
                import openai
                client = openai.AsyncOpenAI(api_key=api_key, base_url="https://api.together.xyz/v1")
                return await self._call_openai_compatible(client, "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo", prompt, system_message, max_tokens, temperature)
            except ImportError:
                logger.warning("OpenAI client not available for Together")
                
        elif provider_name == "anthropic":
            try:
                import anthropic
                client = anthropic.AsyncAnthropic(api_key=api_key)
                return await self._call_anthropic(client, "claude-sonnet-4-20250514", prompt, system_message, max_tokens, temperature)
            except ImportError:
                logger.warning("Anthropic client not available")
        
        return None
    
    def _estimate_cost(self, content: str, provider_used: str) -> float:
        """Estimate generation cost based on content and provider"""
        # Rough token estimation
        token_count = len(content.split()) * 1.3
        
        # Cost per 1K tokens based on Railway providers
        cost_rates = {
            "groq": 0.00013,
            "deepseek": 0.00089,
            "together": 0.0008,
            "anthropic": 0.009,
            "ultra_cheap": 0.0005,
            "smart_router": 0.0007,
            "emergency_fallback": 0.0
        }
        
        rate = cost_rates.get(provider_used, 0.001)
        return (token_count / 1000) * rate
    
    def _track_generation_metrics(self, result: Dict[str, Any], generation_time: float):
        """Track generation metrics for analytics"""
        self.cost_tracker["total_requests"] += 1
        self.cost_tracker["total_cost"] += result.get("cost", 0)
        
        provider_used = result.get("provider_used", "unknown")
        if provider_used not in self.cost_tracker["provider_distribution"]:
            self.cost_tracker["provider_distribution"][provider_used] = {
                "count": 0,
                "total_cost": 0.0,
                "avg_time": 0.0
            }
        
        provider_stats = self.cost_tracker["provider_distribution"][provider_used]
        provider_stats["count"] += 1
        provider_stats["total_cost"] += result.get("cost", 0)
        provider_stats["avg_time"] = (provider_stats["avg_time"] * (provider_stats["count"] - 1) + generation_time) / provider_stats["count"]
    
    async def get_optimization_analytics(self) -> Dict[str, Any]:
        """Get analytics on optimization performance"""
        
        # Calculate session statistics
        session_duration = (datetime.datetime.now() - self.cost_tracker["session_start"]).total_seconds() / 3600
        
        total_requests = self.cost_tracker["total_requests"]
        if total_requests > 0:
            avg_cost_per_request = self.cost_tracker["total_cost"] / total_requests
            expensive_cost_per_request = 0.030  # OpenAI rate
            estimated_savings = (expensive_cost_per_request - avg_cost_per_request) * total_requests
        else:
            estimated_savings = 0
        
        return {
            "session_info": {
                "generator_type": self.generator_type,
                "session_duration_hours": round(session_duration, 2),
                "total_requests": total_requests,
                "enhanced_routing_enabled": True
            },
            "cost_optimization": {
                "total_cost": round(self.cost_tracker["total_cost"], 4),
                "average_cost_per_request": round(avg_cost_per_request, 4) if total_requests > 0 else 0,
                "estimated_savings": round(estimated_savings, 4),
                "savings_percentage": round((estimated_savings / (estimated_savings + self.cost_tracker["total_cost"])) * 100, 1) if estimated_savings > 0 else 0
            },
            "provider_distribution": self.cost_tracker["provider_distribution"],
            "optimization_decisions": self.cost_tracker["optimization_decisions"][-10:],  # Last 10 decisions
        }
    
    def _create_enhanced_response(
        self, 
        content: Dict[str, Any],
        title: str,
        product_name: str,
        ai_result: Dict[str, Any],
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create enhanced response with optimization metadata"""
        
        if preferences is None:
            preferences = {}
        
        return {
            "content_type": self.generator_type,
            "title": title,
            "content": content,
            "metadata": {
                "generated_by": f"enhanced_{self.generator_type}_generator",
                "product_name": product_name,
                "content_type": self.generator_type,
                "generation_id": self.generation_id,
                "generated_at": datetime.datetime.now(),
                "preferences_used": preferences,
                "ai_optimization": {
                    "provider_used": ai_result.get("provider_used"),
                    "generation_cost": ai_result.get("cost", 0.0),
                    "quality_score": ai_result.get("quality_score", 0),
                    "generation_time": ai_result.get("generation_time", 0.0),
                    "enhanced_routing_enabled": True,
                    "optimization_metadata": ai_result.get("optimization_metadata", {}),
                    "fallback_used": ai_result.get("optimization_metadata", {}).get("fallback_used", False)
                },
                "generator_version": "3.0.0-enhanced-no-circular-imports"
            }
        }
    
    # Utility methods for enum serialization (from your existing code)
    def _serialize_enum_field(self, field_value):
        """Serialize enum fields to prevent issues"""
        if hasattr(field_value, 'value'):
            return field_value.value
        elif isinstance(field_value, dict):
            return {k: self._serialize_enum_field(v) for k, v in field_value.items()}
        elif isinstance(field_value, list):
            return [self._serialize_enum_field(item) for item in field_value]
        else:
            return field_value
    
    @abstractmethod
    async def generate_content(self, intelligence_data: Dict[str, Any], preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Abstract method for content generation - must be implemented by subclasses"""
        pass


# Integration adapter for existing generators (no circular imports)
class DynamicRoutingMixin:
    """Mixin to add dynamic routing to existing generators (no circular imports)"""
    
    async def _call_ultra_cheap_ai_with_routing(
        self,
        prompt: str,
        intelligence: Dict[str, Any],
        content_type: str = "text",
        system_message: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.3,
        task_complexity: str = "standard"
    ) -> Dict[str, Any]:
        """Call ultra-cheap AI with routing (no circular imports)"""
        
        # Get enhanced base generator instance if not exists
        if not hasattr(self, '_enhanced_generator'):
            self._enhanced_generator = BaseContentGenerator(
                getattr(self, 'generator_type', 'content')
            )
        
        # Use enhanced routing for generation
        return await self._enhanced_generator._generate_with_dynamic_ai(
            content_type=content_type,
            prompt=prompt,
            system_message=system_message,
            max_tokens=max_tokens,
            temperature=temperature,
            task_complexity=task_complexity
        )


# Convenience functions for easy migration (no circular imports)
async def enhance_existing_generator(generator_instance):
    """Enhance existing generator with dynamic routing capabilities (no circular imports)"""
    
    # Add dynamic routing mixin
    class Generator(generator_instance.__class__, DynamicRoutingMixin):
        pass
    
    # Create enhanced instance
    enhanced = Generator()
    
    # Copy existing attributes
    for attr_name in dir(generator_instance):
        if not attr_name.startswith('_') and not callable(getattr(generator_instance, attr_name)):
            setattr(enhanced, attr_name, getattr(generator_instance, attr_name))
    
    return enhanced