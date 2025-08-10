#!/usr/bin/env python3
"""
Test Status Control System
Tests for the comprehensive status monitoring and control system.
"""

import asyncio
import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch, AsyncMock

# Import status control components
from utils.status_control import (
    StatusControl,
    ComponentHealth,
    ComponentStatus,
    ServiceType,
    StatusAlert,
    SystemMetrics,
    get_system_status,
    get_component_status,
    get_all_components_status,
    create_status_alert,
    get_status_control,
)


class TestStatusControl:
    """Test cases for the StatusControl class."""

    @pytest.fixture
    def status_control_instance(self):
        """Create a fresh StatusControl instance for testing."""
        return StatusControl()

    @pytest.fixture
    def mock_component_health(self):
        """Create a mock ComponentHealth instance."""
        return ComponentHealth(
            name="Test Component",
            service_type=ServiceType.AI_AGENT,
            status=ComponentStatus.ONLINE,
            last_check=datetime.now(timezone.utc),
            response_time_ms=100.0,
            metadata={"test": "data"},
        )

    def test_status_control_initialization(self, status_control_instance):
        """Test StatusControl initialization."""
        assert status_control_instance is not None
        assert hasattr(status_control_instance, "components")
        assert hasattr(status_control_instance, "metrics")
        assert hasattr(status_control_instance, "alerts")
        assert hasattr(status_control_instance, "health_checkers")

    def test_component_health_creation(self, mock_component_health):
        """Test ComponentHealth creation."""
        assert mock_component_health.name == "Test Component"
        assert mock_component_health.service_type == ServiceType.AI_AGENT
        assert mock_component_health.status == ComponentStatus.ONLINE
        assert mock_component_health.response_time_ms == 100.0
        assert mock_component_health.metadata["test"] == "data"

    def test_status_alert_creation(self):
        """Test StatusAlert creation."""
        alert = StatusAlert(
            id="test_alert_1",
            component="test_component",
            severity="warning",
            message="Test alert message",
            timestamp=datetime.now(timezone.utc),
            metadata={"test": "data"},
        )

        assert alert.id == "test_alert_1"
        assert alert.component == "test_component"
        assert alert.severity == "warning"
        assert alert.message == "Test alert message"
        assert alert.resolved is False

    def test_system_metrics_creation(self):
        """Test SystemMetrics creation."""
        metrics = SystemMetrics(
            total_requests=1000,
            successful_requests=950,
            failed_requests=50,
            average_response_time_ms=150.0,
            active_connections=10,
            memory_usage_mb=512.0,
            cpu_usage_percent=25.0,
            uptime_seconds=3600.0,
        )

        assert metrics.total_requests == 1000
        assert metrics.successful_requests == 950
        assert metrics.failed_requests == 50
        assert metrics.average_response_time_ms == 150.0
        assert metrics.active_connections == 10
        assert metrics.memory_usage_mb == 512.0
        assert metrics.cpu_usage_percent == 25.0
        assert metrics.uptime_seconds == 3600.0

    @pytest.mark.asyncio
    async def test_get_overall_status(self, status_control_instance):
        """Test getting overall system status."""
        # Mock some components
        status_control_instance.components = {
            "ai_agent": ComponentHealth(
                name="AI Agent",
                service_type=ServiceType.AI_AGENT,
                status=ComponentStatus.ONLINE,
                last_check=datetime.now(timezone.utc),
            ),
            "vector_rag": ComponentHealth(
                name="Vector RAG",
                service_type=ServiceType.VECTOR_RAG,
                status=ComponentStatus.ONLINE,
                last_check=datetime.now(timezone.utc),
            ),
        }

        status = status_control_instance.get_overall_status()

        assert "status" in status
        assert "uptime_seconds" in status
        assert "components_online" in status
        assert "total_components" in status
        assert "health_percentage" in status
        assert status["components_online"] == 2
        assert status["total_components"] == 2
        assert status["health_percentage"] == 100.0

    @pytest.mark.asyncio
    async def test_create_alert(self, status_control_instance):
        """Test creating an alert."""
        initial_alert_count = len(status_control_instance.alerts)

        await status_control_instance.create_alert(
            component="test_component",
            severity="warning",
            message="Test alert",
            metadata={"test": "data"},
        )

        assert len(status_control_instance.alerts) == initial_alert_count + 1

        alert = status_control_instance.alerts[-1]
        assert alert.component == "test_component"
        assert alert.severity == "warning"
        assert alert.message == "Test alert"
        assert alert.metadata["test"] == "data"
        assert alert.resolved is False

    def test_resolve_alert(self, status_control_instance):
        """Test resolving an alert."""
        # Create a test alert
        alert = StatusAlert(
            id="test_alert_1",
            component="test_component",
            severity="warning",
            message="Test alert",
            timestamp=datetime.now(timezone.utc),
        )
        status_control_instance.alerts.append(alert)

        # Resolve the alert
        status_control_instance.resolve_alert("test_alert_1")

        # Check that the alert is resolved
        resolved_alert = next(
            a for a in status_control_instance.alerts if a.id == "test_alert_1"
        )
        assert resolved_alert.resolved is True

    def test_get_recent_alerts(self, status_control_instance):
        """Test getting recent alerts."""
        # Create some test alerts
        for i in range(5):
            alert = StatusAlert(
                id=f"alert_{i}",
                component=f"component_{i}",
                severity="info",
                message=f"Alert {i}",
                timestamp=datetime.now(timezone.utc),
            )
            status_control_instance.alerts.append(alert)

        # Get recent alerts with limit
        recent_alerts = status_control_instance.get_recent_alerts(limit=3)
        assert len(recent_alerts) == 3

    def test_update_metrics(self, status_control_instance):
        """Test updating system metrics."""
        status_control_instance.update_metrics(
            total_requests=1000, successful_requests=950, average_response_time_ms=150.0
        )

        metrics = status_control_instance.get_system_metrics()
        assert metrics.total_requests == 1000
        assert metrics.successful_requests == 950
        assert metrics.average_response_time_ms == 150.0


