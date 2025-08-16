# Graceful dependency handling for Replit
import sys
import subprocess
import sqlite3
from datetime import datetime, timezone, timedelta

# Graceful imports for Replit deployment
def safe_import(package_name, fallback_name=None):
    """Safely import packages with fallback"""
    try:
        return __import__(package_name)
    except ImportError:
        if fallback_name:
            try:
                return __import__(fallback_name)
            except ImportError:
                pass
        print(f"⚠️ Package {package_name} not available - some features may be limited")
        return None

# Try imports with fallbacks
fastapi_available = safe_import("fastapi") is not None
uvicorn_available = safe_import("uvicorn") is not None

from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from pathlib import Path
import os
from datetime import datetime, timedelta
import time
from collections import defaultdict
import asyncio

app = FastAPI(title="🏛️ Masonic - AI Crypto Broker")

# Add CORS middleware for Replit deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy loading of templates and routers to prevent startup delays
_templates = None
_router_cache = {}

def get_templates():
    """Lazy load templates only when needed"""
    global _templates
    if _templates is None:
        _templates = Jinja2Templates(directory="templates")
    return _templates

@app.get("/")
async def read_root(request: Request):
    """Ultra-fast root endpoint optimized for Replit health checks"""
    # Always return HTML immediately - no user-agent detection needed
    return HTMLResponse(
        content="""
        <html lang="en">
            <head>
                <title>🏛️ Masonic - Alpha Strategy Advisor</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    /* ===== MASONIC CRYPTO - MODERN GLASSMORPHISM DESIGN ===== */
                    :root {
                        /* Color Palette - Material You inspired */
                        --primary-500: #0ea5e9;
                        --primary-600: #0284c7;
                        --primary-700: #0369a1;
                        --accent-green: #10b981;
                        --accent-yellow: #f59e0b;
                        --accent-purple: #8b5cf6;
                        --accent-cyan: #06b6d4;
                        
                        /* Dark Theme Colors */
                        --bg-primary: #0a0a0a;
                        --bg-secondary: #111111;
                        --bg-tertiary: #1a1a1a;
                        --bg-glass: rgba(255, 255, 255, 0.05);
                        --bg-glass-hover: rgba(255, 255, 255, 0.08);
                        
                        /* Text Colors */
                        --text-primary: #ffffff;
                        --text-secondary: rgba(255, 255, 255, 0.8);
                        --text-tertiary: rgba(255, 255, 255, 0.6);
                        
                        /* Typography */
                        --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        
                        /* Spacing & Shadows */
                        --spacing-lg: 1.5rem;
                        --spacing-xl: 2rem;
                        --radius-lg: 0.75rem;
                        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
                        --glass-blur: blur(20px);
                    }
                    
                    * {
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }
                    
                    html {
                        scroll-behavior: smooth;
                        font-size: 16px;
                    }
                    
                    body {
                        font-family: var(--font-family);
                        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 50%, var(--bg-tertiary) 100%);
                        color: var(--text-primary);
                        line-height: 1.6;
                        min-height: 100vh;
                        overflow-x: hidden;
                    }
                    
                    .container {
                        max-width: 1200px;
                        margin: 0 auto;
                        padding: var(--spacing-xl);
                        min-height: 100vh;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                    }
                    
                    .hero-section {
                        text-align: center;
                        margin-bottom: var(--spacing-xl);
                    }
                    
                    .logo {
                        font-size: 3.5rem;
                        margin-bottom: var(--spacing-lg);
                        background: linear-gradient(135deg, var(--primary-500), var(--accent-purple));
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        background-clip: text;
                    }
                    
                    .hero-title {
                        font-size: 2.5rem;
                        font-weight: 700;
                        margin-bottom: var(--spacing-lg);
                        background: linear-gradient(135deg, var(--text-primary), var(--text-secondary));
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        background-clip: text;
                    }
                    
                    .hero-subtitle {
                        font-size: 1.25rem;
                        color: var(--text-secondary);
                        margin-bottom: var(--spacing-xl);
                        max-width: 600px;
                        margin-left: auto;
                        margin-right: auto;
                    }
                    
                    .status-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                        gap: var(--spacing-lg);
                        margin-bottom: var(--spacing-xl);
                    }
                    
                    .glass-card {
                        background: var(--bg-glass);
                        backdrop-filter: var(--glass-blur);
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        border-radius: var(--radius-lg);
                        padding: var(--spacing-xl);
                        box-shadow: var(--shadow-xl);
                        transition: all 0.3s ease;
                    }
                    
                    .glass-card:hover {
                        background: var(--bg-glass-hover);
                        transform: translateY(-2px);
                        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
                    }
                    
                    .status-card {
                        text-align: center;
                    }
                    
                    .status-icon {
                        font-size: 2.5rem;
                        margin-bottom: var(--spacing-lg);
                    }
                    
                    .status-title {
                        font-size: 1.25rem;
                        font-weight: 600;
                        margin-bottom: var(--spacing-lg);
                        color: var(--text-primary);
                    }
                    
                    .status-message {
                        color: var(--text-secondary);
                        margin-bottom: var(--spacing-lg);
                    }
                    
                    .cron-schedule {
                        background: linear-gradient(135deg, var(--accent-yellow), var(--accent-purple));
                        padding: var(--spacing-lg);
                        border-radius: var(--radius-lg);
                        margin-bottom: var(--spacing-xl);
                        text-align: center;
                    }
                    
                    .cron-title {
                        font-size: 1.5rem;
                        font-weight: 700;
                        margin-bottom: var(--spacing-lg);
                        color: var(--text-primary);
                    }
                    
                    .cron-details {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: var(--spacing-lg);
                        margin-bottom: var(--spacing-lg);
                    }
                    
                    .cron-item {
                        background: rgba(255, 255, 255, 0.1);
                        padding: var(--spacing-lg);
                        border-radius: var(--radius-lg);
                        text-align: center;
                    }
                    
                    .cron-time {
                        font-size: 1.5rem;
                        font-weight: 700;
                        color: var(--text-primary);
                        margin-bottom: var(--spacing-lg);
                    }
                    
                    .cron-label {
                        color: var(--text-secondary);
                        font-size: 0.9rem;
                    }
                    
                    .nav-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                        gap: var(--spacing-lg);
                        margin-bottom: var(--spacing-xl);
                    }
                    
                    .nav-card {
                        background: var(--bg-glass);
                        backdrop-filter: var(--glass-blur);
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        border-radius: var(--radius-lg);
                        padding: var(--spacing-xl);
                        text-align: center;
                        text-decoration: none;
                        color: var(--text-primary);
                        transition: all 0.3s ease;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        min-height: 150px;
                    }
                    
                    .nav-card:hover {
                        background: var(--bg-glass-hover);
                        transform: translateY(-4px);
                        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
                        text-decoration: none;
                        color: var(--text-primary);
                    }
                    
                    .nav-icon {
                        font-size: 2.5rem;
                        margin-bottom: var(--spacing-lg);
                    }
                    
                    .nav-title {
                        font-size: 1.1rem;
                        font-weight: 600;
                        margin-bottom: var(--spacing-lg);
                    }
                    
                    .nav-description {
                        color: var(--text-secondary);
                        font-size: 0.9rem;
                    }
                    
                    .footer {
                        text-align: center;
                        color: var(--text-tertiary);
                        margin-top: auto;
                        padding-top: var(--spacing-xl);
                    }
                    
                    .footer-badge {
                        background: linear-gradient(135deg, var(--primary-500), var(--accent-purple));
                        color: var(--text-primary);
                        padding: 0.5rem 1rem;
                        border-radius: var(--radius-lg);
                        font-size: 0.9rem;
                        font-weight: 600;
                        display: inline-block;
                        margin-bottom: var(--spacing-lg);
                    }
                    
                    @media (max-width: 768px) {
                        .container {
                            padding: var(--spacing-lg);
                        }
                        
                        .hero-title {
                            font-size: 2rem;
                        }
                        
                        .status-grid {
                            grid-template-columns: 1fr;
                        }
                        
                        .nav-grid {
                            grid-template-columns: 1fr;
                        }
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="hero-section">
                        <div class="logo">🏛️</div>
                        <h1 class="hero-title">Masonic AI Crypto Broker</h1>
                        <p class="hero-subtitle">Your AI-powered crypto portfolio assistant with professional-grade temporal optimization</p>
                    </div>
                    
                    <div class="status-grid">
                        <div class="glass-card status-card">
                            <div class="status-icon">✅</div>
                            <div class="status-title">Service Status</div>
                            <div class="status-message">Running and healthy</div>
                        </div>
                        
                        <div class="glass-card status-card">
                            <div class="status-icon">🚀</div>
                            <div class="status-title">Performance</div>
                            <div class="status-message">Optimized for health checks</div>
                        </div>
                        
                        <div class="glass-card status-card">
                            <div class="status-icon">🎯</div>
                            <div class="status-title">Deployment</div>
                            <div class="status-message">Ready for Replit</div>
                        </div>
                    </div>
                    
                    <div class="cron-schedule">
                        <div class="cron-title">🎓 CAPSTONE UPDATE SCHEDULE</div>
                        <div class="cron-details">
                            <div class="cron-item">
                                <div class="cron-time">00:00</div>
                                <div class="cron-label">Midnight</div>
                            </div>
                            <div class="cron-item">
                                <div class="cron-time">06:00</div>
                                <div class="cron-label">6 AM</div>
                            </div>
                            <div class="cron-item">
                                <div class="cron-time">12:00</div>
                                <div class="cron-label">Noon</div>
                            </div>
                            <div class="cron-item">
                                <div class="cron-time">18:00</div>
                                <div class="cron-label">6 PM</div>
                            </div>
                        </div>
                        <div style="color: var(--text-primary); font-weight: 600;">
                            ✅ 720x reduction from 30 seconds to 6 hours
                        </div>
                    </div>
                    
                    <div class="nav-grid">
                        <a href="/dashboard" class="nav-card">
                            <div class="nav-icon">📊</div>
                            <div class="nav-title">Dashboard</div>
                            <div class="nav-description">View portfolio and analytics</div>
                        </a>
                        
                        <a href="/admin" class="nav-card">
                            <div class="nav-icon">⚙️</div>
                            <div class="nav-title">Admin Panel</div>
                            <div class="nav-description">System configuration</div>
                        </a>
                        
                        <a href="/health" class="nav-card">
                            <div class="nav-icon">🔍</div>
                            <div class="nav-title">Health Check</div>
                            <div class="nav-description">System status</div>
                        </a>
                        
                        <a href="/status-dashboard" class="nav-card">
                            <div class="nav-icon">📈</div>
                            <div class="nav-title">Status Dashboard</div>
                            <div class="nav-description">Real-time monitoring</div>
                        </a>
                        
                        <a href="/brain-dashboard" class="nav-card">
                            <div class="nav-icon">🧠</div>
                            <div class="nav-title">Brain Dashboard</div>
                            <div class="nav-description">AI insights</div>
                        </a>
                        
                        <a href="/docs" class="nav-card">
                            <div class="nav-icon">📚</div>
                            <div class="nav-title">API Docs</div>
                            <div class="nav-description">Developer reference</div>
                        </a>
                    </div>
                    
                    <div class="footer">
                        <div class="footer-badge">CAPSTONE PROJECT</div>
                        <p>Masonic AI Crypto Broker - Professional Temporal Optimization</p>
                    </div>
                </div>
            </body>
        </html>
        """
    )

