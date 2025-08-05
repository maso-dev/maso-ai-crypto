import os
import httpx
from typing import List, Dict, Optional

NEWSAPI_URL = "https://newsapi.org/v2/everything"


async def fetch_news_articles(
    terms: List[str], api_key: Optional[str] = None, hours_back: int = 24
) -> List[Dict]:
    """
    Fetch news articles with enhanced temporal context.

    Args:
        terms: List of search terms
        api_key: NewsAPI key (optional, uses env var if not provided)
        hours_back: How many hours back to search (default: 24)
    """
    api_key = api_key or os.getenv("NEWSAPI_KEY")
    if not api_key:
        raise ValueError("No NewsAPI key provided.")

    from datetime import datetime, timedelta

    # Calculate date range for better temporal relevance
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(hours=hours_back)

    articles = []
    async with httpx.AsyncClient() as client:
        for term in terms:
            params = {
                "q": term,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 20,  # Increased for better coverage
                "from": start_date.isoformat() + "Z",
                "to": end_date.isoformat() + "Z",
                "apiKey": api_key,
            }
            resp = await client.get(NEWSAPI_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
            for art in data.get("articles", []):
                # Calculate time-based relevance score
                pub_time = datetime.fromisoformat(
                    art["publishedAt"].replace("Z", "+00:00")
                )
                hours_ago = (
                    end_date - pub_time.replace(tzinfo=None)
                ).total_seconds() / 3600

                articles.append(
                    {
                        "crypto_topic": term,
                        "source_url": art["url"],
                        "published_at": art["publishedAt"],
                        "title": art["title"],
                        "content": art["content"] or art.get("description", ""),
                        "source_name": art.get("source", {}).get("name", "Unknown"),
                        "hours_ago": hours_ago,
                        "is_breaking": hours_ago <= 2,  # Breaking news flag
                        "is_recent": hours_ago <= 24,  # Recent news flag
                    }
                )

    # Sort by recency for better temporal relevance
    articles.sort(key=lambda x: x["hours_ago"])
    return articles
