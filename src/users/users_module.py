# src/users/users_module.py - CORRECTED VERSION

from typing import Dict, Any
from fastapi import APIRouter
from datetime import datetime

from src.core.interfaces.module_interfaces import ModuleInterface


class UsersModule(ModuleInterface):
    """
    Users Module - Handles authentication, user management, and user dashboard
    """
    
    def __init__(self):
        """Initialize the Users module"""
        # Initialize service placeholders - only create if they exist
        self.user_service = None
        self.auth_service = None
        self.dashboard_service = None
        self._router = None
        self._initialized = False
    
    @property
    def name(self) -> str:
        """Module name identifier"""
        return "users"
    
    @property 
    def version(self) -> str:
        """Module version"""
        return "1.0.0"
    
    async def initialize(self) -> bool:
        """
        Initialize the Users module
        
        Returns:
            bool: True if initialization successful
        """
        try:
            # Try to import and initialize services
            try:
                from src.users.api.routes import router as users_router
                self._router = users_router
            except ImportError as e:
                print(f"Warning: Could not import users router: {e}")
                self._router = APIRouter()  # Create empty router as fallback
            
            try:
                from src.users.services.user_service import UserService
                self.user_service = UserService()
                if hasattr(self.user_service, 'initialize'):
                    await self.user_service.initialize()
            except ImportError as e:
                print(f"Warning: Could not import UserService: {e}")
            
            try:
                from src.users.services.auth_service import AuthService
                self.auth_service = AuthService()
                if hasattr(self.auth_service, 'initialize'):
                    await self.auth_service.initialize()
            except ImportError as e:
                print(f"Warning: Could not import AuthService: {e}")
                
            try:
                from src.users.dashboard.dashboard_service import UserDashboardService
                self.dashboard_service = UserDashboardService()
                if hasattr(self.dashboard_service, 'initialize'):
                    await self.dashboard_service.initialize()
            except ImportError as e:
                print(f"Warning: Could not import UserDashboardService: {e}")
            
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"Users module initialization failed: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """
        Shutdown the Users module gracefully
        
        Returns:
            bool: True if shutdown successful
        """
        try:
            # Cleanup services if they exist and have shutdown methods
            if self.user_service and hasattr(self.user_service, 'shutdown'):
                await self.user_service.shutdown()
                
            if self.auth_service and hasattr(self.auth_service, 'shutdown'):
                await self.auth_service.shutdown()
                
            if self.dashboard_service and hasattr(self.dashboard_service, 'shutdown'):
                await self.dashboard_service.shutdown()
            
            self._initialized = False
            return True
            
        except Exception as e:
            print(f"Users module shutdown failed: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the Users module
        
        Returns:
            Dict[str, Any]: Health status and metrics
        """
        try:
            services_status = {}
            
            # Check each service health if available
            if self.user_service:
                if hasattr(self.user_service, 'health_check'):
                    user_health = await self.user_service.health_check()
                    services_status["user_service"] = user_health.get("status", "unknown")
                else:
                    services_status["user_service"] = "healthy"
            else:
                services_status["user_service"] = "not_loaded"
                
            if self.auth_service:
                if hasattr(self.auth_service, 'health_check'):
                    auth_health = await self.auth_service.health_check()
                    services_status["auth_service"] = auth_health.get("status", "unknown")
                else:
                    services_status["auth_service"] = "healthy"
            else:
                services_status["auth_service"] = "not_loaded"
                
            if self.dashboard_service:
                if hasattr(self.dashboard_service, 'health_check'):
                    dashboard_health = await self.dashboard_service.health_check()
                    services_status["dashboard_service"] = dashboard_health.get("status", "unknown")
                else:
                    services_status["dashboard_service"] = "healthy"
            else:
                services_status["dashboard_service"] = "not_loaded"
            
            return {
                "module": self.name,
                "version": self.version,
                "status": "healthy" if self._initialized else "not_initialized",
                "services": services_status,
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            return {
                "module": self.name,
                "version": self.version,
                "status": "error",
                "error": str(e),
                "timestamp": self._get_timestamp()
            }
    
    def get_api_router(self) -> APIRouter:
        """
        Get the API router for this module
        
        Returns:
            APIRouter: FastAPI router with all user endpoints
        """
        if self._router is None:
            # Return empty router if not initialized
            return APIRouter()
        return self._router
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for health checks"""
        return datetime.utcnow().isoformat()


# Export the module instance
users_module = UsersModule()