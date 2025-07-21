# src/intelligence/schemas/monitoring_schemas.py
"""
AI MONITORING SCHEMAS - PYDANTIC MODELS
📊 Data structures for AI monitoring and optimization system
🔧 Response models for monitoring API endpoints
✅ Type safety and validation for monitoring data
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum

# Enums for status types
class SystemStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    ERROR = "error"

class ProviderStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DEGRADED = "degraded"
    DOWN = "down"

# Base models
class ProviderInfo(BaseModel):
    """Information about an AI provider"""
    name: str
    status: ProviderStatus
    cost_per_1k: Optional[float] = None
    cost_per_image: Optional[float] = None
    priority: int
    models: List[str] = []
    capabilities: List[str] = []
    last_checked: Optional[datetime] = None
    error_message: Optional[str] = None

class CacheStatus(BaseModel):
    """Cache system status"""
    cached_selections: int
    cache_ttl: int
    hit_rate: Optional[float] = None
    last_updated: Optional[datetime] = None

# Response models
class ProviderStatusResponse(BaseModel):
    """Response for provider status endpoint"""
    status: SystemStatus
    timestamp: datetime
    available_providers: List[ProviderInfo]
    unavailable_providers: List[ProviderInfo]
    monitoring_active: bool
    cache_status: CacheStatus
    total_providers: Optional[int] = None
    system_health_score: Optional[float] = None

class CostAnalyticsResponse(BaseModel):
    """Response for cost analytics endpoint"""
    period_days: int
    total_requests: int
    total_cost: float
    average_cost_per_request: float
    cost_by_provider: Dict[str, Dict[str, Union[int, float]]]
    cost_by_content_type: Dict[str, Dict[str, Union[int, float]]]
    savings_vs_expensive: float
    savings_percentage: float
    top_performing_providers: List[Dict[str, Any]]
    cost_trends: List[Dict[str, Any]]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class OptimizationDecision(BaseModel):
    """Single optimization decision record"""
    timestamp: datetime
    content_type: str
    selected_provider: str
    alternative_providers: List[str]
    decision_factors: Dict[str, Any]
    cost_impact: float
    quality_impact: str
    reasoning: str

class RoutingDecisionResponse(BaseModel):
    """Response for routing decisions endpoint"""
    content_type: str
    current_provider: str
    backup_providers: List[str]
    decision_timestamp: datetime
    decision_reasoning: str
    cost_per_unit: float
    quality_score: float
    expires_at: Optional[datetime] = None
    manual_override: bool = False
    override_reason: Optional[str] = None

class PerformanceMetrics(BaseModel):
    """Performance metrics for a provider"""
    provider_name: str
    content_type: str
    average_response_time: float
    success_rate: float
    quality_score: float
    cost_effectiveness: float
    total_requests: int
    last_benchmark: datetime

class SystemHealthResponse(BaseModel):
    """Response for system health endpoint"""
    overall_status: SystemStatus
    timestamp: datetime
    issues: List[str]
    provider_health: List[Dict[str, Any]]
    monitoring_health: Dict[str, Any]
    routing_health: Dict[str, Any]
    recommendations: List[str]
    uptime_percentage: Optional[float] = None
    last_incident: Optional[datetime] = None

class OptimizationAnalyticsResponse(BaseModel):
    """Response for optimization analytics"""
    analytics_period: str
    total_optimizations: int
    cost_savings_achieved: float
    performance_improvements: Dict[str, float]
    provider_effectiveness: Dict[str, Dict[str, Any]]
    optimization_success_rate: float
    recent_decisions: List[OptimizationDecision]
    trends: Dict[str, List[Dict[str, Any]]]

# Request models
class RoutingOverrideRequest(BaseModel):
    """Request to override routing decision"""
    content_type: str
    provider_name: str
    duration_minutes: int = Field(default=60, ge=1, le=1440)  # 1 minute to 24 hours
    reason: str = "manual_override"
    force_override: bool = False

class OptimizationSettingsRequest(BaseModel):
    """Request to update optimization settings"""
    cost_priority_weight: float = Field(default=0.6, ge=0.0, le=1.0)
    quality_priority_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    speed_priority_weight: float = Field(default=0.1, ge=0.0, le=1.0)
    minimum_quality_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    enable_automatic_fallback: bool = True
    cache_ttl_seconds: int = Field(default=300, ge=60, le=3600)

# Error response models
class MonitoringErrorResponse(BaseModel):
    """Error response for monitoring endpoints"""
    error_type: str
    error_message: str
    timestamp: datetime
    endpoint: str
    suggested_actions: List[str] = []
    support_info: Optional[str] = None

# WebSocket message models
class MonitoringUpdate(BaseModel):
    """WebSocket update message"""
    update_type: str  # "status_change", "cost_update", "performance_alert"
    timestamp: datetime
    data: Dict[str, Any]
    severity: str = "info"  # "info", "warning", "error", "critical"

class ProviderAlert(BaseModel):
    """Alert about provider issues"""
    provider_name: str
    alert_type: str  # "down", "degraded", "rate_limited", "cost_spike"
    message: str
    timestamp: datetime
    severity: str
    affected_content_types: List[str]
    recommended_action: str

# Dashboard models
class DashboardSummary(BaseModel):
    """Summary data for monitoring dashboard"""
    system_status: SystemStatus
    active_providers: int
    total_providers: int
    cost_savings_24h: float
    total_requests_24h: int
    average_response_time: float
    success_rate: float
    alerts_count: int
    last_updated: datetime

class CostTrend(BaseModel):
    """Cost trend data point"""
    date: datetime
    total_cost: float
    request_count: int
    average_cost: float
    primary_provider: str
    savings_vs_baseline: float

class ProviderPerformanceSummary(BaseModel):
    """Provider performance summary"""
    provider_name: str
    total_requests: int
    success_rate: float
    average_cost: float
    average_response_time: float
    quality_score: float
    uptime_percentage: float
    last_used: datetime
    trending: str  # "up", "down", "stable"

# Configuration models
class MonitoringConfig(BaseModel):
    """Monitoring system configuration"""
    monitoring_enabled: bool = True
    monitoring_interval_minutes: int = Field(default=60, ge=5, le=1440)
    cost_tracking_enabled: bool = True
    performance_benchmarking_enabled: bool = True
    automatic_optimization_enabled: bool = True
    alert_thresholds: Dict[str, float] = {
        "error_rate_threshold": 0.05,
        "response_time_threshold": 10.0,
        "cost_spike_threshold": 2.0
    }
    webhook_urls: List[str] = []

# Utility models
class TimeRange(BaseModel):
    """Time range for analytics queries"""
    start_date: datetime
    end_date: datetime
    
    def validate_range(self):
        if self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")
        return self

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=1000)
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

# Export all models for easy importing
__all__ = [
    "SystemStatus",
    "ProviderStatus", 
    "ProviderInfo",
    "CacheStatus",
    "ProviderStatusResponse",
    "CostAnalyticsResponse",
    "OptimizationDecision",
    "RoutingDecisionResponse",
    "PerformanceMetrics",
    "SystemHealthResponse",
    "OptimizationAnalyticsResponse",
    "RoutingOverrideRequest",
    "OptimizationSettingsRequest",
    "MonitoringErrorResponse",
    "MonitoringUpdate",
    "ProviderAlert",
    "DashboardSummary",
    "CostTrend",
    "ProviderPerformanceSummary",
    "MonitoringConfig",
    "TimeRange",
    "PaginationParams"
]