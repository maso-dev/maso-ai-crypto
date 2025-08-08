# 🚀 Masonic AI Crypto - Development Branch

## Quick Start (Replit)

### 1. Import to Replit
1. Go to [replit.com](https://replit.com)
2. Click "Create Repl"
3. Choose "Import from GitHub"
4. Enter: `maso-dev/maso-ai-crypto`
5. Select branch: `dev-replit-local`

### 2. Install Packages (One Time Setup)
1. In Replit, go to **Packages** tab (left sidebar)
2. Search for and install these packages:
   ```
   fastapi
   uvicorn[standard]
   jinja2
   httpx
   pydantic
   openai
   langchain
   langchain-openai
   langchain-core
   langgraph
   python-binance
   newsapi-python
   tavily-python
   neo4j
   pymilvus
   python-dotenv
   python-dateutil
   pytz
   websockets
   aiohttp
   ```

### 3. Set Environment Variables
In Replit, go to **Tools** → **Secrets** and add:
```
OPENAI_API_KEY=your_openai_key
LIVECOINWATCH_API_KEY=your_livecoinwatch_key
TAVILY_API_KEY=your_tavily_key
NEWSAPI_KEY=your_newsapi_key
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password
LANGSMITH_API_KEY=your_langsmith_key
```

### 4. Run the Application
Click the **Run** button! 🚀

### 5. Access Your App
- Your app will be available at: `https://your-repl-name.your-username.repl.co`

## Features

✅ **Real-time crypto data** (LiveCoinWatch)
✅ **AI-powered analysis** (OpenAI + LangChain)
✅ **News sentiment analysis** (NewsAPI + Tavily)
✅ **Vector search** (Milvus)
✅ **Graph database** (Neo4j)
✅ **Admin transparency** (Real vs mock data indicators)
✅ **Cache system** (Intelligent caching with fallbacks)

## Troubleshooting

### Common Issues:
1. **"No module named 'uvicorn'"**: Install packages using Replit's Package Manager
2. **"externally-managed-environment"**: Use Replit's Package Manager (not pip)
3. **API Keys**: Make sure all environment variables are set in Replit Secrets

### Quick Fix:
If you see missing package errors, just go to **Packages** tab and install them!

## Development

- **Auto-reload**: Enabled for development
- **Hot reload**: Changes are reflected immediately
- **Debug mode**: Full logging enabled
- **Local testing**: Perfect for development and testing
