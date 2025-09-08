# src/campaigns/campaigns_module.py - COMPLETE WITH PROPER CLEANUP
import asyncio
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter
from src.core.database.connection import AsyncSessionLocal
from src.core.interfaces.module_interfaces import ModuleInterface
from src.campaigns.services.campaign_service import CampaignService

logger = logging.getLogger(__name__)

class CampaignModule(ModuleInterface):
    def __init__(self):
        self._name = "campaigns"
        self._version = "1.0.0"
        self.dependencies = ["core", "users", "intelligence"]
        self.description = "Campaign creation, management, and workflows"
        self._initialized = False
        
        # Services (will be initialized later)
        self.campaign_service = None
        self.workflow_service = None
        self.dashboard_service = None
        
        # Runtime tracking
        self._background_tasks: List[asyncio.Task] = []
        self._campaign_cache = {}
        self._db_pool = None
        self._router = None

    @property
    def name(self) -> str:
        return self._name
    
    @property 
    def version(self) -> str:
        return self._version
    
    async def initialize(self) -> bool:
        """Initialize the Campaigns module"""
        try:
            logger.info(f"Initializing {self.name} module...")

            # Skip database-dependent services during module initialization
            self.campaign_service = None
            self.workflow_service = None  # Don't create without database session
            self.dashboard_service = None
        
            logger.info("Skipping service initialization - services will be created when needed")
        
            # Initialize API router
            try:
                from src.campaigns.api.routes import router
                self._router = router
            except ImportError as e:
                logger.warning(f"Could not import campaigns router: {e}")
                from fastapi import APIRouter
                self._router = APIRouter()
        
            self._initialized = True
            logger.info(f"{self.name} module initialized successfully")
            return True
        
        except Exception as e:
            logger.error(f"Campaign module initialization failed: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown the Campaign module gracefully"""
        try:
            logger.info(f"Shutting down {self.name} module...")
            
            # 1. Stop any running workflow processes
            if self.workflow_service:
                try:
                    if hasattr(self.workflow_service, 'stop_all_workflows'):
                        logger.info("Stopping all active workflows...")
                        await self.workflow_service.stop_all_workflows()
                    
                    # Save pending workflow states before shutdown
                    if hasattr(self.workflow_service, 'save_pending_states'):
                        logger.info("Saving pending workflow states...")
                        await self.workflow_service.save_pending_states()
                        
                    if hasattr(self.workflow_service, 'shutdown'):
                        await self.workflow_service.shutdown()
                except Exception as e:
                    logger.error(f"Error during workflow service shutdown: {e}")
            
            # 2. Close campaign service connections
            if self.campaign_service:
                try:
                    if hasattr(self.campaign_service, 'shutdown'):
                        logger.info("Shutting down campaign service...")
                        await self.campaign_service.shutdown()
                except Exception as e:
                    logger.error(f"Error during campaign service shutdown: {e}")
            
            # 3. Cleanup dashboard service
            if self.dashboard_service:
                try:
                    if hasattr(self.dashboard_service, 'shutdown'):
                        logger.info("Shutting down dashboard service...")
                        await self.dashboard_service.shutdown()
                except Exception as e:
                    logger.error(f"Error during dashboard service shutdown: {e}")
            
            # 4. Cancel any background tasks
            if self._background_tasks:
                logger.info(f"Cancelling {len(self._background_tasks)} background tasks...")
                for task in self._background_tasks:
                    if not task.done():
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            pass
                        except Exception as e:
                            logger.error(f"Error cancelling background task: {e}")
                self._background_tasks.clear()
            
            # 5. Clear any caches
            if self._campaign_cache:
                logger.info("Clearing campaign cache...")
                self._campaign_cache.clear()
            
            # 6. Close database connections specific to campaigns
            if self._db_pool:
                try:
                    logger.info("Closing database pool...")
                    await self._db_pool.close()
                    self._db_pool = None
                except Exception as e:
                    logger.error(f"Error closing database pool: {e}")
            
            # 7. Mark module as shutdown
            self._initialized = False
            
            logger.info(f"{self.name} module shutdown completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Campaign module shutdown failed: {e}")
            # Even if cleanup fails, mark as shutdown to prevent further operations
            self._initialized = False
            return False
    
    async def _start_background_tasks(self):
        """Start background tasks for campaign management"""
        try:
            # Start workflow monitoring task
            if self.workflow_service and hasattr(self.workflow_service, 'monitor_workflows'):
                task = asyncio.create_task(self._workflow_monitor_task())
                self._background_tasks.append(task)
            
            # Start analytics collection task
            if self.dashboard_service and hasattr(self.dashboard_service, 'collect_analytics'):
                task = asyncio.create_task(self._analytics_collection_task())
                self._background_tasks.append(task)
                
            logger.info(f"Started {len(self._background_tasks)} background tasks")
            
        except Exception as e:
            logger.error(f"Error starting background tasks: {e}")
    
    async def _workflow_monitor_task(self):
        """Background task to monitor workflow execution"""
        try:
            while self._initialized:
                if self.workflow_service:
                    await self.workflow_service.monitor_workflows()
                await asyncio.sleep(30)  # Monitor every 30 seconds
        except asyncio.CancelledError:
            logger.info("Workflow monitor task cancelled")
        except Exception as e:
            logger.error(f"Workflow monitor task error: {e}")
    
    async def _analytics_collection_task(self):
        """Background task to collect campaign analytics"""
        try:
            while self._initialized:
                if self.dashboard_service:
                    await self.dashboard_service.collect_analytics()
                await asyncio.sleep(300)  # Collect every 5 minutes
        except asyncio.CancelledError:
            logger.info("Analytics collection task cancelled")
        except Exception as e:
            logger.error(f"Analytics collection task error: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check module health"""
        try:
            services_status = {}
            
            # Check campaign service
            if self.campaign_service:
                if hasattr(self.campaign_service, 'health_check'):
                    campaign_health = await self.campaign_service.health_check()
                    services_status["campaign_service"] = campaign_health.get("status", "unknown")
                else:
                    services_status["campaign_service"] = "operational"
            else:
                services_status["campaign_service"] = "not_loaded"
            
            # Check workflow service
            if self.workflow_service:
                if hasattr(self.workflow_service, 'health_check'):
                    workflow_health = await self.workflow_service.health_check()
                    services_status["workflow_service"] = workflow_health.get("status", "unknown")
                else:
                    services_status["workflow_service"] = "operational"
            else:
                services_status["workflow_service"] = "not_loaded"
            
            # Check dashboard service
            if self.dashboard_service:
                if hasattr(self.dashboard_service, 'health_check'):
                    dashboard_health = await self.dashboard_service.health_check()
                    services_status["dashboard_service"] = dashboard_health.get("status", "unknown")
                else:
                    services_status["dashboard_service"] = "operational"
            else:
                services_status["dashboard_service"] = "not_loaded"
            
            return {
                "module": self.name,
                "status": "healthy" if self._initialized else "not_initialized",
                "version": self.version,
                "description": self.description,
                "services": services_status,
                "background_tasks": len(self._background_tasks),
                "cache_entries": len(self._campaign_cache),
                "features": [
                    "campaign_creation",
                    "campaign_management", 
                    "workflow_automation",
                    "intelligence_integration",
                    "dashboard_analytics"
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


# Export the module instance
campaigns_module = CampaignModule()