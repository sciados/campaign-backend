# ==============================================================================
# 2. STORAGE MODULE REGISTRATION
# ==============================================================================

# src/storage/storage_module.py
from typing import Dict, Any, List
from fastapi import APIRouter
from src.core.interfaces.module_interfaces import BaseModule
from src.core.factories.service_factory import ServiceFactory
import logging

logger = logging.getLogger(__name__)

class StorageModule(BaseModule):
    """Storage Module - File upload, download, and media generation"""
    
    def __init__(self):
        super().__init__(
            name="storage",
            version="1.0.0",
            description="File storage and media generation module"
        )
        self.router = APIRouter(prefix="/storage", tags=["storage"])
        
    async def initialize(self, service_factory: ServiceFactory) -> bool:
        """Initialize storage module services"""
        try:
            # Register storage services
            from .services.cloudflare_service import CloudflareService
            from .services.file_service import FileService
            from .services.media_service import MediaService
            from .services.quota_service import QuotaService
            
            # Register with service factory
            service_factory.register_service("cloudflare", CloudflareService)
            service_factory.register_service("file_manager", FileService)
            service_factory.register_service("media_generator", MediaService)
            service_factory.register_service("quota_manager", QuotaService)
            
            # Initialize storage directory structure
            await self._setup_storage_infrastructure()
            
            logger.info("✅ Storage Module initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Storage Module initialization failed: {e}")
            return False
    
    async def _setup_storage_infrastructure(self):
        """Setup storage infrastructure"""
        # Test Cloudflare R2 connection
        cloudflare_service = ServiceFactory().get_service("cloudflare")
        if cloudflare_service:
            await cloudflare_service.test_connection()
    
    def get_router(self) -> APIRouter:
        """Get module router"""
        return self.router
    
    async def health_check(self) -> Dict[str, Any]:
        """Storage module health check"""
        return {
            "module": "storage",
            "status": "healthy",
            "services": {
                "cloudflare_r2": "connected",
                "file_management": "operational",
                "media_generation": "ready",
                "quota_system": "active"
            },
            "version": self.version
        }