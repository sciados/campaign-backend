# src/intelligence/generators/stability_ai_generator.py
"""
STABILITY AI IMAGE GENERATOR
✅ Ultra-cheap image generation ($0.002-0.01 per image)
✅ High quality marketing images
✅ Multiple model options
✅ Social media optimized
"""

import os
import requests
import asyncio
import aiohttp
import base64
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class StabilityAIGenerator:
    """Generate images using Stability AI for ultra-cheap costs"""
    
    def __init__(self):
        self.api_key = os.getenv("STABILITY_API_KEY")
        self.base_url = "https://api.stability.ai/v1/generation"
        
        # Available models (from cheapest to most expensive)
        self.models = {
            "stable-diffusion-xl-1024-v0-9": {
                "cost_per_image": 0.002,
                "quality": "good",
                "speed": "fast",
                "best_for": "high_volume"
            },
            "stable-diffusion-xl-1024-v1-0": {
                "cost_per_image": 0.004,
                "quality": "great", 
                "speed": "medium",
                "best_for": "balanced"
            },
            "stable-diffusion-512-v2-1": {
                "cost_per_image": 0.002,
                "quality": "good",
                "speed": "very_fast",
                "best_for": "testing"
            }
        }
        
        # Default to cheapest high-quality model
        self.default_model = "stable-diffusion-xl-1024-v1-0"
        
        if not self.api_key:
            logger.warning("⚠️ STABILITY_API_KEY not found. Get it from: https://platform.stability.ai/")
    
    async def generate_social_media_image(
        self, 
        prompt: str, 
        platform: str = "instagram",
        style: str = "marketing"
    ) -> Dict[str, Any]:
        """Generate image optimized for specific social media platform"""
        
        if not self.api_key:
            return {
                "error": "Stability AI API key required",
                "setup_instructions": "Get API key from https://platform.stability.ai/",
                "cost_benefit": "Images cost only $0.002-0.01 each vs $0.040 for DALL-E"
            }
        
        # Platform-specific optimization
        platform_specs = {
            "instagram": {"width": 1024, "height": 1024, "aspect": "square"},
            "instagram_story": {"width": 1024, "height": 1820, "aspect": "vertical"},
            "facebook": {"width": 1200, "height": 630, "aspect": "landscape"},
            "twitter": {"width": 1024, "height": 512, "aspect": "landscape"},
            "linkedin": {"width": 1200, "height": 627, "aspect": "landscape"},
            "pinterest": {"width": 1000, "height": 1500, "aspect": "tall"},
            "tiktok": {"width": 1080, "height": 1920, "aspect": "vertical"}
        }
        
        spec = platform_specs.get(platform, platform_specs["instagram"])
        
        # Enhance prompt for marketing
        enhanced_prompt = self._enhance_marketing_prompt(prompt, style, platform)
        
        try:
            # Generate image
            image_data = await self._generate_image(
                prompt=enhanced_prompt,
                width=spec["width"],
                height=spec["height"]
            )
            
            return {
                "success": True,
                "image_data": image_data,
                "platform": platform,
                "dimensions": f"{spec['width']}x{spec['height']}",
                "aspect_ratio": spec["aspect"],
                "original_prompt": prompt,
                "enhanced_prompt": enhanced_prompt,
                "model_used": self.default_model,
                "estimated_cost": self.models[self.default_model]["cost_per_image"],
                "savings_vs_dalle": f"${0.040 - self.models[self.default_model]['cost_per_image']:.3f} saved"
            }
            
        except Exception as e:
            logger.error(f"Stability AI generation failed: {str(e)}")
            return {
                "error": str(e),
                "fallback_suggestion": "Try simpler prompt or check API key"
            }
    
    async def _generate_image(
        self, 
        prompt: str, 
        width: int = 1024, 
        height: int = 1024,
        model: str = None
    ) -> Dict[str, Any]:
        """Generate image using Stability AI"""
        
        if model is None:
            model = self.default_model
        
        url = f"{self.base_url}/{model}/text-to-image"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "text_prompts": [
                {
                    "text": prompt,
                    "weight": 1
                }
            ],
            "cfg_scale": 7,
            "height": height,
            "width": width,
            "samples": 1,
            "steps": 20,
            "style_preset": "photographic"  # Good for marketing images
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Process the response
                    if "artifacts" in result and len(result["artifacts"]) > 0:
                        artifact = result["artifacts"][0]
                        
                        return {
                            "image_base64": artifact["base64"],
                            "seed": artifact.get("seed"),
                            "finish_reason": artifact.get("finishReason"),
                            "generation_time": datetime.utcnow().isoformat(),
                            "save_instructions": "Decode base64 and save as PNG/JPG"
                        }
                    else:
                        raise Exception("No image generated in response")
                else:
                    error_text = await response.text()
                    raise Exception(f"API Error {response.status}: {error_text}")
    
    def _enhance_marketing_prompt(self, prompt: str, style: str, platform: str) -> str:
        """Enhance prompt for better marketing images"""
        
        # Base enhancements for marketing
        enhancements = [
            "professional marketing photography",
            "high quality",
            "clean composition",
            "vibrant colors",
            "commercial photography style"
        ]
        
        # Style-specific enhancements
        style_enhancements = {
            "product": ["product photography", "studio lighting", "white background"],
            "lifestyle": ["lifestyle photography", "natural lighting", "authentic feel"],
            "health": ["health and wellness", "natural colors", "clean aesthetic"],
            "professional": ["corporate style", "professional lighting", "business appropriate"]
        }
        
        # Platform-specific enhancements
        platform_enhancements = {
            "instagram": ["instagram-worthy", "social media optimized", "eye-catching"],
            "linkedin": ["professional", "business-focused", "corporate appropriate"],
            "pinterest": ["pinterest-style", "inspirational", "save-worthy"],
            "tiktok": ["trendy", "engaging", "dynamic composition"]
        }
        
        # Combine all enhancements
        all_enhancements = (
            enhancements + 
            style_enhancements.get(style, []) + 
            platform_enhancements.get(platform, [])
        )
        
        # Create enhanced prompt
        enhanced_prompt = f"{prompt}, {', '.join(all_enhancements)}"
        
        return enhanced_prompt
    
    async def generate_batch_images(
        self, 
        prompts: List[str], 
        platform: str = "instagram"
    ) -> Dict[str, Any]:
        """Generate multiple images efficiently"""
        
        results = []
        total_cost = 0
        
        for i, prompt in enumerate(prompts):
            try:
                result = await self.generate_social_media_image(prompt, platform)
                results.append(result)
                
                if result.get("success"):
                    total_cost += result.get("estimated_cost", 0)
                
                # Small delay to avoid rate limits
                await asyncio.sleep(0.5)
                
                logger.info(f"Generated image {i+1}/{len(prompts)} for {platform}")
                
            except Exception as e:
                logger.error(f"Batch generation failed for prompt {i+1}: {str(e)}")
                results.append({
                    "error": str(e),
                    "prompt": prompt
                })
        
        return {
            "total_images": len(prompts),
            "successful_generations": len([r for r in results if r.get("success")]),
            "failed_generations": len([r for r in results if r.get("error")]),
            "total_cost": total_cost,
            "cost_per_image": total_cost / len(prompts) if prompts else 0,
            "results": results,
            "savings_vs_dalle": (len(prompts) * 0.040) - total_cost
        }
    
    def save_image_from_base64(self, base64_data: str, filename: str) -> str:
        """Save base64 image data to file"""
        
        try:
            # Decode base64
            image_data = base64.b64decode(base64_data)
            
            # Save to file
            with open(filename, 'wb') as f:
                f.write(image_data)
            
            logger.info(f"Image saved to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to save image: {str(e)}")
            raise
    
    async def test_generation(self) -> Dict[str, Any]:
        """Test the Stability AI setup"""
        
        test_prompt = "Professional product photography of a health supplement bottle, clean white background, studio lighting, marketing photo"
        
        result = await self.generate_social_media_image(
            prompt=test_prompt,
            platform="instagram",
            style="product"
        )
        
        if result.get("success"):
            return {
                "test_status": "✅ SUCCESS",
                "api_working": True,
                "cost_per_image": result["estimated_cost"],
                "model_used": result["model_used"],
                "message": "Stability AI is ready to use!",
                "savings_info": f"You'll save {result['savings_vs_dalle']} per image vs DALL-E"
            }
        else:
            return {
                "test_status": "❌ FAILED", 
                "api_working": False,
                "error": result.get("error"),
                "setup_help": "Check API key and account balance"
            }


