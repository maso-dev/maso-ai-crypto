# 🏛️ Masonic Status Control System

A comprehensive monitoring and status management system for the crypto trading platform, providing real-time health checks, alerting, and performance metrics.

## 🚀 Features

### Core Monitoring
- **Real-time Component Health Checks**: Monitors all system components every 30 seconds
- **Multi-Status Support**: Online, Offline, Degraded, Maintenance, Error states
- **Automatic Alert System**: Creates alerts for status changes and errors
- **Performance Metrics**: Tracks response times, success rates, and system metrics

### Monitored Components
- **AI Agent**: LangGraph workflows and agent reasoning
- **Vector RAG**: Milvus vector database and semantic search
- **Hybrid RAG**: Combined vector and graph database operations
- **Real-time Data**: WebSocket connections and data streams
- **News Pipeline**: News processing and enrichment
- **Cost Tracking**: API usage and cost monitoring
- **LangSmith**: Tracing and monitoring integration
- **Binance API**: Trading data and portfolio access
- **NewsAPI**: News data retrieval
- **Database**: SQLite database health
- **WebSocket**: Real-time connection management

### API Endpoints

#### Status Endpoints
- `GET /status/overall` - Overall system status
- `GET /status/components` - All component statuses
- `GET /status/components/{component_name}` - Specific component status
- `POST /status/components/{component_name}/check` - Manual health check

#### Alert Endpoints
- `GET /status/alerts` - Recent system alerts
- `POST /status/alerts` - Create new alert
- `PUT /status/alerts/{alert_id}/resolve` - Resolve alert

#### Metrics Endpoints
- `GET /status/metrics` - System performance metrics
- `POST /status/metrics/update` - Update metrics

#### Control Endpoints
- `POST /status/control/refresh` - Refresh all components
- `GET /status/control/health` - Status control system health
- `GET /status/info` - System information

## 🛠️ Installation & Setup

### 1. Automatic Integration
The status control system is automatically integrated when you start the application:

```python
# The system is initialized in utils/status_control.py
from utils.status_control import status_control

# Background monitoring starts automatically
# Health checks run every 30 seconds
```

### 2. Manual Health Checks
You can trigger manual health checks:

```python
from utils.status_control import status_control

# Check all components
await status_control.check_all_components()

# Get overall status
status = await status_control.get_overall_status()
```

### 3. Creating Alerts
Create custom alerts for your application:

```python
from utils.status_control import create_status_alert

# Create an alert
await create_status_alert(
    component="my_component",
    severity="warning",
    message="High memory usage detected",
    metadata={"memory_usage": "85%"}
)
```

## 📊 Dashboard

### Access the Dashboard
Visit `/status-dashboard` to view the comprehensive status dashboard.

### Dashboard Features
- **Real-time Updates**: Auto-refreshes every 30 seconds
- **Component Status**: Visual indicators for all components
- **Alert Management**: View and resolve alerts
- **Performance Metrics**: System performance overview
- **Quick Actions**: Manual refresh and control options

### Dashboard Sections
1. **System Overview**: Overall health, uptime, and key metrics
2. **Component Status**: Individual component health indicators
3. **Recent Alerts**: Latest system alerts with severity levels
4. **Performance Metrics**: Request counts, success rates, response times
5. **Quick Actions**: Manual controls for system management

## 🔧 Configuration

### Environment Variables
The status control system respects these environment variables:

```bash
# LangSmith Integration
LANGSMITH_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=masonic-brain
LANGCHAIN_ORGANIZATION=your_org_id

# API Keys for Health Checks
BINANCE_API_KEY=your_binance_key
NEWSAPI_KEY=your_newsapi_key
OPENAI_API_KEY=your_openai_key

# Database
DATABASE_URL=sqlite:///cost_tracking.db
```

### Custom Health Checkers
Add custom health checkers for your components:

```python
from utils.status_control import StatusControl, ComponentHealth, ComponentStatus

class CustomStatusControl(StatusControl):
    async def _check_custom_component_health(self) -> ComponentHealth:
        try:
            # Your custom health check logic
            return ComponentHealth(
                name="Custom Component",
                service_type=ServiceType.CUSTOM,
                status=ComponentStatus.ONLINE,
                last_check=datetime.now(timezone.utc),
                metadata={"custom_metric": "value"}
            )
        except Exception as e:
            return ComponentHealth(
                name="Custom Component",
                service_type=ServiceType.CUSTOM,
                status=ComponentStatus.ERROR,
                last_check=datetime.now(timezone.utc),
                error_message=str(e)
            )
```

## 📈 Monitoring Integration

### LangSmith Integration
The status control system integrates with LangSmith for enhanced monitoring:

```python
# Automatic LangSmith health checks
if os.getenv("LANGSMITH_API_KEY"):
    # Test LangSmith connection
    # Monitor tracing and project status
    # Track agent performance
```

### Cost Tracking Integration
Monitor API usage and costs:

```python
# Automatic cost tracking health checks
from utils.cost_tracker import cost_tracker

# Monitor total costs, call counts, and database health
# Alert on high usage or cost thresholds
```

### Real-time Data Monitoring
Monitor WebSocket connections and data streams:

