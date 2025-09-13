# src/content/services/ai_image_generator.py
"""
AI Image Generation Service for Video Frames
Generates scene-specific images using DALL-E 3, Midjourney, or Stable Diffusion
"""

from typing import Dict, List, Optional, Any, Tuple
import asyncio
import aiohttp
import logging
from dataclasses import dataclass
from datetime import datetime
import base64
import io
from PIL import Image
import os
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

@dataclass
class ImageGenerationRequest:
    scene_id: str
    prompt: str
    style_requirements: Dict[str, Any]
    dimensions: Tuple[int, int]  # (width, height)
    brand_colors: Optional[List[str]] = None
    brand_elements: Optional[Dict[str, Any]] = None
    reference_images: Optional[List[str]] = None

@dataclass
class GeneratedImage:
    scene_id: str
    image_url: str
    local_path: str
    generation_prompt: str
    provider: str
    generation_time: float
    dimensions: Tuple[int, int]
    metadata: Dict[str, Any]

class AIImageGenerator:
    """
    Handles AI image generation for video scenes using multiple providers
    """
    
    def __init__(self):
        self.providers = {
            "dall-e-3": DallE3Provider(),
            "midjourney": MidjourneyProvider(),
            "stable-diffusion": StableDiffusionProvider()
        }
        self.default_provider = "dall-e-3"
        
        # Create local storage directory
        self.storage_dir = os.path.join(os.getcwd(), "generated_assets", "images")
        os.makedirs(self.storage_dir, exist_ok=True)
    
    async def generate_scene_images(
        self,
        requests: List[ImageGenerationRequest],
        video_style: str,
        intelligence_data: Dict[str, Any],
        provider: Optional[str] = None
    ) -> List[GeneratedImage]:
        """
        Generate images for multiple video scenes
        """
        
        provider_name = provider or self.default_provider
        image_provider = self.providers.get(provider_name)
        
        if not image_provider:
            raise ValueError(f"Unsupported image provider: {provider_name}")
        
        logger.info(f"Generating {len(requests)} images using {provider_name}")
        
        # Enhance prompts with intelligence data and style
        enhanced_requests = []
        for request in requests:
            enhanced_prompt = self._enhance_prompt(
                request.prompt,
                video_style,
                intelligence_data,
                request.brand_colors,
                request.brand_elements
            )
            
            enhanced_request = ImageGenerationRequest(
                scene_id=request.scene_id,
                prompt=enhanced_prompt,
                style_requirements=request.style_requirements,
                dimensions=request.dimensions,
                brand_colors=request.brand_colors,
                brand_elements=request.brand_elements,
                reference_images=request.reference_images
            )
            enhanced_requests.append(enhanced_request)
        
        # Generate images concurrently (with rate limiting)
        semaphore = asyncio.Semaphore(3)  # Limit concurrent requests
        tasks = []
        
        for request in enhanced_requests:
            task = self._generate_single_image(
                semaphore, image_provider, request, provider_name
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        generated_images = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Image generation failed: {result}")
            else:
                generated_images.append(result)
        
        logger.info(f"Successfully generated {len(generated_images)}/{len(requests)} images")
        return generated_images
    
    async def _generate_single_image(
        self,
        semaphore: asyncio.Semaphore,
        provider: 'BaseImageProvider',
        request: ImageGenerationRequest,
        provider_name: str
    ) -> GeneratedImage:
        """
        Generate a single image with rate limiting
        """
        async with semaphore:
            start_time = datetime.now()
            
            try:
                # Generate image using provider
                image_data = await provider.generate_image(request)
                
                # Save image locally
                local_path = await self._save_image_locally(
                    image_data, request.scene_id, provider_name
                )
                
                generation_time = (datetime.now() - start_time).total_seconds()
                
                return GeneratedImage(
                    scene_id=request.scene_id,
                    image_url=image_data["url"],
                    local_path=local_path,
                    generation_prompt=request.prompt,
                    provider=provider_name,
                    generation_time=generation_time,
                    dimensions=request.dimensions,
                    metadata=image_data.get("metadata", {})
                )
                
            except Exception as e:
                logger.error(f"Failed to generate image for scene {request.scene_id}: {e}")
                raise
    
    def _enhance_prompt(
        self,
        base_prompt: str,
        video_style: str,
        intelligence_data: Dict[str, Any],
        brand_colors: Optional[List[str]],
        brand_elements: Optional[Dict[str, Any]]
    ) -> str:
        """
        Enhance the base prompt with style, brand, and intelligence context
        """
        
        # Start with base prompt
        enhanced_prompt = base_prompt
        
        # Add style requirements
        style_modifiers = {
            "realistic": "photorealistic, high quality, professional photography",
            "animated": "3D rendered, animated style, colorful, engaging",
            "minimalist": "clean, minimal, simple composition, white background",
            "infographic": "infographic style, data visualization, clean layout",
            "product_focus": "product photography, clean background, commercial style",
            "lifestyle": "lifestyle photography, natural lighting, authentic feel"
        }
        
        if video_style in style_modifiers:
            enhanced_prompt += f", {style_modifiers[video_style]}"
        
        # Add brand colors if available
        if brand_colors:
            color_str = ", ".join(brand_colors)
            enhanced_prompt += f", incorporating brand colors: {color_str}"
        
        # Add brand context from intelligence
        if intelligence_data.get("brand_analysis"):
            brand_info = intelligence_data["brand_analysis"]
            if brand_info.get("tone"):
                enhanced_prompt += f", {brand_info['tone']} brand aesthetic"
            if brand_info.get("industry"):
                enhanced_prompt += f", {brand_info['industry']} industry context"
        
        # Add product context
        if intelligence_data.get("product_analysis"):
            product_info = intelligence_data["product_analysis"]
            if product_info.get("category"):
                enhanced_prompt += f", {product_info['category']} product"
        
        # Add quality and technical specifications
        enhanced_prompt += ", high resolution, 4K quality, professional composition"
        
        # Limit prompt length (most providers have limits)
        if len(enhanced_prompt) > 1000:
            enhanced_prompt = enhanced_prompt[:997] + "..."
        
        return enhanced_prompt
    
    async def _save_image_locally(
        self,
        image_data: Dict[str, Any],
        scene_id: str,
        provider: str
    ) -> str:
        """
        Save generated image to local storage
        """
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{scene_id}_{provider}_{timestamp}.png"
        file_path = os.path.join(self.storage_dir, filename)
        
        try:
            if "url" in image_data:
                # Download from URL
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_data["url"]) as response:
                        if response.status == 200:
                            image_bytes = await response.read()
                            with open(file_path, 'wb') as f:
                                f.write(image_bytes)
            
            elif "base64" in image_data:
                # Decode base64
                image_bytes = base64.b64decode(image_data["base64"])
                with open(file_path, 'wb') as f:
                    f.write(image_bytes)
            
            else:
                raise ValueError("No valid image data found")
            
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to save image locally: {e}")
            raise