# Integration with your existing social media generator
class EnhancedSocialWithStability:
    """Enhanced social media generator with Stability AI integration"""
    
    def __init__(self):
        self.stability_generator = StabilityAIGenerator()
        # Your existing initialization code...
    
    async def generate_complete_social_post(
        self, 
        intelligence_data: Dict[str, Any],
        platform: str = "instagram"
    ) -> Dict[str, Any]:
        """Generate complete social media post with AI image"""
        
        # 1. Generate content concept (your existing code)
        concept = await self._generate_visual_concept(platform, intelligence_data, "benefits", 0)
        
        # 2. Generate caption (your existing code) 
        caption = await self._generate_caption(platform, intelligence_data, concept, 200)
        
        # 3. Generate hashtags (your existing code)
        hashtags = await self._generate_hashtags(platform, intelligence_data, "benefits", 10)
        
        # 4. Generate actual image with Stability AI
        image_prompt = await self._generate_image_prompt(concept, intelligence_data)
        
        image_result = await self.stability_generator.generate_social_media_image(
            prompt=image_prompt,
            platform=platform,
            style="health"
        )
        
        return {
            "platform": platform,
            "content_type": "complete_social_post",
            "caption": caption,
            "hashtags": hashtags,
            "image_concept": concept,
            "image_result": image_result,
            "ready_to_publish": True,
            "total_cost": image_result.get("estimated_cost", 0),
            "post_performance_prediction": "High engagement expected"
        }