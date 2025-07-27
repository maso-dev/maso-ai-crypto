# 💰 Cost Tracking System Documentation

## Overview

The Cost Tracking System provides comprehensive monitoring and analysis of API usage costs across all services in the Crypto AI Platform. It tracks costs in real-time, provides alerts for budget thresholds, and offers detailed analytics for cost optimization.

## 🎯 Key Features

### ✅ Real-Time Cost Tracking
- **Automatic tracking** of all API calls
- **Real-time cost calculation** based on current rates
- **SQLite database** for persistent storage
- **Granular tracking** by service, endpoint, and model

### ✅ Cost Analytics
- **Daily summaries** with service breakdown
- **Monthly reports** with trend analysis
- **Projected costs** based on current usage
- **Service-specific analytics**

### ✅ Budget Alerts
- **Configurable thresholds** for daily/monthly costs
- **Service-specific alerts** for high usage
- **Real-time notifications** via API endpoints
- **Severity levels** (critical, high, medium)

### ✅ API Integration
- **RESTful endpoints** for cost data access
- **JSON responses** with structured data
- **Real-time updates** via dashboard
- **Historical data** analysis

## 🏗️ Architecture

### Core Components

```
utils/cost_tracker.py          # Main cost tracking system
routers/cost_tracking.py       # FastAPI endpoints
templates/dashboard.html       # UI integration
static/css/style.css          # Cost tracking styles
```

### Database Schema

```sql
-- API calls table
CREATE TABLE api_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service TEXT NOT NULL,           -- openai, tavily, newsapi, milvus
    endpoint TEXT NOT NULL,          -- gpt-4-turbo, search, everything, etc.
    timestamp TEXT NOT NULL,         -- ISO format
    tokens_input INTEGER,            -- Input tokens (for OpenAI)
    tokens_output INTEGER,           -- Output tokens (for OpenAI)
    cost_usd REAL NOT NULL,          -- Calculated cost
    success BOOLEAN NOT NULL,        -- Call success status
    error_message TEXT,              -- Error details if failed
    metadata TEXT                    -- JSON metadata
);

-- Daily costs summary table
CREATE TABLE daily_costs (
    date TEXT PRIMARY KEY,
    total_cost REAL NOT NULL,
    openai_cost REAL NOT NULL,
    tavily_cost REAL NOT NULL,
    newsapi_cost REAL NOT NULL,
    milvus_cost REAL NOT NULL,
    call_count INTEGER NOT NULL
);
```

## 💵 Cost Rates

### Current Pricing (as of 2024)

| Service | Model/Endpoint | Input Cost | Output Cost | Per Call |
|---------|---------------|------------|-------------|----------|
| **OpenAI** | gpt-4-turbo | $0.01/1K | $0.03/1K | - |
| **OpenAI** | gpt-4 | $0.03/1K | $0.06/1K | - |
| **OpenAI** | gpt-3.5-turbo | $0.0015/1K | $0.002/1K | - |
| **OpenAI** | text-embedding-ada-002 | $0.0001/1K | - | - |
| **Tavily** | search | - | - | $0.01 |
| **NewsAPI** | everything | - | - | $0.001 |
| **Milvus** | insert/search | - | - | $0.00 (free tier) |

### Cost Calculation Examples

```python
# OpenAI GPT-4-turbo: 1000 input + 500 output tokens
cost = (1000/1000) * 0.01 + (500/1000) * 0.03 = $0.025

# Tavily search: 1 call
cost = $0.01

# NewsAPI: 1 call
cost = $0.001
```

## 🔌 API Endpoints

### Cost Summary Endpoints

#### GET `/costs/daily`
Get daily cost summary for a specific date or today.

**Query Parameters:**
- `date` (optional): Date in YYYY-MM-DD format

**Response:**
```json
{
  "date": "2024-01-15",
  "total_cost": 0.036,
  "call_count": 3,
  "service_costs": {
    "openai": 0.025,
    "tavily": 0.01,
    "newsapi": 0.001,
    "milvus": 0.0
  },
  "service_breakdown": {
    "openai": {"calls": 1, "cost": 0.025},
    "tavily": {"calls": 1, "cost": 0.01},
    "newsapi": {"calls": 1, "cost": 0.001}
  }
}
```

#### GET `/costs/monthly/{year}/{month}`
Get monthly cost summary.

**Response:**
```json
{
  "year": 2024,
  "month": 1,
  "total_cost": 0.036,
  "call_count": 3,
  "service_costs": {
    "openai": 0.025,
    "tavily": 0.01,
    "newsapi": 0.001,
    "milvus": 0.0
  }
}
```

#### GET `/costs/current-month`
Get current month summary with projections.

**Response:**
```json
{
  "monthly": {...},
  "today": {...},
  "projected_monthly": {
    "total_cost": 0.04,
    "call_count": 3
  }
}
```

### Detailed Analytics

#### GET `/costs/recent`
Get recent API calls.

**Query Parameters:**
- `limit` (optional): Number of calls to return (default: 50)

**Response:**
```json
[
  {
    "service": "openai",
    "endpoint": "gpt-4-turbo",
    "timestamp": "2024-01-15T10:30:00Z",
    "tokens_input": 1000,
    "tokens_output": 500,
    "cost_usd": 0.025,
    "success": true,
    "error_message": null
  }
]
```

#### GET `/costs/services`
Get service breakdown analysis.

**Response:**
```json
{
  "monthly_breakdown": {...},
  "daily_breakdown": {...},
  "service_stats": {...}
}
```

