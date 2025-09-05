# =====================================
# File: src/intelligence/intelligence_module.py
# =====================================

"""
Intelligence Module implementation for CampaignForge modular architecture.

Implements the ModuleInterface for consistent module behavior and provides
the main entry point for Intelligence Engine functionality.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter

from src.core.interfaces.module_interfaces import ModuleInterface
from src.core.database import test_database_connection
from src.core.config import ai_provider_config
from .api.intelligence_routes import router as intelligence_router
from .services.intelligence_service import IntelligenceService
from .cache.intelligence_cache import intelligence_cache
from .providers.ai_provider_router import AIProviderRouter

logger = logging.getLogger(__name__)


class IntelligenceModule(ModuleInterface):
    """Intelligence Engine module implementation."""
    
    def __init__(self):
        self.intelligence_service = IntelligenceService()
        self.ai_router = AIProviderRouter()
        self._initialized = False
        self._healthy = False
    
    @property
    def name(self) -> str:
        """Return the module name."""
        return "intelligence"
    
    @property
    def version(self) -> str:
        """Return the module version."""
        return "2.0.0"
    
    async def initialize(self) -> bool:
        """
        Initialize the Intelligence Engine module.
        
        Sets up AI providers, cache system, and validates configuration.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("Initializing Intelligence Engine module...")
            
            # Check database connectivity
            db_connected = await test_database_connection()
            if not db_connected:
                logger.error("Database connection failed during Intelligence module initialization")
                return False
            
            # Validate AI provider configuration
            available_providers = [
                name for name, provider in ai_provider_config.providers.items() 
                if provider.enabled
            ]
            
            if not available_providers:
                logger.error("No AI providers available for Intelligence module")
                return False
            
            logger.info(f"Intelligence module initialized with {len(available_providers)} AI providers: {available_providers}")
            
            # Initialize cache cleanup task
            asyncio.create_task(self._cache_cleanup_task())
            
            self._initialized = True
            self._healthy = True
            
            logger.info("Intelligence Engine module initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Intelligence module initialization failed: {e}")
            self._initialized = False
            self._healthy = False
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check of the Intelligence Engine module.
        
        Returns:
            Dict[str, Any]: Health status information
        """
        try:
            # Basic health status
            if not self._initialized:
                return {
                    "status": "unhealthy",
                    "details": {"error": "Module not initialized"},
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            
            # Check AI providers
            available_providers = len([
                p for p in ai_provider_config.providers.values() 
                if p.enabled
            ])
            
            # Check cache statistics
            cache_stats = intelligence_cache.get_cache_statistics()
            
            # Check AI router statistics
            provider_stats = self.ai_router.get_provider_statistics()
            
            # Determine overall health
            status = "healthy"
            details = {
                "initialized": self._initialized,
                "available_providers": available_providers,
                "cache_entries": cache_stats["total_entries"],
                "provider_statistics": provider_stats
            }
            
            if available_providers == 0:
                status = "degraded"
                details["warning"] = "No AI providers available"
            
            return {
                "status": status,
                "details": details,
                "timestamp": "2024-01-01T00:00:00Z"  # In practice, use datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Intelligence module health check failed: {e}")
            return {
                "status": "unhealthy",
                "details": {"error": str(e)},
                "timestamp": "2024-01-01T00:00:00Z"
            }
    
    def get_api_router(self) -> Optional[APIRouter]:
        """
        Get the FastAPI router for Intelligence Engine endpoints.
        
        Returns:
            Optional[APIRouter]: FastAPI router with intelligence endpoints
        """
        return intelligence_router
    
    async def shutdown(self) -> None:
        """
        Clean shutdown of the Intelligence Engine module.
        
        Performs cleanup of resources, cache, and connections.
        """
        try:
            logger.info("Shutting down Intelligence Engine module...")
            
            # Cleanup cache
            intelligence_cache.cleanup_expired()
            
            # Mark as not healthy
            self._healthy = False
            
            logger.info("Intelligence Engine module shutdown complete")
            
        except Exception as e:
            logger.error(f"Intelligence module shutdown error: {e}")
    
    async def get_dependencies(self) -> Dict[str, str]:
        """
        Get module dependencies.
        
        Returns:
            Dict[str, str]: Dictionary of required dependencies
        """
        return {
            "core": "1.0.0",
            "database": "required",
            "ai_providers": "8 providers configured"
        }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get Intelligence Engine performance metrics.
        
        Returns:
            Dict[str, Any]: Performance and usage metrics
        """
        try:
            cache_stats = intelligence_cache.get_cache_statistics()
            provider_stats = self.ai_router.get_provider_statistics()
            
            return {
                "module": self.name,
                "version": self.version,
                "initialized": self._initialized,
                "healthy": self._healthy,
                "cache": cache_stats,
                "providers": provider_stats,
                "total_providers": len(ai_provider_config.providers),
                "enabled_providers": len([
                    p for p in ai_provider_config.providers.values() 
                    if p.enabled
                ])
            }
            
        except Exception as e:
            logger.error(f"Failed to get Intelligence module metrics: {e}")
            return {
                "module": self.name,
                "error": str(e)
            }
    
    async def _cache_cleanup_task(self):
        """Background task for cache cleanup."""
        while self._healthy:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                intelligence_cache.cleanup_expired()
                logger.debug("Intelligence cache cleanup completed")
            except Exception as e:
                logger.error(f"Cache cleanup task error: {e}")


# Global Intelligence Module instance
intelligence_module = IntelligenceModule()