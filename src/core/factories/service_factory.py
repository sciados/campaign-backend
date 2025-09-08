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
    
    @classmethod
    def register_service(cls, name: str, service_class: Type):
        """Register a service class for factory creation"""
        cls._service_registry[name] = service_class
        logger.info(f"Registered service: {name}")
    
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
        if service_name not in cls._service_registry:
            raise ValueError(f"Service '{service_name}' not registered")
        
        service_class = cls._service_registry[service_name]
        async with cls.create_service(service_class) as service:
            yield service
    
    @classmethod
    def list_registered_services(cls) -> Dict[str, str]:
        """List all registered services"""
        return {name: cls.__name__ for name, cls in cls._service_registry.items()}