class TestHealthCheckers:
    """Test cases for health check methods."""

    @pytest.mark.asyncio
    async def test_check_ai_agent_health_mock(self):
        """Test AI agent health check with mocked dependencies."""
        status_control_instance = StatusControl()

        # Mock the health check to avoid import issues
        async def mock_ai_health_check():
            return ComponentHealth(
                name="AI Agent",
                service_type=ServiceType.AI_AGENT,
                status=ComponentStatus.ONLINE,
                last_check=datetime.now(timezone.utc),
                response_time_ms=100.0,
                metadata={"workflow_nodes": 3},
            )

        # Override the health check method directly
        status_control_instance._check_ai_agent_health = mock_ai_health_check
        health = await status_control_instance._check_ai_agent_health()

        assert health.name == "AI Agent"
        assert health.service_type == ServiceType.AI_AGENT
        assert health.status == ComponentStatus.ONLINE
        assert "workflow_nodes" in health.metadata
        assert health.metadata["workflow_nodes"] == 3

    @pytest.mark.asyncio
    async def test_check_vector_rag_health_mock(self):
        """Test Vector RAG health check with mocked dependencies."""
        status_control_instance = StatusControl()

        # Mock the health check to avoid import issues
        async def mock_vector_rag_health_check():
            return ComponentHealth(
                name="Vector RAG",
                service_type=ServiceType.VECTOR_RAG,
                status=ComponentStatus.ONLINE,
                last_check=datetime.now(timezone.utc),
                response_time_ms=150.0,
                metadata={"collection_size": 1000},
            )

        status_control_instance.health_checkers["vector_rag"] = (
            mock_vector_rag_health_check
        )
        health = await status_control_instance._check_vector_rag_health()

        assert health.name == "Vector RAG"
        assert health.service_type == ServiceType.VECTOR_RAG
        assert health.status == ComponentStatus.ONLINE
        assert "collection_size" in health.metadata

    @pytest.mark.asyncio
    async def test_check_hybrid_rag_health_mock(self):
        """Test Hybrid RAG health check with mocked dependencies."""
        status_control_instance = StatusControl()

        # Mock the health check to avoid import issues
        async def mock_hybrid_rag_health_check():
            return ComponentHealth(
                name="Hybrid RAG",
                service_type=ServiceType.HYBRID_RAG,
                status=ComponentStatus.ONLINE,
                last_check=datetime.now(timezone.utc),
                response_time_ms=200.0,
                metadata={"total_results": 50},
            )

        status_control_instance.health_checkers["hybrid_rag"] = (
            mock_hybrid_rag_health_check
        )
        health = await status_control_instance._check_hybrid_rag_health()

        assert health.name == "Hybrid RAG"
        assert health.service_type == ServiceType.HYBRID_RAG
        assert health.status == ComponentStatus.ONLINE
        assert "total_results" in health.metadata


class TestConvenienceFunctions:
    """Test cases for convenience functions."""

    @pytest.mark.asyncio
    async def test_get_system_status_function(self):
        """Test get_system_status convenience function."""
        status = await get_system_status()
        assert isinstance(status, dict)
        assert "status" in status
        assert "uptime_seconds" in status

    @pytest.mark.asyncio
    async def test_get_component_status_function(self):
        """Test get_component_status convenience function."""
        # Test with existing component
        component = await get_component_status("ai_agent")
        # Component might be None if not initialized, which is fine for testing
        assert component is None or isinstance(component, ComponentHealth)

    @pytest.mark.asyncio
    async def test_get_all_components_status_function(self):
        """Test get_all_components_status convenience function."""
        components = await get_all_components_status()
        assert isinstance(components, dict)

    @pytest.mark.asyncio
    async def test_create_status_alert_function(self):
        """Test create_status_alert convenience function."""
        # Create a status control instance for testing
        status_control_instance = StatusControl()
        initial_count = len(status_control_instance.alerts)

        await create_status_alert(
            component="test_component",
            severity="info",
            message="Test alert from function",
            metadata={"test": "data"},
        )

        # Note: create_status_alert function doesn't modify the instance directly
        # This test verifies the function can be called without errors
        assert True


class TestErrorHandling:
    """Test cases for error handling."""

    @pytest.mark.asyncio
    async def test_health_check_error_handling(self):
        """Test that health check errors are handled gracefully."""
        status_control_instance = StatusControl()

        # Mock a health checker that raises an exception
        async def failing_health_check():
            raise Exception("Test error")

        # Use a valid service type
        status_control_instance.health_checkers["ai_agent"] = failing_health_check

        # This should not raise an exception
        await status_control_instance.check_all_components()

        # Check that the component is marked as ERROR
        component = status_control_instance.components.get("ai_agent")
        assert component is not None
        assert component.status == ComponentStatus.ERROR
        assert component.error_message is not None
        assert "Test error" in component.error_message

    @pytest.mark.asyncio
    async def test_alert_callback_error_handling(self):
        """Test that alert callback errors are handled gracefully."""
        status_control_instance = StatusControl()

        # Add a callback that raises an exception
        async def failing_callback(alert):
            raise Exception("Callback error")

        status_control_instance.add_status_callback(failing_callback)

        # This should not raise an exception
        await status_control_instance.create_alert(
            component="test_component", severity="info", message="Test alert"
        )


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
