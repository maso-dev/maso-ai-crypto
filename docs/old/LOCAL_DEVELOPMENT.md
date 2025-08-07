# 🏛️ Masonic - Local Development Guide

## 🎯 **Why Local Development?**

Local development provides the best experience for testing real data and API integrations:

- ✅ **Full Binance API access** (no regional restrictions)
- ✅ **Real-time data testing** with actual portfolio data
- ✅ **Fast development cycle** with hot reload
- ✅ **Complete API testing** for all services
- ✅ **Debugging capabilities** with detailed logs

## 🚀 **Quick Start**

### **1. Environment Setup**
```bash
# Clone the repository
git clone https://github.com/maso-dev/maso-ai-crypto.git
cd maso-ai-crypto

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Environment Variables**
Create a `.env` file in the root directory:
```bash
# Required APIs
OPENAI_API_KEY=your_openai_api_key_here
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET_KEY=your_binance_secret_key_here
NEWSAPI_KEY=your_newsapi_key_here

# Optional: Development settings
DEBUG=true
LOG_LEVEL=INFO
```

### **3. Start Development Server**
```bash
# Start with hot reload
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Or with specific settings
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload --log-level debug
```

## 🌐 **Local Endpoints**

| Endpoint | Description | Status |
|----------|-------------|---------|
| `http://localhost:8000/` | Welcome page | ✅ Working |
| `http://localhost:8000/dashboard` | Smart dashboard (auto-detects real data) | ✅ Working |
| `http://localhost:8000/dashboard` | Smart dashboard (auto-detect) | ✅ Working |
| `http://localhost:8000/admin` | Admin interface | ✅ Working |
| `http://localhost:8000/admin_conf` | Admin API (JSON) | ✅ Working |

## 📊 **Service Status Monitoring**

### **Admin Dashboard**
Visit `http://localhost:8000/admin` to monitor all services:

- **🤖 OpenAI**: API key status and model testing
- **💰 Binance**: Account connectivity and portfolio data
- **📰 NewsAPI**: News fetching capabilities

### **Real-time Testing**
```bash
# Check service status
curl http://localhost:8000/admin_conf | python3 -m json.tool

# Test portfolio data
curl http://localhost:8000/api/portfolio | python3 -m json.tool

# Test smart dashboard detection
curl http://localhost:8000/dashboard | grep -i "demo"
```

## 🔧 **Development Features**

### **Smart Dashboard Detection**
The `/dashboard` endpoint automatically detects:
- **Real Binance data** → Live dashboard with API calls
- **Mock/No data** → Smart dashboard with mock data

### **Hot Reload**
The development server automatically reloads when you make changes to:
- Python files (`.py`)
- HTML templates (`.html`)
- Static files (CSS, JS)

### **Detailed Logging**
Local development includes comprehensive logging:
```
🏛️ Smart Dashboard: API keys configured: True
🏛️ Smart Dashboard: Total value: 28.29, Asset count: 2
🏛️ Smart Dashboard: Is mock data: False
🏛️ Smart Dashboard: Detected REAL data!
```

## 🎨 **UI Development**

### **Templates Structure**
```
templates/
├── welcome.html          # Welcome page
├── dashboard.html        # Live dashboard (API calls)
├── dashboard.html        # Smart dashboard (auto-detect)
└── admin.html           # Admin interface
```

### **Styling**
- **CSS**: `static/css/style.css`
- **Theme**: Masonic (dark, gold accents)
- **Responsive**: Mobile-friendly design

## 🔍 **Debugging**

### **Common Issues**

**1. API Key Issues**
```bash
# Check environment variables
echo $OPENAI_API_KEY
echo $BINANCE_API_KEY
echo $NEWSAPI_KEY
```

**2. Port Already in Use**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
python -m uvicorn main:app --port 8001 --reload
```

**3. Import Errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### **Log Analysis**
```bash
# Monitor logs in real-time
tail -f logs/app.log

# Filter specific service logs
grep "🏛️" logs/app.log
```

## 🚀 **Production vs Development**

| Feature | Local Development | Vercel/Replit |
|---------|------------------|---------------|
| **Binance API** | ✅ Full access | ❌ Regional restrictions |
| **Real Data** | ✅ Live portfolio | ❌ Mock data only |
| **Hot Reload** | ✅ Instant updates | ❌ Manual deployment |
| **Debugging** | ✅ Full logs | ❌ Limited access |
| **API Testing** | ✅ All services | ⚠️ Partial access |

## 📈 **Performance Optimization**

### **Local Development Tips**
1. **Use `.env` file** for environment variables
2. **Enable hot reload** for fast development
3. **Monitor admin dashboard** for service health
4. **Test with real data** for accurate results

### **API Rate Limits**
- **OpenAI**: 3,500 requests/minute
- **Binance**: 1,200 requests/minute
- **NewsAPI**: 1,000 requests/day (free tier)

## 🎯 **Next Steps**

1. **Set up all API keys** in `.env` file
2. **Test all endpoints** locally
3. **Monitor service health** via admin dashboard
4. **Develop new features** with real data
5. **Deploy to production** when ready

## 🔗 **Useful Commands**

```bash
# Start development
source .venv/bin/activate && python -m uvicorn main:app --reload

# Check service status
curl localhost:8000/admin_conf | python3 -m json.tool

# Test dashboard
curl localhost:8000/dashboard | grep -i "demo"

# Monitor logs
tail -f logs/app.log

# Update dependencies
pip install -r requirements.txt --upgrade
```

---

**🏛️ Happy coding with real data!** 🚀 