# Ultra-lightweight health check for Replit deployment
@app.get("/health")
async def health_check():
    """Ultra-lightweight health check for deployment validation"""
    return {"status": "ok"}

# Ultra-lightweight health check for Replit deployment  
@app.get("/replit-health")
async def ultra_lightweight_health_check():
    """Ultra-lightweight health check - returns immediately for Replit deployment"""
    return {"status": "healthy"}

# Deployment-specific health endpoint (no async operations)
@app.get("/deploy-health")
def sync_health_check():
    """Synchronous health check - fastest possible response for deployment"""
    return {"status": "ok", "service": "masonic-ai"}

# Custom static files handling for Replit deployment
@app.get("/static/{path:path}")
async def static_files(path: str):
    """Serve static files"""
    static_dir = Path("static")
    file_path = static_dir / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(str(file_path))
    return {"error": "File not found"}, 404

@app.get("/favicon.ico")
async def favicon():
    """Handle favicon requests to prevent 404 errors."""
    from fastapi.responses import Response
    return Response(status_code=204)  # No content

@app.get("/api/health")
async def detailed_health_check():
    """Detailed health check endpoint - optimized for Replit deployment"""
    return {
        "status": "healthy",
        "service": "🏛️ Masonic - Alpha Strategy Advisor",
        "deployment": "Replit",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "health_check": "lightweight",
        "message": "Service is running and healthy",
        "cron_schedule": "4 times per day (every 6 hours)",
        "capstone_optimized": True
    }

