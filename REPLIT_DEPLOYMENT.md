# 🚀 Replit Deployment Guide

## Quick Deploy to Replit

### 1. Fork/Import to Replit
1. Go to [replit.com](https://replit.com)
2. Click "Create Repl"
3. Choose "Import from GitHub"
4. Enter: `maso-dev/maso-ai-crypto`
5. Select branch: `dev-replit-local`

### 2. Set Environment Variables
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

### 3. Install Dependencies
**Using Replit's Package Manager (Recommended)**
1. In Replit, go to the **Packages** tab (left sidebar)
2. Search for and install these packages:
   - `fastapi`
   - `uvicorn[standard]`
   - `jinja2`
   - `httpx`
   - `pydantic`
   - `openai`
   - `langchain`
   - `langchain-openai`
   - `langchain-core`
   - `langgraph`
   - `python-binance`
   - `newsapi-python`
   - `tavily-python`
   - `neo4j`
   - `pymilvus`
   - `python-dotenv`
   - `python-dateutil`
   - `pytz`
   - `websockets`
   - `aiohttp`

**Alternative: Use pyproject.toml**
The project includes a `pyproject.toml` file that Replit can use for dependency management.

### 4. Run the Application
Click the **Run** button or use the shell:
```bash
python run.py
```

### 5. Access Your App
- Your app will be available at: `https://your-repl-name.your-username.repl.co`
- The app automatically uses the port Replit provides

## Features Available

✅ **Real-time crypto data** (LiveCoinWatch)  
✅ **AI-powered analysis** (OpenAI + LangChain)  
✅ **News sentiment analysis** (NewsAPI + Tavily)  
✅ **Vector search** (Milvus)  
✅ **Graph database** (Neo4j)  
✅ **Admin transparency** (Real vs mock data indicators)  
✅ **Cache system** (Intelligent caching with fallbacks)  

## Troubleshooting

### Common Issues:
1. **"No module named 'uvicorn'"**: Install packages using Replit's Package Manager (Packages tab)
2. **"externally-managed-environment"**: Use Replit's Package Manager instead of pip install
3. **API Keys**: Make sure all environment variables are set in Replit Secrets
4. **Dependencies**: Install packages through Replit's Package Manager interface
5. **Port**: Replit automatically handles port assignment
6. **Database**: SQLite files are created automatically

### Logs:
Check the Replit console for detailed error messages and service status.

## Development

- **Auto-reload**: Enabled for development
- **Hot reload**: Changes are reflected immediately
- **Debug mode**: Full logging enabled
- **Local testing**: Perfect for development and testing

## Next Steps

1. **Test all features** in the Replit environment
2. **Verify API connections** through the admin panel
3. **Check cache system** is working properly
4. **Monitor performance** and adjust as needed