class BaseImageProvider:
    """Base class for image generation providers"""
    
    async def generate_image(self, request: ImageGenerationRequest) -> Dict[str, Any]:
        raise NotImplementedError

class DallE3Provider(BaseImageProvider):
    """OpenAI DALL-E 3 image generation"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_url = "https://api.openai.com/v1/images/generations"
    
    async def generate_image(self, request: ImageGenerationRequest) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        
        # Map dimensions to DALL-E 3 supported sizes
        width, height = request.dimensions
        if width == height:
            size = "1024x1024"
        elif width > height:
            size = "1792x1024"
        else:
            size = "1024x1792"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "dall-e-3",
            "prompt": request.prompt,
            "n": 1,
            "size": size,
            "quality": "hd",
            "style": "natural"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "url": data["data"][0]["url"],
                        "revised_prompt": data["data"][0].get("revised_prompt"),
                        "metadata": {
                            "model": "dall-e-3",
                            "size": size,
                            "quality": "hd"
                        }
                    }
                else:
                    error_data = await response.json()
                    raise Exception(f"DALL-E 3 API error: {error_data}")

class MidjourneyProvider(BaseImageProvider):
    """Midjourney image generation (via API wrapper)"""
    
    def __init__(self):
        self.api_key = os.getenv("MIDJOURNEY_API_KEY")
        self.api_url = os.getenv("MIDJOURNEY_API_URL", "https://api.midjourney.com/v1/imagine")
    
    async def generate_image(self, request: ImageGenerationRequest) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("Midjourney API key not configured")
        
        # Add Midjourney-specific parameters
        width, height = request.dimensions
        aspect_ratio = f"{width}:{height}"
        
        # Enhance prompt with Midjourney parameters
        mj_prompt = f"{request.prompt} --ar {aspect_ratio} --v 6 --style raw"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": mj_prompt,
            "webhook_url": None  # Could add webhook for async processing
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    # Note: Midjourney API typically returns job ID for async processing
                    # This is simplified - real implementation would poll for completion
                    return {
                        "url": data.get("image_url"),
                        "job_id": data.get("job_id"),
                        "metadata": {
                            "provider": "midjourney",
                            "version": "v6",
                            "aspect_ratio": aspect_ratio
                        }
                    }
                else:
                    error_data = await response.json()
                    raise Exception(f"Midjourney API error: {error_data}")

class StableDiffusionProvider(BaseImageProvider):
    """Stable Diffusion image generation"""
    
    def __init__(self):
        self.api_key = os.getenv("STABILITY_API_KEY")
        self.api_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    
    async def generate_image(self, request: ImageGenerationRequest) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("Stability AI API key not configured")
        
        width, height = request.dimensions
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "text_prompts": [
                {
                    "text": request.prompt,
                    "weight": 1.0
                }
            ],
            "cfg_scale": 7,
            "height": height,
            "width": width,
            "samples": 1,
            "steps": 30,
            "style_preset": "photographic"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    # Stable Diffusion returns base64 encoded image
                    return {
                        "base64": data["artifacts"][0]["base64"],
                        "seed": data["artifacts"][0]["seed"],
                        "metadata": {
                            "provider": "stable-diffusion",
                            "model": "stable-diffusion-xl-1024-v1-0",
                            "cfg_scale": 7,
                            "steps": 30
                        }
                    }
                else:
                    error_data = await response.json()
                    raise Exception(f"Stability AI API error: {error_data}")

# Factory function for easy instantiation
def create_ai_image_generator() -> AIImageGenerator:
    """Create and return an AI image generator instance"""
    return AIImageGenerator()