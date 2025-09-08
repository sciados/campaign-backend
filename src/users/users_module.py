# ============================================================================
# MODULE UPDATES FOR SERVICE RE-ENABLEMENT
# ============================================================================

# src/users/users_module.py (Updated for Session 5)

from typing import Dict, Any
from fastapi import APIRouter
from datetime import datetime

from src.core.interfaces.module_interfaces import ModuleInterface
from src.core.factories.service_factory import ServiceFactory

class UsersModule(ModuleInterface):
    """Users Module - Enhanced with service re-enablement"""
    
    def __init__(self):
        self.name = "users"
        self.version = "1.1.0"  # Updated version
        self.description = "User management with authentication and dashboard services"
        self._router = None
        self._initialized = False
        
        # Register services with factory
        self._register_services()
    
    def _register_services(self):
        """Register services with ServiceFactory"""
        try:
            from src.users.services.user_service import UserService
            from src.users.services.auth_service import AuthService
            
            ServiceFactory.register_service("user_service", UserService)
            ServiceFactory.register_service("auth_service", AuthService)
            
        except ImportError as e:
            print(f"Warning: Could not register user services: {e}")
    
    async def initialize(self) -> bool:
        """Initialize the Users module with service re-enablement"""
        try:
            # Initialize API router
            try:
                from src.users.api.routes import router as users_router
                self._router = users_router
            except ImportError as e:
                print(f"Warning: Could not import users router: {e}")
                self._router = APIRouter()
            
            # Services are now created on-demand using ServiceFactory
            print("User services registered and available via ServiceFactory")
            
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"Users module initialization failed: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Enhanced health check with service testing"""
        try:
            services_status = {}
            
            # Test UserService
            try:
                async with ServiceFactory.create_named_service("user_service") as user_service:
                    health = await user_service.health_check() if hasattr(user_service, 'health_check') else {"status": "healthy"}
                    services_status["user_service"] = health.get("status", "operational")
            except Exception as e:
                services_status["user_service"] = f"error: {str(e)}"
            
            # Test AuthService
            try:
                async with ServiceFactory.create_named_service("auth_service") as auth_service:
                    health = await auth_service.health_check()
                    services_status["auth_service"] = health.get("status", "operational")
            except Exception as e:
                services_status["auth_service"] = f"error: {str(e)}"
            
            return {
                "module": self.name,
                "version": self.version,
                "status": "healthy" if self._initialized else "not_initialized",
                "services": services_status,
                "features": [
                    "user_registration",
                    "user_authentication",
                    "profile_management",
                    "company_management",
                    "dashboard_preferences",
                    "user_type_management"
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "module": self.name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_api_router(self) -> APIRouter:
        """Get the API router for this module"""
        if self._router is None:
            return APIRouter()
        return self._router