# =====================================
# File: src/core/health/metrics.py
# =====================================

"""
System metrics collection for CampaignForge.

Provides performance monitoring and usage statistics
for Railway deployment monitoring.
"""

import psutil
import time
from typing import Dict, Any
from datetime import datetime
import logging
from fastapi import FastAPI

logger = logging.getLogger(__name__)

class MetricsCollector:
    """System metrics collection and monitoring."""
    
    def __init__(self):
        self.start_time = time.time()
        self._cache_hits = 0
        self._cache_misses = 0
        self._request_count = 0
        self._error_count = 0
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Collect comprehensive system metrics.
        
        Returns:
            Dict[str, Any]: System performance metrics
        """
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Process metrics
            process = psutil.Process()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "uptime_seconds": time.time() - self.start_time,
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                },
                "memory": {
                    "total_bytes": memory.total,
                    "available_bytes": memory.available,
                    "used_bytes": memory.used,
                    "percent": memory.percent,
                },
                "disk": {
                    "total_bytes": disk.total,
                    "free_bytes": disk.free,
                    "used_bytes": disk.used,
                    "percent": (disk.used / disk.total) * 100,
                },
                "process": {
                    "cpu_percent": process.cpu_percent(),
                    "memory_bytes": process.memory_info().rss,
                    "threads": process.num_threads(),
                    "connections": len(process.connections()),
                },
            }
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
            }
    
    def get_application_metrics(self) -> Dict[str, Any]:
        """
        Collect application-specific metrics.
        
        Returns:
            Dict[str, Any]: Application performance metrics
        """
        cache_hit_rate = 0
        if self._cache_hits + self._cache_misses > 0:
            cache_hit_rate = self._cache_hits / (self._cache_hits + self._cache_misses)
        
        error_rate = 0
        if self._request_count > 0:
            error_rate = self._error_count / self._request_count
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": time.time() - self.start_time,
            "cache_stats": {
                "hits": self._cache_hits,
                "misses": self._cache_misses,
                "hit_rate": cache_hit_rate,
            },
            "request_stats": {
                "total_requests": self._request_count,
                "total_errors": self._error_count,
                "error_rate": error_rate,
            },
        }
    
    def record_cache_hit(self):
        """Record a cache hit."""
        self._cache_hits += 1
    
    def record_cache_miss(self):
        """Record a cache miss."""
        self._cache_misses += 1
    
    def record_request(self):
        """Record an API request."""
        self._request_count += 1
    
    def record_error(self):
        """Record an error."""
        self._error_count += 1
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive performance summary.
        
        Returns:
            Dict[str, Any]: Performance summary
        """
        try:
            system_metrics = self.get_system_metrics()
            app_metrics = self.get_application_metrics()
            
            # Calculate performance score (0-100)
            cpu_score = max(0, 100 - system_metrics.get("cpu", {}).get("percent", 0))
            memory_score = max(0, 100 - system_metrics.get("memory", {}).get("percent", 0))
            cache_score = app_metrics.get("cache_stats", {}).get("hit_rate", 0) * 100
            error_score = max(0, 100 - (app_metrics.get("request_stats", {}).get("error_rate", 0) * 100))
            
            overall_score = (cpu_score + memory_score + cache_score + error_score) / 4
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_performance_score": round(overall_score, 2),
                "component_scores": {
                    "cpu_performance": round(cpu_score, 2),
                    "memory_performance": round(memory_score, 2),
                    "cache_performance": round(cache_score, 2),
                    "error_performance": round(error_score, 2),
                },
                "system": system_metrics,
                "application": app_metrics,
            }
        except Exception as e:
            logger.error(f"Failed to generate performance summary: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
            }


# Global metrics collector
metrics_collector = MetricsCollector()


def initialize_health_checks(app: FastAPI) -> None:
    """
    Initialize health check metrics for the FastAPI application.
    
    Args:
        app (FastAPI): The FastAPI application instance to initialize metrics for.
    """
    try:
        global metrics_collector
        # Ensure metrics collector is initialized
        if not isinstance(metrics_collector, MetricsCollector):
            metrics_collector = MetricsCollector()
            logger.info("Initialized new MetricsCollector instance")
        
        # Attach metrics collector to app state for access in routes
        app.state.metrics_collector = metrics_collector
        logger.info("MetricsCollector attached to FastAPI app state")
        
        # Optionally initialize any background tasks for metrics collection
        # (e.g., periodic metrics refresh, if needed in the future)
        logger.info("Health checks initialization completed")
    except Exception as e:
        logger.error(f"Failed to initialize health checks: {e}")
        raise


def get_system_metrics() -> Dict[str, Any]:
    """
    Get current system metrics.
    
    Returns:
        Dict[str, Any]: System metrics
    """
    return metrics_collector.get_system_metrics()


def get_application_metrics() -> Dict[str, Any]:
    """
    Get current application metrics.
    
    Returns:
        Dict[str, Any]: Application metrics
    """
    return metrics_collector.get_application_metrics()


def get_performance_summary() -> Dict[str, Any]:
    """
    Get comprehensive performance summary.
    
    Returns:
        Dict[str, Any]: Performance summary
    """
    return metrics_collector.get_performance_summary()


def record_cache_hit():
    """Record a cache hit for metrics."""
    metrics_collector.record_cache_hit()


def record_cache_miss():
    """Record a cache miss for metrics."""
    metrics_collector.record_cache_miss()


def record_request():
    """Record an API request for metrics."""
    metrics_collector.record_request()


def record_error():
    """Record an error for metrics."""
    metrics_collector.record_error()