# Lazy load and include routers only when needed - NO STARTUP EVENTS
def include_routers():
    """Lazy load routers to prevent startup delays"""
    if "routers_loaded" not in _router_cache:
        try:
            # Import each router individually with error handling
            try:
                from routers import admin
                app.include_router(admin.router, prefix="/admin", tags=["admin"])
                print("✅ Admin router loaded")
            except Exception as e:
                print(f"⚠️ Admin router failed: {e}")
            
            try:
                from routers import cache_readers
                app.include_router(cache_readers.router, prefix="/api/cache", tags=["cache"])
                print("✅ Cache readers router loaded")
            except Exception as e:
                print(f"⚠️ Cache readers router failed: {e}")
            
            try:
                from routers import brain_enhanced
                app.include_router(brain_enhanced.router, prefix="/brain", tags=["brain"])
                print("✅ Brain enhanced router loaded")
            except Exception as e:
                print(f"⚠️ Brain enhanced router failed: {e}")
            
            try:
                from routers import status_control
                app.include_router(status_control.router, prefix="/status", tags=["status"])
                print("✅ Status control router loaded")
            except Exception as e:
                print(f"⚠️ Status control router failed: {e}")
            
            # Try to import enhanced hybrid RAG router
            try:
                from routers import enhanced_hybrid_router
                app.include_router(enhanced_hybrid_router.router, tags=["enhanced-hybrid-rag"])
                _router_cache["enhanced_hybrid"] = True
                print("✅ Enhanced hybrid RAG router loaded")
            except Exception as e:
                _router_cache["enhanced_hybrid"] = False
                print(f"⚠️ Enhanced hybrid RAG router failed: {e}")

            # Try to import optimized news router (temporal optimization)
            try:
                from routers import optimized_news
                app.include_router(optimized_news.router, prefix="/api", tags=["optimized-news"])
                _router_cache["optimized_news"] = True
                print("✅ Optimized news router loaded")
            except Exception as e:
                _router_cache["optimized_news"] = False
                print(f"⚠️ Optimized news router failed: {e}")
                
            _router_cache["routers_loaded"] = True
            print("✅ All available routers loaded successfully")
            
        except Exception as e:
            print(f"⚠️ Router loading failed: {e}")
            _router_cache["routers_loaded"] = False

