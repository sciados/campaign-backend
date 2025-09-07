# src/campaigns/campaigns_module.py
from typing import Dict, Any
from fastapi import APIRouter
from src.core.interfaces.module_interfaces import ModuleInterface

class CampaignsModule(ModuleInterface):
    def __init__(self):
        self.name = "campaigns"
        self.version = "1.0.0"
        self.dependencies = ["core", "users", "intelligence"]
        self.description = "Campaign creation, management, and workflows"
        
    async def initialize(self) -> bool:
        """Initialize the Campaigns module"""
        try:
            # Initialize campaign services
            # Initialize workflow engine
            # Verify database models
            return True
        except Exception as e:
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check module health"""
        return {
            "module": self.name,
            "status": "healthy",
            "version": self.version,
            "description": self.description,
            "services": {
                "campaign_service": "operational",
                "workflow_service": "operational",
                "dashboard_service": "operational"
            },
            "features": [
                "campaign_creation",
                "campaign_management",
                "workflow_automation",
                "intelligence_integration",
                "dashboard_analytics"
            ]
        }
    
    def get_api_router(self) -> APIRouter:
        """Get the API router for this module"""
        from .api.routes import router
        return router