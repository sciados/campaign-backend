# src/intelligence/adapters/dynamic_router.py
"""
DYNAMIC AI ROUTER - INTELLIGENT PROVIDER SELECTION
🎯 Automatically routes to optimal AI provider based on real-time data
💰 Maximizes cost savings while maintaining quality
🔄 Adapts to provider availability and performance changes
⚡ Falls back gracefully when providers are unavailable
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import os

from ..monitoring.ai_monitor import get_ai_monitor
from ..generators.base_generator import BaseContentGenerator

logger = logging.getLogger(__name__)

@dataclass
class ProviderSelection:
    """Selected provider configuration"""
    provider_name: str
    model_name: str
    api_key: str
    config: Dict[str, Any]
    backup_providers: List[str]
    selection_reason: str

class DynamicAIRouter:
    """Intelligent router that selects optimal AI providers automatically"""
    
    def __init__(self):
        self.monitor = None
        self.cache_ttl = 300  # 5 minutes cache
        self.provider_cache = {}
        self.last_cache_update = {}
        
        # Provider configuration templates
        self.provider_configs = {
            "groq": {
                "client_class": "groq.AsyncGroq",
                "client_init": lambda api_key: {"api_key": api_key},
                "models": {
                    "text": "llama-3.3-70b-versatile",
                    "reasoning": "llama-3.3-70b-versatile"
                }
            },
            "deepseek": {
                "client_class": "openai.AsyncOpenAI",
                "client_init": lambda api_key: {
                    "api_key": api_key,
                    "base_url": "https://api.deepseek.com"
                },
                "models": {
                    "text": "deepseek-chat",
                    "reasoning": "deepseek-reasoner"
                }
            },
            "together": {
                "client_class": "openai.AsyncOpenAI",
                "client_init": lambda api_key: {
                    "api_key": api_key,
                    "base_url": "https://api.together.xyz/v1"
                },
                "models": {
                    "text": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
                }
            },
            "anthropic": {
                "client_class": "anthropic.AsyncAnthropic",
                "client_init": lambda api_key: {"api_key": api_key},
                "models": {
                    "text": "claude-sonnet-4-20250514",
                    "reasoning": "claude-sonnet-4-20250514"
                }
            },
            "stability": {
                "client_class": "stability_sdk.client.StabilityInference",
                "client_init": lambda api_key: {
                    "key": api_key,
                    "host": "grpc.stability.ai:443"
                },
                "models": {
                    "image": "stable-diffusion-xl-1024-v1-0"
                }
            },
            "replicate": {
                "client_class": "replicate.Client",
                "client_init": lambda api_key: {"api_token": api_key},
                "models": {
                    "image": "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
                }
            },
            "fal": {
                "client_class": "fal.client.AsyncClient",
                "client_init": lambda api_key: {"api_key": api_key},
                "models": {
                    "image": "fal-ai/flux-pro"
                }
            }
        }
        
        logger.info("🤖 Dynamic AI Router initialized")
    
    async def get_optimal_provider(self, content_type: str, task_complexity: str = "standard") -> ProviderSelection:
        """Get optimal provider for content type with intelligent selection"""
        
        # Check cache first
        cache_key = f"{content_type}_{task_complexity}"
        if self._is_cache_valid(cache_key):
            logger.debug(f"📋 Using cached provider for {content_type}")
            return self.provider_cache[cache_key]
        
        # Get AI monitor
        if not self.monitor:
            self.monitor = await get_ai_monitor()
        
        # Get optimal provider from monitoring system
        try:
            optimal_config = await self.monitor.get_optimal_provider(content_type)
            
            if optimal_config:
                provider_selection = await self._create_provider_selection(
                    optimal_config, content_type, task_complexity
                )
                
                # Cache the selection
                self.provider_cache[cache_key] = provider_selection
                self.last_cache_update[cache_key] = datetime.utcnow()
                
                logger.info(f"🎯 Selected {provider_selection.provider_name} for {content_type} ({provider_selection.selection_reason})")
                return provider_selection
            
        except Exception as e:
            logger.warning(f"⚠️ Monitor selection failed for {content_type}: {str(e)}")
        
        # Fallback to manual selection
        return await self._fallback_provider_selection(content_type, task_complexity)
    
    async def execute_with_optimal_provider(
        self, 
        content_type: str, 
        generation_function: callable,
        task_complexity: str = "standard",
        **kwargs
    ) -> Tuple[Any, Dict[str, Any]]:
        """Execute generation with optimal provider and automatic fallback"""
        
        provider_selection = await self.get_optimal_provider(content_type, task_complexity)
        
        # Track attempts for fallback
        attempted_providers = []
        last_error = None
        
        # Try primary provider
        try:
            result = await self._execute_with_provider(
                provider_selection, generation_function, **kwargs
            )
            
            # Log successful usage
            await self._log_successful_usage(provider_selection, content_type)
            
            return result, {
                "provider_used": provider_selection.provider_name,
                "selection_reason": provider_selection.selection_reason,
                "attempt_number": 1,
                "fallback_used": False
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Primary provider {provider_selection.provider_name} failed: {str(e)}")
            attempted_providers.append(provider_selection.provider_name)
            last_error = str(e)
        
        # Try backup providers
        for i, backup_provider in enumerate(provider_selection.backup_providers):
            try:
                backup_selection = await self._get_backup_provider_config(
                    backup_provider, content_type, task_complexity
                )
                
                if backup_selection:
                    result = await self._execute_with_provider(
                        backup_selection, generation_function, **kwargs
                    )
                    
                    # Log fallback usage
                    await self._log_fallback_usage(backup_selection, content_type, attempted_providers)
                    
                    return result, {
                        "provider_used": backup_selection.provider_name,
                        "selection_reason": f"Fallback from {provider_selection.provider_name}",
                        "attempt_number": i + 2,
                        "fallback_used": True,
                        "primary_failure": last_error
                    }
                    
            except Exception as e:
                logger.warning(f"⚠️ Backup provider {backup_provider} failed: {str(e)}")
                attempted_providers.append(backup_provider)
                last_error = str(e)
        
        # All providers failed
        raise Exception(f"All providers failed for {content_type}. Attempted: {attempted_providers}. Last error: {last_error}")
    
    async def _create_provider_selection(
        self, 
        optimal_config: Dict[str, Any], 
        content_type: str, 
        task_complexity: str
    ) -> ProviderSelection:
        """Create provider selection from optimal configuration"""
        
        provider_name = optimal_config["provider_name"]
        model_name = optimal_config["model_name"]
        
        # Get API key from environment
        api_key_env = optimal_config.get("api_key_env", f"{provider_name.upper()}_API_KEY")
        api_key = os.getenv(api_key_env)
        
        if not api_key:
            raise ValueError(f"API key {api_key_env} not found in environment")
        
        # Get provider configuration
        provider_config = self.provider_configs.get(provider_name)
        if not provider_config:
            raise ValueError(f"Provider {provider_name} not configured")
        
        # Select model based on task complexity
        model_map = provider_config["models"]
        if task_complexity == "reasoning" and "reasoning" in model_map:
            selected_model = model_map["reasoning"]
        elif content_type in model_map:
            selected_model = model_map[content_type]
        else:
            selected_model = model_name  # Use from monitor
        
        return ProviderSelection(
            provider_name=provider_name,
            model_name=selected_model,
            api_key=api_key,
            config=provider_config,
            backup_providers=optimal_config.get("backup_providers", []),
            selection_reason=optimal_config.get("decision_factors", {}).get("reasoning", "Monitor optimization")
        )
    
    async def _execute_with_provider(
        self, 
        provider_selection: ProviderSelection, 
        generation_function: callable,
        **kwargs
    ) -> Any:
        """Execute generation function with selected provider"""
        
        # Import provider client dynamically
        client_class_path = provider_selection.config["client_class"]
        module_name, class_name = client_class_path.rsplit(".", 1)
        
        try:
            module = __import__(module_name, fromlist=[class_name])
            client_class = getattr(module, class_name)
        except ImportError:
            raise Exception(f"Provider client {client_class_path} not available")
        
        # Initialize client
        client_init_params = provider_selection.config["client_init"](provider_selection.api_key)
        client = client_class(**client_init_params)
        
        # Execute generation with provider-specific configuration
        provider_context = {
            "client": client,
            "model": provider_selection.model_name,
            "provider_name": provider_selection.provider_name
        }
        
        return await generation_function(provider_context, **kwargs)
    
    async def _fallback_provider_selection(self, content_type: str, task_complexity: str) -> ProviderSelection:
        """Fallback provider selection when monitoring system is unavailable"""
        
        # Predefined fallback hierarchy based on your Railway environment
        fallback_hierarchy = {
            "text": ["groq", "deepseek", "together", "anthropic"],
            "image": ["stability", "replicate", "fal"],
            "video": ["replicate", "stability"]  # For video generation
        }
        
        content_category = "text" if content_type in ["email_sequence", "ad_copy", "social_media", "blog_post", "landing_page"] else content_type
        providers = fallback_hierarchy.get(content_category, fallback_hierarchy["text"])
        
        # Find first available provider
        for provider_name in providers:
            api_key_env = f"{provider_name.upper()}_API_KEY"
            if provider_name == "replicate":
                api_key_env = "REPLICATE_API_TOKEN"
            
            api_key = os.getenv(api_key_env)
            if api_key and provider_name in self.provider_configs:
                provider_config = self.provider_configs[provider_name]
                
                # Select appropriate model
                model_map = provider_config["models"]
                if task_complexity == "reasoning" and "reasoning" in model_map:
                    model = model_map["reasoning"]
                elif content_category in model_map:
                    model = model_map[content_category]
                else:
                    model = list(model_map.values())[0]  # First available model
                
                return ProviderSelection(
                    provider_name=provider_name,
                    model_name=model,
                    api_key=api_key,
                    config=provider_config,
                    backup_providers=providers[providers.index(provider_name)+1:],
                    selection_reason="Fallback selection - monitoring unavailable"
                )
        
        raise Exception(f"No available providers found for {content_type}")
    
    async def _get_backup_provider_config(
        self, 
        provider_name: str, 
        content_type: str, 
        task_complexity: str
    ) -> Optional[ProviderSelection]:
        """Get configuration for backup provider"""
        
        api_key_env = f"{provider_name.upper()}_API_KEY"
        if provider_name == "replicate":
            api_key_env = "REPLICATE_API_TOKEN"
        
        api_key = os.getenv(api_key_env)
        if not api_key or provider_name not in self.provider_configs:
            return None
        
        provider_config = self.provider_configs[provider_name]
        model_map = provider_config["models"]
        
        # Select appropriate model
        content_category = "text" if content_type in ["email_sequence", "ad_copy", "social_media", "blog_post", "landing_page"] else content_type
        
        if task_complexity == "reasoning" and "reasoning" in model_map:
            model = model_map["reasoning"]
        elif content_category in model_map:
            model = model_map[content_category]
        else:
            model = list(model_map.values())[0]
        
        return ProviderSelection(
            provider_name=provider_name,
            model_name=model,
            api_key=api_key,
            config=provider_config,
            backup_providers=[],
            selection_reason=f"Backup provider for {content_type}"
        )
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached provider selection is still valid"""
        if cache_key not in self.provider_cache:
            return False
        
        last_update = self.last_cache_update.get(cache_key)
        if not last_update:
            return False
        
        return (datetime.utcnow() - last_update).total_seconds() < self.cache_ttl
    
    async def _log_successful_usage(self, provider_selection: ProviderSelection, content_type: str):
        """Log successful provider usage for monitoring"""
        try:
            if self.monitor:
                await self.monitor.log_usage_success(
                    provider_selection.provider_name,
                    content_type,
                    datetime.utcnow()
                )
        except Exception as e:
            logger.debug(f"Failed to log successful usage: {str(e)}")
    
    async def _log_fallback_usage(self, provider_selection: ProviderSelection, content_type: str, failed_providers: List[str]):
        """Log fallback provider usage for monitoring"""
        try:
            if self.monitor:
                await self.monitor.log_fallback_usage(
                    provider_selection.provider_name,
                    content_type,
                    failed_providers,
                    datetime.utcnow()
                )
        except Exception as e:
            logger.debug(f"Failed to log fallback usage: {str(e)}")
    
    async def invalidate_cache(self, content_type: str = None):
        """Invalidate provider cache for content type or all"""
        if content_type:
            # Invalidate specific content type
            keys_to_remove = [k for k in self.provider_cache.keys() if k.startswith(content_type)]
            for key in keys_to_remove:
                self.provider_cache.pop(key, None)
                self.last_cache_update.pop(key, None)
        else:
            # Invalidate all cache
            self.provider_cache.clear()
            self.last_cache_update.clear()
        
        logger.info(f"🔄 Cache invalidated for {content_type or 'all content types'}")
    
    async def get_provider_status(self) -> Dict[str, Any]:
        """Get current status of all providers"""
        status = {
            "available_providers": [],
            "unavailable_providers": [],
            "cache_status": {
                "cached_selections": len(self.provider_cache),
                "cache_ttl": self.cache_ttl
            }
        }
        
        for provider_name in self.provider_configs.keys():
            api_key_env = f"{provider_name.upper()}_API_KEY"
            if provider_name == "replicate":
                api_key_env = "REPLICATE_API_TOKEN"
            
            api_key = os.getenv(api_key_env)
            if api_key:
                status["available_providers"].append({
                    "name": provider_name,
                    "models": list(self.provider_configs[provider_name]["models"].keys()),
                    "status": "available"
                })
            else:
                status["unavailable_providers"].append({
                    "name": provider_name,
                    "reason": f"Missing {api_key_env}",
                    "status": "unavailable"
                })
        
        return status

# Global router instance
_router_instance = None

async def get_dynamic_router() -> DynamicAIRouter:
    """Get global dynamic router instance"""
    global _router_instance
    if _router_instance is None:
        _router_instance = DynamicAIRouter()
    return _router_instance

# Convenience functions for easy integration
async def route_text_generation(generation_function: callable, content_type: str = "text", **kwargs):
    """Route text generation to optimal provider"""
    router = await get_dynamic_router()
    return await router.execute_with_optimal_provider(content_type, generation_function, **kwargs)

async def route_image_generation(generation_function: callable, **kwargs):
    """Route image generation to optimal provider"""
    router = await get_dynamic_router()
    return await router.execute_with_optimal_provider("image", generation_function, **kwargs)

async def route_video_generation(generation_function: callable, **kwargs):
    """Route video generation to optimal provider"""
    router = await get_dynamic_router()
    return await router.execute_with_optimal_provider("video", generation_function, **kwargs)