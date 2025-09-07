# src/users/users_module.py
from typing import Dict, Any
from fastapi import APIRouter
from src.core.interfaces.module_interfaces import ModuleInterface
import logging

logger = logging.getLogger(__name__)

class UsersModule(ModuleInterface):
    """Users Module - Authentication and User Management"""
    
    def __init__(self):
        self.name = "users"
        self.version = "1.0.0" 
        self.dependencies = ["core"]
        self.description = "Authentication, user management, and dashboards"
        
    async def initialize(self) -> bool:
        """Initialize the Users module"""
        try:
            logger.info(f"Initializing {self.name} module v{self.version}")
            
            # Verify database models are available
            from .models.user import User
            from .models.user_storage import UserStorage
            
            # Verify services can be imported
            from .services.user_service import UserService
            from .services.auth_service import AuthService
            
            logger.info("Users module initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Users module: {str(e)}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check module health"""
        return {
            "module": self.name,
            "status": "healthy",
            "version": self.version,
            "description": self.description,
            "services": {
                "auth_service": "operational",
                "user_service": "operational",
                "dashboard_service": "operational"
            },
            "features": [
                "user_authentication",
                "user_management", 
                "admin_dashboard",
                "user_dashboard",
                "profile_management"
            ]
        }
    
    def get_api_router(self) -> APIRouter:
        """Get the API router for this module"""
        router = APIRouter()
        
        # Include auth and user management routes
        from .api.routes import router as users_router
        router.include_router(users_router)
        
        # Include dashboard routes
        from .dashboard.dashboard_routes import router as dashboard_router
        router.include_router(dashboard_router)
        
        return router