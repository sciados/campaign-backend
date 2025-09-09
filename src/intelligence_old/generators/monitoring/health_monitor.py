# src/intelligence/generators/monitoring/health_monitor.py
"""
ENHANCED HEALTH MONITORING SYSTEM
🏥 Real-time health monitoring for all generators
📊 Performance metrics and analytics
🚨 Proactive alerting and auto-recovery
🔧 Self-healing capabilities
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import aiohttp

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"
    RECOVERING = "recovering"

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class HealthMetric:
    """Individual health metric"""
    name: str
    value: float
    unit: str
    threshold_warning: float
    threshold_critical: float
    timestamp: datetime
    status: HealthStatus

@dataclass
class GeneratorHealthReport:
    """Comprehensive health report for a generator"""
    generator_name: str
    status: HealthStatus
    uptime_percentage: float
    response_time_ms: float
    success_rate: float
    error_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float
    active_generations: int
    queue_size: int
    last_error: Optional[str]
    metrics: List[HealthMetric]
    alerts: List[Dict[str, Any]]
    recovery_actions: List[str]
    timestamp: datetime

@dataclass
class SystemHealthSummary:
    """Overall system health summary"""
    overall_status: HealthStatus
    healthy_generators: int
    degraded_generators: int
    down_generators: int
    total_generations: int
    total_errors: int
    average_response_time: float
    cost_efficiency_score: float
    alerts_count: int
    critical_alerts_count: int
    last_updated: datetime

class HealthMonitor:
    """Enhanced health monitoring system with proactive alerting"""
    
    def __init__(self):
        self.generator_health: Dict[str, GeneratorHealthReport] = {}
        self.system_metrics: Dict[str, List[float]] = {}
        self.alert_handlers: List[Callable] = []
        self.recovery_handlers: Dict[str, Callable] = {}
        
        # Monitoring configuration
        self.monitoring_interval = 30  # seconds
        self.metric_retention_hours = 24
        self.alert_cooldown_minutes = 5
        
        # Thresholds
        self.thresholds = {
            "response_time_warning": 5000,  # ms
            "response_time_critical": 10000,  # ms
            "success_rate_warning": 0.8,
            "success_rate_critical": 0.6,
            "error_rate_warning": 0.1,
            "error_rate_critical": 0.2,
            "memory_warning": 500,  # MB
            "memory_critical": 1000,  # MB
            "cpu_warning": 70,  # percent
            "cpu_critical": 90  # percent
        }
        
        # State tracking
        self.monitoring_active = False
        self.last_alerts: Dict[str, datetime] = {}
        self.recovery_attempts: Dict[str, int] = {}
        self.performance_history: Dict[str, List[Dict]] = {}
        
        logger.info("🏥 Enhanced Health Monitor initialized")
    
    async def start_monitoring(self):
        """Start continuous health monitoring"""
        
        if self.monitoring_active:
            logger.warning("⚠️ Health monitoring already active")
            return
        
        self.monitoring_active = True
        logger.info("🟢 Starting health monitoring...")
        
        # Start monitoring tasks
        await asyncio.gather(
            self._continuous_health_check(),
            self._metric_collection_loop(),
            self._alert_processing_loop(),
            self._cleanup_old_data_loop(),
            return_exceptions=True
        )
    
    async def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring_active = False
        logger.info("🛑 Health monitoring stopped")
    
    async def _continuous_health_check(self):
        """Continuous health checking loop"""
        
        while self.monitoring_active:
            try:
                # Get all registered generators
                from ..factory import get_global_enhanced_factory
                factory = get_global_enhanced_factory()
                
                # Check health of all generators
                for generator_type in factory.get_available_generators():
                    await self._check_generator_health(generator_type, factory)
                
                # Update system health summary
                await self._update_system_health()
                
            except Exception as e:
                logger.error(f"❌ Health check loop error: {e}")
            
            await asyncio.sleep(self.monitoring_interval)
    
    async def _check_generator_health(self, generator_type: str, factory):
        """Check health of individual generator"""
        
        start_time = time.time()
        
        try:
            # Get generator instance
            generator = await factory.get_generator(generator_type)
            
            # Collect basic metrics
            response_time = (time.time() - start_time) * 1000
            
            # Get performance data from factory
            factory_status = factory.get_factory_status()
            perf_data = factory_status["generator_performance"].get(generator_type, {})
            
            success_rate = perf_data.get("success_rate", 100.0) / 100.0
            error_count = perf_data.get("total_generations", 0) - perf_data.get("successful_generations", 0)
            total_generations = perf_data.get("total_generations", 0)
            error_rate = error_count / max(total_generations, 1)
            
            # Check if generator has custom health check
            custom_health = None
            if hasattr(generator, 'health_check'):
                try:
                    custom_health = await generator.health_check()
                except Exception as e:
                    logger.debug(f"Custom health check failed for {generator_type}: {e}")
            
            # Collect system metrics (simplified)
            memory_usage = self._get_memory_usage(generator_type)
            cpu_usage = self._get_cpu_usage(generator_type)
            active_generations = self._get_active_generations(generator_type)
            queue_size = self._get_queue_size(generator_type)
            
            # Create health metrics
            metrics = [
                HealthMetric(
                    name="response_time",
                    value=response_time,
                    unit="ms",
                    threshold_warning=self.thresholds["response_time_warning"],
                    threshold_critical=self.thresholds["response_time_critical"],
                    timestamp=datetime.now(timezone.utc),
                    status=self._evaluate_metric_status(response_time, self.thresholds["response_time_warning"], self.thresholds["response_time_critical"], inverted=True)
                ),
                HealthMetric(
                    name="success_rate",
                    value=success_rate,
                    unit="percent",
                    threshold_warning=self.thresholds["success_rate_warning"],
                    threshold_critical=self.thresholds["success_rate_critical"],
                    timestamp=datetime.now(timezone.utc),
                    status=self._evaluate_metric_status(success_rate, self.thresholds["success_rate_warning"], self.thresholds["success_rate_critical"])
                ),
                HealthMetric(
                    name="error_rate",
                    value=error_rate,
                    unit="percent",
                    threshold_warning=self.thresholds["error_rate_warning"],
                    threshold_critical=self.thresholds["error_rate_critical"],
                    timestamp=datetime.now(timezone.utc),
                    status=self._evaluate_metric_status(error_rate, self.thresholds["error_rate_warning"], self.thresholds["error_rate_critical"], inverted=True)
                )
            ]
            
            # Determine overall status
            metric_statuses = [m.status for m in metrics]
            if HealthStatus.DOWN in metric_statuses:
                overall_status = HealthStatus.DOWN
            elif HealthStatus.CRITICAL in metric_statuses:
                overall_status = HealthStatus.DEGRADED
            elif HealthStatus.DEGRADED in metric_statuses:
                overall_status = HealthStatus.DEGRADED
            else:
                overall_status = HealthStatus.HEALTHY
            
            # Get recent errors
            last_error = None
            error_analytics = factory_status.get("error_analytics", {}).get(generator_type, {})
            recent_errors = error_analytics.get("last_errors", [])
            if recent_errors:
                last_error = recent_errors[-1].get("error_message", "Unknown error")
            
            # Generate alerts
            alerts = await self._generate_alerts(generator_type, metrics, overall_status)
            
            # Generate recovery actions
            recovery_actions = self._generate_recovery_actions(generator_type, overall_status, metrics)
            
            # Calculate uptime
            uptime_percentage = self._calculate_uptime(generator_type, success_rate)
            
            # Create health report
            health_report = GeneratorHealthReport(
                generator_name=generator_type,
                status=overall_status,
                uptime_percentage=uptime_percentage,
                response_time_ms=response_time,
                success_rate=success_rate * 100,
                error_rate=error_rate * 100,
                memory_usage_mb=memory_usage,
                cpu_usage_percent=cpu_usage,
                active_generations=active_generations,
                queue_size=queue_size,
                last_error=last_error,
                metrics=metrics,
                alerts=alerts,
                recovery_actions=recovery_actions,
                timestamp=datetime.now(timezone.utc)
            )
            
            # Store health report
            self.generator_health[generator_type] = health_report
            
            # Store performance history
            if generator_type not in self.performance_history:
                self.performance_history[generator_type] = []
            
            self.performance_history[generator_type].append({
                "timestamp": datetime.now(timezone.utc),
                "response_time": response_time,
                "success_rate": success_rate,
                "error_rate": error_rate,
                "status": overall_status.value
            })
            
            # Keep only recent history
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.metric_retention_hours)
            self.performance_history[generator_type] = [
                entry for entry in self.performance_history[generator_type]
                if entry["timestamp"] > cutoff_time
            ]
            
            # Trigger alerts if needed
            for alert in alerts:
                await self._process_alert(alert)
            
            # Attempt recovery if needed
            if overall_status in [HealthStatus.DOWN, HealthStatus.DEGRADED]:
                await self._attempt_recovery(generator_type, overall_status)
                
        except Exception as e:
            logger.error(f"❌ Health check failed for {generator_type}: {e}")
            
            # Create error health report
            error_report = GeneratorHealthReport(
                generator_name=generator_type,
                status=HealthStatus.DOWN,
                uptime_percentage=0.0,
                response_time_ms=0.0,
                success_rate=0.0,
                error_rate=100.0,
                memory_usage_mb=0.0,
                cpu_usage_percent=0.0,
                active_generations=0,
                queue_size=0,
                last_error=str(e),
                metrics=[],
                alerts=[{
                    "level": AlertLevel.CRITICAL.value,
                    "message": f"Health check failed: {str(e)}",
                    "generator": generator_type,
                    "timestamp": datetime.now(timezone.utc)
                }],
                recovery_actions=["restart_generator", "check_dependencies"],
                timestamp=datetime.now(timezone.utc)
            )
            
            self.generator_health[generator_type] = error_report
    
    def _evaluate_metric_status(self, value: float, warning_threshold: float, critical_threshold: float, inverted: bool = False) -> HealthStatus:
        """Evaluate metric status based on thresholds"""
        
        if inverted:
            # For metrics where higher values are worse (like response time, error rate)
            if value >= critical_threshold:
                return HealthStatus.DOWN
            elif value >= warning_threshold:
                return HealthStatus.DEGRADED
            else:
                return HealthStatus.HEALTHY
        else:
            # For metrics where lower values are worse (like success rate)
            if value <= critical_threshold:
                return HealthStatus.DOWN
            elif value <= warning_threshold:
                return HealthStatus.DEGRADED
            else:
                return HealthStatus.HEALTHY
    
    async def _generate_alerts(self, generator_type: str, metrics: List[HealthMetric], status: HealthStatus) -> List[Dict[str, Any]]:
        """Generate alerts based on health metrics"""
        
        alerts = []
        current_time = datetime.now(timezone.utc)
        
        # Check alert cooldown
        last_alert_key = f"{generator_type}_status"
        if last_alert_key in self.last_alerts:
            time_since_last = (current_time - self.last_alerts[last_alert_key]).total_seconds() / 60
            if time_since_last < self.alert_cooldown_minutes:
                return alerts  # Skip alerts during cooldown
        
        # Generate status alerts
        if status == HealthStatus.DOWN:
            alerts.append({
                "level": AlertLevel.CRITICAL.value,
                "type": "generator_down",
                "message": f"Generator {generator_type} is DOWN",
                "generator": generator_type,
                "timestamp": current_time,
                "requires_action": True
            })
            self.last_alerts[last_alert_key] = current_time
            
        elif status == HealthStatus.DEGRADED:
            alerts.append({
                "level": AlertLevel.WARNING.value,
                "type": "generator_degraded",
                "message": f"Generator {generator_type} performance is DEGRADED",
                "generator": generator_type,
                "timestamp": current_time,
                "requires_action": True
            })
            self.last_alerts[last_alert_key] = current_time
        
        # Generate metric-specific alerts
        for metric in metrics:
            if metric.status in [HealthStatus.DOWN, HealthStatus.DEGRADED]:
                alert_level = AlertLevel.CRITICAL if metric.status == HealthStatus.DOWN else AlertLevel.WARNING
                
                alerts.append({
                    "level": alert_level.value,
                    "type": "metric_threshold",
                    "message": f"{generator_type} {metric.name} is {metric.status.value}: {metric.value} {metric.unit}",
                    "generator": generator_type,
                    "metric": metric.name,
                    "value": metric.value,
                    "threshold": metric.threshold_critical if metric.status == HealthStatus.DOWN else metric.threshold_warning,
                    "timestamp": current_time,
                    "requires_action": metric.status == HealthStatus.DOWN
                })
        
        return alerts
    
    def _generate_recovery_actions(self, generator_type: str, status: HealthStatus, metrics: List[HealthMetric]) -> List[str]:
        """Generate recovery actions based on health status"""
        
        actions = []
        
        if status == HealthStatus.DOWN:
            actions.extend([
                "restart_generator",
                "check_api_connectivity",
                "verify_authentication",
                "clear_cache",
                "check_system_resources"
            ])
        elif status == HealthStatus.DEGRADED:
            actions.extend([
                "optimize_parameters",
                "clear_queue",
                "reduce_concurrent_requests",
                "check_provider_status"
            ])
        
        # Add metric-specific actions
        for metric in metrics:
            if metric.status in [HealthStatus.DOWN, HealthStatus.DEGRADED]:
                if metric.name == "response_time":
                    actions.append("optimize_request_routing")
                elif metric.name == "success_rate":
                    actions.append("switch_to_backup_provider")
                elif metric.name == "error_rate":
                    actions.append("investigate_error_patterns")
                elif metric.name == "memory_usage":
                    actions.append("garbage_collection")
                elif metric.name == "cpu_usage":
                    actions.append("reduce_processing_load")
        
        return list(set(actions))  # Remove duplicates
    
    async def _attempt_recovery(self, generator_type: str, status: HealthStatus):
        """Attempt automatic recovery actions"""
        
        if generator_type not in self.recovery_attempts:
            self.recovery_attempts[generator_type] = 0
        
        # Limit recovery attempts
        if self.recovery_attempts[generator_type] >= 3:
            logger.warning(f"⚠️ Max recovery attempts reached for {generator_type}")
            return
        
        self.recovery_attempts[generator_type] += 1
        
        try:
            logger.info(f"🔧 Attempting recovery for {generator_type} (attempt {self.recovery_attempts[generator_type]})")
            
            # Get factory instance
            from ..factory import get_global_enhanced_factory
            factory = get_global_enhanced_factory()
            
            if status == HealthStatus.DOWN:
                # Restart generator (clear cache)
                await factory.invalidate_generator_cache(generator_type)
                logger.info(f"🔄 Restarted {generator_type}")
                
            elif status == HealthStatus.DEGRADED:
                # Optimize generator performance
                await factory.optimize_factory_performance()
                logger.info(f"⚡ Optimized {generator_type}")
            
            # Reset attempt counter on successful recovery check
            await asyncio.sleep(30)  # Wait before checking
            current_health = self.generator_health.get(generator_type)
            if current_health and current_health.status == HealthStatus.HEALTHY:
                self.recovery_attempts[generator_type] = 0
                logger.info(f"✅ Recovery successful for {generator_type}")
                
        except Exception as e:
            logger.error(f"❌ Recovery failed for {generator_type}: {e}")
    
    def _calculate_uptime(self, generator_type: str, current_success_rate: float) -> float:
        """Calculate uptime percentage based on historical data"""
        
        if generator_type not in self.performance_history:
            return current_success_rate * 100
        
        history = self.performance_history[generator_type]
        if not history:
            return current_success_rate * 100
        
        # Calculate uptime from last 24 hours
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        recent_history = [entry for entry in history if entry["timestamp"] > cutoff_time]
        
        if not recent_history:
            return current_success_rate * 100
        
        healthy_periods = len([entry for entry in recent_history if entry["status"] == HealthStatus.HEALTHY.value])
        total_periods = len(recent_history)
        
        return (healthy_periods / total_periods) * 100
    
    def _get_memory_usage(self, generator_type: str) -> float:
        """Get memory usage for generator (simplified implementation)"""
        # In a real implementation, this would measure actual memory usage
        # For now, return a simulated value based on generator activity
        base_memory = 50  # MB
        activity_factor = len(self.performance_history.get(generator_type, [])) * 0.1
        return base_memory + activity_factor
    
    def _get_cpu_usage(self, generator_type: str) -> float:
        """Get CPU usage for generator (simplified implementation)"""
        # Simulated CPU usage based on recent activity
        if generator_type not in self.performance_history:
            return 10.0
        
        recent_activity = len([
            entry for entry in self.performance_history[generator_type]
            if entry["timestamp"] > datetime.now(timezone.utc) - timedelta(minutes=5)
        ])
        
        return min(90.0, 10.0 + recent_activity * 2.0)
    
    def _get_active_generations(self, generator_type: str) -> int:
        """Get number of active generations (simplified implementation)"""
        # Simulated active generations
        import random
        return random.randint(0, 3)
    
    def _get_queue_size(self, generator_type: str) -> int:
        """Get queue size for generator (simplified implementation)"""
        # Simulated queue size
        import random
        return random.randint(0, 5)
    
    async def _metric_collection_loop(self):
        """Collect and aggregate system metrics"""
        
        while self.monitoring_active:
            try:
                # Collect system-wide metrics
                total_response_time = []
                total_success_rates = []
                total_errors = 0
                total_generations = 0
                
                for generator_type, health_report in self.generator_health.items():
                    total_response_time.append(health_report.response_time_ms)
                    total_success_rates.append(health_report.success_rate)
                    total_errors += health_report.error_rate
                    total_generations += 1  # Simplified
                
                # Calculate system metrics
                if total_response_time:
                    avg_response_time = statistics.mean(total_response_time)
                    self._store_system_metric("avg_response_time", avg_response_time)
                
                if total_success_rates:
                    avg_success_rate = statistics.mean(total_success_rates)
                    self._store_system_metric("avg_success_rate", avg_success_rate)
                
                if total_generations > 0:
                    overall_error_rate = total_errors / total_generations
                    self._store_system_metric("overall_error_rate", overall_error_rate)
                
                # Calculate cost efficiency (simplified)
                cost_efficiency = self._calculate_cost_efficiency()
                self._store_system_metric("cost_efficiency", cost_efficiency)
                
            except Exception as e:
                logger.error(f"❌ Metric collection error: {e}")
            
            await asyncio.sleep(60)  # Collect metrics every minute
    
    def _store_system_metric(self, metric_name: str, value: float):
        """Store system metric with timestamp"""
        
        if metric_name not in self.system_metrics:
            self.system_metrics[metric_name] = []
        
        self.system_metrics[metric_name].append({
            "value": value,
            "timestamp": datetime.now(timezone.utc)
        })
        
        # Keep only recent metrics
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.metric_retention_hours)
        self.system_metrics[metric_name] = [
            entry for entry in self.system_metrics[metric_name]
            if entry["timestamp"] > cutoff_time
        ]
    
    def _calculate_cost_efficiency(self) -> float:
        """Calculate cost efficiency score (0-100)"""
        
        try:
            from ..factory import get_global_enhanced_factory
            factory = get_global_enhanced_factory()
            status = factory.get_factory_status()
            
            total_cost = status["cost_performance"]["total_cost"]
            total_savings = status["cost_performance"]["total_savings"]
            
            if total_cost + total_savings == 0:
                return 100.0
            
            efficiency = (total_savings / (total_cost + total_savings)) * 100
            return min(100.0, max(0.0, efficiency))
            
        except Exception:
            return 75.0  # Default reasonable efficiency
    
    async def _alert_processing_loop(self):
        """Process and handle alerts"""
        
        while self.monitoring_active:
            try:
                # Collect all current alerts
                all_alerts = []
                for health_report in self.generator_health.values():
                    all_alerts.extend(health_report.alerts)
                
                # Process critical alerts
                critical_alerts = [alert for alert in all_alerts if alert["level"] == AlertLevel.CRITICAL.value]
                
                for alert in critical_alerts:
                    await self._handle_critical_alert(alert)
                
                # Send alert notifications
                if all_alerts:
                    await self._send_alert_notifications(all_alerts)
                
            except Exception as e:
                logger.error(f"❌ Alert processing error: {e}")
            
            await asyncio.sleep(30)  # Process alerts every 30 seconds
    
    async def _handle_critical_alert(self, alert: Dict[str, Any]):
        """Handle critical alerts with immediate action"""
        
        generator_name = alert.get("generator")
        alert_type = alert.get("type")
        
        if alert_type == "generator_down":
            # Immediate recovery attempt for down generators
            await self._attempt_recovery(generator_name, HealthStatus.DOWN)
        
        elif alert_type == "metric_threshold":
            metric_name = alert.get("metric")
            if metric_name == "error_rate" and alert.get("value", 0) > 50:
                # High error rate - switch to backup provider
                logger.warning(f"🚨 High error rate for {generator_name}, initiating provider switch")
                # This would trigger provider switching logic
    
    async def _send_alert_notifications(self, alerts: List[Dict[str, Any]]):
        """Send alert notifications to registered handlers"""
        
        for handler in self.alert_handlers:
            try:
                await handler(alerts)
            except Exception as e:
                logger.error(f"❌ Alert handler failed: {e}")
    
    async def _cleanup_old_data_loop(self):
        """Clean up old monitoring data"""
        
        while self.monitoring_active:
            try:
                cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.metric_retention_hours)
                
                # Clean up performance history
                for generator_type in list(self.performance_history.keys()):
                    self.performance_history[generator_type] = [
                        entry for entry in self.performance_history[generator_type]
                        if entry["timestamp"] > cutoff_time
                    ]
                
                # Clean up system metrics
                for metric_name in list(self.system_metrics.keys()):
                    self.system_metrics[metric_name] = [
                        entry for entry in self.system_metrics[metric_name]
                        if entry["timestamp"] > cutoff_time
                    ]
                
                # Clean up old alerts from last_alerts
                alert_cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
                self.last_alerts = {
                    key: timestamp for key, timestamp in self.last_alerts.items()
                    if timestamp > alert_cutoff
                }
                
                logger.debug("🧹 Cleaned up old monitoring data")
                
            except Exception as e:
                logger.error(f"❌ Data cleanup error: {e}")
            
            await asyncio.sleep(3600)  # Clean up every hour
    
    async def _update_system_health(self):
        """Update overall system health summary"""
        
        if not self.generator_health:
            return
        
        # Count generators by status
        status_counts = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 0,
            HealthStatus.DOWN: 0,
            HealthStatus.UNKNOWN: 0,
            HealthStatus.RECOVERING: 0
        }
        
        total_response_times = []
        total_alerts = 0
        critical_alerts = 0
        
        for health_report in self.generator_health.values():
            status_counts[health_report.status] += 1
            total_response_times.append(health_report.response_time_ms)
            total_alerts += len(health_report.alerts)
            critical_alerts += len([a for a in health_report.alerts if a["level"] == AlertLevel.CRITICAL.value])
        
        # Determine overall system status
        if status_counts[HealthStatus.DOWN] > 0:
            overall_status = HealthStatus.DOWN
        elif status_counts[HealthStatus.DEGRADED] > 0:
            overall_status = HealthStatus.DEGRADED
        elif status_counts[HealthStatus.RECOVERING] > 0:
            overall_status = HealthStatus.RECOVERING
        else:
            overall_status = HealthStatus.HEALTHY
        
        # Calculate averages
        avg_response_time = statistics.mean(total_response_times) if total_response_times else 0
        cost_efficiency = self._calculate_cost_efficiency()
        
        # Get total counts from factory
        try:
            from ..factory import get_global_enhanced_factory
            factory = get_global_enhanced_factory()
            factory_status = factory.get_factory_status()
            total_generations = factory_status["cost_performance"]["total_generations"]
            total_errors = sum(
                perf.get("total_generations", 0) - perf.get("successful_generations", 0)
                for perf in factory_status["generator_performance"].values()
            )
        except Exception:
            total_generations = 0
            total_errors = 0
        
        # Create system health summary
        self.system_health_summary = SystemHealthSummary(
            overall_status=overall_status,
            healthy_generators=status_counts[HealthStatus.HEALTHY],
            degraded_generators=status_counts[HealthStatus.DEGRADED],
            down_generators=status_counts[HealthStatus.DOWN],
            total_generations=total_generations,
            total_errors=total_errors,
            average_response_time=avg_response_time,
            cost_efficiency_score=cost_efficiency,
            alerts_count=total_alerts,
            critical_alerts_count=critical_alerts,
            last_updated=datetime.now(timezone.utc)
        )
    
    # Public API methods
    
    def add_alert_handler(self, handler: Callable):
        """Add alert handler function"""
        self.alert_handlers.append(handler)
        logger.info(f"📢 Added alert handler: {handler.__name__}")
    
    def add_recovery_handler(self, generator_type: str, handler: Callable):
        """Add custom recovery handler for generator"""
        self.recovery_handlers[generator_type] = handler
        logger.info(f"🔧 Added recovery handler for {generator_type}")
    
    def get_generator_health(self, generator_type: str = None) -> Dict[str, GeneratorHealthReport]:
        """Get health reports for generators"""
        
        if generator_type:
            if generator_type in self.generator_health:
                return {generator_type: self.generator_health[generator_type]}
            else:
                return {}
        
        return self.generator_health.copy()
    
    def get_system_health_summary(self) -> Optional[SystemHealthSummary]:
        """Get overall system health summary"""
        return getattr(self, 'system_health_summary', None)
    
    def get_performance_trends(self, generator_type: str, hours: int = 24) -> Dict[str, List[float]]:
        """Get performance trends for generator"""
        
        if generator_type not in self.performance_history:
            return {}
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        recent_history = [
            entry for entry in self.performance_history[generator_type]
            if entry["timestamp"] > cutoff_time
        ]
        
        trends = {
            "timestamps": [entry["timestamp"].isoformat() for entry in recent_history],
            "response_times": [entry["response_time"] for entry in recent_history],
            "success_rates": [entry["success_rate"] for entry in recent_history],
            "error_rates": [entry["error_rate"] for entry in recent_history]
        }
        
        return trends
    
    def get_system_metrics(self, metric_name: str = None, hours: int = 24) -> Dict[str, List[Dict]]:
        """Get system metrics"""
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        if metric_name:
            if metric_name in self.system_metrics:
                recent_metrics = [
                    entry for entry in self.system_metrics[metric_name]
                    if entry["timestamp"] > cutoff_time
                ]
                return {metric_name: recent_metrics}
            else:
                return {}
        
        # Return all metrics
        result = {}
        for name, metrics_list in self.system_metrics.items():
            recent_metrics = [
                entry for entry in metrics_list
                if entry["timestamp"] > cutoff_time
            ]
            result[name] = recent_metrics
        
        return result
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get monitoring system status"""
        
        return {
            "monitoring_active": self.monitoring_active,
            "monitored_generators": len(self.generator_health),
            "system_metrics_tracked": len(self.system_metrics),
            "alert_handlers": len(self.alert_handlers),
            "recovery_handlers": len(self.recovery_handlers),
            "monitoring_interval": self.monitoring_interval,
            "metric_retention_hours": self.metric_retention_hours,
            "thresholds": self.thresholds,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    
    async def force_health_check(self, generator_type: str = None):
        """Force immediate health check"""
        
        try:
            from ..factory import get_global_enhanced_factory
            factory = get_global_enhanced_factory()
            
            if generator_type:
                await self._check_generator_health(generator_type, factory)
                logger.info(f"🔍 Forced health check for {generator_type}")
            else:
                for gen_type in factory.get_available_generators():
                    await self._check_generator_health(gen_type, factory)
                logger.info("🔍 Forced health check for all generators")
            
            await self._update_system_health()
            
        except Exception as e:
            logger.error(f"❌ Forced health check failed: {e}")


# Global health monitor instance
_global_health_monitor = None

async def get_health_monitor() -> HealthMonitor:
    """Get global health monitor instance"""
    global _global_health_monitor
    
    if _global_health_monitor is None:
        _global_health_monitor = HealthMonitor()
    
    return _global_health_monitor

async def start_health_monitoring():
    """Start health monitoring system"""
    monitor = await get_health_monitor()
    await monitor.start_monitoring()

async def stop_health_monitoring():
    """Stop health monitoring system"""
    global _global_health_monitor
    if _global_health_monitor:
        await _global_health_monitor.stop_monitoring()

# Convenience functions
async def get_generator_health_report(generator_type: str = None) -> Dict[str, Any]:
    """Get generator health report"""
    monitor = await get_health_monitor()
    health_reports = monitor.get_generator_health(generator_type)
    
    return {
        gen_type: asdict(report) for gen_type, report in health_reports.items()
    }

async def get_system_health_dashboard() -> Dict[str, Any]:
    """Get system health dashboard data"""
    monitor = await get_health_monitor()
    
    system_summary = monitor.get_system_health_summary()
    generator_health = monitor.get_generator_health()
    monitoring_status = monitor.get_monitoring_status()
    
    return {
        "system_summary": asdict(system_summary) if system_summary else None,
        "generator_health": {
            gen_type: asdict(report) for gen_type, report in generator_health.items()
        },
        "monitoring_status": monitoring_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

async def force_generator_health_check(generator_type: str = None):
    """Force health check for generator(s)"""
    monitor = await get_health_monitor()
    await monitor.force_health_check(generator_type)

# Example alert handler
async def log_alert_handler(alerts: List[Dict[str, Any]]):
    """Example alert handler that logs alerts"""
    for alert in alerts:
        level = alert["level"].upper()
        generator = alert.get("generator", "system")
        message = alert["message"]
        timestamp = alert["timestamp"]
        
        if level == "CRITICAL":
            logger.critical(f"🚨 [{level}] {generator}: {message} at {timestamp}")
        elif level == "WARNING":
            logger.warning(f"⚠️ [{level}] {generator}: {message} at {timestamp}")
        else:
            logger.info(f"ℹ️ [{level}] {generator}: {message} at {timestamp}")

# CLI interface for health monitoring
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Health Monitoring System")
    parser.add_argument("--start", action="store_true", help="Start health monitoring")
    parser.add_argument("--status", action="store_true", help="Show monitoring status")
    parser.add_argument("--health", help="Show health for specific generator")
    parser.add_argument("--dashboard", action="store_true", help="Show health dashboard")
    parser.add_argument("--check", help="Force health check for generator")
    args = parser.parse_args()
    
    async def main():
        if args.start:
            print("🟢 Starting health monitoring...")
            await start_health_monitoring()
        
        elif args.status:
            monitor = await get_health_monitor()
            status = monitor.get_monitoring_status()
            print(json.dumps(status, indent=2, default=str))
        
        elif args.health:
            health_report = await get_generator_health_report(args.health)
            print(json.dumps(health_report, indent=2, default=str))
        
        elif args.dashboard:
            dashboard = await get_system_health_dashboard()
            print(json.dumps(dashboard, indent=2, default=str))
        
        elif args.check:
            await force_generator_health_check(args.check)
            print(f"✅ Health check completed for {args.check}")
        
        else:
            parser.print_help()
    
    asyncio.run(main())