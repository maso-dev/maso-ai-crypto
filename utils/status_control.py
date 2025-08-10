#!/usr/bin/env python3
"""
Status Control System for Crypto Trading Platform
Comprehensive monitoring and status management for all system components.
"""

import os
import asyncio
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager
import logging
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComponentStatus(Enum):
    """Status enumeration for system components."""

    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    UNKNOWN = "unknown"


class ServiceType(Enum):
    """Types of services in the system."""

    AI_AGENT = "ai_agent"
    VECTOR_RAG = "vector_rag"
    HYBRID_RAG = "hybrid_rag"
    REALTIME_DATA = "realtime_data"
    NEWS_PIPELINE = "news_pipeline"
    COST_TRACKING = "cost_tracking"
    LANGSMITH = "langsmith"
    BINANCE_API = "binance_api"
    NEWSAPI = "newsapi"
    DATABASE = "database"
    WEBSOCKET = "websocket"


@dataclass
class ComponentHealth:
    """Health status for a system component."""

    name: str
    service_type: ServiceType
    status: ComponentStatus
    last_check: datetime
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class SystemMetrics:
    """System-wide metrics and performance data."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time_ms: float = 0.0
    active_connections: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    uptime_seconds: float = 0.0


class StatusAlert(BaseModel):
    """Alert model for status notifications."""

    id: str
    component: str
    severity: str  # "info", "warning", "error", "critical"
    message: str
    timestamp: datetime
    resolved: bool = False
    metadata: Dict[str, Any] = {}


class StatusControl:
    """
    Centralized status control system for monitoring all platform components.
    """

    def __init__(self):
        self.components: Dict[str, ComponentHealth] = {}
        self.metrics = SystemMetrics()
        self.alerts: List[StatusAlert] = []
        self.start_time = datetime.now(timezone.utc)
        self.health_checkers: Dict[str, Callable] = {}
        self.status_callbacks: List[Callable] = []
        self._monitoring_task = None
        self._lightweight_mode = True  # Start in lightweight mode for Replit
        self._initialize_health_checkers()

    def set_lightweight_mode(self, enabled: bool):
        """Enable/disable lightweight mode for health checks"""
        self._lightweight_mode = enabled
        if enabled:
            print("🔧 Status control: Lightweight mode enabled (skipping expensive checks)")
        else:
            print("🔧 Status control: Full monitoring mode enabled")

    def _initialize_health_checkers(self):
        """Initialize health check functions for each component."""
        self.health_checkers = {
            "ai_agent": self._check_ai_agent_health,
            "vector_rag": self._check_vector_rag_health,
            "hybrid_rag": self._check_hybrid_rag_health,
            "realtime_data": self._check_realtime_data_health,
            "news_pipeline": self._check_news_pipeline_health,
            "cost_tracking": self._check_cost_tracking_health,
            "langsmith": self._check_langsmith_health,
            "binance_api": self._check_binance_api_health,
            "newsapi": self._check_newsapi_health,
            "database": self._check_database_health,
            "websocket": self._check_websocket_health,
        }

    async def _check_ai_agent_health(self) -> ComponentHealth:
        """Check AI agent health status."""
        start_time = datetime.now(timezone.utc)
        
        # In lightweight mode, skip expensive AI operations
        if self._lightweight_mode:
            return ComponentHealth(
                name="AI Agent",
                service_type=ServiceType.AI_AGENT,
                status=ComponentStatus.ONLINE,
                last_check=datetime.now(timezone.utc),
                response_time_ms=0.1,
                metadata={
                    "agent_id": "masonic-ai-agent",
                    "mode": "lightweight",
                    "note": "Full health check disabled for deployment"
                },
            )
        
        try:
            # Import and check AI agent
            from .ai_agent import CryptoAIAgent, AgentTask

            agent = CryptoAIAgent()

            # Test basic functionality
            test_result = await agent.execute_task(
                task=AgentTask.MARKET_ANALYSIS,
                query="Test health check",
                symbols=["BTC"],
            )

            response_time = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds() * 1000

            return ComponentHealth(
                name="AI Agent",
                service_type=ServiceType.AI_AGENT,
                status=ComponentStatus.ONLINE,
                last_check=datetime.now(timezone.utc),
                response_time_ms=response_time,
                metadata={
                    "agent_id": "masonic-ai-agent",
                    "model": "gpt-4o",
                    "workflow_nodes": len(agent.workflow.nodes),
                },
            )
        except Exception as e:
            return ComponentHealth(
                name="AI Agent",
                service_type=ServiceType.AI_AGENT,
                status=ComponentStatus.ERROR,
                last_check=datetime.now(timezone.utc),
                error_message=str(e),
            )

    async def _check_vector_rag_health(self) -> ComponentHealth:
        """Check Vector RAG health status."""
        start_time = datetime.now(timezone.utc)
        
        # In lightweight mode, skip expensive vector operations
        if self._lightweight_mode:
            return ComponentHealth(
                name="Vector RAG",
                service_type=ServiceType.VECTOR_RAG,
                status=ComponentStatus.ONLINE,
                last_check=datetime.now(timezone.utc),
                response_time_ms=0.1,
                metadata={
                    "mode": "lightweight",
                    "note": "Full health check disabled for deployment"
                },
            )
        
        try:
            from .vector_rag import EnhancedVectorRAG, VectorQuery, QueryType

            rag = EnhancedVectorRAG()

            # Test search functionality
            test_query = VectorQuery(
                query_text="test health check",
                query_type=QueryType.SEMANTIC_SEARCH,
                limit=1,
            )
            results = await rag.intelligent_search(test_query)

            response_time = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds() * 1000

            return ComponentHealth(
                name="Vector RAG",
                service_type=ServiceType.VECTOR_RAG,
                status=ComponentStatus.ONLINE,
                last_check=datetime.now(timezone.utc),
                response_time_ms=response_time,
                metadata={
                    "collection_size": len(results) if results else 0,
                    "embedding_model": "text-embedding-3-small",
                },
            )
        except Exception as e:
            return ComponentHealth(
                name="Vector RAG",
                service_type=ServiceType.VECTOR_RAG,
                status=ComponentStatus.ERROR,
                last_check=datetime.now(timezone.utc),
                error_message=str(e),
            )

    async def _check_hybrid_rag_health(self) -> ComponentHealth:
        """Check Hybrid RAG health status."""
        start_time = datetime.now(timezone.utc)
        try:
            from .hybrid_rag import HybridRAGSystem, HybridQuery, HybridQueryType

            hybrid_rag = HybridRAGSystem()

            # Test hybrid search
            test_query = HybridQuery(
                query_text="test health check",
                query_type=HybridQueryType.HYBRID,
                limit=1,
            )
            results = await hybrid_rag.hybrid_search(test_query)

            response_time = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds() * 1000

            return ComponentHealth(
                name="Hybrid RAG",
                service_type=ServiceType.HYBRID_RAG,
                status=ComponentStatus.ONLINE,
                last_check=datetime.now(timezone.utc),
                response_time_ms=response_time,
                metadata={
                    "total_results": len(results) if results else 0,
                    "vector_rag_available": True,
                    "graph_rag_available": (
                        hybrid_rag.graph_rag.connected
                        if hasattr(hybrid_rag.graph_rag, "connected")
                        else False
                    ),
                },
            )
        except Exception as e:
            return ComponentHealth(
                name="Hybrid RAG",
                service_type=ServiceType.HYBRID_RAG,
                status=ComponentStatus.ERROR,
                last_check=datetime.now(timezone.utc),
                error_message=str(e),
            )

    async def _check_realtime_data_health(self) -> ComponentHealth:
        """Check real-time data health status."""
        try:
            from .realtime_data import realtime_manager

            # Simple check if realtime_manager exists
            if realtime_manager:
                return ComponentHealth(
                    name="Real-time Data",
                    service_type=ServiceType.REALTIME_DATA,
                    status=ComponentStatus.ONLINE,
                    last_check=datetime.now(timezone.utc),
                    metadata={"manager_available": True, "status": "operational"},
                )
            else:
                return ComponentHealth(
                    name="Real-time Data",
                    service_type=ServiceType.REALTIME_DATA,
                    status=ComponentStatus.OFFLINE,
                    last_check=datetime.now(timezone.utc),
                    error_message="Realtime manager not available",
                )
        except Exception as e:
            return ComponentHealth(
                name="Real-time Data",
                service_type=ServiceType.REALTIME_DATA,
                status=ComponentStatus.ERROR,
                last_check=datetime.now(timezone.utc),
                error_message=str(e),
            )

    async def _check_news_pipeline_health(self) -> ComponentHealth:
        """Check news pipeline health status."""
        try:
            from .enhanced_news_pipeline import EnhancedNewsPipeline

            pipeline = EnhancedNewsPipeline()

            return ComponentHealth(
                name="News Pipeline",
                service_type=ServiceType.NEWS_PIPELINE,
                status=ComponentStatus.ONLINE,
                last_check=datetime.now(timezone.utc),
                metadata={"pipeline_available": True, "status": "operational"},
            )
        except Exception as e:
            return ComponentHealth(
                name="News Pipeline",
                service_type=ServiceType.NEWS_PIPELINE,
                status=ComponentStatus.ERROR,
                last_check=datetime.now(timezone.utc),
                error_message=str(e),
            )

    async def _check_cost_tracking_health(self) -> ComponentHealth:
        """Check cost tracking health status."""
        try:
            from .cost_tracker import cost_tracker

            return ComponentHealth(
                name="Cost Tracking",
                service_type=ServiceType.COST_TRACKING,
                status=ComponentStatus.ONLINE,
                last_check=datetime.now(timezone.utc),
                metadata={"tracker_available": True, "status": "operational"},
            )
        except Exception as e:
            return ComponentHealth(
                name="Cost Tracking",
                service_type=ServiceType.COST_TRACKING,
                status=ComponentStatus.ERROR,
                last_check=datetime.now(timezone.utc),
                error_message=str(e),
            )

    async def _check_langsmith_health(self) -> ComponentHealth:
        """Check LangSmith health status."""
        langsmith_key = os.getenv("LANGSMITH_API_KEY")

        if not langsmith_key:
            return ComponentHealth(
                name="LangSmith",
                service_type=ServiceType.LANGSMITH,
                status=ComponentStatus.OFFLINE,
                last_check=datetime.now(timezone.utc),
                error_message="LANGSMITH_API_KEY not configured",
            )

        try:
            # Test LangSmith connection
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.smith.langchain.com/runs",
                    headers={"Authorization": f"Bearer {langsmith_key}"},
                    timeout=5.0,
                )

            return ComponentHealth(
                name="LangSmith",
                service_type=ServiceType.LANGSMITH,
                status=(
                    ComponentStatus.ONLINE
                    if response.status_code == 200
                    else ComponentStatus.DEGRADED
                ),
                last_check=datetime.now(timezone.utc),
                metadata={
                    "project": os.getenv("LANGCHAIN_PROJECT", "masonic-brain"),
                    "organization": os.getenv("LANGCHAIN_ORGANIZATION", ""),
                },
            )
        except Exception as e:
            return ComponentHealth(
                name="LangSmith",
                service_type=ServiceType.LANGSMITH,
                status=ComponentStatus.ERROR,
                last_check=datetime.now(timezone.utc),
                error_message=str(e),
            )

    async def _check_binance_api_health(self) -> ComponentHealth:
        """Check Binance API health status."""
        binance_key = os.getenv("BINANCE_API_KEY")

        if not binance_key:
            return ComponentHealth(
                name="Binance API",
                service_type=ServiceType.BINANCE_API,
                status=ComponentStatus.OFFLINE,
                last_check=datetime.now(timezone.utc),
                error_message="BINANCE_API_KEY not configured",
            )

        try:
            from .binance_client import get_portfolio_data

            portfolio = await get_portfolio_data()

            return ComponentHealth(
                name="Binance API",
                service_type=ServiceType.BINANCE_API,
                status=ComponentStatus.ONLINE,
                last_check=datetime.now(timezone.utc),
                metadata={
                    "portfolio_connected": portfolio is not None,
                    "total_assets": len(portfolio.assets) if portfolio else 0,
                },
            )
        except Exception as e:
            return ComponentHealth(
                name="Binance API",
                service_type=ServiceType.BINANCE_API,
                status=ComponentStatus.ERROR,
                last_check=datetime.now(timezone.utc),
                error_message=str(e),
            )

    async def _check_newsapi_health(self) -> ComponentHealth:
        """Check NewsAPI health status."""
        newsapi_key = os.getenv("NEWSAPI_KEY")

        if not newsapi_key:
            return ComponentHealth(
                name="NewsAPI",
                service_type=ServiceType.NEWSAPI,
                status=ComponentStatus.OFFLINE,
                last_check=datetime.now(timezone.utc),
                error_message="NEWSAPI_KEY not configured",
            )

        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://newsapi.org/v2/top-headlines",
                    params={"country": "us", "apiKey": newsapi_key},
                    timeout=5.0,
                )

            return ComponentHealth(
                name="NewsAPI",
                service_type=ServiceType.NEWSAPI,
                status=(
                    ComponentStatus.ONLINE
                    if response.status_code == 200
                    else ComponentStatus.DEGRADED
                ),
                last_check=datetime.now(timezone.utc),
                metadata={
                    "status": response.status_code,
                    "remaining_requests": response.headers.get(
                        "X-RateLimit-Remaining", "unknown"
                    ),
                },
            )
        except Exception as e:
            return ComponentHealth(
                name="NewsAPI",
                service_type=ServiceType.NEWSAPI,
                status=ComponentStatus.ERROR,
                last_check=datetime.now(timezone.utc),
                error_message=str(e),
            )

    async def _check_database_health(self) -> ComponentHealth:
        """Check database health status."""
        try:
            import sqlite3
            from pathlib import Path

            db_path = Path("cost_tracking.db")
            if not db_path.exists():
                return ComponentHealth(
                    name="Database",
                    service_type=ServiceType.DATABASE,
                    status=ComponentStatus.OFFLINE,
                    last_check=datetime.now(timezone.utc),
                    error_message="Database file not found",
                )

            # Test database connection
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM api_calls")
            count = cursor.fetchone()[0]
            conn.close()

            return ComponentHealth(
                name="Database",
                service_type=ServiceType.DATABASE,
                status=ComponentStatus.ONLINE,
                last_check=datetime.now(timezone.utc),
                metadata={
                    "total_records": count,
                    "file_size_mb": db_path.stat().st_size / (1024 * 1024),
                },
            )
        except Exception as e:
            return ComponentHealth(
                name="Database",
                service_type=ServiceType.DATABASE,
                status=ComponentStatus.ERROR,
                last_check=datetime.now(timezone.utc),
                error_message=str(e),
            )

    async def _check_websocket_health(self) -> ComponentHealth:
        """Check WebSocket health status."""
        try:
            from .realtime_data import realtime_manager

            return ComponentHealth(
                name="WebSocket",
                service_type=ServiceType.WEBSOCKET,
                status=ComponentStatus.ONLINE,
                last_check=datetime.now(timezone.utc),
                metadata={"websocket_available": True, "status": "operational"},
            )
        except Exception as e:
            return ComponentHealth(
                name="WebSocket",
                service_type=ServiceType.WEBSOCKET,
                status=ComponentStatus.ERROR,
                last_check=datetime.now(timezone.utc),
                error_message=str(e),
            )

    def _start_monitoring(self):
        """Start background monitoring task."""
        if self._monitoring_task is None or self._monitoring_task.done():
            try:
                self._monitoring_task = asyncio.create_task(self._monitor_components())
            except RuntimeError:
                # No running event loop, monitoring will start when needed
                pass

    async def _monitor_components(self):
        """Background task to monitor all components."""
        while True:
            try:
                await self.check_all_components()
                # CAPSTONE: Changed from 30 seconds to 6 hours (4 times per day)
                await asyncio.sleep(6 * 60 * 60)  # Check every 6 hours
            except Exception as e:
                logger.error(f"Error in component monitoring: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    async def check_all_components(self):
        """Check health of all components."""
        for component_name, health_checker in self.health_checkers.items():
            try:
                health = await health_checker()
                self.components[component_name] = health

                # Check for status changes and trigger alerts
                await self._check_status_changes(component_name, health)

            except Exception as e:
                logger.error(f"Error checking {component_name}: {e}")
                self.components[component_name] = ComponentHealth(
                    name=component_name,
                    service_type=ServiceType(component_name),
                    status=ComponentStatus.ERROR,
                    last_check=datetime.now(timezone.utc),
                    error_message=str(e),
                )

    async def _check_status_changes(self, component_name: str, health: ComponentHealth):
        """Check for status changes and create alerts."""
        # This is a simplified version - you could add more sophisticated change detection
        if health.status == ComponentStatus.ERROR:
            await self.create_alert(
                component=component_name,
                severity="error",
                message=f"Component {component_name} is in error state: {health.error_message}",
            )
        elif health.status == ComponentStatus.DEGRADED:
            await self.create_alert(
                component=component_name,
                severity="warning",
                message=f"Component {component_name} is in degraded state",
            )

    async def create_alert(
        self,
        component: str,
        severity: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Create a new status alert."""
        alert = StatusAlert(
            id=f"alert_{len(self.alerts) + 1}_{int(datetime.now().timestamp())}",
            component=component,
            severity=severity,
            message=message,
            timestamp=datetime.now(timezone.utc),
            metadata=metadata or {},
        )

        self.alerts.append(alert)

        # Trigger callbacks
        for callback in self.status_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                logger.error(f"Error in status callback: {e}")

    def add_status_callback(self, callback: Callable):
        """Add a callback function to be called when status changes."""
        self.status_callbacks.append(callback)

    def get_overall_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        online_count = sum(
            1 for c in self.components.values() if c.status == ComponentStatus.ONLINE
        )
        total_count = len(self.components)

        # Calculate uptime
        uptime = (datetime.now(timezone.utc) - self.start_time).total_seconds()

        return {
            "status": (
                "healthy"
                if online_count == total_count
                else "degraded" if online_count > total_count // 2 else "unhealthy"
            ),
            "uptime_seconds": uptime,
            "components_online": online_count,
            "total_components": total_count,
            "health_percentage": (
                (online_count / total_count * 100) if total_count > 0 else 0
            ),
            "last_check": datetime.now(timezone.utc).isoformat(),
            "alerts_count": len([a for a in self.alerts if not a.resolved]),
        }

    def get_component_status(self, component_name: str) -> Optional[ComponentHealth]:
        """Get status of a specific component."""
        return self.components.get(component_name)

    def get_all_components_status(self) -> Dict[str, ComponentHealth]:
        """Get status of all components."""
        return self.components.copy()

    def get_recent_alerts(self, limit: int = 10) -> List[StatusAlert]:
        """Get recent alerts."""
        return sorted(self.alerts, key=lambda x: x.timestamp, reverse=True)[:limit]

    def resolve_alert(self, alert_id: str):
        """Mark an alert as resolved."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                break

    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        self.metrics.uptime_seconds = (
            datetime.now(timezone.utc) - self.start_time
        ).total_seconds()
        return self.metrics

    def update_metrics(self, **kwargs):
        """Update system metrics."""
        for key, value in kwargs.items():
            if hasattr(self.metrics, key):
                setattr(self.metrics, key, value)

    def start_monitoring(self):
        """Start monitoring when the app is ready."""
        self._start_monitoring()

    def enable_full_monitoring(self):
        """Enable full monitoring mode after app is stable"""
        self._lightweight_mode = False
        print("🔧 Status control: Transitioning to full monitoring mode")
        # Start monitoring if not already running
        if not self._monitoring_task or self._monitoring_task.done():
            self._start_monitoring()


# Global status control instance - lazy initialization
_status_control_instance = None


def get_status_control() -> StatusControl:
    """Get the global status control instance, creating it if needed."""
    global _status_control_instance
    if _status_control_instance is None:
        _status_control_instance = StatusControl()
    return _status_control_instance


# Don't create the instance during import - make it truly lazy


# Convenience functions
async def get_system_status() -> Dict[str, Any]:
    """Get overall system status."""
    return get_status_control().get_overall_status()


async def get_component_status(component_name: str) -> Optional[ComponentHealth]:
    """Get status of a specific component."""
    return get_status_control().get_component_status(component_name)


async def get_all_components_status() -> Dict[str, ComponentHealth]:
    """Get status of all components."""
    return get_status_control().get_all_components_status()


async def create_status_alert(
    component: str,
    severity: str,
    message: str,
    metadata: Optional[Dict[str, Any]] = None,
):
    """Create a status alert."""
    await get_status_control().create_alert(component, severity, message, metadata)


@asynccontextmanager
async def status_monitor(component_name: str, operation: str):
    """Context manager for monitoring operations."""
    start_time = datetime.now(timezone.utc)
    try:
        yield
        # Operation successful
        logger.info(f"Operation {operation} on {component_name} completed successfully")
    except Exception as e:
        # Operation failed
        await create_status_alert(
            component=component_name,
            severity="error",
            message=f"Operation {operation} failed: {str(e)}",
            metadata={
                "operation": operation,
                "duration_ms": (datetime.now(timezone.utc) - start_time).total_seconds()
                * 1000,
            },
        )
        raise
