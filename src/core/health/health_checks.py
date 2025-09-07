# =====================================
# File: src/core/health/health_checks.py
# =====================================

"""
Health check system for CampaignForge.

Provides comprehensive health monitoring for database,
external services, and system components.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp
from enum import Enum

from src.core.database.connection import test_database_connection
from src.core.config import settings

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthChecker:
    """Comprehensive health checking system."""
    
    def __init__(self):
        self.checks = {
            "database": self._check_database,
            "ai_discovery_service": self._check_ai_discovery_service,
            "redis": self._check_redis,
            "storage": self._check_storage,
        }
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """
        Run all health checks concurrently.
        
        Returns:
            Dict[str, Any]: Complete health status
        """
        results = {}
        
        # Run checks concurrently
        check_tasks = {
            name: asyncio.create_task(check_func())
            for name, check_func in self.checks.items()
        }
        
        # Wait for all checks to complete
        for name, task in check_tasks.items():
            try:
                results[name] = await asyncio.wait_for(task, timeout=10.0)
            except asyncio.TimeoutError:
                results[name] = {
                    "status": HealthStatus.UNHEALTHY.value,
                    "message": "Health check timed out",
                    "details": {"timeout": True}
                }
            except Exception as e:
                logger.error(f"Health check {name} failed: {e}")
                results[name] = {
                    "status": HealthStatus.UNHEALTHY.value,
                    "message": f"Health check failed: {str(e)}",
                    "details": {"error": str(e)}
                }
        
        # Determine overall status
        overall_status = self._determine_overall_status(results)
        
        return {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": results,
        }
    
    async def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity."""
        try:
            is_connected = await test_database_connection()
            if is_connected:
                return {
                    "status": HealthStatus.HEALTHY.value,
                    "message": "Database connection successful",
                    "details": {"url": settings.DATABASE_URL.split("@")[-1]}  # Hide credentials
                }
            else:
                return {
                    "status": HealthStatus.UNHEALTHY.value,
                    "message": "Database connection failed",
                    "details": {}
                }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY.value,
                "message": f"Database check failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    async def _check_ai_discovery_service(self) -> Dict[str, Any]:
        """Check AI Discovery Service connectivity."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{settings.AI_DISCOVERY_SERVICE_URL}/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        return {
                            "status": HealthStatus.HEALTHY.value,
                            "message": "AI Discovery Service is healthy",
                            "details": {"url": settings.AI_DISCOVERY_SERVICE_URL}
                        }
                    else:
                        return {
                            "status": HealthStatus.DEGRADED.value,
                            "message": f"AI Discovery Service returned status {response.status}",
                            "details": {"status_code": response.status}
                        }
        except Exception as e:
            return {
                "status": HealthStatus.DEGRADED.value,
                "message": f"AI Discovery Service unavailable: {str(e)}",
                "details": {"error": str(e)}
            }
    
    async def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity if configured."""
        if not settings.REDIS_URL:
            return {
                "status": HealthStatus.HEALTHY.value,
                "message": "Redis not configured",
                "details": {"configured": False}
            }
        
        try:
            # Redis check would go here if redis-py is available
            # For now, return healthy since it's optional
            return {
                "status": HealthStatus.HEALTHY.value,
                "message": "Redis check skipped",
                "details": {"configured": True, "checked": False}
            }
        except Exception as e:
            return {
                "status": HealthStatus.DEGRADED.value,
                "message": f"Redis check failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    async def _check_storage(self) -> Dict[str, Any]:
        """Check storage service health."""
        try:
            # Basic check - ensure configuration is present
            if not all([
                settings.CLOUDFLARE_R2_ACCESS_KEY_ID,
                settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY,
                settings.CLOUDFLARE_R2_BUCKET_NAME
            ]):
                return {
                    "status": HealthStatus.UNHEALTHY.value,
                    "message": "Storage configuration incomplete",
                    "details": {"configured": False}
                }
            
            return {
                "status": HealthStatus.HEALTHY.value,
                "message": "Storage configuration valid",
                "details": {
                    "provider": "cloudflare_r2",
                    "bucket": settings.CLOUDFLARE_R2_BUCKET_NAME
                }
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY.value,
                "message": f"Storage check failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    def _determine_overall_status(self, results: Dict[str, Dict[str, Any]]) -> HealthStatus:
        """Determine overall health status from individual checks."""
        statuses = [HealthStatus(result["status"]) for result in results.values()]
        
        if any(status == HealthStatus.UNHEALTHY for status in statuses):
            return HealthStatus.UNHEALTHY
        elif any(status == HealthStatus.DEGRADED for status in statuses):
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY


# Global health checker instance
health_checker = HealthChecker()


async def get_health_status() -> Dict[str, Any]:
    """
    Get current system health status.
    
    Returns:
        Dict[str, Any]: Health status information
    """
    return await health_checker.run_all_checks()