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
from datetime import datetime, timezone

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
                "success": False,
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
            "tiktok": {"width": 1080, "height": 1920, "aspect": "vertical"},
            "general": {"width": 1024, "height": 1024, "aspect": "square"}
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
                "success": False,
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
                            "generation_time": datetime.now(timezone.utc),
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
            "professional": ["corporate style", "professional lighting", "business appropriate"],
            "marketing": ["marketing ready", "brand focused", "commercial appeal"]
        }
        
        # Platform-specific enhancements
        platform_enhancements = {
            "instagram": ["instagram-worthy", "social media optimized", "eye-catching"],
            "linkedin": ["professional", "business-focused", "corporate appropriate"],
            "pinterest": ["pinterest-style", "inspirational", "save-worthy"],
            "tiktok": ["trendy", "engaging", "dynamic composition"],
            "general": ["versatile", "multi-purpose", "adaptable"]
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
        platform: str = "instagram",
        style: str = "marketing"
    ) -> Dict[str, Any]:
        """Generate multiple images efficiently"""
        
        results = []
        total_cost = 0
        
        for i, prompt in enumerate(prompts):
            try:
                result = await self.generate_social_media_image(prompt, platform, style)
                results.append(result)
                
                if result.get("success"):
                    total_cost += result.get("estimated_cost", 0)
                
                # Small delay to avoid rate limits
                await asyncio.sleep(0.5)
                
                logger.info(f"Generated image {i+1}/{len(prompts)} for {platform}")
                
            except Exception as e:
                logger.error(f"Batch generation failed for prompt {i+1}: {str(e)}")
                results.append({
                    "success": False,
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
    
    async def generate_campaign_image_set(
        self,
        product_name: str,
        campaign_theme: str = "health_wellness",
        image_count: int = 4
    ) -> Dict[str, Any]:
        """Generate a complete set of marketing images for a campaign"""
        
        # Define campaign-specific prompts
        theme_prompts = {
            "health_wellness": [
                f"Professional product photography of {product_name}, health supplement bottle, clean white background, studio lighting",
                f"Lifestyle image showing person taking {product_name}, natural wellness, healthy living, authentic feel",
                f"{product_name} benefits visualization, before and after transformation, health improvement",
                f"Call-to-action image for {product_name}, marketing visual, professional design, compelling offer"
            ],
            "fitness": [
                f"Athletic lifestyle image featuring {product_name}, fitness supplement, gym setting, energetic feel",
                f"Professional {product_name} product shot, sports nutrition, clean design, performance focused",
                f"Transformation results with {product_name}, fitness journey, motivational image",
                f"Call-to-action for {product_name}, fitness marketing, strong visual impact"
            ],
            "beauty": [
                f"Elegant beauty shot of {product_name}, skincare product, luxury feel, soft lighting",
                f"Before and after results with {product_name}, beauty transformation, glowing skin",
                f"Lifestyle beauty image featuring {product_name}, natural beauty, confident person",
                f"Premium {product_name} marketing image, beauty brand, call-to-action design"
            ],
            "general": [
                f"Professional marketing image for {product_name}, clean modern design, brand focused",
                f"Lifestyle image showing {product_name} in daily life, authentic usage, natural setting",
                f"{product_name} benefits showcase, visual representation of value, compelling design",
                f"Call-to-action marketing visual for {product_name}, conversion focused, professional"
            ]
        }
        
        # Get prompts for the specified theme
        prompts = theme_prompts.get(campaign_theme, theme_prompts["general"])[:image_count]
        
        # Generate images
        batch_result = await self.generate_batch_images(
            prompts=prompts,
            platform="general",
            style="marketing"
        )
        
        # Add campaign metadata
        batch_result.update({
            "product_name": product_name,
            "campaign_theme": campaign_theme,
            "image_set_complete": batch_result["successful_generations"] >= (image_count * 0.75),  # 75% success rate
            "recommended_usage": {
                "social_media": "Use for Instagram, Facebook, LinkedIn posts",
                "email_marketing": "Perfect for email campaigns and newsletters",
                "web_content": "Great for landing pages and product pages",
                "advertising": "Ready for Facebook Ads, Google Ads"
            }
        })
        
        return batch_result
    
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
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models"""
        
        return {
            "available_models": self.models,
            "default_model": self.default_model,
            "api_status": "Connected" if self.api_key else "API Key Required",
            "cost_comparison": {
                "stability_ai_range": "$0.002 - $0.004 per image",
                "dalle_3_cost": "$0.040 per image",
                "savings_range": "90% - 95% cost reduction"
            },
            "supported_platforms": [
                "instagram", "instagram_story", "facebook", "twitter", 
                "linkedin", "pinterest", "tiktok", "general"
            ],
            "supported_styles": [
                "product", "lifestyle", "health", "professional", "marketing"
            ]
        }


# Integration with your existing social media generator  
class SocialWithStability:
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
        
        # Import your existing social media generator components
        try:
            from .social_media_generator import SocialMediaGenerator
        except ImportError:
            logger.error("SocialMediaGenerator not found")
            return {"error": "Social media generator not available"}
        
        social_generator = SocialMediaGenerator()
        
        # 1. Extract product name from intelligence
        try:
            from ..utils.product_name_fix import extract_product_name_from_intelligence
            product_name = extract_product_name_from_intelligence(intelligence_data)
        except ImportError:
            product_name = "Health Product"
        
        # 2. Generate visual concept
        concept_result = await social_generator._generate_visual_concept_with_routing(
            platform, intelligence_data, "benefits", 0
        )
        
        concept = concept_result.get("content", {}) if concept_result.get("success") else {}
        
        # 3. Generate caption
        caption_result = await social_generator._generate_caption_with_routing(
            platform, intelligence_data, concept, 200
        )
        
        caption = caption_result.get("content", f"Discover the benefits of {product_name}!") if caption_result.get("success") else f"Transform your health with {product_name}!"
        
        # 4. Generate hashtags
        hashtags_result = await social_generator._generate_hashtags_with_routing(
            platform, intelligence_data, "benefits", 10
        )
        
        hashtags = hashtags_result.get("content", ["#health", "#wellness"]) if hashtags_result.get("success") else ["#health", "#wellness", f"#{product_name.lower().replace(' ', '')}"]
        
        # 5. Generate image prompt
        image_prompt = f"Professional marketing image for {product_name}, health supplement, {platform} optimized, clean modern design"
        
        # 6. Generate actual image with Stability AI
        image_result = await self.stability_generator.generate_social_media_image(
            prompt=image_prompt,
            platform=platform,
            style="health"
        )
        
        # Calculate total cost
        total_cost = 0
        if concept_result.get("success"):
            total_cost += concept_result.get("cost", 0)
        if caption_result.get("success"):
            total_cost += caption_result.get("cost", 0)
        if hashtags_result.get("success"):
            total_cost += hashtags_result.get("cost", 0)
        if image_result.get("success"):
            total_cost += image_result.get("estimated_cost", 0)
        
        return {
            "platform": platform,
            "content_type": "complete_social_post",
            "product_name": product_name,
            "caption": caption,
            "hashtags": hashtags,
            "image_concept": concept,
            "image_result": image_result,
            "ready_to_publish": True,
            "total_cost": total_cost,
            "cost_breakdown": {
                "concept_generation": concept_result.get("cost", 0) if concept_result.get("success") else 0,
                "caption_generation": caption_result.get("cost", 0) if caption_result.get("success") else 0,
                "hashtag_generation": hashtags_result.get("cost", 0) if hashtags_result.get("success") else 0,
                "image_generation": image_result.get("estimated_cost", 0) if image_result.get("success") else 0
            },
            "post_performance_prediction": "High engagement expected",
            "savings_vs_traditional": f"${0.10 - total_cost:.3f} saved vs traditional tools"
        }
    
    async def generate_multi_platform_campaign(
        self,
        intelligence_data: Dict[str, Any],
        platforms: List[str] = None
    ) -> Dict[str, Any]:
        """Generate complete multi-platform social media campaign"""
        
        if platforms is None:
            platforms = ["instagram", "facebook", "linkedin", "twitter"]
        
        campaign_results = []
        total_campaign_cost = 0
        
        for platform in platforms:
            try:
                post_result = await self.generate_complete_social_post(
                    intelligence_data=intelligence_data,
                    platform=platform
                )
                
                campaign_results.append(post_result)
                total_campaign_cost += post_result.get("total_cost", 0)
                
                # Small delay between platforms
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Failed to generate content for {platform}: {str(e)}")
                campaign_results.append({
                    "platform": platform,
                    "error": str(e),
                    "success": False
                })
        
        successful_platforms = len([r for r in campaign_results if r.get("ready_to_publish")])
        
        return {
            "campaign_type": "multi_platform_social_media",
            "platforms_requested": len(platforms),
            "platforms_successful": successful_platforms,
            "success_rate": (successful_platforms / len(platforms)) * 100,
            "total_campaign_cost": total_campaign_cost,
            "cost_per_platform": total_campaign_cost / len(platforms) if platforms else 0,
            "platform_results": campaign_results,
            "ready_to_publish": successful_platforms >= (len(platforms) * 0.75),  # 75% success rate
            "campaign_savings": f"${len(platforms) * 0.10 - total_campaign_cost:.2f} saved vs traditional tools"
        }


# Enhanced Content Generator that combines everything
class EnhancedContentGenerator:
    """Complete content generator with Stability AI and Slideshow Video integration"""
    
    def __init__(self):
        self.stability_generator = StabilityAIGenerator()
        self.social_generator = SocialWithStability()
        
        # Import slideshow generator - DISABLED FOR RAILWAY DEPLOYMENT
        try:
            # from .slideshow_video_generator import SlideshowVideoGenerator
            # self.slideshow_generator = SlideshowVideoGenerator()
            logger.warning("SlideshowVideoGenerator disabled - legacy dependency")
            self.slideshow_generator = None
        except ImportError:
            logger.warning("SlideshowVideoGenerator not available")
            self.slideshow_generator = None
        
        # Import storage manager
        try:
            # from src.storage.universal_dual_storage import... # TODO: Fix this import
            self.storage_manager = get_storage_manager()
        except ImportError:
            logger.warning("Storage manager not available")
            self.storage_manager = None
    
    async def generate_complete_campaign_with_video(
        self,
        intelligence_data: Dict[str, Any],
        campaign_id: str,
        current_user: Any,
        content_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate complete campaign including slideshow video"""
        
        if content_preferences is None:
            content_preferences = {}
        
        results = {
            "campaign_id": campaign_id,
            "content_generated": [],
            "images_generated": [],
            "videos_generated": [],
            "social_posts": [],
            "total_cost": 0.0
        }
        
        try:
            # Extract product name
            try:
                from ..utils.product_name_fix import extract_product_name_from_intelligence
                product_name = extract_product_name_from_intelligence(intelligence_data)
            except ImportError:
                product_name = "Health Product"
            
            # 1. Generate marketing images first
            image_set_result = await self.stability_generator.generate_campaign_image_set(
                product_name=product_name,
                campaign_theme=content_preferences.get("theme", "health_wellness"),
                image_count=content_preferences.get("image_count", 4)
            )
            
            results["images_generated"] = image_set_result
            results["total_cost"] += image_set_result.get("total_cost", 0)
            
            # Save images to storage if storage manager is available
            image_assets = []
            if self.storage_manager and image_set_result.get("successful_generations", 0) > 0:
                for i, image_result in enumerate(image_set_result.get("results", [])):
                    if image_result.get("success") and "image_data" in image_result:
                        try:
                            image_filename = f"campaign_{campaign_id}_image_{i+1}.png"
                            storage_result = await self.storage_manager.save_content_dual_storage(
                                content_data=image_result["image_data"]["image_base64"],
                                content_type="image",
                                filename=image_filename,
                                user_id=str(current_user.id),
                                campaign_id=campaign_id,
                                metadata={
                                    "content_type": "campaign_image", 
                                    "sequence": i+1,
                                    "prompt": image_result.get("original_prompt"),
                                    "platform": image_result.get("platform")
                                }
                            )
                            
                            if storage_result.get("success"):
                                image_assets.append({
                                    "id": storage_result.get("asset_id"),
                                    "url": storage_result["public_url"],
                                    "sequence": i+1,
                                    "prompt": image_result.get("original_prompt")
                                })
                        except Exception as e:
                            logger.error(f"Failed to save image {i+1}: {str(e)}")
            
            # 2. Generate slideshow video using the images
            if self.slideshow_generator and image_assets:
                video_result = await self.slideshow_generator.generate_slideshow_video_with_image_generation(
                    intelligence_data=intelligence_data,
                    campaign_id=campaign_id,
                    current_user=current_user,
                    image_assets=image_assets,
                    video_preferences=content_preferences.get("video_preferences")
                )
                
                if video_result.get("success"):
                    results["videos_generated"].append(video_result)
                    results["total_cost"] += video_result.get("cost", 0)
            
            # 3. Generate multi-platform social media content
            social_platforms = content_preferences.get("social_platforms", ["instagram", "facebook", "linkedin"])
            
            social_campaign = await self.social_generator.generate_multi_platform_campaign(
                intelligence_data=intelligence_data,
                platforms=social_platforms
            )
            
            results["social_posts"] = social_campaign
            results["total_cost"] += social_campaign.get("total_campaign_cost", 0)
            
            # 4. Generate other content types as needed
            # Add email sequences, blog posts, ad copy, etc. here
            
            return {
                "success": True,
                "campaign_results": results,
                "product_name": product_name,
                "slideshow_video": results["videos_generated"][0] if results["videos_generated"] else None,
                "image_assets": image_assets,
                "social_campaign": social_campaign,
                "total_generation_cost": results["total_cost"],
                "cost_savings": f"${len(social_platforms) * 0.15 - results['total_cost']:.2f} saved vs traditional tools",
                "content_ready": {
                    "images": len(image_assets),
                    "videos": len(results["videos_generated"]),
                    "social_posts": social_campaign.get("platforms_successful", 0),
                    "total_pieces": len(image_assets) + len(results["videos_generated"]) + social_campaign.get("platforms_successful", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Complete campaign generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "partial_results": results,
                "recovery_suggestions": [
                    "Try with simpler preferences",
                    "Check API keys and credentials",
                    "Ensure storage system is available",
                    "Verify intelligence data format"
                ]
            }