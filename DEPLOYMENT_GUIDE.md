# 🚀 Vercel Deployment Guide

## Quick Deploy to Vercel

### Prerequisites
1. Install Vercel CLI: `npm i -g vercel`
2. Have a GitHub account
3. Have the required API keys (optional for demo)

### Step 1: Prepare Environment Variables

Copy the environment variables to your local `.env` file:
```bash
cp env.example .env
```

### Step 2: Deploy to Vercel

1. **Login to Vercel:**
   ```bash
   vercel login
   ```

2. **Deploy the application:**
   ```bash
   vercel --prod
   ```

3. **Set up environment variables in Vercel Dashboard:**
   - Go to your project in Vercel dashboard
   - Navigate to Settings > Environment Variables
   - Add the following variables:
     - `BINANCE_API_KEY` (optional - will use mock data if not set)
     - `BINANCE_SECRET_KEY` (optional - will use mock data if not set)
     - `OPENAI_API_KEY` (optional - will use fallback sentiment if not set)
     - `NEWSAPI_KEY` (optional - will use mock news if not set)
     - `TAVILY_API_KEY` (optional - for web search features)

### Step 3: Test Your Deployment

Your app will be available at: `https://your-project-name.vercel.app`

Test the endpoints:
- `GET /` - Dashboard
- `GET /api/portfolio` - Portfolio data
- `POST /agent/analyze` - Agent analysis

## Features Available Without API Keys

The application works with mock data when API keys are not provided:
- ✅ Portfolio analysis with mock data
- ✅ Market data from Binance public API
- ✅ News sentiment with mock articles
- ✅ Agent recommendations
- ✅ Full UI dashboard

## Features Available With API Keys

- 🔑 Real portfolio data from Binance
- 🔑 Live crypto news from NewsAPI
- 🔑 AI-powered sentiment analysis
- 🔑 Personalized recommendations

## Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure all dependencies are in `requirements.txt`
2. **Environment Variables**: Check Vercel dashboard for correct variable names
3. **API Limits**: The app gracefully handles missing API keys
4. **Build Errors**: Check Vercel build logs for specific issues

### Local Testing:

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn main:app --reload

# Test endpoints
curl http://localhost:8000/api/portfolio
```

## Production Considerations

1. **Rate Limiting**: Add rate limiting for production use
2. **Caching**: Implement Redis caching for better performance
3. **Monitoring**: Add health checks and monitoring
4. **Security**: Ensure API keys are properly secured
5. **Scaling**: Monitor usage and scale as needed

## Support

For issues or questions:
1. Check the Vercel deployment logs
2. Review the application logs
3. Test locally first
4. Check environment variable configuration 
