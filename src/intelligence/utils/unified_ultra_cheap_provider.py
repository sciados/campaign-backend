# src/intelligence/utils/unified_ultra_cheap_provider.py
"""
UNIFIED ULTRA-CHEAP AI PROVIDER SYSTEM
✅ Combines text + image generation with 95-97% cost savings
✅ Integrates with existing smart_ai_balancer and tiered_ai_provider
✅ Unified API for all content generators
✅ Advanced cost tracking and optimization
✅ Production-ready with comprehensive error handling
"""

import os
import asyncio
import aiohttp
import base64
import logging
import time
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ProviderType(Enum):
    TEXT = "text"
    IMAGE = "image"
    MULTIMODAL = "multimodal"

class ProviderTier(Enum):
    ULTRA_CHEAP = "ultra_cheap"    # $0.0001-0.001/1K tokens
    CHEAP = "cheap"                # $0.001-0.005/1K tokens  
    FALLBACK = "fallback"          # $0.005-0.015/1K tokens
    EMERGENCY = "emergency"        # $0.015+/1K tokens

@dataclass
class UnifiedProvider:
    """Unified provider configuration for text and image generation"""
    name: str
    provider_type: ProviderType
    tier: ProviderTier
    cost_per_1k_tokens: float
    cost_per_image: float
    quality_score: float
    speed_rating: int
    api_key_env: str
    client: Any = None
    available: bool = False
    rate_limited_until: Optional[datetime] = None
    consecutive_failures: int = 0
    total_requests: int = 0
    total_failures: int = 0
    strengths: List[str] = None

