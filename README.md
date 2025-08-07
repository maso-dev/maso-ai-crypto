# 🎓 AI-Powered Crypto Broker MVP

> **Advanced AI Agent Capabilities with LangChain, LangGraph, and Hybrid RAG Architecture**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-orange.svg)](https://langchain.com)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](https://github.com/your-username/maso-ai-crypto)

## **🚀 Quick Start**

### **Local Development**
```bash
# Clone repository
git clone https://github.com/your-username/maso-ai-crypto.git
cd maso-ai-crypto

# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp env.example .env
# Edit .env with your API keys

# Run development server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### **Access Application**
- **Local**: http://localhost:8000
- **Welcome Page**: System overview and portfolio
- **Dashboard**: Real-time portfolio and market analysis
- **Brain Dashboard**: AI agent flow visualization
- **Admin**: System health and configuration

---

## **🎯 System Overview**

### **Key Features**
- **🤖 AI Agent Intelligence**: LangGraph-based decision making with confidence scoring
- **📊 Real-time Data**: LiveCoinWatch API integration with $115K+ portfolio
- **🔍 Hybrid RAG System**: Vector and graph-based knowledge retrieval
- **📰 Multi-source News**: NewsAPI + Tavily with AI-powered quality filtering
- **🎨 Professional UI**: Apple Liquid Glass Design System
- **⚡ Production Ready**: FastAPI with comprehensive error handling

### **Technology Stack**
- **Backend**: FastAPI, Python 3.9+, Uvicorn
- **AI Framework**: LangChain, LangGraph, OpenAI
- **Data Sources**: LiveCoinWatch, NewsAPI, Tavily
- **Vector Database**: Milvus (optional)
- **Frontend**: HTML5, CSS3, JavaScript, Chart.js
- **Deployment**: Replit, Vercel

---

## **📚 Documentation**

### **🎯 Capstone Presentation**
- **[DEMO_SCRIPT.md](DEMO_SCRIPT.md)** - Complete 15-20 minute presentation guide
- **[CAPSTONE_READY.md](CAPSTONE_READY.md)** - System status and readiness summary

### **🚀 Deployment**
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete deployment instructions
- **[vercel.json](vercel.json)** - Vercel configuration
- **[.replit](.replit)** - Replit configuration
- **[replit.nix](replit.nix)** - Replit dependencies

### **📖 Technical Documentation**
- **[SYSTEM_DOCUMENTATION.md](SYSTEM_DOCUMENTATION.md)** - Comprehensive technical architecture
- **[docs/](docs/)** - Additional documentation and historical plans

### **🧪 Testing**
- **[tests/](tests/)** - All test files and test suites
- **pytest.ini** - Test configuration

---

## **🏗️ Project Structure**

```
maso-ai-crypto/
├── 📁 docs/                    # Documentation
│   ├── 📁 plans/              # Development plans
│   ├── 📁 deployment/         # Deployment guides
│   ├── 📁 architecture/       # Architecture docs
│   └── 📁 old/                # Historical docs
├── 📁 tests/                  # Test files
│   ├── test_api.py           # API tests
│   ├── test_dashboard.py     # Frontend tests
│   └── test_*.py             # Component tests
├── 📁 templates/              # HTML templates
├── 📁 static/                 # CSS, JS, assets
├── 📁 routers/                # FastAPI routers
├── 📁 utils/                  # Core utilities
├── 📁 scripts/                # Utility scripts
├── 📁 .github/                # GitHub Actions
├── 🎯 main.py                 # FastAPI application
├── 📋 requirements.txt        # Python dependencies
├── 🔧 .env.example            # Environment template
├── 🚀 DEMO_SCRIPT.md          # Presentation guide
├── 📖 SYSTEM_DOCUMENTATION.md # Technical docs
├── 🚀 DEPLOYMENT_GUIDE.md     # Deployment guide
├── ✅ CAPSTONE_READY.md       # Readiness summary
└── 📝 README.md               # This file
```

---

## **🎯 Core Capabilities**

### **1. Portfolio Dashboard**
- **Real-time Data**: LiveCoinWatch integration with $115K+ portfolio
- **Interactive Charts**: Performance and allocation visualization
- **Technical Analysis**: RSI, MACD, support/resistance levels
- **Portfolio Builder**: Asset selection interface

### **2. AI Agent Brain**
- **LangGraph Flow**: Step-by-step reasoning visualization
- **News Gathering**: 25 articles, 8 quality filtered
- **Processing Pipeline**: Summarization, enrichment, embeddings
- **Confidence Scoring**: Real-time AI agent confidence (0.85)

### **3. Alpha Signals**
- **AI-Generated Signals**: BTC BUY with 85% confidence
- **Technical Indicators**: RSI: 65, MACD: bullish
- **Risk Assessment**: Target prices and stop losses
- **Real-time Updates**: Live signal generation

### **4. Brotherhood Intelligence**
- **News Sentiment**: 45% positive, 23% negative
- **Multi-source News**: NewsAPI + Tavily integration
- **Quality Filtering**: AI-powered spam detection
- **Market Insights**: Real-time news processing

---

## **🔧 API Endpoints**

### **Core Endpoints**
```http
GET /api/cache/portfolio/livecoinwatch    # Portfolio data
GET /api/cache/signals/latest             # AI trading signals
GET /api/cache/news/latest-summary        # News analysis
GET /api/technical-analysis/{symbol}      # Technical indicators
```

### **AI Agent Endpoints**
```http
POST /api/ai-agent/trigger-news-gathering # News gathering
POST /api/ai-agent/execute-flow           # Flow execution
```

### **Admin Endpoints**
```http
GET /api/admin/mvp-status                 # System health
GET /api/admin/configuration              # API configurations
```

---

## **🚀 Deployment**

### **Replit Deployment**
1. Create new Replit with Python template
2. Upload project files
3. Configure environment variables in Secrets
4. Run: `python -m uvicorn main:app --host 0.0.0.0 --port 8000`

### **Vercel Deployment**
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod

# Configure environment variables in dashboard
```

### **Environment Variables**
```bash
# Required
OPENAI_API_KEY=your_openai_key
LIVECOINWATCH_API_KEY=your_livecoinwatch_key
NEWSAPI_KEY=your_newsapi_key
TAVILY_API_KEY=your_tavily_key

# Optional
MILVUS_URI=your_milvus_uri
LANGSMITH_API_KEY=your_langsmith_key
```

---

## **🧪 Testing**

### **Run Tests**
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=.
```

### **Test Coverage**
- **API Endpoints**: All endpoints tested
- **Frontend**: Dashboard functionality
- **AI Agent**: LangGraph flow testing
- **Data Pipeline**: Processing validation

---

## **📊 Performance**

### **Response Times**
- **API Endpoints**: < 2 seconds average
- **Chart Rendering**: < 1 second
- **AI Agent Flow**: < 30 seconds
- **Page Load**: < 3 seconds

### **Real-time Features**
- **Data Updates**: 15-30 second intervals
- **Live Charts**: Real-time price updates
- **AI Signals**: Continuous analysis
- **News Processing**: Real-time sentiment

---

## **🎯 Capstone Alignment**

### **✅ AI Agent Capabilities**
- **Multi-step Reasoning**: News → Classification → Processing → Analysis
- **Confidence Scoring**: Real-time confidence meters (0.85)
- **Decision Making**: AI-powered trading signals with reasoning
- **LangGraph Integration**: Full flow implementation

### **✅ System Architecture**
- **Scalable Design**: Microservice architecture with FastAPI
- **Error Handling**: Graceful degradation and auto-retry
- **Monitoring**: Real-time service health checks
- **Documentation**: Comprehensive API documentation

### **✅ User Experience**
- **Professional UI**: Apple Liquid Glass Design System
- **Real-time Updates**: Live data with smooth transitions
- **Interactive Features**: Charts, portfolio builder, AI agent controls
- **Responsive Design**: Works on all devices

---

## **🤝 Contributing**

### **Development Workflow**
1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Run tests: `pytest`
4. Commit changes: `git commit -m "feat: your feature description"`
5. Push and create pull request

### **Code Standards**
- **Python**: Type hints, async/await, Pydantic models
- **Frontend**: Apple Liquid Glass Design System
- **Testing**: Comprehensive test coverage
- **Documentation**: Clear API documentation

---

## **📄 License**

This project is part of a capstone project demonstrating advanced AI agent capabilities.

---

## **🎉 Status**

**✅ PRODUCTION READY** - All features implemented, tested, and documented.

**🚀 Ready for Capstone Presentation** - Complete demo script and documentation prepared.

**📚 Comprehensive Documentation** - Technical docs, deployment guides, and presentation materials.

---

**🎓 AI-Powered Crypto Broker MVP - Advanced AI Agent Capabilities with Real-time Data Integration** 