### Alerts & Monitoring

#### GET `/costs/alerts`
Get cost alerts and warnings.

**Response:**
```json
{
  "alerts": [
    {
      "type": "warning",
      "message": "Daily cost exceeded $5: $5.25",
      "severity": "high"
    }
  ],
  "daily_cost": 5.25,
  "monthly_cost": 45.67,
  "thresholds": {
    "daily_warning": 5.0,
    "monthly_warning": 100.0,
    "service_warning": 2.0
  }
}
```

## 🎨 Dashboard Integration

### Cost Tracking Section

The dashboard includes a dedicated "💰 Cost Tracking & Usage" section that displays:

- **Current Month Cost**: Total cost for the current month
- **Today's Cost**: Cost for the current day
- **Projected Monthly**: Estimated monthly cost based on current usage
- **Total API Calls**: Number of API calls made
- **Service Breakdown**: Visual breakdown of costs by service
- **Cost Alerts**: Real-time alerts for budget thresholds

### Visual Elements

- **Cost Cards**: Display key metrics with crypto-themed styling
- **Progress Bars**: Visual representation of service costs
- **Alert Indicators**: Color-coded alerts (critical, high, medium)
- **Responsive Design**: Mobile-friendly layout

## 🔧 Integration Guide

### Automatic Tracking

The cost tracking system automatically tracks API calls when using the provided utilities:

```python
from utils.cost_tracker import track_openai_call, track_tavily_call, track_newsapi_call

# Track OpenAI calls
await track_openai_call(
    model="gpt-4-turbo",
    tokens_input=1000,
    tokens_output=500,
    metadata={"operation": "news_enrichment"}
)

# Track Tavily calls
await track_tavily_call(
    endpoint="search",
    metadata={"query": "bitcoin price"}
)

# Track NewsAPI calls
await track_newsapi_call(
    endpoint="everything",
    metadata={"terms": ["BTC", "ETH"]}
)
```

### Context Manager Usage

```python
from utils.cost_tracker import track_api_call

async with track_api_call(
    service="openai",
    endpoint="gpt-4-turbo",
    model="gpt-4-turbo",
    tokens_input=1000,
    tokens_output=500
):
    # Your API call here
    result = await openai_client.chat.completions.create(...)
```

### Manual Tracking

```python
from utils.cost_tracker import cost_tracker

# Manual tracking
await cost_tracker.track_call(
    service="openai",
    endpoint="gpt-4-turbo",
    model="gpt-4-turbo",
    tokens_input=1000,
    tokens_output=500,
    success=True,
    metadata={"custom": "data"}
)
```

## 📊 Monitoring & Alerts

### Default Thresholds

- **Daily Warning**: $5.00
- **Monthly Warning**: $100.00
- **Service Warning**: $2.00 per service

### Alert Types

- **Critical**: Monthly cost exceeded $100
- **High**: Daily cost exceeded $5
- **Medium**: Service-specific cost exceeded $2

### Custom Thresholds

You can modify thresholds in `utils/cost_tracker.py`:

```python
# In get_cost_alerts method
if daily["total_cost"] > 5.0:  # Modify this value
    alerts.append({
        "type": "warning",
        "message": f"Daily cost exceeded $5: ${daily['total_cost']:.2f}",
        "severity": "high"
    })
```

## 🚀 Performance Optimization

### Database Optimization

- **Indexed queries** for fast retrieval
- **Daily aggregation** to reduce query time
- **Efficient storage** with JSON metadata

### Caching Strategy

- **Daily summaries** cached in separate table
- **Real-time updates** for current day
- **Batch processing** for historical data

### Memory Management

- **Connection pooling** for database access
- **Async operations** for non-blocking calls
- **Efficient data structures** for cost calculation

## 🔒 Security Considerations

### Data Protection

- **No sensitive data** stored in cost tracking
- **Metadata sanitization** before storage
- **Access control** via API endpoints

### Privacy Compliance

- **No personal information** tracked
- **Service-level aggregation** only
- **Configurable retention** policies

## 📈 Future Enhancements

### Planned Features

- **Cost forecasting** with ML models
- **Budget management** with spending limits
- **Cost optimization** recommendations
- **Multi-currency** support
- **Export functionality** for accounting
- **Integration** with billing systems

### Advanced Analytics

- **Usage patterns** analysis
- **Cost trends** over time
- **Service efficiency** metrics
- **ROI calculations** for features

## 🛠️ Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check file permissions for `cost_tracking.db`
   - Ensure SQLite is available

2. **Cost Calculation Discrepancies**
   - Verify cost rates in `cost_rates` dictionary
   - Check token counting accuracy

3. **Missing Cost Data**
   - Ensure tracking calls are made
   - Check for exceptions in tracking functions

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Database Maintenance

```python
# Reset cost tracking database
import os
if os.path.exists("cost_tracking.db"):
    os.remove("cost_tracking.db")

# Reinitialize
from utils.cost_tracker import cost_tracker
cost_tracker.init_database()
```

## 📚 Additional Resources

- [OpenAI Pricing](https://openai.com/pricing)
- [Tavily Pricing](https://tavily.com/pricing)
- [NewsAPI Pricing](https://newsapi.org/pricing)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**💡 Pro Tip**: Monitor your costs regularly and set up alerts to avoid unexpected bills. The cost tracking system provides real-time visibility into your API usage, helping you optimize costs and stay within budget. 
