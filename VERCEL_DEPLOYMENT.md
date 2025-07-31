# Vercel Deployment Guide

## Configuration Changes Made

Based on the working example at `hello_vercel_success/`, the following changes were made to ensure successful Vercel deployment:

### 1. Vercel Configuration (`vercel.json`)
- **Entry Point**: Changed from `index.py` to `main.py` to match working example
- **Build Configuration**: Uses `@vercel/python` builder
- **Routes**: All routes point to `/main.py`

### 2. Static Files Handling
- **Removed**: `app.mount("/static", StaticFiles(directory="static"), name="static")`
- **Added**: Custom static file handler similar to working example:
```python
@app.get("/static/{path:path}")
async def static_files(path: str):
    """Serve static files"""
    static_dir = Path("static")
    file_path = static_dir / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(str(file_path))
    return {"error": "File not found"}, 404
```

### 3. Dependencies (`requirements.txt`)
- **Pinned Versions**: Used exact versions matching working example
- **Core Dependencies**: 
  - `fastapi==0.104.1`
  - `uvicorn[standard]==0.24.0`
  - `jinja2==3.1.2`
  - `python-multipart==0.0.6`
- **Removed**: `tavily-python` (heavy dependency)
- **Added**: Required langchain packages for AI functionality

### 4. Health Check Endpoint
- **Added**: `/api/health` endpoint for deployment verification

## Deployment Steps

### 1. Environment Variables Setup
Set up the following environment variables in Vercel dashboard:

```bash
# Required for core functionality
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
OPENAI_API_KEY=your_openai_api_key
NEWS_API_KEY=your_news_api_key

# Optional for enhanced features
TAVILY_API_KEY=your_tavily_api_key
DATABASE_URL=sqlite:///cost_tracking.db
DEBUG=False
ENVIRONMENT=production
```

### 2. Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy (first time)
vercel

# Deploy to production
vercel --prod
```

### 3. Verify Deployment

1. **Health Check**: Visit `https://your-app.vercel.app/api/health`
2. **Main Dashboard**: Visit `https://your-app.vercel.app/`
3. **API Endpoints**: Test portfolio endpoints

## Key Differences from Working Example

| Aspect | Working Example | Our Project |
|--------|----------------|-------------|
| **Complexity** | Simple Hello World | Full portfolio analyzer |
| **Dependencies** | Minimal (4 packages) | Extended (15+ packages) |
| **Static Files** | Custom handler | Custom handler |
| **Entry Point** | `main.py` | `main.py` |
| **Routes** | Simple endpoints | Complex router structure |

## Troubleshooting

### Common Issues:

1. **500 Errors**: Check environment variables are set correctly
2. **Import Errors**: Ensure all dependencies are in `requirements.txt`
3. **Static Files**: Verify custom handler is working
4. **Timeout**: Heavy operations may timeout on serverless

### Debug Steps:

1. Check Vercel function logs in dashboard
2. Test health endpoint first
3. Verify environment variables
4. Check for missing dependencies

## Performance Considerations

- **Cold Starts**: Serverless functions may have cold start delays
- **Memory Limits**: Vercel has memory constraints (1024MB default)
- **Timeout**: Functions timeout after 10 seconds
- **File Size**: Large dependencies may cause deployment issues

## Success Indicators

✅ Health endpoint returns 200  
✅ Main dashboard loads  
✅ Static files serve correctly  
✅ API endpoints respond  
✅ No 500 errors in logs  

## Next Steps

1. Deploy and test basic functionality
2. Monitor performance and errors
3. Optimize heavy operations if needed
4. Add caching for expensive operations
5. Consider CDN for static assets 
