# 🚀 Deployment Guide - AI Crypto Broker MVP

## **📋 Prerequisites**

### **Required Environment Variables**
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# News APIs
NEWSAPI_KEY=your_newsapi_key
TAVILY_API_KEY=your_tavily_api_key

# LiveCoinWatch API
LIVECOINWATCH_API_KEY=your_livecoinwatch_api_key

# Vector Database (Optional for MVP)
MILVUS_URI=http://localhost:19530

# LangSmith Tracing (Optional)
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=your_project_name
```

---

## **🎯 Replit Deployment**

### **1. Create New Replit**
1. Go to [replit.com](https://replit.com)
2. Click "Create Repl"
3. Choose "Python" template
4. Name: `ai-crypto-broker-mvp`

### **2. Upload Project Files**
```bash
# Clone or upload all project files
# Ensure these files are present:
- main.py
- requirements.txt
- .replit
- replit.nix
- templates/
- static/
- utils/
- routers/
```

### **3. Configure Environment Variables**
1. Go to "Tools" → "Secrets"
2. Add all required environment variables
3. Ensure variable names match exactly

### **4. Install Dependencies**
```bash
# Replit will auto-install, but verify:
pip install -r requirements.txt
```

### **5. Run Application**
```bash
# Replit will auto-run based on .replit config
# Or manually:
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### **6. Access Application**
- **URL**: `https://your-repl-name.your-username.repl.co`
- **Port**: 8000 (auto-configured)

---

## **🌐 Vercel Deployment**

### **1. Prepare for Vercel**
```bash
# Ensure these files exist:
- vercel.json
- requirements.txt
- main.py
```

### **2. Install Vercel CLI**
```bash
npm install -g vercel
```

### **3. Deploy to Vercel**
```bash
# Login to Vercel
vercel login

# Deploy
vercel

# Follow prompts:
# - Project name: ai-crypto-broker-mvp
# - Directory: ./
# - Override settings: No
```

### **4. Configure Environment Variables**
1. Go to Vercel Dashboard
2. Select your project
3. Go to "Settings" → "Environment Variables"
4. Add all required variables

### **5. Redeploy with Environment Variables**
```bash
vercel --prod
```

### **6. Access Production URL**
- **URL**: `https://your-project-name.vercel.app`

---

## **🔧 Local Development Setup**

### **1. Create Virtual Environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Set Environment Variables**
```bash
# Create .env file
cp .env.example .env
# Edit .env with your API keys
```

### **4. Run Development Server**
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### **5. Access Local Application**
- **URL**: `http://localhost:8000`

---

## **📊 Health Check Endpoints**

### **Test All Endpoints**
```bash
# Health Check
curl http://localhost:8000/health

# Portfolio Data
curl http://localhost:8000/api/cache/portfolio/livecoinwatch

# Alpha Signals
curl http://localhost:8000/api/cache/signals/latest

# News Summary
curl http://localhost:8000/api/cache/news/latest-summary

# Technical Analysis
curl http://localhost:8000/api/technical-analysis/BTC

# Admin Status
curl http://localhost:8000/api/admin/mvp-status
```

---

## **🚨 Troubleshooting**

### **Common Issues**

#### **1. Module Import Errors**
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run from project root
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

#### **2. API Key Errors**
```bash
# Verify environment variables
echo $OPENAI_API_KEY
echo $NEWSAPI_KEY
echo $LIVECOINWATCH_API_KEY

# Check .env file exists and is loaded
```

#### **3. Port Already in Use**
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or use different port
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

#### **4. Replit Issues**
```bash
# Clear cache and restart
# Tools → "Restart Repl"

# Check logs
# Console tab for error messages
```

#### **5. Vercel Issues**
```bash
# Check build logs
vercel logs

# Redeploy
vercel --prod

# Check function timeout
# Increase maxDuration in vercel.json
```

---

## **🔒 Security Considerations**

### **Environment Variables**
- ✅ Never commit API keys to git
- ✅ Use environment variables for all secrets
- ✅ Rotate API keys regularly
- ✅ Use least privilege access

### **API Rate Limits**
- ⚠️ Monitor LiveCoinWatch API usage
- ⚠️ Monitor NewsAPI rate limits
- ⚠️ Implement request caching
- ⚠️ Add rate limiting middleware

### **Data Privacy**
- ✅ No sensitive data in logs
- ✅ Secure API endpoints
- ✅ Input validation
- ✅ Error handling without data exposure

---

## **📈 Performance Optimization**

### **Caching Strategy**
```python
# Implement Redis caching for:
- API responses
- Technical indicators
- News summaries
- Portfolio data
```

### **Database Optimization**
```python
# For production:
- Use PostgreSQL for structured data
- Use Redis for caching
- Use Milvus for vector search
- Implement connection pooling
```

### **API Optimization**
```python
# Implement:
- Request batching
- Response compression
- Pagination
- Rate limiting
```

---

## **🎯 Production Checklist**

### **Pre-Deployment**
- [ ] All environment variables configured
- [ ] API keys tested and working
- [ ] All endpoints returning data
- [ ] Error handling implemented
- [ ] Logging configured

### **Post-Deployment**
- [ ] Health check endpoints working
- [ ] All pages loading correctly
- [ ] Real-time data updating
- [ ] AI agent flow executing
- [ ] Charts rendering properly

### **Monitoring**
- [ ] Set up error tracking
- [ ] Monitor API usage
- [ ] Track performance metrics
- [ ] Set up alerts for failures

---

## **🚀 Quick Deploy Commands**

### **Replit**
```bash
# 1. Upload files to Replit
# 2. Add environment variables
# 3. Run: python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### **Vercel**
```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Deploy
vercel --prod

# 3. Add environment variables in dashboard
```

### **Local**
```bash
# 1. Setup environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure .env file
# 3. Run server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

**🎉 Ready for Production Deployment!** 
