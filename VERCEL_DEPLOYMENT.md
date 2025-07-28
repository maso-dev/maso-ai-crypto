# Vercel Deployment Guide for FastAPI

## 🚀 Quick Deployment Steps

### 1. **Framework Selection in Vercel**
- **Framework Preset**: Select **"Other"** (not FastAPI - it's not in the list)
- **Root Directory**: Leave as default (your repo root)
- **Build Command**: Leave empty (Vercel will auto-detect)
- **Output Directory**: Leave empty

### 2. **Environment Variables**
Set these in Vercel Dashboard → Settings → Environment Variables:

```
OPENAI_API_KEY=your_openai_key
NEWSAPI_API_KEY=your_newsapi_key
TAVILY_API_KEY=your_tavily_key
BINANCE_API_KEY=your_binance_key
BINANCE_SECRET_KEY=your_binance_secret
MILVUS_TOKEN=your_milvus_token
```

### 3. **Deployment Configuration**
Your `vercel.json` is already configured correctly:
- Entry point: `api/index.py`
- Static files: `/static/`
- Function timeout: 30 seconds
- Cron jobs: Daily news population and health checks

### 4. **Build Process**
Vercel will:
1. Install dependencies from `requirements.txt`
2. Use `api/index.py` as the serverless function
3. Route all requests through the FastAPI app
4. Serve static files from `/static/`

### 5. **Troubleshooting**

#### If build fails:
- Check that all dependencies are in `requirements.txt`
- Ensure `api/index.py` exists and imports correctly
- Verify environment variables are set

#### If app doesn't work:
- Check Vercel function logs
- Test endpoints individually
- Verify API keys are working

### 6. **Post-Deployment**
- Your app will be available at: `https://your-project.vercel.app`
- Test the main endpoints:
  - `/` - Dashboard
  - `/admin/status` - System status
  - `/portfolio/assets` - Portfolio data
  - `/agent/insights` - Agent analysis

### 7. **Cron Jobs**
- Daily news population: 6 AM UTC
- Health checks: Every 6 hours

## 📁 File Structure for Vercel
```
maso-ai-crypto/
├── api/
│   └── index.py          # ← Vercel entry point
├── static/               # ← Static files
├── templates/            # ← Jinja2 templates
├── routers/              # ← FastAPI routers
├── utils/                # ← Utility modules
├── main.py               # ← FastAPI app
├── requirements.txt      # ← Dependencies
├── vercel.json           # ← Vercel config
└── README.md
```

## 🔧 Manual Deployment
If automatic deployment fails:

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Deploy manually**:
   ```bash
   vercel --prod
   ```

3. **Set environment variables**:
   ```bash
   vercel env add OPENAI_API_KEY
   vercel env add NEWSAPI_API_KEY
   # ... repeat for all keys
   ``` 
