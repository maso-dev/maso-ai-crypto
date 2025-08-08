# 🚀 Masonic AI Crypto - Development Branch

## Quick Start (Replit/Local)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Copy `env.example` to `.env` and add your API keys:
```bash
cp env.example .env
```

Required API Keys:
- `OPENAI_API_KEY` - For AI analysis
- `LIVECOINWATCH_API_KEY` - For crypto prices
- `TAVILY_API_KEY` - For web search
- `NEWSAPI_KEY` - For news articles
- `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` - For graph database

### 3. Run the Application
```bash
python main.py
```

Or with uvicorn:
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Access the Application
- **Main Dashboard**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **Brain Dashboard**: http://localhost:8000/brain-dashboard

## Features

✅ **Real-time crypto data** (LiveCoinWatch)  
✅ **AI-powered analysis** (OpenAI + LangChain)  
✅ **News sentiment analysis** (NewsAPI + Tavily)  
✅ **Vector search** (Milvus)  
✅ **Graph database** (Neo4j)  
✅ **Admin transparency** (Real vs mock data indicators)  
✅ **Cache system** (Intelligent caching with fallbacks)  

## Current Status

- **6/7 services** using real data
- **Admin transparency** working
- **Cache system** operational
- **Local development** ready

## Troubleshooting

### Common Issues:
1. **API Rate Limits**: NewsAPI has daily limits, will auto-fallback
2. **Neo4j Connection**: Graph features work in mock mode if Neo4j unavailable
3. **Port Conflicts**: Change port in uvicorn command if 8000 is busy

### Logs:
Check console output for detailed error messages and service status.
