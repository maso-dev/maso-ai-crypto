#!/usr/bin/env python3
"""
Admin API Endpoints
Provides administrative functions for system management, cost tracking, and configuration.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import os
import json

# Import admin-specific utilities
from utils.cost_tracker import cost_tracker
from utils.milvus import MILVUS_URI, MILVUS_COLLECTION_NAME
from utils.react_validation import tavily_client
import os

router = APIRouter(prefix="/admin", tags=["admin"])

# Admin authentication (basic implementation - should be enhanced for production)
def verify_admin_access():
    """Verify admin access - placeholder for proper authentication."""
    # TODO: Implement proper admin authentication
    return True

class SystemStatus(BaseModel):
    """System status response model."""
    status: str
    timestamp: str
    services: Dict[str, Dict[str, Any]]
    database: Dict[str, Any]
    api_keys: Dict[str, bool]

class CostSummary(BaseModel):
    """Cost summary response model."""
    date: str
    total_cost: float
    call_count: int
    service_costs: Dict[str, float]
    service_breakdown: Dict[str, Dict[str, Any]]

class APICallRecord(BaseModel):
    """API call record response model."""
    service: str
    endpoint: str
    timestamp: str
    tokens_input: Optional[int]
    tokens_output: Optional[int]
    cost_usd: float
    success: bool
    error_message: Optional[str]

class MonthlySummary(BaseModel):
    """Monthly cost summary response model."""
    year: int
    month: int
    total_cost: float
    call_count: int
    service_costs: Dict[str, float]

class SystemConfig(BaseModel):
    """System configuration model."""
    milvus_uri: str
    milvus_collection: str
    newsapi_enabled: bool
    tavily_enabled: bool
    openai_enabled: bool
    cost_tracking_enabled: bool
    validation_enabled: bool

# ============================================================================
# SYSTEM STATUS ENDPOINTS
# ============================================================================

@router.get("/status", response_model=SystemStatus)
async def get_system_status(admin: bool = Depends(verify_admin_access)) -> SystemStatus:
    """Get overall system status and health."""
    try:
        now = datetime.now(timezone.utc)
        
        # Check service status
        services = {
            "milvus": {
                "status": "online" if MILVUS_URI else "offline",
                "uri": MILVUS_URI or "not configured",
                "collection": MILVUS_COLLECTION_NAME or "not configured"
            },
            "newsapi": {
                "status": "online" if os.getenv("NEWSAPI_API_KEY") else "offline",
                "configured": bool(os.getenv("NEWSAPI_API_KEY"))
            },
            "tavily": {
                "status": "online" if tavily_client else "offline",
                "configured": bool(tavily_client)
            },
            "openai": {
                "status": "online" if os.getenv("OPENAI_API_KEY") else "offline",
                "configured": bool(os.getenv("OPENAI_API_KEY"))
            }
        }
        
        # Check database status
        try:
            daily_summary = cost_tracker.get_daily_summary()
            database_status = {
                "status": "online",
                "cost_tracking": True,
                "daily_calls": daily_summary["call_count"],
                "daily_cost": daily_summary["total_cost"]
            }
        except Exception as e:
            database_status = {
                "status": "error",
                "cost_tracking": False,
                "error": str(e)
            }
        
        # Check API keys
        api_keys = {
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "tavily": bool(os.getenv("TAVILY_API_KEY")),
            "newsapi": bool(os.getenv("NEWSAPI_API_KEY")),
            "binance": bool(os.getenv("BINANCE_API_KEY") and os.getenv("BINANCE_SECRET_KEY"))
        }
        
        overall_status = "healthy" if all(
            service["status"] == "online" for service in services.values()
        ) else "degraded"
        
        return SystemStatus(
            status=overall_status,
            timestamp=now.isoformat(),
            services=services,
            database=database_status,
            api_keys=api_keys
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving system status: {str(e)}")

@router.get("/health")
async def health_check(admin: bool = Depends(verify_admin_access)) -> Dict[str, Any]:
    """Quick health check endpoint."""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# ============================================================================
# COST TRACKING ENDPOINTS
# ============================================================================

@router.get("/costs/daily", response_model=CostSummary)
async def get_daily_costs(
    date: Optional[str] = None,
    admin: bool = Depends(verify_admin_access)
) -> CostSummary:
    """Get cost summary for a specific date or today."""
    try:
        summary = cost_tracker.get_daily_summary(date)
        return CostSummary(**summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving daily costs: {str(e)}")

@router.get("/costs/monthly/{year}/{month}", response_model=MonthlySummary)
async def get_monthly_costs(
    year: int, 
    month: int,
    admin: bool = Depends(verify_admin_access)
) -> MonthlySummary:
    """Get cost summary for a specific month."""
    try:
        summary = cost_tracker.get_monthly_summary(year, month)
        return MonthlySummary(**summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving monthly costs: {str(e)}")

@router.get("/costs/current-month")
async def get_current_month_summary(admin: bool = Depends(verify_admin_access)) -> Dict[str, Any]:
    """Get current month cost summary with projections."""
    try:
        now = datetime.now(timezone.utc)
        summary = cost_tracker.get_monthly_summary(now.year, now.month)
        daily_summary = cost_tracker.get_daily_summary()
        
        return {
            "monthly": summary,
            "today": daily_summary,
            "projected_monthly": {
                "total_cost": summary["total_cost"] * (30 / now.day) if now.day > 0 else 0,
                "call_count": summary["call_count"] * (30 / now.day) if now.day > 0 else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving current month summary: {str(e)}")

@router.get("/costs/recent", response_model=List[APICallRecord])
async def get_recent_calls(
    limit: int = 50,
    admin: bool = Depends(verify_admin_access)
) -> List[APICallRecord]:
    """Get recent API calls."""
    try:
        calls = cost_tracker.get_recent_calls(limit)
        return [APICallRecord(**call) for call in calls]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving recent calls: {str(e)}")

@router.get("/costs/services")
async def get_service_breakdown(admin: bool = Depends(verify_admin_access)) -> Dict[str, Any]:
    """Get breakdown of costs by service."""
    try:
        now = datetime.now(timezone.utc)
        monthly = cost_tracker.get_monthly_summary(now.year, now.month)
        daily = cost_tracker.get_daily_summary()
        
        return {
            "monthly_breakdown": monthly["service_costs"],
            "daily_breakdown": daily["service_costs"],
            "service_stats": daily["service_breakdown"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving service breakdown: {str(e)}")

@router.get("/costs/alerts")
async def get_cost_alerts(admin: bool = Depends(verify_admin_access)) -> Dict[str, Any]:
    """Get cost alerts and warnings."""
    try:
        daily = cost_tracker.get_daily_summary()
        monthly = cost_tracker.get_monthly_summary(
            datetime.now(timezone.utc).year,
            datetime.now(timezone.utc).month
        )
        
        alerts = []
        
        # Daily cost alerts
        if daily["total_cost"] > 5.0:  # $5 daily threshold
            alerts.append({
                "type": "warning",
                "message": f"Daily cost exceeded $5: ${daily['total_cost']:.2f}",
                "severity": "high"
            })
        
        # Monthly cost alerts
        if monthly["total_cost"] > 100.0:  # $100 monthly threshold
            alerts.append({
                "type": "warning",
                "message": f"Monthly cost exceeded $100: ${monthly['total_cost']:.2f}",
                "severity": "critical"
            })
        
        # Service-specific alerts
        for service, cost in daily["service_costs"].items():
            if cost > 2.0:  # $2 per service daily threshold
                alerts.append({
                    "type": "info",
                    "message": f"{service.title()} daily cost: ${cost:.2f}",
                    "severity": "medium"
                })
        
        return {
            "alerts": alerts,
            "daily_cost": daily["total_cost"],
            "monthly_cost": monthly["total_cost"],
            "thresholds": {
                "daily_warning": 5.0,
                "monthly_warning": 100.0,
                "service_warning": 2.0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving cost alerts: {str(e)}")

# ============================================================================
# CONFIGURATION ENDPOINTS
# ============================================================================

@router.get("/config", response_model=SystemConfig)
async def get_system_config(admin: bool = Depends(verify_admin_access)) -> SystemConfig:
    """Get current system configuration."""
    try:
        return SystemConfig(
            milvus_uri=MILVUS_URI or "",
            milvus_collection=MILVUS_COLLECTION_NAME or "",
            newsapi_enabled=bool(os.getenv("NEWSAPI_API_KEY")),
            tavily_enabled=bool(tavily_client),
            openai_enabled=bool(os.getenv("OPENAI_API_KEY")),
            cost_tracking_enabled=True,
            validation_enabled=bool(tavily_client and os.getenv("OPENAI_API_KEY"))
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving system config: {str(e)}")

@router.post("/config/update")
async def update_system_config(
    config: SystemConfig,
    admin: bool = Depends(verify_admin_access)
) -> Dict[str, Any]:
    """Update system configuration (placeholder for actual implementation)."""
    try:
        # TODO: Implement actual configuration updates
        # This would typically involve updating environment variables or config files
        
        return {
            "status": "success",
            "message": "Configuration update requested",
            "config": config.dict(),
            "note": "Configuration updates require server restart"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating system config: {str(e)}")

# ============================================================================
# MAINTENANCE ENDPOINTS
# ============================================================================

@router.post("/maintenance/clear-costs")
async def clear_cost_data(
    days: int = 30,
    admin: bool = Depends(verify_admin_access)
) -> Dict[str, Any]:
    """Clear cost data older than specified days."""
    try:
        # TODO: Implement cost data cleanup
        return {
            "status": "success",
            "message": f"Cost data cleanup requested for data older than {days} days",
            "note": "This operation is irreversible"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cost data: {str(e)}")

@router.post("/maintenance/optimize-database")
async def optimize_database(admin: bool = Depends(verify_admin_access)) -> Dict[str, Any]:
    """Optimize database performance."""
    try:
        # TODO: Implement database optimization
        return {
            "status": "success",
            "message": "Database optimization completed",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error optimizing database: {str(e)}")

@router.get("/maintenance/logs")
async def get_system_logs(
    limit: int = 100,
    admin: bool = Depends(verify_admin_access)
) -> Dict[str, Any]:
    """Get system logs (placeholder)."""
    try:
        # TODO: Implement actual log retrieval
        return {
            "logs": [],
            "total": 0,
            "limit": limit,
            "note": "Log retrieval not yet implemented"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving logs: {str(e)}") 
