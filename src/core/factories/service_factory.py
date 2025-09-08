# ============================================================================
# SERVICE RE-ENABLEMENT FOR SESSION 5
# ============================================================================

# src/core/factories/service_factory.py (Enhanced Version)

from typing import TypeVar, Type, Optional, AsyncContextManager, Dict, Any
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database.session import AsyncSessionManager
import logging

T = TypeVar('T')
logger = logging.getLogger(__name__)

class ServiceFactory:
    """Enhanced Factory for creating services with proper database session management"""
    
    _service_registry: Dict[str, Type] = {}
    _initialized = False
    
    @classmethod
    async def initialize(cls):
        """Initialize the service factory and register all services"""
        if cls._initialized:
            return
        
        try:
            logger.info("Initializing ServiceFactory for Session 5...")
            
            # Register User Services
            try:
                from src.users.services.user_service import UserService
                from src.users.services.auth_service import AuthService
                cls.register_service("user", UserService)
                cls.register_service("auth", AuthService)
                logger.info("User services registered successfully")
            except ImportError as e:
                logger.warning(f"Could not register user services: {e}")
            
            # Register Campaign Services
            try:
                from src.campaigns.services.campaign_service import CampaignService
                from src.campaigns.services.workflow_service import WorkflowService
                cls.register_service("campaign", CampaignService)
                cls.register_service("workflow", WorkflowService)
                logger.info("Campaign services registered successfully")
            except ImportError as e:
                logger.warning(f"Could not register campaign services: {e}")
            
            # Register Content Services
            try:
                from src.content.services.content_service import ContentService
                from src.content.services.integrated_content_service import IntegratedContentService
                cls.register_service("content", ContentService)
                cls.register_service("integrated_content", IntegratedContentService)
                logger.info("Content services registered successfully")
            except ImportError as e:
                logger.warning(f"Could not register content services: {e}")
            
            # Register Intelligence Services
            try:
                from src.intelligence.services.intelligence_service import IntelligenceService
                from src.intelligence.services.analysis_service import AnalysisService
                cls.register_service("intelligence", IntelligenceService)
                cls.register_service("analysis", AnalysisService)
                logger.info("Intelligence services registered successfully")
            except ImportError as e:
                logger.warning(f"Could not register intelligence services: {e}")
            
            cls._initialized = True
            logger.info(f"ServiceFactory initialized with {len(cls._service_registry)} services")
            
        except Exception as e:
            logger.error(f"ServiceFactory initialization failed: {e}")
            cls._initialized = False
    
    @classmethod
    def register_service(cls, name: str, service_class: Type):
        """Register a service class for factory creation"""
        cls._service_registry[name] = service_class
        logger.debug(f"Registered service: {name}")
    
    @staticmethod
    @asynccontextmanager
    async def create_service(service_class: Type[T]) -> T:
        """Create a service with an async database session"""
        async with AsyncSessionManager.get_session() as db:
            service = service_class(db)
            try:
                logger.debug(f"Created service: {service_class.__name__}")
                yield service
            except Exception as e:
                logger.error(f"Service error in {service_class.__name__}: {e}")
                raise
            finally:
                logger.debug(f"Cleaning up service: {service_class.__name__}")
    
    @staticmethod
    @asynccontextmanager
    async def create_transactional_service(service_class: Type[T]) -> T:
        """Create a service with an async transaction"""
        async with AsyncSessionManager.get_transaction() as db:
            service = service_class(db)
            try:
                logger.debug(f"Created transactional service: {service_class.__name__}")
                yield service
            except Exception as e:
                logger.error(f"Transactional service error in {service_class.__name__}: {e}")
                raise
            finally:
                logger.debug(f"Cleaning up transactional service: {service_class.__name__}")
    
    @classmethod
    @asynccontextmanager
    async def create_named_service(cls, service_name: str):
        """Create a service by registered name"""
        if not cls._initialized:
            await cls.initialize()
        
        if service_name not in cls._service_registry:
            raise ValueError(f"Service '{service_name}' not registered. Available: {list(cls._service_registry.keys())}")
        
        service_class = cls._service_registry[service_name]
        async with cls.create_service(service_class) as service:
            yield service
    
    @classmethod
    def list_registered_services(cls) -> Dict[str, str]:
        """List all registered services"""
        return {name: service_class.__name__ for name, service_class in cls._service_registry.items()}
    
    @classmethod
    async def health_check(cls) -> Dict[str, Any]:
        """Check health of service factory"""
        try:
            if not cls._initialized:
                await cls.initialize()
            
            # Test database connectivity
            async with AsyncSessionManager.get_session() as db:
                pass  # Just test we can get a session
            
            return {
                "status": "healthy",
                "initialized": cls._initialized,
                "registered_services": len(cls._service_registry),
                "services": list(cls._service_registry.keys()),
                "database_session": "available"
            }
            
        except Exception as e:
            logger.error(f"ServiceFactory health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "initialized": cls._initialized
            }

# Convenience functions for common service patterns
@asynccontextmanager
async def get_user_service():
    """Get UserService with proper session management"""
    async with ServiceFactory.create_named_service("user") as service:
        yield service

@asynccontextmanager
async def get_auth_service():
    """Get AuthService with proper session management"""
    async with ServiceFactory.create_named_service("auth") as service:
        yield service

@asynccontextmanager
async def get_campaign_service():
    """Get CampaignService with proper session management"""
    async with ServiceFactory.create_named_service("campaign") as service:
        yield service

@asynccontextmanager
async def get_content_service():
    """Get IntegratedContentService with proper session management"""
    async with ServiceFactory.create_named_service("integrated_content") as service:
        yield service