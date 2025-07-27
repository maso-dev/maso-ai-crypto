#!/usr/bin/env python3
"""
Cost Tracking API Endpoints
Provides endpoints to monitor API usage and costs.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from utils.cost_tracker import cost_tracker

router = APIRouter()

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

@router.get("/costs/daily", response_model=CostSummary)
async def get_daily_costs(date: Optional[str] = None) -> CostSummary:
    """Get cost summary for a specific date or today."""
    try:
        summary = cost_tracker.get_daily_summary(date)
        return CostSummary(**summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving daily costs: {str(e)}")

@router.get("/costs/monthly/{year}/{month}", response_model=MonthlySummary)
async def get_monthly_costs(year: int, month: int) -> MonthlySummary:
    """Get cost summary for a specific month."""
    try:
        summary = cost_tracker.get_monthly_summary(year, month)
        return MonthlySummary(**summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving monthly costs: {str(e)}")

@router.get("/costs/recent", response_model=List[APICallRecord])
async def get_recent_calls(limit: int = 50) -> List[APICallRecord]:
    """Get recent API calls."""
    try:
        calls = cost_tracker.get_recent_calls(limit)
        return [APICallRecord(**call) for call in calls]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving recent calls: {str(e)}")

@router.get("/costs/current-month")
async def get_current_month_summary() -> Dict[str, Any]:
    """Get current month cost summary."""
    try:
        now = datetime.now(timezone.utc)
        summary = cost_tracker.get_monthly_summary(now.year, now.month)
        
        # Add some additional metrics
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

@router.get("/costs/services")
async def get_service_breakdown() -> Dict[str, Any]:
    """Get breakdown of costs by service."""
    try:
        # Get current month data
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
async def get_cost_alerts() -> Dict[str, Any]:
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
