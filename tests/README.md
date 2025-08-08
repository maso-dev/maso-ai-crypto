# 🧪 Test Suite Documentation

## Overview
This directory contains comprehensive tests for the Masonic AI Crypto Broker system, organized by test type and functionality.

## Directory Structure

```
tests/
├── api/                    # API integration tests
│   ├── test_tavily.py     # Tavily search API tests
│   ├── test_livecoinwatch.py # LiveCoinWatch price API tests
│   ├── test_newsapi.py    # NewsAPI tests
│   └── test_neo4j.py      # Neo4j database tests
├── integration/           # End-to-end integration tests
├── unit/                  # Unit tests for individual components
└── README.md             # This file
```

## API Tests

### Tavily API Tests
- **test_tavily.py**: Basic Tavily API connectivity test
- **test_tavily_formats.py**: Tests different authentication formats
- **test_tavily_fixed.py**: Tests the fixed Tavily client
- **test_old_tavily.py**: Tests old API key compatibility

### LiveCoinWatch API Tests
- **test_livecoinwatch.py**: Basic LiveCoinWatch API test
- **test_livecoinwatch_processor.py**: Tests the LiveCoinWatch processor
- **test_livecoinwatch_map.py**: Tests the /coins/map endpoint
- **test_livecoinwatch_debug.py**: Debug API response structure

### Other API Tests
- **test_newsapi.py**: NewsAPI connectivity and rate limit tests
- **test_neo4j.py**: Neo4j database connection tests

## Running Tests

### Individual API Tests
```bash
# Test Tavily API
python tests/api/test_tavily.py

# Test LiveCoinWatch API
python tests/api/test_livecoinwatch.py

# Test NewsAPI
python tests/api/test_newsapi.py

# Test Neo4j
python tests/api/test_neo4j.py
```

### All API Tests
```bash
# Run all API tests
for test in tests/api/test_*.py; do
    echo "Running $test..."
    python "$test"
done
```

## Test Environment Setup

### Required Environment Variables
```bash
# API Keys
export TAVILY_API_KEY="your-tavily-key"
export LIVECOINWATCH_API_KEY="your-livecoinwatch-key"
export NEWSAPI_KEY="your-newsapi-key"

# Database
export NEO4J_URI="your-neo4j-uri"
export NEO4J_USERNAME="neo4j"
export NEO4J_PASSWORD="your-neo4j-password"

# AI Services
export OPENAI_API_KEY="your-openai-key"
export LANGSMITH_API_KEY="your-langsmith-key"
```

### Virtual Environment
```bash
# Activate virtual environment
source .venv/bin/activate

# Install test dependencies
pip install httpx asyncio neo4j
```

## Test Results Interpretation

### ✅ Success Indicators
- **Status 200**: API responding correctly
- **Real data returned**: Actual cryptocurrency prices, news articles, etc.
- **No authentication errors**: API keys working properly

### ❌ Failure Indicators
- **Status 401**: Invalid or expired API key
- **Status 429**: Rate limit exceeded
- **Status 500**: Server error
- **DNS errors**: Service unavailable

## Common Issues & Solutions

### Tavily API Issues
- **401 Unauthorized**: Update API key, use Bearer authentication
- **Rate limiting**: Check API plan limits

### LiveCoinWatch Issues
- **401 Unauthorized**: Verify API key format
- **Empty symbols**: Check symbol mapping in processor

### NewsAPI Issues
- **429 Rate Limited**: Wait for rate limit reset (24h for free tier)
- **No articles**: Check query parameters

### Neo4j Issues
- **DNS resolution**: Check if Aura instance is running
- **Connection timeout**: Verify credentials and network

## Maintenance

### Regular Testing Schedule
- **Daily**: Run basic connectivity tests
- **Weekly**: Run comprehensive API tests
- **Monthly**: Update test cases for new features

### Test Data Management
- Tests use minimal API calls to avoid rate limits
- Mock data available for development
- Real data validation for production

## Contributing

When adding new tests:
1. Follow the naming convention: `test_<service>_<purpose>.py`
2. Include proper error handling and logging
3. Add documentation for new test cases
4. Update this README with new test descriptions

