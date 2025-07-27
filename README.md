# 🚀 Agentic Crypto Broker

An AI-powered cryptocurrency portfolio management system with personalized trading recommendations.

## 🎯 **Features**

- **🤖 Agentic Intelligence**: AI-generated personalized trading recommendations
- **📊 Portfolio Analytics**: Real-time Binance integration with ROI tracking
- **📰 News RAG**: Vector-based crypto news search and analysis
- **💰 Cost Tracking**: API usage monitoring and budget management
- **🔍 REACT Validation**: Fact-checking and real-time data validation

## 🚀 **Quick Start**

### Local Development
```bash
# Clone and setup
git clone <your-repo>
cd maso-ai-crypto
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your_key"
export NEWSAPI_API_KEY="your_key"
export TAVILY_API_KEY="your_key"

# Run
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Vercel Deployment
1. Connect your GitHub repo to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push

## 📡 **API Endpoints**

### Core Endpoints
- `GET /` - Dashboard
- `GET /portfolio/assets` - Portfolio data
- `GET /agent/insights` - AI insights
- `GET /admin/status` - System status

### Agent Intelligence
- `POST /agent/analyze` - Full analysis
- `GET /agent/recommendations` - Trading recommendations
- `GET /agent/market-sentiment` - Market sentiment

### News & RAG
- `POST /crypto_news/populate` - Populate news database
- `GET /crypto_news/search` - Search news

## 🧪 **Testing**

```bash
# Run tests
pytest tests/

# Run specific tests
pytest tests/test_agent.py
pytest tests/test_api.py
```

## 🔧 **Environment Variables**

Required for Vercel:
```env
OPENAI_API_KEY=your_openai_key
NEWSAPI_API_KEY=your_newsapi_key
TAVILY_API_KEY=your_tavily_key
```

Optional:
```env
BINANCE_API_KEY=your_binance_key
BINANCE_SECRET_KEY=your_binance_secret
MILVUS_URI=your_milvus_uri
```

## 📊 **Current State**

✅ **Implemented**:
- Agent Decision Engine
- Portfolio integration
- News RAG system
- Cost tracking
- REACT validation
- Vercel deployment ready

🚧 **Next Steps**:
- Neo4j integration
- React frontend
- Advanced analytics

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test with `pytest tests/`
5. Submit PR

---

**Built for Vercel deployment with ❤️** 
