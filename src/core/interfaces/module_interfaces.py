# =====================================
# File: src/core/interfaces/module_interfaces.py
# =====================================

"""
Core module interface contracts for CampaignForge modular architecture.

Every module must implement these interfaces to ensure consistent
initialization, health checking, and API router registration.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from fastapi import APIRouter


class ModuleInterface(ABC):
    """
    Base interface that all CampaignForge modules must implement.
    
    This ensures consistent module behavior across the entire application
    and enables proper dependency management and health monitoring.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the module name."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Return the module version."""
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the module.
        
        This method should set up any required resources, connections,
        or dependencies for the module to function properly.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check of the module.
        
        Returns:
            Dict[str, Any]: Health status information including:
                - status: "healthy" | "unhealthy" | "degraded"
                - details: Additional health information
                - timestamp: When the check was performed
        """
        pass
    
    @abstractmethod
    def get_api_router(self) -> Optional[APIRouter]:
        """
        Get the FastAPI router for this module.
        
        Returns:
            Optional[APIRouter]: FastAPI router with module endpoints,
                                or None if module has no API endpoints
        """
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """
        Clean shutdown of the module.
        
        This method should clean up any resources, close connections,
        and perform any necessary cleanup before application shutdown.
        """
        pass
    
    async def get_dependencies(self) -> Dict[str, str]:
        """
        Get module dependencies.
        
        Returns:
            Dict[str, str]: Dictionary of required dependencies and their versions
        """
        return {}
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get module performance metrics.
        
        Returns:
            Dict[str, Any]: Performance and usage metrics
        """
        return {}