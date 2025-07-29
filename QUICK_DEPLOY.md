# 🚀 Quick Deploy to Vercel (No CLI Required)

## Method 1: GitHub Integration (Recommended)

### Step 1: Push to GitHub
```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit: Agentic Crypto Broker MVP"

# Create a new repository on GitHub and push
git remote add origin https://github.com/YOUR_USERNAME/maso-ai-crypto.git
git push -u origin main
```

### Step 2: Deploy via Vercel Dashboard

1. **Go to [vercel.com](https://vercel.com)**
2. **Sign up/Login with GitHub**
3. **Click "New Project"**
4. **Import your GitHub repository**
5. **Configure the project:**
   - Framework Preset: `Other`
   - Root Directory: `./`
   - Build Command: Leave empty
   - Output Directory: Leave empty
   - Install Command: Leave empty

### Step 3: Set Environment Variables

In the Vercel dashboard, go to your project settings:

1. **Navigate to Settings > Environment Variables**
2. **Add the following variables (all optional for demo):**
   ```
   BINANCE_API_KEY=your_binance_api_key
   BINANCE_SECRET_KEY=your_binance_secret_key
   OPENAI_API_KEY=your_openai_api_key
   NEWS_API_KEY=your_news_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```

### Step 4: Deploy

Click "Deploy" and wait for the build to complete!

## Method 2: Direct Upload

1. **Zip your project:**
   ```bash
   zip -r crypto-broker.zip . -x "*.git*" "*.venv*" "__pycache__/*"
   ```

2. **Go to [vercel.com](https://vercel.com)**
3. **Create new project**
4. **Upload the zip file**
5. **Configure as above**

## 🎯 Your App Will Be Live At:

`https://your-project-name.vercel.app`

## ✅ Features Available Immediately:

- **Portfolio Dashboard** - Real-time crypto portfolio analysis
- **Market Intelligence** - Live market data and technical indicators
- **AI Agent** - Personalized investment recommendations
- **News Sentiment** - Crypto news analysis (mock data)
- **Responsive UI** - Works on desktop and mobile

## 🔧 Testing Your Deployment:

```bash
# Test the main endpoints
curl https://your-project-name.vercel.app/api/portfolio
curl -X POST https://your-project-name.vercel.app/agent/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["BTC", "ETH"], "include_news": true}'
```

## 🚨 Important Notes:

1. **No API Keys Required** - The app works with mock data
2. **Real Data Available** - Add API keys for live data
3. **Serverless** - Scales automatically
4. **Free Tier** - Vercel has generous free limits

## 🎉 Success!

Your Agentic Crypto Broker is now live and ready for your capstone presentation!

### Demo Features:
- ✅ Real-time portfolio analysis
- ✅ Market data integration
- ✅ AI-powered recommendations
- ✅ News sentiment analysis
- ✅ Professional UI/UX
- ✅ Mobile responsive
- ✅ Production ready 
