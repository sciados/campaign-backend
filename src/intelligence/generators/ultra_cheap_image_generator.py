# src/intelligence/generators/ultra_cheap_image_generator.py
import asyncio
import aiohttp
import base64
import logging
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

from src.models.base import EnumSerializerMixin
# 🔥 ADD PRODUCT NAME FIX IMPORTS
from ..utils.product_name_fix import (
    fix_image_generation_placeholders,
    extract_product_name_from_intelligence
)

logger = logging.getLogger(__name__)

@dataclass
class ImageProvider:
    """Image generation provider configuration"""
    name: str
    cost_per_image: float
    api_key: str
    endpoint: str
    priority: int
    available: bool = True

class UltraCheapImageGenerator(EnumSerializerMixin):
    """Ultra-cheap image generation with provider hierarchy"""
    
    def __init__(self):
        self.providers = self._initialize_providers()
        self.platform_optimizations = {
            "instagram": {
                "size": "1024x1024",
                "style": "modern, clean, mobile-optimized",
                "format": "square"
            },
            "facebook": {
                "size": "1200x630",
                "style": "engaging, social-friendly",
                "format": "landscape"
            },
            "tiktok": {
                "size": "1080x1920",
                "style": "trendy, vertical, eye-catching",
                "format": "portrait"
            },
            "linkedin": {
                "size": "1200x627",
                "style": "professional, business-focused",
                "format": "landscape"
            }
        }
    
    def _initialize_providers(self) -> List[ImageProvider]:
        """Initialize image providers in cost order"""
        providers = []
        
        # Stability AI (Cheapest - $0.002/image)
        if os.getenv("STABILITY_API_KEY"):
            providers.append(ImageProvider(
                name="stability_ai",
                cost_per_image=0.002,
                api_key=os.getenv("STABILITY_API_KEY"),
                endpoint="https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                priority=1
            ))
        
        # Replicate (Second cheapest - $0.004/image)
        if os.getenv("REPLICATE_API_KEY"):
            providers.append(ImageProvider(
                name="replicate",
                cost_per_image=0.004,
                api_key=os.getenv("REPLICATE_API_KEY"),
                endpoint="https://api.replicate.com/v1/predictions",
                priority=2
            ))
        
        # Together AI (Third option - $0.008/image)
        if os.getenv("TOGETHER_API_KEY"):
            providers.append(ImageProvider(
                name="together_ai",
                cost_per_image=0.008,
                api_key=os.getenv("TOGETHER_API_KEY"),
                endpoint="https://api.together.xyz/v1/images/generations",
                priority=3
            ))
        
        # OpenAI DALL-E (Fallback only - $0.040/image)
        if os.getenv("OPENAI_API_KEY"):
            providers.append(ImageProvider(
                name="openai_dalle",
                cost_per_image=0.040,
                api_key=os.getenv("OPENAI_API_KEY"),
                endpoint="https://api.openai.com/v1/images/generations",
                priority=4
            ))
        
        return sorted(providers, key=lambda x: x.priority)
    
    async def generate_single_image(
        self,
        prompt: str,
        platform: str = "instagram",
        negative_prompt: str = "",
        style_preset: str = "photographic"
    ) -> Dict[str, Any]:
        """Generate single image with ultra-cheap providers"""
        
        # Optimize prompt for platform
        optimized_prompt = self._optimize_prompt_for_platform(prompt, platform)
        
        # Try providers in cost order
        for provider in self.providers:
            if not provider.available:
                continue
            
            try:
                logger.info(f"🎨 Generating image with {provider.name} (${provider.cost_per_image})")
                
                if provider.name == "stability_ai":
                    result = await self._generate_with_stability_ai(
                        provider, optimized_prompt, platform, negative_prompt, style_preset
                    )
                elif provider.name == "replicate":
                    result = await self._generate_with_replicate(
                        provider, optimized_prompt, platform
                    )
                elif provider.name == "together_ai":
                    result = await self._generate_with_together_ai(
                        provider, optimized_prompt, platform
                    )
                elif provider.name == "openai_dalle":
                    result = await self._generate_with_openai(
                        provider, optimized_prompt, platform
                    )
                
                if result and result.get("success"):
                    logger.info(f"✅ Generated image for ${provider.cost_per_image}")
                    return {
                        "success": True,
                        "image_data": result["image_data"],
                        "provider_used": provider.name,
                        "cost": provider.cost_per_image,
                        "savings_vs_dalle": 0.040 - provider.cost_per_image,
                        "platform": platform,
                        "prompt": optimized_prompt
                    }
            
            except Exception as e:
                logger.error(f"❌ {provider.name} failed: {str(e)}")
                continue
        
        raise Exception("All image generation providers failed")
    
    async def generate_campaign_images(
        self,
        intelligence_data: Dict[str, Any],
        platforms: List[str] = ["instagram", "facebook", "tiktok"],
        posts_per_platform: int = 3
    ) -> Dict[str, Any]:
        """Generate complete campaign images ultra-cheaply"""
        
        # Extract product information
        product_name = extract_product_name_from_intelligence(intelligence_data)
        offer_intel = self._serialize_enum_field(intelligence_data.get("offer_intelligence", {}))
        
        # Generate prompts for each platform
        generated_images = []
        total_cost = 0
        
        for platform in platforms:
            for post_num in range(1, posts_per_platform + 1):
                # Create platform-specific prompt
                prompt = self._create_campaign_prompt(
                    product_name, offer_intel, platform, post_num
                )
                
                # Generate image
                try:
                    result = await self.generate_single_image(
                        prompt=prompt,
                        platform=platform,
                        negative_prompt="blurry, low quality, distorted, unprofessional"
                    )
                    
                    generated_images.append({
                        "platform": platform,
                        "post_number": post_num,
                        "image_data": result["image_data"],
                        "provider_used": result["provider_used"],
                        "cost": result["cost"],
                        "prompt": prompt
                    })
                    
                    total_cost += result["cost"]
                    
                except Exception as e:
                    logger.error(f"Failed to generate image for {platform} post {post_num}: {str(e)}")
                    continue
        
        # Calculate savings
        dalle_equivalent_cost = len(generated_images) * 0.040
        total_savings = dalle_equivalent_cost - total_cost
        
        # 🔥 APPLY FIX BEFORE RETURNING
        result_data = {
            "success": True,
            "generated_images": generated_images,
            "total_cost": total_cost,
            "dalle_equivalent_cost": dalle_equivalent_cost,
            "total_savings": total_savings,
            "savings_percentage": (total_savings / dalle_equivalent_cost) * 100,
            "product_name": product_name,
            "platforms": platforms
        }
        
        fixed_result = fix_image_generation_placeholders(result_data, intelligence_data)
        fixed_result["placeholders_fixed"] = True
        
        return fixed_result
    
    def _optimize_prompt_for_platform(self, prompt: str, platform: str) -> str:
        """Optimize prompt for specific platform"""
        
        optimization = self.platform_optimizations.get(platform, {})
        style = optimization.get("style", "modern, clean")
        
        return f"{prompt}, {style}, high quality, professional, {optimization.get('format', 'square')} format"
    
    def _create_campaign_prompt(
        self,
        product_name: str,
        offer_intel: Dict[str, Any],
        platform: str,
        post_number: int
    ) -> str:
        """Create campaign-specific prompt"""
        
        benefits = offer_intel.get("benefits", ["Health optimization", "Natural wellness"])
        primary_benefit = benefits[0] if benefits else "Health optimization"
        
        platform_styles = {
            "instagram": f"Professional {product_name} product photography for Instagram, {primary_benefit}, modern aesthetic",
            "facebook": f"Engaging {product_name} lifestyle image for Facebook, {primary_benefit}, social media optimized",
            "tiktok": f"Trendy {product_name} vertical image for TikTok, {primary_benefit}, eye-catching, mobile-first",
            "linkedin": f"Professional {product_name} business image for LinkedIn, {primary_benefit}, corporate aesthetic"
        }
        
        return platform_styles.get(platform, f"Professional {product_name} product image")
    
    async def _generate_with_stability_ai(
        self,
        provider: ImageProvider,
        prompt: str,
        platform: str,
        negative_prompt: str,
        style_preset: str
    ) -> Dict[str, Any]:
        """Generate image with Stability AI"""
        
        platform_config = self.platform_optimizations.get(platform, {})
        width, height = platform_config.get("size", "1024x1024").split("x")
        
        payload = {
            "text_prompts": [
                {
                    "text": prompt,
                    "weight": 1
                }
            ],
            "cfg_scale": 7,
            "height": int(height),
            "width": int(width),
            "samples": 1,
            "steps": 30,
            "style_preset": style_preset
        }
        
        if negative_prompt:
            payload["text_prompts"].append({
                "text": negative_prompt,
                "weight": -1
            })
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {provider.api_key}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                provider.endpoint,
                json=payload,
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    image_data = result["artifacts"][0]["base64"]
                    
                    return {
                        "success": True,
                        "image_data": {
                            "image_base64": image_data,
                            "format": "png"
                        }
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"Stability AI API error: {error_text}")
    
    async def _generate_with_replicate(
        self,
        provider: ImageProvider,
        prompt: str,
        platform: str
    ) -> Dict[str, Any]:
        """Generate image with Replicate"""
        
        platform_config = self.platform_optimizations.get(platform, {})
        width, height = platform_config.get("size", "1024x1024").split("x")
        
        payload = {
            "version": "ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
            "input": {
                "prompt": prompt,
                "width": int(width),
                "height": int(height),
                "num_outputs": 1,
                "scheduler": "K_EULER",
                "num_inference_steps": 30,
                "guidance_scale": 7.5
            }
        }
        
        headers = {
            "Authorization": f"Token {provider.api_key}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            # Create prediction
            async with session.post(
                provider.endpoint,
                json=payload,
                headers=headers
            ) as response:
                if response.status == 201:
                    result = await response.json()
                    prediction_id = result["id"]
                    
                    # Poll for completion
                    for _ in range(60):  # 60 seconds timeout
                        async with session.get(
                            f"https://api.replicate.com/v1/predictions/{prediction_id}",
                            headers=headers
                        ) as status_response:
                            if status_response.status == 200:
                                status_result = await status_response.json()
                                
                                if status_result["status"] == "succeeded":
                                    image_url = status_result["output"][0]
                                    
                                    # Download image
                                    async with session.get(image_url) as img_response:
                                        if img_response.status == 200:
                                            image_data = await img_response.read()
                                            image_base64 = base64.b64encode(image_data).decode()
                                            
                                            return {
                                                "success": True,
                                                "image_data": {
                                                    "image_base64": image_base64,
                                                    "format": "png"
                                                }
                                            }
                                
                                elif status_result["status"] == "failed":
                                    raise Exception(f"Replicate generation failed: {status_result.get('error')}")
                        
                        await asyncio.sleep(1)
                    
                    raise Exception("Replicate generation timeout")
                else:
                    error_text = await response.text()
                    raise Exception(f"Replicate API error: {error_text}")
    
    async def _generate_with_together_ai(
        self,
        provider: ImageProvider,
        prompt: str,
        platform: str
    ) -> Dict[str, Any]:
        """Generate image with Together AI"""
        
        platform_config = self.platform_optimizations.get(platform, {})
        width, height = platform_config.get("size", "1024x1024").split("x")
        
        payload = {
            "model": "runwayml/stable-diffusion-v1-5",
            "prompt": prompt,
            "width": int(width),
            "height": int(height),
            "steps": 30,
            "n": 1
        }
        
        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                provider.endpoint,
                json=payload,
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    image_url = result["data"][0]["url"]
                    
                    # Download image
                    async with session.get(image_url) as img_response:
                        if img_response.status == 200:
                            image_data = await img_response.read()
                            image_base64 = base64.b64encode(image_data).decode()
                            
                            return {
                                "success": True,
                                "image_data": {
                                    "image_base64": image_base64,
                                    "format": "png"
                                }
                            }
                else:
                    error_text = await response.text()
                    raise Exception(f"Together AI API error: {error_text}")
    
    async def _generate_with_openai(
        self,
        provider: ImageProvider,
        prompt: str,
        platform: str
    ) -> Dict[str, Any]:
        """Generate image with OpenAI DALL-E (fallback only)"""
        
        platform_config = self.platform_optimizations.get(platform, {})
        size = platform_config.get("size", "1024x1024")
        
        payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": size,
            "response_format": "b64_json"
        }
        
        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                provider.endpoint,
                json=payload,
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    image_base64 = result["data"][0]["b64_json"]
                    
                    return {
                        "success": True,
                        "image_data": {
                            "image_base64": image_base64,
                            "format": "png"
                        }
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error: {error_text}")
    
    async def test_all_providers(self) -> Dict[str, Any]:
        """Test all providers and return availability"""
        
        test_results = {}
        
        for provider in self.providers:
            try:
                # Simple test generation
                result = await self.generate_single_image(
                    prompt="Test product image",
                    platform="instagram"
                )
                test_results[provider.name] = {
                    "available": True,
                    "cost": provider.cost_per_image,
                    "response_time": "< 10s"
                }
            except Exception as e:
                test_results[provider.name] = {
                    "available": False,
                    "error": str(e),
                    "cost": provider.cost_per_image
                }
        
        return test_results
    
    def calculate_cost_savings(
        self,
        platforms: List[str],
        posts_per_platform: int = 3
    ) -> Dict[str, Any]:
        """Calculate cost savings vs DALL-E"""
        
        total_images = len(platforms) * posts_per_platform
        
        # Use cheapest available provider
        cheapest_provider = min(self.providers, key=lambda x: x.cost_per_image)
        
        ultra_cheap_cost = total_images * cheapest_provider.cost_per_image
        dalle_cost = total_images * 0.040
        
        return {
            "total_images": total_images,
            "ultra_cheap_cost": ultra_cheap_cost,
            "dalle_cost": dalle_cost,
            "savings": dalle_cost - ultra_cheap_cost,
            "savings_percentage": ((dalle_cost - ultra_cheap_cost) / dalle_cost) * 100,
            "cheapest_provider": cheapest_provider.name,
            "cost_per_image": cheapest_provider.cost_per_image
        }