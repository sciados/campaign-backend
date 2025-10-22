# src/content/content_module.py - Complete Session 5 Implementation

import asyncio
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter
from src.core.interfaces.module_interfaces import ModuleInterface

logger = logging.getLogger(__name__)

class ContentModule(ModuleInterface):
    """Content Generation Module - Complete Session 5 Implementation"""
    
    def __init__(self):
        self._name = "content"
        self._version = "2.1.0"
        self.dependencies = ["core", "intelligence", "users", "campaigns"]
        self.description = "Complete content generation system with intelligence integration"
        self._initialized = False
        
        # Enhanced module state
        self._router = None
        self._generator_status = {}
        self._service_factory_ready = False
        self._dependency_status = {}

    @property
    def name(self) -> str:
        return self._name
    
    @property 
    def version(self) -> str:
        return self._version
    
    async def initialize(self) -> bool:
        """Complete Session 5 initialization"""
        try:
            logger.info(f"Initializing {self.name} module for Session 5...")

            # Phase 1: Initialize Service Factory
            try:
                from src.core.factories.service_factory import ServiceFactory
                await ServiceFactory.initialize()
                self._service_factory_ready = True
                logger.info("Service Factory initialized for content module")
            except Exception as e:
                logger.warning(f"Service Factory initialization failed: {e}")
                self._service_factory_ready = False

            # Phase 2: Test integrated content service with proper error handling
            try:
                if self._service_factory_ready:
                    async with ServiceFactory.create_named_service("integrated_content") as test_service:
                        # Get available generators from the service
                        generator_list = test_service.get_available_generators()

                        # Build generator status from the list
                        self._generator_status = {
                            "total_available": len(generator_list) if generator_list else 0,
                            "generators": generator_list if generator_list else [],
                            "initialized": True
                        }

                        logger.info(f"Integrated content service tested successfully - {len(generator_list)} generators available")
                else:
                    # Test direct service creation
                    from src.content.services.integrated_content_service import IntegratedContentService
                    from src.core.database.session import AsyncSessionManager
                    async with AsyncSessionManager.get_session() as db:
                        test_service = IntegratedContentService(db)

                        # Get available generators from the service
                        generator_list = test_service.get_available_generators()

                        # Build generator status from the list
                        self._generator_status = {
                            "total_available": len(generator_list) if generator_list else 0,
                            "generators": generator_list if generator_list else [],
                            "initialized": True
                        }

                        logger.info(f"Direct content service tested successfully - {len(generator_list)} generators available")
                
                # FIXED: Safe access to generator status
                available_count = self._generator_status.get("total_available", 0)
                logger.info(f"Content generators available: {available_count}")
                    
            except Exception as e:
                logger.warning(f"Content service test failed: {e}")
                self._generator_status = {"error": str(e), "fallback": True, "total_available": 0}

            # Phase 3: Load API router
            try:
                from src.content.api.routes import router
                self._router = router
                logger.info("Content API router loaded successfully")
            except ImportError as e:
                logger.warning(f"Could not import content router: {e}")
                # Create fallback router
                self._router = self._create_fallback_router()

            # Phase 4: Validate dependencies
            self._dependency_status = await self._check_dependencies()
            
            # Phase 5: Validate overall readiness
            readiness_score = self._calculate_readiness()
            
            self._initialized = readiness_score >= 0.5  # 50% minimum for basic operation
            
            if self._initialized:
                logger.info(f"{self.name} module initialized successfully (readiness: {readiness_score:.1%})")
            else:
                logger.warning(f"{self.name} module initialization incomplete (readiness: {readiness_score:.1%})")
            
            return self._initialized
        
        except Exception as e:
            logger.error(f"Content module initialization failed: {e}")
            return False
    
    def _create_fallback_router(self) -> APIRouter:
        """Create a fallback router when imports fail"""
        from fastapi import APIRouter
        fallback_router = APIRouter(prefix="/api/content", tags=["content"])
        
        @fallback_router.get("/health")
        async def content_fallback_health():
            return {
                "status": "fallback",
                "module": "content",
                "message": "Running in fallback mode - limited functionality"
            }
        
        @fallback_router.get("/status")
        async def content_fallback_status():
            return {
                "status": "fallback_mode",
                "available_endpoints": ["/health", "/status"],
                "full_functionality": False
            }
        
        return fallback_router
    
    async def _check_dependencies(self) -> Dict[str, str]:
        """Comprehensive dependency checking"""
        dependencies = {}
        
        # Check core dependency
        try:
            from src.core.database.session import AsyncSessionManager
            # Test actual session creation
            async with AsyncSessionManager.get_session() as db:
                dependencies["core"] = "available"
        except Exception as e:
            dependencies["core"] = f"error: {str(e)[:50]}"
        
        # Check intelligence dependency
        try:
            from src.intelligence.intelligence_module import intelligence_module
            intelligence_health = await intelligence_module.health_check()
            if intelligence_health.get("status") == "healthy":
                dependencies["intelligence"] = "available"
            else:
                dependencies["intelligence"] = "degraded"
        except Exception as e:
            dependencies["intelligence"] = f"error: {str(e)[:50]}"
        
        # Check users dependency
        try:
            from src.users.services.user_service import UserService
            dependencies["users"] = "available"
        except ImportError:
            dependencies["users"] = "missing"
        except Exception as e:
            dependencies["users"] = f"error: {str(e)[:50]}"
        
        # Check campaigns dependency
        try:
            from src.campaigns.services.campaign_service import CampaignService
            dependencies["campaigns"] = "available"
        except ImportError:
            dependencies["campaigns"] = "missing"
        except Exception as e:
            dependencies["campaigns"] = f"error: {str(e)[:50]}"
        
        return dependencies
    
    def _calculate_readiness(self) -> float:
        """Calculate module readiness score"""
        score = 0.0
        total_factors = 5
        
        # Service factory ready (20%)
        if self._service_factory_ready:
            score += 0.2
        
        # Generator status (20%) - FIXED: Safe access
        if self._generator_status and not self._generator_status.get("error"):
            score += 0.2
        
        # Router loaded (20%)
        if self._router is not None:
            score += 0.2
        
        # Dependencies available (40% total, 10% each)
        if self._dependency_status:
            available_deps = sum(1 for status in self._dependency_status.values() if status == "available")
            score += (available_deps / len(self._dependency_status)) * 0.4
        
        return score

    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for Session 5"""
        try:
            readiness_score = self._calculate_readiness()
            
            # Determine health status
            if not self._initialized:
                health_status = "not_initialized"
            elif readiness_score >= 0.8:
                health_status = "healthy"
            elif readiness_score >= 0.5:
                health_status = "degraded"
            else:
                health_status = "unhealthy"
            
            return {
                "module": self.name,
                "status": health_status,
                "version": self.version,
                "description": self.description,
                "session": "5_complete",
                "readiness_score": round(readiness_score, 2),
                "service_factory": "available" if self._service_factory_ready else "unavailable",
                "dependencies": self._dependency_status,
                "generator_integration": self._generator_status,
                "router_status": "loaded" if self._router else "missing",
                "features": [
                    "integrated_content_generation",
                    "intelligence_engine_integration", 
                    "service_factory_pattern",
                    "database_session_management",
                    "email_sequence_generation",
                    "social_media_content_creation",
                    "ad_copy_generation",
                    "blog_content_creation",
                    "template_management",
                    "railway_compatible",
                    "session_5_ready"
                ],
                "capabilities": {
                    "content_types": ["email", "social_media", "ad_copy", "blog"],
                    "ai_integration": self._generator_status.get("existing_generators", {}),
                    "ultra_cheap_ai": self._generator_status.get("ultra_cheap_ai_enabled", False),
                    "factory_pattern": self._service_factory_ready,
                    "end_to_end_workflow": readiness_score >= 0.8
                }
            }
        except Exception as e:
            return {
                "module": self.name,
                "status": "error",
                "error": str(e),
                "version": self.version,
                "session": "5_error"
            }
    
    def get_api_router(self) -> APIRouter:
        """Get the API router for this module"""
        if self._router is None:
            # Create emergency fallback router
            logger.warning("Creating emergency fallback router for content module")
            return self._create_fallback_router()
        
        return self._router
    
    async def shutdown(self) -> bool:
        """Shutdown the content module"""
        try:
            logger.info(f"Shutting down {self.name} module...")
            
            # Clean up any resources
            self._generator_status = {}
            self._dependency_status = {}
            self._service_factory_ready = False
            self._initialized = False
            
            logger.info(f"{self.name} module shutdown complete")
            return True
            
        except Exception as e:
            logger.error(f"{self.name} module shutdown error: {e}")
            return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive module metrics"""
        try:
            readiness_score = self._calculate_readiness()
            
            metrics = {
                "module": self.name,
                "version": self.version,
                "initialized": self._initialized,
                "readiness_score": readiness_score,
                "service_factory_ready": self._service_factory_ready,
                "session": "5_complete",
                "generators": self._generator_status,
                "dependencies": self._dependency_status,
                "dependency_count": len(self._dependency_status),
                "healthy_dependencies": sum(
                    1 for status in self._dependency_status.values() 
                    if status == "available"
                ),
                "router_loaded": self._router is not None,
                "operational_level": (
                    "full" if readiness_score >= 0.8 else
                    "partial" if readiness_score >= 0.5 else
                    "minimal"
                )
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get {self.name} module metrics: {e}")
            return {
                "module": self.name,
                "error": str(e),
                "version": self.version
            }
    
    async def validate_session_5_completion(self) -> Dict[str, Any]:
        """Validate Session 5 completion status"""
        try:
            validation_results = {}
            
            # Test service factory integration
            try:
                from src.core.factories.service_factory import ServiceFactory
                async with ServiceFactory.create_named_service("integrated_content") as service:
                    validation_results["service_factory_integration"] = True
            except Exception as e:
                validation_results["service_factory_integration"] = False
                validation_results["service_factory_error"] = str(e)
            
            # Test database session management
            try:
                from src.core.database.session import AsyncSessionManager
                async with AsyncSessionManager.get_session() as db:
                    validation_results["database_session_management"] = True
            except Exception as e:
                validation_results["database_session_management"] = False
                validation_results["database_error"] = str(e)
            
            # Test content generation capability - FIXED: Safe access
            try:
                if validation_results.get("service_factory_integration"):
                    async with ServiceFactory.create_named_service("integrated_content") as service:
                        status_result = service.get_generator_status()
                        
                        # Handle both list and dict responses safely
                        if isinstance(status_result, list):
                            total_available = len(status_result)
                        elif isinstance(status_result, dict):
                            total_available = status_result.get("total_available", 0)
                        else:
                            total_available = 0
                        
                        validation_results["content_generation_capability"] = total_available > 0
                else:
                    validation_results["content_generation_capability"] = False
            except Exception as e:
                validation_results["content_generation_capability"] = False
                validation_results["content_generation_error"] = str(e)
            
            # Calculate overall Session 5 readiness
            core_requirements = [
                validation_results.get("service_factory_integration", False),
                validation_results.get("database_session_management", False),
                validation_results.get("content_generation_capability", False)
            ]
            
            session_5_ready = all(core_requirements)
            completion_percentage = sum(core_requirements) / len(core_requirements) * 100
            
            return {
                "session_5_validation": {
                    "ready": session_5_ready,
                    "completion_percentage": round(completion_percentage, 1),
                    "core_requirements": validation_results,
                    "next_steps": [
                        "Session 6: Storage & Media Module" if session_5_ready else "Fix Session 5 issues",
                        "Load testing" if session_5_ready else "Service integration fixes",
                        "Production optimization" if session_5_ready else "Dependency resolution"
                    ]
                }
            }
            
        except Exception as e:
            return {
                "session_5_validation": {
                    "ready": False,
                    "error": str(e),
                    "completion_percentage": 0
                }
            }

# Global Content Module instance
content_module = ContentModule()