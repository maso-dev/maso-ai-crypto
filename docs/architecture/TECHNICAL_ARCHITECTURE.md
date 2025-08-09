# 🏗️ Technical System Architecture

## **System Overview**
The Masonic AI Crypto Broker is built on a microservices architecture with hybrid RAG capabilities, real-time data processing, and AI-powered analysis.

## **🏗️ Technical Architecture Diagram**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Web Browser / Mobile App                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Welcome   │  │  Dashboard  │  │    Admin    │  │Brain Dashboard│          │
│  │    Page     │  │             │  │             │  │             │          │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            API GATEWAY LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│  FastAPI Application (main.py)                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │  Middleware Stack                                                          │ │
│  │  ├─ CORS Handling                                                          │ │
│  │  ├─ Rate Limiting                                                          │ │
│  │  ├─ Authentication (Future)                                                │ │
│  │  └─ Error Handling                                                         │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │  Router Layer                                                              │ │
│  │  ├─ /api/portfolio     → Portfolio Analysis                               │ │
│  │  ├─ /api/opportunities → Trading Signals                                  │ │
│  │  ├─ /api/news-briefing → News Analysis                                    │ │
│  │  ├─ /api/technical-*   → Technical Analysis                               │ │
│  │  ├─ /admin/*           → System Monitoring                                │ │
│  │  └─ /brain/*           → AI Agent Control                                 │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           BUSINESS LOGIC LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │  AI Agent System (LangGraph)                                              │ │
│  │  ├─ Market Analysis Agent                                                 │ │
│  │  ├─ Trading Signal Agent                                                  │ │
│  │  ├─ News Sentiment Agent                                                  │ │
│  │  └─ Portfolio Optimization Agent                                          │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │  Hybrid RAG System                                                        │ │
│  │  ├─ Vector RAG (Milvus)                                                   │ │
│  │  │  ├─ Semantic Search                                                    │ │
│  │  │  ├─ Embedding Generation                                               │ │
│  │  │  └─ Similarity Scoring                                                 │ │
│  │  └─ Graph RAG (Neo4j)                                                     │ │
│  │      ├─ Entity Relationships                                              │ │
│  │      ├─ Market Correlations                                               │ │
│  │      └─ Network Analysis                                                  │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │  Data Processing Pipeline                                                  │ │
│  │  ├─ News Ingestion (NewsAPI + Tavily)                                     │ │
│  │  ├─ Price Data (LiveCoinWatch)                                            │ │
│  │  ├─ Portfolio Data (Binance API)                                          │ │
│  │  └─ Quality Filtering & Enrichment                                        │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            DATA STORAGE LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │  Vector Database (Milvus)                                                 │ │
│  │  ├─ News Embeddings                                                       │ │
│  │  ├─ Market Analysis                                                       │ │
│  │  └─ Portfolio Insights                                                    │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │  Graph Database (Neo4j)                                                   │ │
│  │  ├─ Crypto Entity Graph                                                   │ │
│  │  ├─ Market Relationships                                                  │ │
│  │  └─ News Entity Network                                                   │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │  Cache Layer (SQLite + Redis)                                             │ │
│  │  ├─ News Cache                                                            │ │
│  │  ├─ Price Cache                                                           │ │
│  │  └─ Analysis Cache                                                        │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL SERVICES LAYER                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │  Data Providers                                                            │ │
│  │  ├─ NewsAPI (Crypto News)                                                 │ │
│  │  ├─ LiveCoinWatch (Price Data)                                            │ │
│  │  ├─ Tavily (Web Search)                                                   │ │
│  │  └─ Binance (Portfolio Data)                                              │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │  AI Services                                                               │ │
│  │  ├─ OpenAI (GPT-4)                                                        │ │
│  │  ├─ LangSmith (Tracing)                                                   │ │
│  │  └─ LangChain (Orchestration)                                             │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## **🔐 Authentication & Security Flow**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───▶│  Rate      │───▶│  API Key   │───▶│  Endpoint   │
│  Request    │    │  Limiter   │    │ Validation │    │  Access     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### **Security Features**
- **Rate Limiting**: Per-IP request throttling
- **API Key Validation**: Secure key management
- **Input Sanitization**: XSS and injection protection
- **Error Handling**: Secure error messages

## **📊 Data Flow Architecture**

### **1. News Ingestion Pipeline**
```
NewsAPI/Tavily → Quality Filter → Enrichment → Vector DB → Graph DB → Cache
```

### **2. Portfolio Analysis Pipeline**
```
Binance API → LiveCoinWatch → Technical Analysis → AI Agent → RAG Search → Response
```

### **3. Trading Signal Pipeline**
```
Market Data → Technical Indicators → AI Analysis → RAG Context → Signal Generation
```

## **⚡ Performance Optimization**

### **Caching Strategy**
- **L1 Cache**: In-memory (Redis)
- **L2 Cache**: SQLite persistent
- **Cache TTL**: 15 minutes for prices, 1 hour for news

### **Async Processing**
- **Non-blocking I/O**: All external API calls
- **Background Tasks**: News collection, analysis
- **Connection Pooling**: Database connections

### **Load Balancing**
- **Horizontal Scaling**: Multiple FastAPI instances
- **Database Sharding**: Milvus collections
- **CDN Integration**: Static asset delivery

## **🔧 Infrastructure Components**

### **Database Connections**
```python
# Connection pooling configuration
MILVUS_POOL_SIZE = 10
NEO4J_POOL_SIZE = 5
REDIS_POOL_SIZE = 20
```

### **API Rate Limits**
```python
# Rate limiting configuration
RATE_LIMIT_PER_MINUTE = 100
RATE_LIMIT_PER_HOUR = 1000
RATE_LIMIT_PER_DAY = 10000
```

### **Error Handling**
```python
# Graceful degradation
FALLBACK_TO_MOCK = True
RETRY_ATTEMPTS = 3
TIMEOUT_SECONDS = 30
```

## **🚀 Deployment Architecture**

### **Development Environment**
- **Local**: FastAPI + SQLite + Mock Services
- **Testing**: pytest + Mock APIs
- **Validation**: Integration tests

### **Production Environment**
- **Web Server**: FastAPI + Uvicorn
- **Database**: Milvus + Neo4j + Redis
- **Monitoring**: Admin dashboard + Health checks
- **Scaling**: Horizontal scaling ready

## **📈 Monitoring & Observability**

### **Health Checks**
- **API Endpoints**: /api/health
- **Database Status**: Connection monitoring
- **External Services**: API availability
- **System Metrics**: Memory, CPU, response times

### **Logging & Tracing**
- **LangSmith**: AI agent tracing
- **Structured Logging**: JSON format
- **Error Tracking**: Exception monitoring
- **Performance Metrics**: Response time tracking

## **🔮 Future Architecture Enhancements**

### **Phase 6: Advanced Features**
- **User Authentication**: JWT + OAuth
- **Real-time Updates**: WebSocket integration
- **Mobile API**: REST + GraphQL
- **Advanced Analytics**: ML model serving

### **Phase 7: Enterprise Features**
- **Multi-tenancy**: User isolation
- **Advanced Security**: RBAC + Audit logs
- **Compliance**: GDPR + SOC2
- **Integration**: Webhook system

---

**🎯 This technical architecture addresses all feedback points and provides a comprehensive view of the system's infrastructure-level interactions.**
