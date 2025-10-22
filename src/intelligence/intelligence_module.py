# =====================================
# File: src/intelligence/intelligence_module.py
# =====================================

"""
Intelligence Module implementation for CampaignForge modular architecture.
Enhanced for Session 5 with async loop fixes.

Implements the ModuleInterface for consistent module behavior and provides
the main entry point for Intelligence Engine functionality.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter

from src.core.interfaces.module_interfaces import ModuleInterface
from src.core.config import ai_provider_config
from src.intelligence.api.intelligence_routes import router as intelligence_router
from src.intelligence.services.intelligence_service import IntelligenceService
from src.intelligence.cache.intelligence_cache import intelligence_cache
from src.intelligence.providers.ai_provider_router import AIProviderRouter

logger = logging.getLogger(__name__)


class IntelligenceModule(ModuleInterface):
    """Intelligence Engine module implementation with Session 5 async fixes."""
    
    def __init__(self):
        self._intelligence_service = None  # Lazy initialization to avoid async context issues
        self.ai_router = AIProviderRouter()
        self._initialized = False
        self._healthy = False
        self._cache_cleanup_task = None  # Track cleanup task for proper shutdown
    
    @property
    def intelligence_service(self) -> IntelligenceService:
        """Lazy initialization of intelligence service to ensure proper async context."""
        if self._intelligence_service is None:
            self._intelligence_service = IntelligenceService()
        return self._intelligence_service

    @property
    def name(self) -> str:
        """Return the module name."""
        return "intelligence"
    
    @property
    def version(self) -> str:
        """Return the module version."""
        return "2.1.0"  # Updated for Session 5

    async def initialize(self) -> bool:        
        try:
            logger.info("Initializing Intelligence Engine module (Session 5 with async fixes)...")
            
            # FIXED: Check database connectivity without creating async loop conflicts
            db_connected = await self._safe_database_check()
            if not db_connected:
                logger.error("Database connection failed during Intelligence module initialization")
                return False
            
            # Validate AI provider configuration - check both enabled AND valid API key
            available_providers = [
                name for name, provider in ai_provider_config.providers.items()
                if provider.enabled and provider.api_key and len(provider.api_key.strip()) > 10
            ]

            if not available_providers:
                logger.warning("No AI providers available for Intelligence module - check API keys are configured")
                logger.warning(f"Total providers configured: {len(ai_provider_config.providers)}")
                # Continue initialization even without providers - mark as degraded instead of failing
                # This allows the module to report its status
                logger.warning("Intelligence module will be marked as degraded until API keys are configured")
                self._initialized = True
                self._healthy = False  # Mark as unhealthy but initialized
                return True  # Allow initialization to complete

            logger.info(f"Intelligence module initialized with {len(available_providers)} AI providers: {available_providers}")
            
            # FIXED: Only initialize cache cleanup task if not already running
            if self._cache_cleanup_task is None or self._cache_cleanup_task.done():
                try:
                    # Check if we're in an event loop already
                    loop = asyncio.get_running_loop()
                    self._cache_cleanup_task = loop.create_task(self._cache_cleanup_task_impl())
                    logger.info("Cache cleanup task initialized successfully")
                except RuntimeError:
                    # No running loop, skip cache cleanup task
                    logger.warning("No running event loop, skipping cache cleanup task initialization")
                    self._cache_cleanup_task = None
            
            self._initialized = True
            self._healthy = True
            
            logger.info("Intelligence Engine module initialized successfully with async fixes")
            return True
            
        except Exception as e:
            logger.error(f"Intelligence module initialization failed: {e}")
            self._initialized = False
            self._healthy = False
            return False
    
    async def _safe_database_check(self) -> bool:
        """
        Safely check database connection without creating async loop conflicts.
    
        FIXED: Uses session manager directly with proper SQL text() declaration
        """
        try:
            from src.core.database.session import AsyncSessionManager
            from sqlalchemy import text  # FIXED: Import text for SQL execution
        
            # Test async session creation directly
            async with AsyncSessionManager.get_session() as session:
                # FIXED: Properly declare textual SQL with text()
                result = await session.execute(text("SELECT 1"))
                test_value = result.scalar()
            
                if test_value == 1:
                    logger.info("Intelligence Engine database connectivity verified")
                    return True
                else:
                    logger.warning("Database connection test returned unexpected result")
                    return False
                
        except Exception as e:
            logger.error(f"Database connectivity check failed: {e}")
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
            
            # Check AI providers - must have valid API keys
            available_providers = len([
                p for p in ai_provider_config.providers.values()
                if p.enabled and p.api_key and len(p.api_key.strip()) > 10
            ])
            
            # Check cache statistics
            cache_stats = intelligence_cache.get_cache_statistics()
            
            # Check AI router statistics
            provider_stats = self.ai_router.get_provider_statistics()
            
            # Check cache cleanup task status
            cache_task_status = "running" if (
                self._cache_cleanup_task and not self._cache_cleanup_task.done()
            ) else "stopped"
            
            # Determine overall health
            status = "healthy"
            details = {
                "initialized": self._initialized,
                "available_providers": available_providers,
                "cache_entries": cache_stats["total_entries"],
                "provider_statistics": provider_stats,
                "cache_cleanup_task": cache_task_status,
                "async_loop_fix": "applied",  # Session 5 enhancement
                "session_5_ready": True,  # Session 5 enhancement
                "database_check": "safe_method_used"  # Session 5 fix
            }

            if available_providers == 0:
                status = "unhealthy"
                details["error"] = "No AI providers available - check API keys configuration"
                details["warning"] = "Intelligence module requires at least one AI provider with valid API key"
            
            return {
                "status": status,
                "details": details,
                "timestamp": "2024-01-01T00:00:00Z"
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
    
    async def shutdown(self) -> bool:       
        try:
            logger.info("Shutting down Intelligence Engine module...")
            
            # FIXED: Properly cancel cache cleanup task
            if self._cache_cleanup_task and not self._cache_cleanup_task.done():
                self._cache_cleanup_task.cancel()
                try:
                    await self._cache_cleanup_task
                except asyncio.CancelledError:
                    logger.info("Cache cleanup task cancelled successfully")
                except Exception as e:
                    logger.warning(f"Cache cleanup task cancellation error: {e}")
            
            # Cleanup cache
            intelligence_cache.cleanup_expired()
            
            # Mark as not healthy
            self._healthy = False
            self._initialized = False
            
            logger.info("Intelligence Engine module shutdown complete")
            return True
        
        except Exception as e:
            logger.error(f"Intelligence module shutdown error: {e}")
            return False
        
    async def get_dependencies(self) -> Dict[str, str]:
        """
        Get module dependencies.
        
        Returns:
            Dict[str, str]: Dictionary of required dependencies
        """
        return {
            "core": "1.0.0",
            "database": "required",
            "ai_providers": "8 providers configured",
            "session_5_fixes": "applied"  # Session 5 enhancement
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
                ]),
                "async_fixes": {  # Session 5 enhancements
                    "cache_cleanup_task": "fixed",
                    "event_loop_handling": "improved",
                    "database_check": "safe_method_implemented",
                    "session_5_ready": True
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get Intelligence module metrics: {e}")
            return {
                "module": self.name,
                "error": str(e),
                "version": self.version
            }
    
    async def _cache_cleanup_task_impl(self):
        """Background task for cache cleanup with proper async handling."""
        logger.info("Starting cache cleanup background task")
        
        try:
            while self._healthy:
                try:
                    await asyncio.sleep(300)  # Run every 5 minutes
                    
                    if not self._healthy:  # Check if still healthy after sleep
                        break
                        
                    intelligence_cache.cleanup_expired()
                    logger.debug("Intelligence cache cleanup completed")
                    
                except asyncio.CancelledError:
                    logger.info("Cache cleanup task cancelled")
                    break
                except Exception as e:
                    logger.error(f"Cache cleanup task error: {e}")
                    # Continue running despite errors
                    await asyncio.sleep(60)  # Wait before retrying
                    
        except Exception as e:
            logger.error(f"Cache cleanup task failed: {e}")
        finally:
            logger.info("Cache cleanup background task stopped")


# Global Intelligence Module instance with Session 5 fixes
intelligence_module = IntelligenceModule()