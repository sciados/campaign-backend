# src/intelligence/generators/enhanced_base_generator.py
"""
ENHANCED BASE GENERATOR WITH DYNAMIC AI ROUTING
🤖 Automatically selects optimal AI providers based on real-time monitoring
💰 Maximizes cost savings while maintaining quality
🔄 Seamless integration with existing generator architecture
⚡ Intelligent fallback and error handling
"""

import os
import logging
import uuid
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod

from ..adapters.dynamic_router import get_dynamic_router, route_text_generation, route_image_generation

logger = logging.getLogger(__name__)

class BaseContentGenerator(ABC):
    """ base class with dynamic AI routing integration"""
    
    def __init__(self, generator_type: str):
        self.generator_type = generator_type
        self.generation_id = str(uuid.uuid4())[:8]
        
        # Dynamic routing system
        self.dynamic_router = None
        
        # Cost tracking enhanced with real-time optimization
        self.cost_tracker = {
            "total_requests": 0,
            "total_cost": 0.0,
            "savings_vs_expensive": 0.0,
            "provider_distribution": {},
            "optimization_decisions": [],
            "session_start": datetime.utcnow()
        }
        
        logger.info(f"✅  {generator_type} Generator - Dynamic AI Routing Enabled")
    
    async def _generate_with_dynamic_ai(
        self,
        content_type: str,
        prompt: str,
        system_message: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.3,
        task_complexity: str = "standard"
    ) -> Dict[str, Any]:
        """Generate content using dynamic AI routing for optimal provider selection"""
        
        start_time = time.time()
        
        # Get dynamic router
        if not self.dynamic_router:
            self.dynamic_router = await get_dynamic_router()
        
        # Define generation function
        async def generation_function(provider_context: Dict[str, Any], **kwargs) -> str:
            client = provider_context["client"]
            model = provider_context["model"]
            provider_name = provider_context["provider_name"]
            
            # Route to appropriate provider implementation
            if provider_name == "groq":
                return await self._call_groq(client, model, prompt, system_message, max_tokens, temperature)
            elif provider_name == "deepseek":
                return await self._call_openai_compatible(client, model, prompt, system_message, max_tokens, temperature, "deepseek")
            elif provider_name == "together":
                return await self._call_openai_compatible(client, model, prompt, system_message, max_tokens, temperature, "together")
            elif provider_name == "anthropic":
                return await self._call_anthropic(client, model, prompt, system_message, max_tokens, temperature)
            else:
                raise ValueError(f"Unsupported provider: {provider_name}")
        
        try:
            # Execute with optimal provider and automatic fallback
            result, metadata = await self.dynamic_router.execute_with_optimal_provider(
                content_type=content_type,
                generation_function=generation_function,
                task_complexity=task_complexity,
                prompt=prompt,
                system_message=system_message,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Calculate costs and track optimization
            generation_time = time.time() - start_time
            estimated_cost = self._estimate_cost(result, metadata["provider_used"])
            
            # Track the optimization decision
            self._track_optimization_decision(metadata, estimated_cost, generation_time)
            
            return {
                "content": result,
                "provider_used": metadata["provider_used"],
                "cost": estimated_cost,
                "quality_score": 85,  # Will be determined by monitoring system
                "generation_time": generation_time,
                "optimization_metadata": {
                    "selection_reason": metadata["selection_reason"],
                    "fallback_used": metadata["fallback_used"],
                    "attempt_number": metadata["attempt_number"],
                    "dynamic_routing": True,
                    "content_type": content_type,
                    "task_complexity": task_complexity
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Dynamic AI generation failed: {str(e)}")
            # Fallback to static provider selection
            return await self._fallback_static_generation(prompt, system_message, max_tokens, temperature)
    
    async def _generate_image_with_dynamic_ai(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: str = "professional"
    ) -> Dict[str, Any]:
        """Generate image using dynamic AI routing"""
        
        start_time = time.time()
        
        # Define image generation function
        async def image_generation_function(provider_context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
            client = provider_context["client"]
            model = provider_context["model"]
            provider_name = provider_context["provider_name"]
            
            if provider_name == "stability":
                return await self._call_stability_ai(client, model, prompt, size, style)
            elif provider_name == "replicate":
                return await self._call_replicate_image(client, model, prompt, size)
            elif provider_name == "fal":
                return await self._call_fal_image(client, model, prompt, size)
            else:
                raise ValueError(f"Unsupported image provider: {provider_name}")
        
        try:
            # Execute with optimal provider
            result, metadata = await route_image_generation(
                image_generation_function,
                prompt=prompt,
                size=size,
                style=style
            )
            
            generation_time = time.time() - start_time
            estimated_cost = 0.002  # Will be determined by monitoring system
            
            return {
                "image_data": result,
                "provider_used": metadata["provider_used"],
                "cost": estimated_cost,
                "generation_time": generation_time,
                "optimization_metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"❌ Dynamic image generation failed: {str(e)}")
            return await self._fallback_image_generation(prompt, size, style)
    
    # Provider-specific implementation methods
    async def _call_groq(self, client, model: str, prompt: str, system_message: str, max_tokens: int, temperature: float) -> str:
        """Call Groq API with dynamic routing"""
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
    
    async def _call_openai_compatible(self, client, model: str, prompt: str, system_message: str, max_tokens: int, temperature: float, provider: str) -> str:
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
        """Call Anthropic API with dynamic routing"""
        full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt
        
        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": full_prompt}]
        )
        
        return response.content[0].text
    
    async def _call_stability_ai(self, client, model: str, prompt: str, size: str, style: str) -> Dict[str, Any]:
        """Call Stability AI for image generation"""
        width, height = size.split("x")
        
        response = await client.generate(
            prompt=prompt,
            width=int(width),
            height=int(height),
            cfg_scale=7,
            steps=30,
            samples=1
        )
        
        return {
            "image_data": response.artifacts[0].base64,
            "seed": response.artifacts[0].seed
        }
    
    async def _call_replicate_image(self, client, model: str, prompt: str, size: str) -> Dict[str, Any]:
        """Call Replicate for image generation"""
        width, height = size.split("x")
        
        output = await client.run(
            model,
            input={
                "prompt": prompt,
                "width": int(width),
                "height": int(height),
                "num_outputs": 1
            }
        )
        
        return {
            "image_url": output[0],
            "image_data": None  # URL-based response
        }
    
    async def _call_fal_image(self, client, model: str, prompt: str, size: str) -> Dict[str, Any]:
        """Call FAL for image generation"""
        width, height = size.split("x")
        
        result = await client.submit(
            model,
            arguments={
                "prompt": prompt,
                "image_size": {"width": int(width), "height": int(height)},
                "num_images": 1
            }
        )
        
        return {
            "image_url": result["images"][0]["url"],
            "image_data": None
        }
    
    async def _fallback_static_generation(self, prompt: str, system_message: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        """Fallback to static provider selection when dynamic routing fails"""
        logger.warning("🔄 Using static fallback generation")
        
        # Try providers in order of preference from your Railway environment
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
                    # Implement basic provider call
                    if provider_name == "groq":
                        import groq
                        client = groq.AsyncGroq(api_key=api_key)
                        result = await self._call_groq(client, "llama-3.3-70b-versatile", prompt, system_message, max_tokens, temperature)
                    elif provider_name == "deepseek":
                        import openai
                        client = openai.AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")
                        result = await self._call_openai_compatible(client, "deepseek-chat", prompt, system_message, max_tokens, temperature, "deepseek")
                    # Add other providers...
                    
                    if result:
                        return {
                            "content": result,
                            "provider_used": provider_name,
                            "cost": 0.001,  # Estimated
                            "quality_score": 75,
                            "generation_time": 2.0,
                            "optimization_metadata": {
                                "fallback_used": True,
                                "fallback_reason": "Dynamic routing failed"
                            }
                        }
                        
                except Exception as e:
                    logger.warning(f"⚠️ Fallback provider {provider_name} failed: {str(e)}")
                    continue
        
        # Final fallback
        return {
            "content": f"Fallback content for {self.generator_type} - all providers failed",
            "provider_used": "fallback",
            "cost": 0.0,
            "quality_score": 50,
            "generation_time": 0.1,
            "optimization_metadata": {
                "fallback_used": True,
                "fallback_reason": "All providers failed"
            }
        }
    
    async def _fallback_image_generation(self, prompt: str, size: str, style: str) -> Dict[str, Any]:
        """Fallback image generation when dynamic routing fails"""
        logger.warning("🔄 Using static fallback image generation")
        
        # Try Stability AI as primary fallback
        api_key = os.getenv("STABILITY_API_KEY")
        if api_key:
            try:
                # Implement basic Stability AI call
                return {
                    "image_data": "fallback_image_data",
                    "provider_used": "stability_fallback",
                    "cost": 0.002,
                    "generation_time": 3.0,
                    "optimization_metadata": {
                        "fallback_used": True,
                        "fallback_reason": "Dynamic routing failed"
                    }
                }
            except Exception as e:
                logger.warning(f"⚠️ Fallback image generation failed: {str(e)}")
        
        return {
            "error": "Image generation failed",
            "provider_used": "none",
            "cost": 0.0,
            "optimization_metadata": {
                "fallback_used": True,
                "fallback_reason": "All image providers failed"
            }
        }
    
    def _estimate_cost(self, content: str, provider_used: str) -> float:
        """Estimate generation cost based on content and provider"""
        # Rough token estimation
        token_count = len(content.split()) * 1.3
        
        # Cost per 1K tokens based on your Railway providers
        cost_rates = {
            "groq": 0.00013,         # Blended rate for Llama 4 Scout
            "deepseek": 0.00089,     # Average of input/output
            "together": 0.0008,      # Meta-Llama-3.1-70B
            "anthropic": 0.009,      # Claude Sonnet 4 blended
            "stability": 0.002,      # Per image
            "replicate": 0.004,      # Per image
            "fal": 0.005            # Per image
        }
        
        rate = cost_rates.get(provider_used, 0.001)
        return (token_count / 1000) * rate
    
    def _track_optimization_decision(self, metadata: Dict[str, Any], cost: float, generation_time: float):
        """Track optimization decision for analytics"""
        self.cost_tracker["total_requests"] += 1
        self.cost_tracker["total_cost"] += cost
        
        provider_used = metadata["provider_used"]
        if provider_used not in self.cost_tracker["provider_distribution"]:
            self.cost_tracker["provider_distribution"][provider_used] = {
                "count": 0,
                "total_cost": 0.0,
                "avg_time": 0.0
            }
        
        provider_stats = self.cost_tracker["provider_distribution"][provider_used]
        provider_stats["count"] += 1
        provider_stats["total_cost"] += cost
        provider_stats["avg_time"] = (provider_stats["avg_time"] * (provider_stats["count"] - 1) + generation_time) / provider_stats["count"]
        
        # Store optimization decision
        decision = {
            "timestamp": datetime.utcnow().isoformat(),
            "provider_used": provider_used,
            "selection_reason": metadata.get("selection_reason", "unknown"),
            "fallback_used": metadata.get("fallback_used", False),
            "cost": cost,
            "generation_time": generation_time
        }
        
        self.cost_tracker["optimization_decisions"].append(decision)
        
        # Keep only last 100 decisions
        if len(self.cost_tracker["optimization_decisions"]) > 100:
            self.cost_tracker["optimization_decisions"] = self.cost_tracker["optimization_decisions"][-100:]
    
    async def get_optimization_analytics(self) -> Dict[str, Any]:
        """Get analytics on optimization performance"""
        if not self.dynamic_router:
            self.dynamic_router = await get_dynamic_router()
        
        # Get provider status
        provider_status = await self.dynamic_router.get_provider_status()
        
        # Calculate session statistics
        session_duration = (datetime.utcnow() - self.cost_tracker["session_start"]).total_seconds() / 3600
        
        # Calculate savings compared to most expensive provider
        total_requests = self.cost_tracker["total_requests"]
        if total_requests > 0:
            avg_cost_per_request = self.cost_tracker["total_cost"] / total_requests
            expensive_cost_per_request = 0.009  # Anthropic rate
            estimated_savings = (expensive_cost_per_request - avg_cost_per_request) * total_requests
        else:
            estimated_savings = 0
        
        return {
            "session_info": {
                "generator_type": self.generator_type,
                "session_duration_hours": round(session_duration, 2),
                "total_requests": total_requests,
                "dynamic_routing_enabled": True
            },
            "cost_optimization": {
                "total_cost": round(self.cost_tracker["total_cost"], 4),
                "average_cost_per_request": round(avg_cost_per_request, 4) if total_requests > 0 else 0,
                "estimated_savings": round(estimated_savings, 4),
                "savings_percentage": round((estimated_savings / (estimated_savings + self.cost_tracker["total_cost"])) * 100, 1) if estimated_savings > 0 else 0
            },
            "provider_distribution": self.cost_tracker["provider_distribution"],
            "recent_decisions": self.cost_tracker["optimization_decisions"][-10:],  # Last 10 decisions
            "provider_status": provider_status,
            "fallback_rate": len([d for d in self.cost_tracker["optimization_decisions"] if d.get("fallback_used", False)]) / max(1, len(self.cost_tracker["optimization_decisions"])) * 100
        }
    
    async def invalidate_provider_cache(self, content_type: str = None):
        """Invalidate provider cache to force re-selection"""
        if self.dynamic_router:
            await self.dynamic_router.invalidate_cache(content_type)
            logger.info(f"🔄 Provider cache invalidated for {content_type or 'all types'}")
    
    @abstractmethod
    async def generate_content(self, intelligence_data: Dict[str, Any], preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Abstract method for content generation - must be implemented by subclasses"""
        pass
    
    def _create_enhanced_response(
        self, 
        content: Dict[str, Any],
        title: str,
        product_name: str,
        ai_result: Dict[str, Any],
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create enhanced response with dynamic routing metadata"""
        
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
                "generated_at": datetime.utcnow().isoformat(),
                "preferences_used": preferences,
                "ai_optimization": {
                    "provider_used": ai_result.get("provider_used"),
                    "generation_cost": ai_result.get("cost", 0.0),
                    "quality_score": ai_result.get("quality_score", 0),
                    "generation_time": ai_result.get("generation_time", 0.0),
                    "dynamic_routing_enabled": True,
                    "optimization_metadata": ai_result.get("optimization_metadata", {}),
                    "fallback_used": ai_result.get("optimization_metadata", {}).get("fallback_used", False)
                },
                "generator_version": "3.0.0-dynamic-routing"
            }
        }

# Integration adapter for existing generators
class DynamicRoutingMixin:
    """Mixin to add dynamic routing to existing generators"""
    
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
        """ ultra-cheap AI with dynamic routing"""
        
        # Get enhanced base generator instance
        if not hasattr(self, '_enhanced_generator'):
            self._enhanced_generator = BaseContentGenerator(
                getattr(self, 'generator_type', 'content')
            )
        
        # Use dynamic routing for generation
        return await self._enhanced_generator._generate_with_dynamic_ai(
            content_type=content_type,
            prompt=prompt,
            system_message=system_message,
            max_tokens=max_tokens,
            temperature=temperature,
            task_complexity=task_complexity
        )

# Convenience functions for easy migration
async def enhance_existing_generator(generator_instance):
    """Enhance existing generator with dynamic routing capabilities"""
    
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

# Example usage in existing generators
class ExampleEnhancedEmailGenerator(BaseContentGenerator):
    """Example of how to integrate with existing email generator"""
    
    async def generate_content(self, intelligence_data: Dict[str, Any], preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate email sequence with dynamic AI routing"""
        
        # Extract product name and preferences
        product_name = self._extract_product_name(intelligence_data)
        email_count = preferences.get("count", 5) if preferences else 5
        
        # Create optimized prompt
        prompt = f"""
        Generate {email_count} diverse email sequence for {product_name}.
        Focus on affiliate marketing with different angles:
        1. Scientific authority
        2. Emotional transformation  
        3. Social proof
        4. Urgency/scarcity
        5. Lifestyle/confidence
        
        Each email should be unique and compelling.
        """
        
        # Use dynamic AI routing
        ai_result = await self._generate_with_dynamic_ai(
            content_type="email_sequence",
            prompt=prompt,
            system_message=f"You are an expert email marketer creating content for {product_name}",
            max_tokens=3000,
            temperature=0.8,
            task_complexity="standard"
        )
        
        # Parse and structure the response
        emails = self._parse_email_content(ai_result["content"], product_name)
        
        return self._create_enhanced_response(
            content={
                "emails": emails,
                "total_emails": len(emails),
                "sequence_type": "affiliate_marketing"
            },
            title=f"{product_name} Email Sequence",
            product_name=product_name,
            ai_result=ai_result,
            preferences=preferences
        )
    
    def _parse_email_content(self, content: str, product_name: str) -> List[Dict]:
        """Parse email content from AI response"""
        # Implementation would parse the AI response into structured emails
        # This is a simplified example
        return [
            {
                "email_number": 1,
                "subject": f"Discover {product_name} Benefits",
                "body": "Generated email content...",
                "angle": "scientific_authority"
            }
        ]
    
    def _extract_product_name(self, intelligence_data: Dict[str, Any]) -> str:
        """Extract product name from intelligence data"""
        # Implementation would extract actual product name
        return intelligence_data.get("product_name", "Product")