# ============================================================================
# CONTENT MODULE INTEGRATION
# ============================================================================

# src/content/content_module.py (Updated to use existing generators)

import asyncio
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter
from src.core.interfaces.module_interfaces import ModuleInterface

logger = logging.getLogger(__name__)

class ContentModule(ModuleInterface):
    """Content Generation Module - Integrated with existing intelligence generators"""
    
    def __init__(self):
        self._name = "content"
        self._version = "1.1.0"  # Updated to indicate integration
        self.dependencies = ["core", "intelligence"]  # Depends on intelligence module
        self.description = "Content generation using existing AI generator system"
        self._initialized = False
        
        # Module state
        self._router = None
        self._generator_status = {}

    @property
    def name(self) -> str:
        return self._name
    
    @property 
    def version(self) -> str:
        return self._version
    
    async def initialize(self) -> bool:
        """Initialize the Content Generation module"""
        try:
            logger.info(f"Initializing {self.name} module...")

            # Check if intelligence generators are available
            try:
                from src.intelligence.generators import get_generator_status
                self._generator_status = get_generator_status()
                
                available_count = self._generator_status.get("generators_available", 0)
                if available_count == 0:
                    logger.warning("No intelligence generators available")
                else:
                    logger.info(f"Found {available_count} available generators")
                    
            except ImportError as e:
                logger.warning(f"Could not check generator status: {e}")
                self._generator_status = {"error": str(e)}

            # Initialize API router
            try:
                from src.content.api.routes import router
                self._router = router
                logger.info("Content API router loaded successfully")
            except ImportError as e:
                logger.warning(f"Could not import content router: {e}")
                from fastapi import APIRouter
                self._router = APIRouter()
        
            self._initialized = True
            logger.info(f"{self.name} module initialized successfully")
            return True
        
        except Exception as e:
            logger.error(f"Content module initialization failed: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check module health"""
        try:
            return {
                "module": self.name,
                "status": "healthy" if self._initialized else "not_initialized",
                "version": self.version,
                "description": self.description,
                "generator_integration": self._generator_status,
                "features": [
                    "existing_generator_integration",
                    "email_sequence_generation", 
                    "social_media_content_creation",
                    "ad_copy_generation",
                    "ultra_cheap_ai_support",
                    "railway_compatibility",
                    "intelligence_data_integration"
                ]
            }
        except Exception as e:
            return {
                "module": self.name,
                "status": "error",
                "error": str(e),
                "version": self.version
            }
    
    def get_api_router(self) -> APIRouter:
        """Get the API router for this module"""
        if self._router is None:
            return APIRouter()
        return self._router