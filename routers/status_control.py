#!/usr/bin/env python3
"""
Status Control API Router
Provides comprehensive status monitoring and control endpoints for the crypto trading platform.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

# Import status control system
from utils.status_control import (
    status_control,
    get_system_status,
    get_component_status,
    get_all_components_status,
    create_status_alert,
    ComponentHealth,
    ComponentStatus,
    ServiceType,
)

router = APIRouter(prefix="/status", tags=["status"])


# Pydantic models for API responses
class SystemStatusResponse(BaseModel):
    """System status response model."""

    status: str
    uptime_seconds: float
    components_online: int
    total_components: int
    health_percentage: float
    last_check: str
    alerts_count: int


class ComponentStatusResponse(BaseModel):
    """Component status response model."""

    name: str
    service_type: str
    status: str
    last_check: str
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any]


class AlertResponse(BaseModel):
    """Alert response model."""

    id: str
    component: str
    severity: str
    message: str
    timestamp: str
    resolved: bool
    metadata: Dict[str, Any]


class MetricsResponse(BaseModel):
    """System metrics response model."""

    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time_ms: float
    active_connections: int
    memory_usage_mb: float
    cpu_usage_percent: float
    uptime_seconds: float


# ============================================================================
# STATUS ENDPOINTS
# ============================================================================


@router.get("/overall", response_model=SystemStatusResponse)
async def get_overall_system_status() -> SystemStatusResponse:
    """Get overall system status and health."""
    try:
        status = await get_system_status()
        return SystemStatusResponse(**status)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting system status: {str(e)}"
        )


@router.get("/components", response_model=Dict[str, ComponentStatusResponse])
async def get_all_components() -> Dict[str, ComponentStatusResponse]:
    """Get status of all system components."""
    try:
        components = await get_all_components_status()
        return {
            name: ComponentStatusResponse(
                name=comp.name,
                service_type=comp.service_type.value,
                status=comp.status.value,
                last_check=comp.last_check.isoformat(),
                response_time_ms=comp.response_time_ms,
                error_message=comp.error_message,
                metadata=comp.metadata,
            )
            for name, comp in components.items()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting component status: {str(e)}"
        )


@router.get("/components/{component_name}", response_model=ComponentStatusResponse)
async def get_component_status_endpoint(component_name: str) -> ComponentStatusResponse:
    """Get status of a specific component."""
    try:
        component = await get_component_status(component_name)
        if not component:
            raise HTTPException(
                status_code=404, detail=f"Component {component_name} not found"
            )

        return ComponentStatusResponse(
            name=component.name,
            service_type=component.service_type.value,
            status=component.status.value,
            last_check=component.last_check.isoformat(),
            response_time_ms=component.response_time_ms,
            error_message=component.error_message,
            metadata=component.metadata,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting component status: {str(e)}"
        )


@router.post("/components/{component_name}/check")
async def check_component_health(
    component_name: str, background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Manually trigger a health check for a specific component."""
    try:
        # Trigger immediate health check
        background_tasks.add_task(status_control.check_all_components)

        return {
            "message": f"Health check triggered for {component_name}",
            "component": component_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error triggering health check: {str(e)}"
        )


# ============================================================================
# ALERTS ENDPOINTS
# ============================================================================