```python
# Monitor real-time data manager
from utils.realtime_data import realtime_manager

# Track active connections, stream health, and data flow
```

## 🚨 Alert System

### Alert Severities
- **Info**: General information and status updates
- **Warning**: Potential issues that need attention
- **Error**: Component failures or degraded performance
- **Critical**: System-critical issues requiring immediate action

### Alert Management
```python
# Get recent alerts
alerts = status_control.get_recent_alerts(limit=10)

# Resolve an alert
status_control.resolve_alert("alert_id")

# Create custom alerts
await create_status_alert(
    component="trading_engine",
    severity="critical",
    message="Trading engine stopped responding",
    metadata={"last_heartbeat": "2024-01-01T00:00:00Z"}
)
```

## 🔍 Health Check Details

### AI Agent Health Check
- Tests LangGraph workflow compilation
- Verifies agent task execution
- Monitors model availability and response times

### Vector RAG Health Check
- Tests Milvus connection and search functionality
- Verifies embedding model availability
- Monitors collection size and performance

### Hybrid RAG Health Check
- Tests both vector and graph database operations
- Verifies hybrid search functionality
- Monitors result quality and response times

### Real-time Data Health Check
- Tests WebSocket connection stability
- Monitors data stream health
- Verifies client connection management

## 📊 Metrics & Analytics

### System Metrics
- **Total Requests**: Overall system request count
- **Success Rate**: Percentage of successful operations
- **Average Response Time**: Mean response time in milliseconds
- **Active Connections**: Current WebSocket connections
- **Memory Usage**: System memory consumption
- **CPU Usage**: System CPU utilization
- **Uptime**: System uptime in seconds

### Component Metrics
- **Response Times**: Individual component response times
- **Error Rates**: Component-specific error rates
- **Availability**: Component uptime percentages
- **Performance**: Component-specific performance indicators

## 🛡️ Error Handling

### Graceful Degradation
The status control system is designed to handle failures gracefully:

```python
# If a component fails, it's marked as ERROR
# Other components continue to be monitored
# Alerts are created for failed components
# System continues to function with degraded components
```

### Fallback Mechanisms
- **Mock Data**: Uses mock data when external APIs are unavailable
- **Cached Results**: Uses cached health check results on failures
- **Retry Logic**: Automatic retry for transient failures
- **Circuit Breaker**: Prevents cascading failures

## 🔧 Development & Testing

### Running Tests
```bash
# Test status control system
python -m pytest tests/test_status_control.py

# Test specific components
python -m pytest tests/test_status_control.py::test_ai_agent_health
```

### Adding New Components
1. Add component to `ServiceType` enum
2. Implement health check method
3. Add to health checkers dictionary
4. Update dashboard template if needed

### Debugging
```python
# Enable debug logging
import logging
logging.getLogger('utils.status_control').setLevel(logging.DEBUG)

# Manual health check with debugging
health = await status_control._check_ai_agent_health()
print(f"AI Agent Health: {health}")
```

## 📚 API Reference

### StatusControl Class
```python
class StatusControl:
    async def check_all_components() -> None
    async def get_overall_status() -> Dict[str, Any]
    def get_component_status(component_name: str) -> Optional[ComponentHealth]
    def get_all_components_status() -> Dict[str, ComponentHealth]
    async def create_alert(component: str, severity: str, message: str, metadata: Optional[Dict[str, Any]] = None) -> None
    def get_recent_alerts(limit: int = 10) -> List[StatusAlert]
    def resolve_alert(alert_id: str) -> None
    def get_system_metrics() -> SystemMetrics
    def update_metrics(**kwargs) -> None
```

### ComponentHealth Class
```python
@dataclass
class ComponentHealth:
    name: str
    service_type: ServiceType
    status: ComponentStatus
    last_check: datetime
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
```

### StatusAlert Class
```python
class StatusAlert(BaseModel):
    id: str
    component: str
    severity: str
    message: str
    timestamp: datetime
    resolved: bool = False
    metadata: Dict[str, Any] = {}
```

## 🚀 Deployment

### Production Considerations
1. **Monitoring**: Set up external monitoring for the status control system itself
2. **Logging**: Configure proper logging for production environments
3. **Alerts**: Set up external alerting (email, Slack, etc.) for critical issues
4. **Metrics**: Export metrics to external monitoring systems
5. **Backup**: Ensure status data is backed up regularly

### Scaling
- The status control system is designed to be lightweight
- Health checks run asynchronously to avoid blocking
- Background monitoring uses minimal resources
- Can be extended to support distributed monitoring

## 🤝 Contributing

### Adding New Health Checks
1. Fork the repository
2. Add your health check method to `StatusControl`
3. Update the `ServiceType` enum if needed
4. Add tests for your health check
5. Update documentation
6. Submit a pull request

### Reporting Issues
- Use the GitHub issue tracker
- Include relevant logs and error messages
- Provide steps to reproduce the issue
- Include system information and environment details

## 📄 License

This status control system is part of the 🏛️ Masonic crypto trading platform and follows the same licensing terms.

---

**🏛️ Masonic Status Control System** - Comprehensive monitoring for informed trading decisions. 
