import os
import httpx
from typing import List, Dict, Optional

NEWSAPI_URL = "https://newsapi.org/v2/everything"

async def fetch_news_articles(terms: List[str], api_key: Optional[str] = None) -> List[Dict]:
    api_key = api_key or os.getenv("NEWSAPI_KEY")
    if not api_key:
        raise ValueError("No NewsAPI key provided.")
    articles = []
    async with httpx.AsyncClient() as client:
        for term in terms:
            params = {
                "q": term,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 10,
                "apiKey": api_key,
            }
            resp = await client.get(NEWSAPI_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
            for art in data.get("articles", []):
                articles.append({
                    "crypto_topic": term,
                    "source_url": art["url"],
                    "published_at": art["publishedAt"],
                    "title": art["title"],
                    "content": art["content"] or art.get("description", "")
                })
    return articles 