@router.get("/alerts", response_model=List[AlertResponse])
async def get_recent_alerts(limit: int = 10) -> List[AlertResponse]:
    """Get recent system alerts."""
    try:
        alerts = status_control.get_recent_alerts(limit)
        return [
            AlertResponse(
                id=alert.id,
                component=alert.component,
                severity=alert.severity,
                message=alert.message,
                timestamp=alert.timestamp.isoformat(),
                resolved=alert.resolved,
                metadata=alert.metadata,
            )
            for alert in alerts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting alerts: {str(e)}")


@router.post("/alerts")
async def create_alert(
    component: str,
    severity: str,
    message: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create a new system alert."""
    try:
        await create_status_alert(component, severity, message, metadata)
        return {
            "message": "Alert created successfully",
            "component": component,
            "severity": severity,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating alert: {str(e)}")


@router.put("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str) -> Dict[str, Any]:
    """Mark an alert as resolved."""
    try:
        status_control.resolve_alert(alert_id)
        return {
            "message": "Alert resolved successfully",
            "alert_id": alert_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resolving alert: {str(e)}")


# ============================================================================
# METRICS ENDPOINTS
# ============================================================================


@router.get("/metrics", response_model=MetricsResponse)
async def get_system_metrics() -> MetricsResponse:
    """Get system performance metrics."""
    try:
        metrics = status_control.get_system_metrics()
        return MetricsResponse(
            total_requests=metrics.total_requests,
            successful_requests=metrics.successful_requests,
            failed_requests=metrics.failed_requests,
            average_response_time_ms=metrics.average_response_time_ms,
            active_connections=metrics.active_connections,
            memory_usage_mb=metrics.memory_usage_mb,
            cpu_usage_percent=metrics.cpu_usage_percent,
            uptime_seconds=metrics.uptime_seconds,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting metrics: {str(e)}")


@router.post("/metrics/update")
async def update_metrics(
    total_requests: Optional[int] = None,
    successful_requests: Optional[int] = None,
    failed_requests: Optional[int] = None,
    average_response_time_ms: Optional[float] = None,
    active_connections: Optional[int] = None,
    memory_usage_mb: Optional[float] = None,
    cpu_usage_percent: Optional[float] = None,
) -> Dict[str, Any]:
    """Update system metrics."""
    try:
        update_data = {}
        if total_requests is not None:
            update_data["total_requests"] = total_requests
        if successful_requests is not None:
            update_data["successful_requests"] = successful_requests
        if failed_requests is not None:
            update_data["failed_requests"] = failed_requests
        if average_response_time_ms is not None:
            update_data["average_response_time_ms"] = average_response_time_ms
        if active_connections is not None:
            update_data["active_connections"] = active_connections
        if memory_usage_mb is not None:
            update_data["memory_usage_mb"] = memory_usage_mb
        if cpu_usage_percent is not None:
            update_data["cpu_usage_percent"] = cpu_usage_percent

        status_control.update_metrics(**update_data)

        return {
            "message": "Metrics updated successfully",
            "updated_fields": list(update_data.keys()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating metrics: {str(e)}")


# ============================================================================
# CONTROL ENDPOINTS
# ============================================================================


@router.post("/control/refresh")
async def refresh_all_components(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Manually refresh all component statuses."""
    try:
        background_tasks.add_task(status_control.check_all_components)

        return {
            "message": "Component refresh triggered",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": list(status_control.health_checkers.keys()),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error refreshing components: {str(e)}"
        )


@router.get("/control/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for the status control system."""
    try:
        overall_status = await get_system_status()

        return {
            "status": "healthy",
            "service": "Status Control System",
            "version": "1.0.0",
            "overall_system_status": overall_status["status"],
            "components_online": overall_status["components_online"],
            "total_components": overall_status["total_components"],
            "uptime_seconds": overall_status["uptime_seconds"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Status control system error: {str(e)}"
        )


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================


@router.get("/info")
async def get_status_info() -> Dict[str, Any]:
    """Get information about the status control system."""
    return {
        "service": "Status Control System",
        "version": "1.0.0",
        "description": "Comprehensive monitoring and status management for crypto trading platform",
        "monitored_components": [
            "ai_agent",
            "vector_rag",
            "hybrid_rag",
            "realtime_data",
            "news_pipeline",
            "cost_tracking",
            "langsmith",
            "binance_api",
            "newsapi",
            "database",
            "websocket",
        ],
        "features": [
            "Real-time component monitoring",
            "Automatic health checks",
            "Alert system",
            "Performance metrics",
            "Status history",
            "Manual refresh capabilities",
        ],
        "endpoints": [
            "/status/overall",
            "/status/components",
            "/status/components/{component_name}",
            "/status/alerts",
            "/status/metrics",
            "/status/control/refresh",
        ],
    }