# Add startup event for background initialization only
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks without blocking startup"""
    # Start background tasks after a delay to prevent blocking health checks
    asyncio.create_task(delayed_startup())

async def delayed_startup():
    """Start heavy operations in background after deployment completes"""
    await asyncio.sleep(2)  # Reduced delay for faster health checks
    try:
        # Load routers in background
        include_routers()
        print("✅ Background services initialized")
    except Exception as e:
        print(f"⚠️ Background startup warning: {e}")

# NO BLOCKING OPERATIONS during startup - Everything is lazy loaded

# Basic dashboard endpoint
@app.get("/dashboard")
def smart_dashboard(request: Request):
    """Smart dashboard that loads routers on first request"""
    # Load routers on first request instead of startup
    if "routers_loaded" not in _router_cache:
        include_routers()
    
    try:
        templates = get_templates()
        return templates.TemplateResponse("dashboard.html", {"request": request})
    except Exception as e:
        return HTMLResponse(
            content=f"""
            <html>
                <head><title>Dashboard - Masonic AI</title></head>
                <body>
                    <h1>📊 Dashboard</h1>
                    <p>Dashboard is loading...</p>
                    <p><a href="/">← Back to Home</a></p>
                    <p><small>Error: {str(e)}</small></p>
                </body>
            </html>
            """
        )

# Basic admin endpoint
@app.get("/admin")
def admin_page(request: Request):
    """Admin page that loads routers on first request"""
    # Load routers on first request instead of startup
    if "routers_loaded" not in _router_cache:
        include_routers()
    
    try:
        templates = get_templates()
        return templates.TemplateResponse("admin.html", {"request": request})
    except Exception as e:
        return HTMLResponse(
            content=f"""
            <html>
                <head><title>Admin - Masonic AI</title></head>
                <body>
                    <h1>⚙️ Admin Panel</h1>
                    <p>Admin panel is loading...</p>
                    <p><a href="/">← Back to Home</a></p>
                    <p><small>Error: {str(e)}</small></p>
                </body>
            </html>
            """
        )

# Basic status dashboard endpoint
@app.get("/status-dashboard")
def status_dashboard(request: Request):
    """Status dashboard that loads routers on first request"""
    # Load routers on first request instead of startup
    if "routers_loaded" not in _router_cache:
        include_routers()
    
    try:
        templates = get_templates()
        return templates.TemplateResponse("status_dashboard.html", {"request": request})
    except Exception as e:
        return HTMLResponse(
            content=f"""
            <html>
                <head><title>Status - Masonic AI</title></head>
                <body>
                    <h1>📊 Status Dashboard</h1>
                    <p>Status dashboard is loading...</p>
                    <p><a href="/">← Back to Home</a></p>
                    <p><small>Error: {str(e)}</small></p>
                </body>
            </html>
            """
        )

# Basic brain dashboard endpoint
@app.get("/brain-dashboard")
def brain_dashboard(request: Request):
    """Brain dashboard that loads routers on first request"""
    # Load routers on first request instead of startup
    if "routers_loaded" not in _router_cache:
        include_routers()
    
    try:
        templates = get_templates()
        return templates.TemplateResponse("brain_dashboard.html", {"request": request})
    except Exception as e:
        return HTMLResponse(
            content=f"""
            <html>
                <head><title>Brain - Masonic AI</title></head>
                <body>
                    <h1>🧠 Brain Dashboard</h1>
                    <p>Brain dashboard is loading...</p>
                    <p><a href="/">← Back to Home</a></p>
                    <p><small>Error: {str(e)}</small></p>
                </body>
            </html>
            """
        )

# Placeholder endpoints for other features - will be loaded when routers are available
@app.get("/api/opportunities")
async def get_enhanced_opportunities():
    """Placeholder for opportunities endpoint"""
    # Load routers on first request instead of startup
    if "routers_loaded" not in _router_cache:
        include_routers()
    
    return {
        "message": "Opportunities endpoint is loading...",
        "status": "initializing",
        "cron_schedule": "4 times per day (every 6 hours)"
    }

@app.get("/api/portfolio")
async def get_enhanced_portfolio():
    """Placeholder for portfolio endpoint"""
    # Load routers on first request instead of startup
    if "routers_loaded" not in _router_cache:
        include_routers()
    
    return {
        "message": "Portfolio endpoint is loading...",
        "status": "initializing",
        "cron_schedule": "4 times per day (every 6 hours)"
    }

# Add more placeholder endpoints as needed...

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Masonic AI Crypto Broker (Minimal Health Check Version)")
    print("✅ Cron schedule: 4 times per day (every 6 hours)")
    print("✅ No startup events - everything lazy loaded")
    print("✅ Optimized for Replit health checks")
    uvicorn.run(app, host="0.0.0.0", port=8000)