class UnifiedUltraCheapProvider:
    """
    Unified ultra-cheap AI provider for text and image generation
    Integrates with existing load balancer and tiered systems
    """
    
    def __init__(self):
        self.providers = []
        self.text_providers = []
        self.image_providers = []
        self.cost_tracker = {
            "session_start": datetime.now(timezone.utc),
            "total_text_requests": 0,
            "total_image_requests": 0,
            "total_text_cost": 0.0,
            "total_image_cost": 0.0,
            "total_savings": 0.0,
            "provider_performance": {}
        }
        self._initialize_unified_providers()
        
        logger.info("🚀 Unified Ultra-Cheap AI Provider System Initialized")
        self._log_savings_potential()
    
    def _initialize_unified_providers(self):
        """Initialize all ultra-cheap providers for text and image"""
        
        # TEXT PROVIDERS - Ultra-cheap tier
        text_providers_config = [
            {
                "name": "groq",
                "provider_type": ProviderType.TEXT,
                "tier": ProviderTier.ULTRA_CHEAP,
                "cost_per_1k_tokens": 0.0002,
                "cost_per_image": 0.0,
                "quality_score": 78.0,
                "speed_rating": 10,
                "api_key_env": "GROQ_API_KEY",
                "strengths": ["speed", "cost", "conversational", "structured_data"],
                "client_init": self._init_groq
            },
            {
                "name": "together",
                "provider_type": ProviderType.TEXT,
                "tier": ProviderTier.ULTRA_CHEAP,
                "cost_per_1k_tokens": 0.0008,
                "cost_per_image": 0.0,
                "quality_score": 82.0,
                "speed_rating": 7,
                "api_key_env": "TOGETHER_API_KEY",
                "strengths": ["creativity", "long_form", "analysis", "versatility"],
                "client_init": self._init_together
            },
            {
                "name": "deepseek",
                "provider_type": ProviderType.TEXT,
                "tier": ProviderTier.ULTRA_CHEAP,
                "cost_per_1k_tokens": 0.00014,
                "cost_per_image": 0.0,
                "quality_score": 72.0,
                "speed_rating": 6,
                "api_key_env": "DEEPSEEK_API_KEY",
                "strengths": ["reasoning", "math", "structured_content"],
                "client_init": self._init_deepseek
            }
        ]
        
        # IMAGE PROVIDERS - Ultra-cheap tier
        image_providers_config = [
            {
                "name": "stability_ai",
                "provider_type": ProviderType.IMAGE,
                "tier": ProviderTier.ULTRA_CHEAP,
                "cost_per_1k_tokens": 0.0,
                "cost_per_image": 0.002,
                "quality_score": 85.0,
                "speed_rating": 7,
                "api_key_env": "STABILITY_API_KEY",
                "strengths": ["image_quality", "cost", "variety"],
                "client_init": self._init_stability_ai
            },
            {
                "name": "replicate_image",
                "provider_type": ProviderType.IMAGE,
                "tier": ProviderTier.ULTRA_CHEAP,
                "cost_per_1k_tokens": 0.0,
                "cost_per_image": 0.004,
                "quality_score": 80.0,
                "speed_rating": 6,
                "api_key_env": "REPLICATE_API_TOKEN",
                "strengths": ["model_variety", "custom_models"],
                "client_init": self._init_replicate_image
            },
            {
                "name": "together_image",
                "provider_type": ProviderType.IMAGE,
                "tier": ProviderTier.ULTRA_CHEAP,
                "cost_per_1k_tokens": 0.0,
                "cost_per_image": 0.008,
                "quality_score": 78.0,
                "speed_rating": 5,
                "api_key_env": "TOGETHER_API_KEY",
                "strengths": ["fast_generation", "reliable"],
                "client_init": self._init_together_image
            },
            {
                "name": "fal_ai",
                "provider_type": ProviderType.IMAGE,
                "tier": ProviderTier.ULTRA_CHEAP,
                "cost_per_1k_tokens": 0.0,
                "cost_per_image": 0.0015,
                "quality_score": 83.0,
                "speed_rating": 9,
                "api_key_env": "FAL_API_KEY",
                "strengths": ["ultra_fast", "cost_effective", "reliable"],
                "client_init": self._init_fal_ai
            }
        ]
        
        # FALLBACK PROVIDERS - Higher cost but more reliable
        fallback_providers_config = [
            {
                "name": "anthropic",
                "provider_type": ProviderType.TEXT,
                "tier": ProviderTier.FALLBACK,
                "cost_per_1k_tokens": 0.0025,
                "cost_per_image": 0.0,
                "quality_score": 90.0,
                "speed_rating": 6,
                "api_key_env": "ANTHROPIC_API_KEY",
                "strengths": ["long_form", "structured_content", "analysis", "safety"],
                "client_init": self._init_anthropic
            },
            {
                "name": "openai_dalle",
                "provider_type": ProviderType.IMAGE,
                "tier": ProviderTier.EMERGENCY,
                "cost_per_1k_tokens": 0.0,
                "cost_per_image": 0.040,
                "quality_score": 92.0,
                "speed_rating": 8,
                "api_key_env": "OPENAI_API_KEY",
                "strengths": ["image_quality", "reliability", "consistency"],
                "client_init": self._init_openai_dalle
            },
            {
                "name": "openai_text",
                "provider_type": ProviderType.TEXT,
                "tier": ProviderTier.EMERGENCY,
                "cost_per_1k_tokens": 0.0015,  # GPT-3.5-turbo
                "cost_per_image": 0.0,
                "quality_score": 88.0,
                "speed_rating": 7,
                "api_key_env": "OPENAI_API_KEY",
                "strengths": ["reliability", "conversational", "versatility"],
                "client_init": self._init_openai_text
            }
        ]
        
        # Initialize all providers
        all_configs = text_providers_config + image_providers_config + fallback_providers_config
        
        for config in all_configs:
            provider = UnifiedProvider(
                name=config["name"],
                provider_type=config["provider_type"],
                tier=config["tier"],
                cost_per_1k_tokens=config["cost_per_1k_tokens"],
                cost_per_image=config["cost_per_image"],
                quality_score=config["quality_score"],
                speed_rating=config["speed_rating"],
                api_key_env=config["api_key_env"],
                strengths=config["strengths"]
            )
            
            # Try to initialize the provider
            try:
                if config["client_init"](provider):
                    self.providers.append(provider)
                    
                    # Categorize by type
                    if provider.provider_type == ProviderType.TEXT:
                        self.text_providers.append(provider)
                    elif provider.provider_type == ProviderType.IMAGE:
                        self.image_providers.append(provider)
                    
                    logger.info(f"✅ {provider.name}: {provider.provider_type.value} provider initialized")
            
            except Exception as e:
                logger.warning(f"⚠️ {config['name']}: Failed to initialize - {str(e)}")
        
        # Sort providers by cost (cheapest first)
        self.text_providers.sort(key=lambda x: x.cost_per_1k_tokens)
        self.image_providers.sort(key=lambda x: x.cost_per_image)
        self.providers.sort(key=lambda x: x.cost_per_1k_tokens + x.cost_per_image)
    
    def _init_groq(self, provider: UnifiedProvider) -> bool:
        """Initialize Groq client"""
        api_key = os.getenv(provider.api_key_env)
        if not api_key:
            return False
        
        try:
            import groq
            provider.client = groq.AsyncGroq(api_key=api_key)
            provider.available = True
            return True
        except ImportError:
            logger.warning(f"⚠️ {provider.name}: groq package not installed. Run: pip install groq")
            return False
        except Exception as e:
            logger.error(f"❌ {provider.name}: Failed to initialize - {str(e)}")
            return False
    
    def _init_together(self, provider: UnifiedProvider) -> bool:
        """Initialize Together AI client for text"""
        api_key = os.getenv(provider.api_key_env)
        if not api_key:
            return False
        
        try:
            import openai
            provider.client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.together.xyz/v1"
            )
            provider.available = True
            return True
        except Exception as e:
            logger.error(f"❌ {provider.name}: Failed to initialize - {str(e)}")
            return False
    
    def _init_deepseek(self, provider: UnifiedProvider) -> bool:
        """Initialize DeepSeek client"""
        api_key = os.getenv(provider.api_key_env)
        if not api_key:
            return False
        
        try:
            import openai
            provider.client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
            provider.available = True
            return True
        except Exception as e:
            logger.error(f"❌ {provider.name}: Failed to initialize - {str(e)}")
            return False
    
    def _init_stability_ai(self, provider: UnifiedProvider) -> bool:
        """Initialize Stability AI client"""
        api_key = os.getenv(provider.api_key_env)
        if not api_key:
            return False
        
        provider.client = {
            "api_key": api_key,
            "endpoint": "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        }
        provider.available = True
        return True
    
    def _init_replicate_image(self, provider: UnifiedProvider) -> bool:
        """Initialize Replicate client for images"""
        api_key = os.getenv(provider.api_key_env)
        if not api_key:
            return False
        
        try:
            import replicate
            provider.client = replicate.Client(api_token=api_key)
            provider.available = True
            return True
        except ImportError:
            logger.warning(f"⚠️ {provider.name}: replicate package not installed. Run: pip install replicate")
            return False
        except Exception as e:
            logger.error(f"❌ {provider.name}: Failed to initialize - {str(e)}")
            return False
    
    def _init_fal_ai(self, provider: UnifiedProvider) -> bool:
        """Initialize FAL AI client"""
        api_key = os.getenv(provider.api_key_env)
        if not api_key:
            return False
        
        try:
            import fal_client
            provider.client = {
                "api_key": api_key,
                "fal_client": fal_client
            }
            provider.available = True
            return True
        except ImportError:
            logger.warning(f"⚠️ {provider.name}: fal-client package not installed. Run: pip install fal-client")
            return False
        except Exception as e:
            logger.error(f"❌ {provider.name}: Failed to initialize - {str(e)}")
            return False
    
    def _init_together_image(self, provider: UnifiedProvider) -> bool:
        """Initialize Together AI client for images"""
        api_key = os.getenv(provider.api_key_env)
        if not api_key:
            return False
        
        try:
            import openai
            provider.client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.together.xyz/v1"
            )
            provider.available = True
            return True
        except Exception as e:
            logger.error(f"❌ {provider.name}: Failed to initialize - {str(e)}")
            return False
    
    def _init_anthropic(self, provider: UnifiedProvider) -> bool:
        """Initialize Anthropic client"""
        api_key = os.getenv(provider.api_key_env)
        if not api_key:
            return False
        
        try:
            import anthropic
            provider.client = anthropic.AsyncAnthropic(api_key=api_key)
            provider.available = True
            return True
        except ImportError:
            logger.warning(f"⚠️ {provider.name}: anthropic package not installed. Run: pip install anthropic")
            return False
        except Exception as e:
            logger.error(f"❌ {provider.name}: Failed to initialize - {str(e)}")
            return False
    
    def _init_openai_dalle(self, provider: UnifiedProvider) -> bool:
        """Initialize OpenAI client for DALL-E"""
        api_key = os.getenv(provider.api_key_env)
        if not api_key:
            return False
        
        try:
            import openai
            provider.client = openai.AsyncOpenAI(api_key=api_key)
            provider.available = True
            return True
        except Exception as e:
            logger.error(f"❌ {provider.name}: Failed to initialize - {str(e)}")
            return False
    
    def _init_openai_text(self, provider: UnifiedProvider) -> bool:
        """Initialize OpenAI client for text"""
        api_key = os.getenv(provider.api_key_env)
        if not api_key:
            return False
        
        try:
            import openai
            provider.client = openai.AsyncOpenAI(api_key=api_key)
            provider.available = True
            return True
        except Exception as e:
            logger.error(f"❌ {provider.name}: Failed to initialize - {str(e)}")
            return False
    
    def _log_savings_potential(self):
        """Log potential cost savings"""
        if self.text_providers:
            cheapest_text = min(self.text_providers, key=lambda x: x.cost_per_1k_tokens)
            openai_text_cost = 0.030  # GPT-4 baseline
            text_savings = ((openai_text_cost - cheapest_text.cost_per_1k_tokens) / openai_text_cost) * 100
            
            logger.info(f"💰 CHEAPEST TEXT: {cheapest_text.name} (${cheapest_text.cost_per_1k_tokens:.5f}/1K)")
            logger.info(f"🎯 TEXT SAVINGS: {text_savings:.1f}% vs OpenAI GPT-4")
        
        if self.image_providers:
            cheapest_image = min(self.image_providers, key=lambda x: x.cost_per_image)
            dalle_cost = 0.040  # DALL-E baseline
            image_savings = ((dalle_cost - cheapest_image.cost_per_image) / dalle_cost) * 100
            
            logger.info(f"💰 CHEAPEST IMAGE: {cheapest_image.name} (${cheapest_image.cost_per_image:.4f}/image)")
            logger.info(f"🎯 IMAGE SAVINGS: {image_savings:.1f}% vs DALL-E")
        
        total_text = len(self.text_providers)
        total_image = len(self.image_providers)
        logger.info(f"🔄 PROVIDERS: {total_text} text, {total_image} image")
    
    async def generate_text(
        self,
        prompt: str,
        system_message: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.3,
        required_strength: str = None
    ) -> Dict[str, Any]:
        """Generate text using ultra-cheap providers with failover"""
        
        start_time = time.time()
        candidate_providers = self._get_available_text_providers(required_strength)
        
        if not candidate_providers:
            raise Exception("No text providers available")
        
        for provider in candidate_providers:
            try:
                # Check rate limiting
                if provider.rate_limited_until and datetime.now(timezone.utc) < provider.rate_limited_until:
                    continue
                
                logger.info(f"🤖 Text generation with {provider.name} (${provider.cost_per_1k_tokens:.5f}/1K)")
                
                # Estimate cost
                estimated_tokens = len(prompt.split()) * 1.3 + max_tokens
                estimated_cost = (estimated_tokens / 1000) * provider.cost_per_1k_tokens
                
                # Make API call based on provider
                if provider.name == "groq":
                    result = await self._call_groq_text(provider, prompt, system_message, max_tokens, temperature)
                elif provider.name in ["together", "deepseek", "openai_text"]:
                    result = await self._call_openai_compatible_text(provider, prompt, system_message, max_tokens, temperature)
                elif provider.name == "anthropic":
                    result = await self._call_anthropic_text(provider, prompt, system_message, max_tokens, temperature)
                
                if result and result.get("content"):
                    # Track success
                    self._track_text_success(provider, estimated_cost, start_time)
                    
                    return {
                        "content": result["content"],
                        "provider_used": provider.name,
                        "provider_tier": provider.tier.value,
                        "cost": estimated_cost,
                        "quality_score": provider.quality_score,
                        "generation_time": time.time() - start_time,
                        "cost_optimization": {
                            "cost_per_1k": provider.cost_per_1k_tokens,
                            "savings_vs_openai": 0.030 - provider.cost_per_1k_tokens,
                            "total_cost": estimated_cost
                        }
                    }
            
            except Exception as e:
                self._track_text_failure(provider, str(e))
                continue
        
        raise Exception("All text providers failed")
    
    async def generate_image(
        self,
        prompt: str,
        platform: str = "instagram",
        negative_prompt: str = "",
        style_preset: str = "photographic"
    ) -> Dict[str, Any]:
        """Generate image using ultra-cheap providers with failover"""
        
        start_time = time.time()
        candidate_providers = self._get_available_image_providers()
        
        if not candidate_providers:
            raise Exception("No image providers available")
        
        for provider in candidate_providers:
            try:
                # Check rate limiting
                if provider.rate_limited_until and datetime.now(timezone.utc) < provider.rate_limited_until:
                    continue
                
                logger.info(f"🎨 Image generation with {provider.name} (${provider.cost_per_image:.4f}/image)")
                
                # Make API call based on provider
                if provider.name == "stability_ai":
                    result = await self._call_stability_ai(provider, prompt, platform, negative_prompt, style_preset)
                elif provider.name == "replicate_image":
                    result = await self._call_replicate_image(provider, prompt, platform)
                elif provider.name == "fal_ai":
                    result = await self._call_fal_ai(provider, prompt, platform)
                elif provider.name == "together_image":
                    result = await self._call_together_image(provider, prompt, platform)
                elif provider.name == "openai_dalle":
                    result = await self._call_openai_dalle(provider, prompt, platform)
                
                if result and result.get("image_data"):
                    # Track success
                    self._track_image_success(provider, start_time)
                    
                    return {
                        "image_data": result["image_data"],
                        "provider_used": provider.name,
                        "provider_tier": provider.tier.value,
                        "cost": provider.cost_per_image,
                        "quality_score": provider.quality_score,
                        "generation_time": time.time() - start_time,
                        "cost_optimization": {
                            "cost_per_image": provider.cost_per_image,
                            "savings_vs_dalle": 0.040 - provider.cost_per_image,
                            "total_cost": provider.cost_per_image
                        },
                        "platform": platform,
                        "prompt": prompt
                    }
            
            except Exception as e:
                self._track_image_failure(provider, str(e))
                continue
        
        raise Exception("All image providers failed")
    
    def _get_available_text_providers(self, required_strength: str = None) -> List[UnifiedProvider]:
        """Get available text providers, optionally filtered by strength"""
        providers = [p for p in self.text_providers if p.available]
        
        if required_strength:
            providers = [p for p in providers if required_strength in (p.strengths or [])]
        
        return providers
    
    def _get_available_image_providers(self) -> List[UnifiedProvider]:
        """Get available image providers"""
        return [p for p in self.image_providers if p.available]
    
    async def _call_groq_text(self, provider: UnifiedProvider, prompt: str, system_message: str, max_tokens: int, temperature: float) -> Dict:
        """Call Groq for text generation"""
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        response = await provider.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return {"content": response.choices[0].message.content}
    
    async def _call_openai_compatible_text(self, provider: UnifiedProvider, prompt: str, system_message: str, max_tokens: int, temperature: float) -> Dict:
        """Call OpenAI-compatible providers for text"""
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        model_map = {
            "together": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            "deepseek": "deepseek-chat",
            "openai_text": "gpt-3.5-turbo"
        }
        
        response = await provider.client.chat.completions.create(
            model=model_map[provider.name],
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return {"content": response.choices[0].message.content}
    
    async def _call_anthropic_text(self, provider: UnifiedProvider, prompt: str, system_message: str, max_tokens: int, temperature: float) -> Dict:
        """Call Anthropic for text generation"""
        full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt
        
        response = await provider.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": full_prompt}]
        )
        
        return {"content": response.content[0].text}
    
    async def _call_fal_ai(self, provider: UnifiedProvider, prompt: str, platform: str) -> Dict:
        """Call FAL AI for ultra-fast image generation"""
        platform_sizes = {
            "instagram": "square_hd",
            "facebook": "landscape_4_3", 
            "tiktok": "portrait_9_16",
            "linkedin": "landscape_4_3"
        }
        
        image_size = platform_sizes.get(platform, "square_hd")
        
        try:
            # FAL AI Flux model - ultra-fast and cheap
            result = await provider.client["fal_client"].subscribe_async(
                "fal-ai/flux/schnell",
                arguments={
                    "prompt": prompt,
                    "image_size": image_size,
                    "num_inference_steps": 4,  # Ultra-fast
                    "num_images": 1,
                    "enable_safety_checker": True
                }
            )
            
            if result and "images" in result and len(result["images"]) > 0:
                image_url = result["images"][0]["url"]
                
                # Download and encode image
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url) as response:
                        if response.status == 200:
                            image_data = await response.read()
                            image_base64 = base64.b64encode(image_data).decode()
                            
                            return {
                                "image_data": {
                                    "image_base64": image_base64,
                                    "format": "png",
                                    "url": image_url
                                }
                            }
            
            raise Exception("FAL AI returned no image data")
            
        except Exception as e:
            raise Exception(f"FAL AI generation failed: {str(e)}")
    
    async def _call_stability_ai(self, provider: UnifiedProvider, prompt: str, platform: str, negative_prompt: str, style_preset: str) -> Dict:
        """Call Stability AI for image generation"""
        platform_sizes = {
            "instagram": "1024x1024",
            "facebook": "1200x630", 
            "tiktok": "1080x1920",
            "linkedin": "1200x627"
        }
        
        size = platform_sizes.get(platform, "1024x1024")
        width, height = map(int, size.split("x"))
        
        payload = {
            "text_prompts": [{"text": prompt, "weight": 1}],
            "cfg_scale": 7,
            "height": height,
            "width": width,
            "samples": 1,
            "steps": 30,
            "style_preset": style_preset
        }
        
        if negative_prompt:
            payload["text_prompts"].append({"text": negative_prompt, "weight": -1})
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {provider.client['api_key']}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(provider.client["endpoint"], json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "image_data": {
                            "image_base64": result["artifacts"][0]["base64"],
                            "format": "png"
                        }
                    }
                else:
                    raise Exception(f"Stability AI error: {await response.text()}")
    
    async def _call_replicate_image(self, provider: UnifiedProvider, prompt: str, platform: str) -> Dict:
        """Call Replicate for image generation"""
        platform_sizes = {
            "instagram": (1024, 1024),
            "facebook": (1200, 630),
            "tiktok": (1080, 1920),
            "linkedin": (1200, 627)
        }
        
        width, height = platform_sizes.get(platform, (1024, 1024))
        
        output = await provider.client.run(
            "ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
            input={
                "prompt": prompt,
                "width": width,
                "height": height,
                "num_outputs": 1,
                "scheduler": "K_EULER",
                "num_inference_steps": 30,
                "guidance_scale": 7.5
            }
        )
        
        if output and len(output) > 0:
            # Download and encode image
            async with aiohttp.ClientSession() as session:
                async with session.get(output[0]) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        image_base64 = base64.b64encode(image_data).decode()
                        return {
                            "image_data": {
                                "image_base64": image_base64,
                                "format": "png"
                            }
                        }
        
        raise Exception("Replicate image generation failed")
    
    async def _call_together_image(self, provider: UnifiedProvider, prompt: str, platform: str) -> Dict:
        """Call Together AI for image generation"""
        platform_sizes = {
            "instagram": (1024, 1024),
            "facebook": (1200, 630),
            "tiktok": (1080, 1920),
            "linkedin": (1200, 627)
        }
        
        width, height = platform_sizes.get(platform, (1024, 1024))
        
        response = await provider.client.images.generate(
            model="runwayml/stable-diffusion-v1-5",
            prompt=prompt,
            size=f"{width}x{height}",
            n=1,
            response_format="b64_json"
        )
        
        if response.data and len(response.data) > 0:
            return {
                "image_data": {
                    "image_base64": response.data[0].b64_json,
                    "format": "png"
                }
            }
        
        raise Exception("Together AI image generation failed")
    
    async def _call_openai_dalle(self, provider: UnifiedProvider, prompt: str, platform: str) -> Dict:
        """Call OpenAI DALL-E for image generation"""
        platform_sizes = {
            "instagram": "1024x1024",
            "facebook": "1792x1024",
            "tiktok": "1024x1792",
            "linkedin": "1792x1024"
        }
        
        size = platform_sizes.get(platform, "1024x1024")
        
        response = await provider.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            n=1,
            response_format="b64_json"
        )
        
        return {
            "image_data": {
                "image_base64": response.data[0].b64_json,
                "format": "png"
            }
        }
    
    def _track_text_success(self, provider: UnifiedProvider, cost: float, start_time: float):
        """Track successful text generation"""
        provider.consecutive_failures = 0
        provider.total_requests += 1
        
        self.cost_tracker["total_text_requests"] += 1
        self.cost_tracker["total_text_cost"] += cost
        self.cost_tracker["total_savings"] += (0.030 - provider.cost_per_1k_tokens) * (cost / provider.cost_per_1k_tokens)
        
        self._update_provider_performance(provider, True, time.time() - start_time)
    
    def _track_image_success(self, provider: UnifiedProvider, start_time: float):
        """Track successful image generation"""
        provider.consecutive_failures = 0
        provider.total_requests += 1
        
        self.cost_tracker["total_image_requests"] += 1
        self.cost_tracker["total_image_cost"] += provider.cost_per_image
        self.cost_tracker["total_savings"] += (0.040 - provider.cost_per_image)
        
        self._update_provider_performance(provider, True, time.time() - start_time)
    
    def _track_text_failure(self, provider: UnifiedProvider, error_message: str):
        """Track failed text generation"""
        provider.consecutive_failures += 1
        provider.total_requests += 1
        provider.total_failures += 1
        
        self._handle_provider_failure(provider, error_message)
        self._update_provider_performance(provider, False, 0)
    
    def _track_image_failure(self, provider: UnifiedProvider, error_message: str):
        """Track failed image generation"""
        provider.consecutive_failures += 1
        provider.total_requests += 1
        provider.total_failures += 1
        
        self._handle_provider_failure(provider, error_message)
        self._update_provider_performance(provider, False, 0)
    
    def _handle_provider_failure(self, provider: UnifiedProvider, error_message: str):
        """Handle provider failure and rate limiting"""
        if "rate limit" in error_message.lower() or "429" in error_message:
            # Rate limited - disable for a period
            retry_seconds = 60
            provider.rate_limited_until = datetime.now(timezone.utc) + timedelta(seconds=retry_seconds)
            logger.warning(f"🚨 {provider.name}: Rate limited for {retry_seconds}s")
        
        elif provider.consecutive_failures >= 3:
            # Too many failures - disable temporarily
            provider.available = False
            provider.rate_limited_until = datetime.now(timezone.utc) + timedelta(minutes=5)
            logger.warning(f"⚠️ {provider.name}: Disabled due to {provider.consecutive_failures} failures")
    
    def _update_provider_performance(self, provider: UnifiedProvider, success: bool, response_time: float):
        """Update provider performance metrics"""
        if provider.name not in self.cost_tracker["provider_performance"]:
            self.cost_tracker["provider_performance"][provider.name] = {
                "requests": 0,
                "successes": 0,
                "failures": 0,
                "avg_response_time": 0.0,
                "success_rate": 100.0
            }
        
        perf = self.cost_tracker["provider_performance"][provider.name]
        perf["requests"] += 1
        
        if success:
            perf["successes"] += 1
            # Update average response time
            current_avg = perf["avg_response_time"]
            success_count = perf["successes"]
            perf["avg_response_time"] = ((current_avg * (success_count - 1)) + response_time) / success_count
        else:
            perf["failures"] += 1
        
        perf["success_rate"] = (perf["successes"] / perf["requests"]) * 100
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get comprehensive cost summary"""
        session_duration = (datetime.now(timezone.utc) - self.cost_tracker["session_start"]).total_seconds() / 3600
        
        return {
            "unified_provider_system": {
                "version": "1.0.0",
                "text_providers": len(self.text_providers),
                "image_providers": len(self.image_providers),
                "session_duration_hours": session_duration
            },
            "usage_statistics": {
                "total_text_requests": self.cost_tracker["total_text_requests"],
                "total_image_requests": self.cost_tracker["total_image_requests"],
                "total_requests": self.cost_tracker["total_text_requests"] + self.cost_tracker["total_image_requests"]
            },
            "cost_performance": {
                "total_text_cost": self.cost_tracker["total_text_cost"],
                "total_image_cost": self.cost_tracker["total_image_cost"],
                "total_cost": self.cost_tracker["total_text_cost"] + self.cost_tracker["total_image_cost"],
                "total_savings": self.cost_tracker["total_savings"],
                "savings_percentage": (self.cost_tracker["total_savings"] / max(0.001, self.cost_tracker["total_savings"] + self.cost_tracker["total_text_cost"] + self.cost_tracker["total_image_cost"])) * 100
            },
            "provider_performance": self.cost_tracker["provider_performance"],
            "projections": {
                "monthly_cost_1000_users": (self.cost_tracker["total_text_cost"] + self.cost_tracker["total_image_cost"]) * 1000 * 30,
                "monthly_savings_1000_users": self.cost_tracker["total_savings"] * 1000 * 30,
                "annual_savings_1000_users": self.cost_tracker["total_savings"] * 1000 * 365
            }
        }
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        current_time = datetime.now(timezone.utc)
        
        status = {
            "text_providers": [],
            "image_providers": []
        }
        
        for provider in self.text_providers:
            is_available = provider.available and (not provider.rate_limited_until or current_time >= provider.rate_limited_until)
            status["text_providers"].append({
                "name": provider.name,
                "available": is_available,
                "tier": provider.tier.value,
                "cost_per_1k": provider.cost_per_1k_tokens,
                "quality_score": provider.quality_score,
                "consecutive_failures": provider.consecutive_failures,
                "total_requests": provider.total_requests,
                "success_rate": ((provider.total_requests - provider.total_failures) / max(1, provider.total_requests)) * 100,
                "rate_limited_until": provider.rate_limited_until.isoformat() if provider.rate_limited_until else None
            })
        
        for provider in self.image_providers:
            is_available = provider.available and (not provider.rate_limited_until or current_time >= provider.rate_limited_until)
            status["image_providers"].append({
                "name": provider.name,
                "available": is_available,
                "tier": provider.tier.value,
                "cost_per_image": provider.cost_per_image,
                "quality_score": provider.quality_score,
                "consecutive_failures": provider.consecutive_failures,
                "total_requests": provider.total_requests,
                "success_rate": ((provider.total_requests - provider.total_failures) / max(1, provider.total_requests)) * 100,
                "rate_limited_until": provider.rate_limited_until.isoformat() if provider.rate_limited_until else None
            })
        
        return status

    def log_performance_summary(self):
        """Log comprehensive performance summary"""
        summary = self.get_cost_summary()
        
        logger.info("🚀 UNIFIED ULTRA-CHEAP AI PERFORMANCE SUMMARY:")
        logger.info("=" * 60)
        
        # System info
        system = summary["unified_provider_system"]
        logger.info(f"Text providers: {system['text_providers']}")
        logger.info(f"Image providers: {system['image_providers']}")
        logger.info(f"Session duration: {system['session_duration_hours']:.1f} hours")
        
        # Usage statistics
        usage = summary["usage_statistics"]
        logger.info(f"Total requests: {usage['total_requests']} ({usage['total_text_requests']} text, {usage['total_image_requests']} image)")
        
        # Cost performance
        cost = summary["cost_performance"]
        logger.info(f"Total cost: ${cost['total_cost']:.4f}")
        logger.info(f"Total savings: ${cost['total_savings']:.2f}")
        logger.info(f"Savings percentage: {cost['savings_percentage']:.1f}%")
        
        # Top performers
        if summary["provider_performance"]:
            top_provider = max(summary["provider_performance"].items(), key=lambda x: x[1]["requests"])
            logger.info(f"Most used provider: {top_provider[0]} ({top_provider[1]['requests']} requests, {top_provider[1]['success_rate']:.1f}% success)")


# Global unified provider instance
_global_unified_provider = None

def get_unified_provider() -> UnifiedUltraCheapProvider:
    """Get or create global unified provider instance"""
    global _global_unified_provider
    
    if _global_unified_provider is None:
        _global_unified_provider = UnifiedUltraCheapProvider()
    
    return _global_unified_provider

# Convenience functions for easy integration
async def ultra_cheap_text_generation(
    prompt: str,
    system_message: str = "",
    max_tokens: int = 2000,
    temperature: float = 0.3,
    required_strength: str = None
) -> Dict[str, Any]:
    """Generate text using ultra-cheap providers"""
    provider = get_unified_provider()
    return await provider.generate_text(prompt, system_message, max_tokens, temperature, required_strength)

async def ultra_cheap_image_generation(
    prompt: str,
    platform: str = "instagram",
    negative_prompt: str = "",
    style_preset: str = "photographic"
) -> Dict[str, Any]:
    """Generate image using ultra-cheap providers"""
    provider = get_unified_provider()
    return await provider.generate_image(prompt, platform, negative_prompt, style_preset)

def get_ultra_cheap_cost_summary() -> Dict[str, Any]:
    """Get cost summary from unified provider"""
    provider = get_unified_provider()
    return provider.get_cost_summary()

def get_ultra_cheap_provider_status() -> Dict[str, Any]:
    """Get provider status from unified system"""
    provider = get_unified_provider()
    return provider.get_provider_status()

# Integration helpers for existing systems
def integrate_with_smart_balancer():
    """Integration point for smart_ai_balancer.py"""
    provider = get_unified_provider()
    
    # Convert unified providers to smart balancer format
    balancer_providers = []
    for text_provider in provider.text_providers:
        balancer_providers.append({
            "name": text_provider.name,
            "cost_per_1k_tokens": text_provider.cost_per_1k_tokens,
            "quality_score": text_provider.quality_score,
            "available": text_provider.available,
            "client": text_provider.client
        })
    
    return balancer_providers

def integrate_with_tiered_system():
    """Integration point for tiered_ai_provider.py"""
    provider = get_unified_provider()
    
    # Convert to tiered system format
    tiered_providers = []
    for text_provider in provider.text_providers:
        tiered_providers.append({
            "name": text_provider.name,
            "tier": text_provider.tier.value,
            "cost_per_1k_tokens": text_provider.cost_per_1k_tokens,
            "quality_score": text_provider.quality_score,
            "available": text_provider.available,
            "client": text_provider.client,
            "provider_type": "text"
        })
    
    for image_provider in provider.image_providers:
        tiered_providers.append({
            "name": image_provider.name,
            "tier": image_provider.tier.value,
            "cost_per_image": image_provider.cost_per_image,
            "quality_score": image_provider.quality_score,
            "available": image_provider.available,
            "client": image_provider.client,
            "provider_type": "image"
        })
    
    return tiered_providers

# Environment validation for Railway deployment
def validate_api_keys():
    """Validate API keys are properly configured"""
    required_keys = [
        "GROQ_API_KEY",
        "TOGETHER_API_KEY", 
        "DEEPSEEK_API_KEY",
        "STABILITY_API_KEY",
        "REPLICATE_API_TOKEN",
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY"
    ]
    
    available_keys = []
    missing_keys = []
    
    for key in required_keys:
        if os.getenv(key):
            available_keys.append(key)
        else:
            missing_keys.append(key)
    
    logger.info(f"🔑 API Keys Available: {len(available_keys)}/{len(required_keys)}")
    
    if available_keys:
        logger.info(f"✅ Available: {', '.join(available_keys)}")
    
    if missing_keys:
        logger.warning(f"⚠️ Missing: {', '.join(missing_keys)}")
        logger.info("💡 Add missing keys to Railway environment variables for optimal cost savings")
    
    return {
        "total_keys": len(required_keys),
        "available_keys": available_keys,
        "missing_keys": missing_keys,
        "coverage_percentage": (len(available_keys) / len(required_keys)) * 100
    }

# Cost projection helpers
def calculate_monthly_savings_projection(
    monthly_text_generations: int = 10000,
    monthly_image_generations: int = 1000,
    user_count: int = 1000
) -> Dict[str, Any]:
    """Calculate monthly savings projection based on usage"""
    
    # Baseline costs
    openai_text_cost = 0.030  # GPT-4 per 1K tokens
    dalle_image_cost = 0.040  # DALL-E per image
    
    # Ultra-cheap costs (average)
    ultra_cheap_text_cost = 0.0004  # Average of Groq, Together, DeepSeek
    ultra_cheap_image_cost = 0.003  # Average of Stability AI, Replicate
    
    # Calculate per user per month
    user_text_cost_openai = (monthly_text_generations / user_count) * (2000 / 1000) * openai_text_cost  # 2K tokens avg
    user_text_cost_ultra = (monthly_text_generations / user_count) * (2000 / 1000) * ultra_cheap_text_cost
    
    user_image_cost_openai = (monthly_image_generations / user_count) * dalle_image_cost
    user_image_cost_ultra = (monthly_image_generations / user_count) * ultra_cheap_image_cost
    
    # Scale to user count
    total_text_cost_openai = user_text_cost_openai * user_count
    total_text_cost_ultra = user_text_cost_ultra * user_count
    
    total_image_cost_openai = user_image_cost_openai * user_count
    total_image_cost_ultra = user_image_cost_ultra * user_count
    
    total_openai_cost = total_text_cost_openai + total_image_cost_openai
    total_ultra_cost = total_text_cost_ultra + total_image_cost_ultra
    
    monthly_savings = total_openai_cost - total_ultra_cost
    annual_savings = monthly_savings * 12
    
    return {
        "usage_parameters": {
            "user_count": user_count,
            "monthly_text_generations": monthly_text_generations,
            "monthly_image_generations": monthly_image_generations,
            "avg_tokens_per_text": 2000
        },
        "cost_comparison": {
            "openai_monthly": total_openai_cost,
            "ultra_cheap_monthly": total_ultra_cost,
            "monthly_savings": monthly_savings,
            "annual_savings": annual_savings
        },
        "breakdown": {
            "text_savings_monthly": total_text_cost_openai - total_text_cost_ultra,
            "image_savings_monthly": total_image_cost_openai - total_image_cost_ultra,
            "text_savings_percentage": ((total_text_cost_openai - total_text_cost_ultra) / total_text_cost_openai) * 100,
            "image_savings_percentage": ((total_image_cost_openai - total_image_cost_ultra) / total_image_cost_openai) * 100
        },
        "roi_metrics": {
            "payback_period_months": 0,  # Immediate savings
            "5_year_savings": annual_savings * 5,
            "cost_reduction_factor": total_openai_cost / total_ultra_cost if total_ultra_cost > 0 else float('inf')
        }
    }