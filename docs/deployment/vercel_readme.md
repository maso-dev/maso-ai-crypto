# 🚀 Crypto AI Platform - Vercel Deployment Guide

This guide will help you deploy your FastAPI-based crypto AI platform (including crypto news RAG and portfolio management) to Vercel and set it up as a scheduled cron job.

---

## 🧠 News Enrichment (AI Metadata)

**Every news chunk is now enriched with AI-powered metadata before being embedded and stored in Milvus:**
- `sentiment` (0.01–1.0): How positive/negative is the news for the market?
- `trust` (0.01–1.0): How trustworthy is the source/article?
- `categories`: List of fine-grained categories (e.g., DeFi, Regulation, Security, etc.)
- `macro_category`: Broad class (e.g., Macroeconomics, Geopolitics)
- `summary`: 1–2 sentence summary of the news

This metadata enables advanced filtering, ranking, and explainable recommendations downstream.

---

## 📋 Prerequisites

- [Vercel CLI](https://vercel.com/download) installed
- [Git](https://git-scm.com/) installed
- Your project code ready for deployment

## 🛠️ Step 1: Prepare Your FastAPI App for Vercel

### Project Structure

Your unified crypto AI platform includes both crypto news RAG and portfolio management services:

```
maso-ai-crypto/
├── main.py                    # Main FastAPI app
├── routers/
│   ├── crypto_news_rag.py     # News RAG endpoints
│   ├── portfolio.py           # Portfolio endpoints (future)
│   └── dashboard.py           # Dashboard endpoints
├── utils/
│   ├── newsapi.py             # News API utilities
│   ├── embedding.py           # OpenAI embeddings
│   ├── milvus.py              # Milvus vector database
│   └── binance_client.py      # Binance API client
├── static/                    # Static assets
├── templates/                 # HTML templates
├── api/
│   └── index.py               # Vercel entry point
├── vercel.json                # Vercel configuration
└── requirements.txt           # Python dependencies
```

### Create API Directory Structure

Create an `api` directory in your project root and add an entry point:

```bash
mkdir api
```

### Create `api/index.py`

```python
from main import app

# This exposes your unified FastAPI app to Vercel
# Includes both crypto news RAG and portfolio management services
```

### Create `vercel.json`

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "crons": [
    {
      "path": "/populate_crypto_news_rag",
      "schedule": "0 6 * * *"
    }
  ]
}
```

## 🔧 Step 2: Update Requirements

Ensure your `requirements.txt` includes all necessary dependencies:

```txt
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.2
openai==1.3.7
scikit-learn==1.3.2
pydantic==2.5.0
python-multipart==0.0.6
```

## 🔐 Step 3: Set Up Environment Variables

In your Vercel dashboard:

1. Go to your project → **Settings** → **Environment Variables**
2. Add the following variables:

| Variable Name | Description | Example |
|---------------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-...` |
| `NEWSAPI_KEY` | Your NewsAPI key | `your_newsapi_key` |
| `MILVUS_URI` | Milvus REST endpoint | `https://in03-9f01d93b384a0f7.serverless.gcp-us-west1.cloud.zilliz.com` |
| `MILVUS_TOKEN` | Milvus API token | `your_milvus_token` |
| `MILVUS_COLLECTION_NAME` | Milvus collection name | `crypto_news_rag` |
| `MILVUS_CLUSTER_NAME` | Milvus cluster name | `elmaso-free` |
| `BINANCE_API_KEY` | Binance API key (for portfolio) | `your_binance_key` |
| `BINANCE_SECRET_KEY` | Binance secret key (for portfolio) | `your_binance_secret` |

## 🚀 Step 4: Deploy to Vercel

### Install Vercel CLI (if not already installed)

```bash
npm i -g vercel
```

### Login to Vercel

```bash
vercel login
```

### Deploy Your Project

```bash
# Deploy to production
vercel --prod

# Or deploy to preview
vercel
```

## ⏰ Step 5: Configure Cron Job Schedule

The cron job is already configured in `vercel.json`. Here are some common schedule examples:

| Schedule | Description |
|----------|-------------|
| `0 6 * * *` | Every day at 6:00 AM UTC |
| `0 */6 * * *` | Every 6 hours |
| `0 0 * * 0` | Every Sunday at midnight |
| `0 9,18 * * *` | Twice daily at 9 AM and 6 PM |

To modify the schedule, edit the `crons` section in `vercel.json`:

```json
"crons": [
  {
    "path": "/populate_crypto_news_rag",
    "schedule": "0 6 * * *"
  }
]
```

## 🧪 Step 6: Test Your Deployment

### Test the Crypto News RAG Endpoint

```bash
curl -X POST "https://your-vercel-domain.vercel.app/populate_crypto_news_rag" \
  -H "Content-Type: application/json" \
  -d '{
    "terms": ["bitcoin", "ethereum", "crypto"],
    "chunking": {
      "method": "fixed",
      "chunk_size": 200,
      "overlap": 0
    }
  }'
```

### Expected Response

```json
{
  "inserted": 15,
  "updated": 0,
  "errors": null
}
```

### Test the Dashboard Endpoint

```bash
curl -X GET "https://your-vercel-domain.vercel.app/dashboard"
```

### Test Portfolio Endpoints (when implemented)

```bash
# Get portfolio balance
curl -X GET "https://your-vercel-domain.vercel.app/portfolio/balance"

# Get portfolio history
curl -X GET "https://your-vercel-domain.vercel.app/portfolio/history"
```

## 📊 Step 7: Monitor Your Cron Job

### Check Vercel Function Logs

1. Go to your Vercel dashboard
2. Navigate to **Functions** tab
3. Look for your cron job executions
4. Check logs for any errors or issues

### Verify Data in Milvus

Use the test script to verify data insertion:

```bash
python test_milvus_search.py
```

## 🔍 Troubleshooting

### Common Issues

1. **Environment Variables Not Set**
   - Ensure all required environment variables are set in Vercel dashboard
   - Check that variable names match exactly (case-sensitive)

2. **Cron Job Not Running**
   - Verify the cron schedule syntax
   - Check Vercel function logs for errors
   - Ensure the endpoint path is correct

3. **API Errors**
   - Check API key validity
   - Verify Milvus connection
   - Review function logs for detailed error messages

### Debug Commands

```bash
# Check Vercel deployment status
vercel ls

# View function logs
vercel logs

# Redeploy with debug info
vercel --debug
```

## 📚 API Reference

### Crypto News RAG Endpoints

#### `POST /populate_crypto_news_rag`

**Request Body (Recommended for Best Results):**
```json
{
  "terms": ["bitcoin", "ethereum", "crypto"],
  "chunking": {
    "method": "paragraph",
    "chunk_size": 200,
    "overlap": 0
  },
  "newsapi_key": "optional_override_key"
}
```

**Example cURL:**
```bash
curl -X POST "https://your-vercel-domain.vercel.app/populate_crypto_news_rag" \
  -H "Content-Type: application/json" \
  -d '{
    "terms": ["bitcoin", "ethereum", "crypto"],
    "chunking": {
      "method": "paragraph",
      "chunk_size": 200,
      "overlap": 0
    }
  }'
```

**Response:**
```json
{
  "inserted": 10,
  "updated": 0,
  "errors": null
}
```

**Each news chunk in Milvus will now include:**
```json
{
  "chunk_text": "...",
  "crypto_topic": "BTC",
  "source_url": "...",
  "published_at": 1710000000,
  "title": "...",
  "vector": [ ... ],
  "sparse_vector": { ... },
  "sentiment": 0.92,
  "trust": 0.88,
  "categories": ["Market Analysis & Trading", "Adoption & Institutional"],
  "macro_category": "Market Analysis & Trading",
  "summary": "Bitcoin price increased after ETF inflows hit record highs, suggesting a potential bull run."
}
```

#### `GET /search_crypto_news` (Future)

**Query Parameters:**
- `query`: Search query string
- `limit`: Number of results (default: 10)

**Response:**
```json
{
  "results": [
    {
      "title": "Bitcoin Price Analysis",
      "content": "Latest analysis shows...",
      "source_url": "https://...",
      "published_at": 1640995200,
      "similarity_score": 0.95
    }
  ]
}
```

### Portfolio Management Endpoints (Future)

#### `GET /portfolio/balance`

**Response:**
```json
{
  "total_value_usd": 15000.50,
  "assets": [
    {
      "symbol": "BTC",
      "amount": 0.5,
      "value_usd": 12000.00
    }
  ]
}
```

#### `GET /portfolio/history`

**Query Parameters:**
- `days`: Number of days to fetch (default: 30)

**Response:**
```json
{
  "history": [
    {
      "date": "2024-01-01",
      "total_value": 14000.00,
      "change_24h": 500.00
    }
  ]
}
```

### Dashboard Endpoint

#### `GET /dashboard`

**Response:**
```json
{
  "portfolio_summary": {
    "total_value": 15000.50,
    "change_24h": 500.00
  },
  "recent_news": [
    {
      "title": "Latest Crypto News",
      "published_at": 1640995200
    }
  ]
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `terms` | Array[string] | Yes | Search terms for crypto news |
| `chunking.method` | string | Yes | Chunking method ("fixed", "sentence", "paragraph") |
| `chunking.chunk_size` | integer | No | Size of text chunks (default: 200) |
| `chunking.overlap` | integer | No | Overlap between chunks (default: 0) |
| `newsapi_key` | string | No | Override NewsAPI key from environment |

## 🔗 Useful Links

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Cron Jobs](https://vercel.com/docs/cron-jobs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Milvus REST API](https://milvus.io/docs/restful_api.md)
- [NewsAPI Documentation](https://newsapi.org/docs)

## 🎯 Benefits of Unified App Architecture

### Why Single App?

- ✅ **Simplified deployment** - One Vercel project, one set of environment variables
- ✅ **Shared resources** - Common utilities, database connections, API keys
- ✅ **Unified dashboard** - Combined view of news and portfolio data
- ✅ **Cost effective** - Single deployment, shared infrastructure
- ✅ **Easier maintenance** - One codebase to manage

### Service Integration

- **Crypto News RAG** - Fetches, processes, and stores crypto news with AI embeddings
- **Portfolio Management** - Tracks crypto portfolio performance and history
- **Unified Dashboard** - Combines both services for comprehensive crypto insights

## 📝 Notes

- The cron job runs serverless and has execution time limits
- Monitor your API usage to avoid rate limits
- Consider implementing error handling and retry logic
- Keep your API keys secure and rotate them regularly
- The unified app allows for easy expansion of crypto-related features

---

**🎉 Your unified crypto AI platform is now deployed and will automatically populate your Milvus database with fresh crypto news while providing portfolio management capabilities!**



