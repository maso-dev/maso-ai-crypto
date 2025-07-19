import os
import openai
from typing import List, Dict, Tuple
import time
import hashlib

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Simple in-memory cache: {cache_key: (timestamp, (summary, actions))}
_summary_cache = {}
CACHE_TTL = 21600  # 6 hours in seconds

def _make_cache_key(symbols: List[str], news: List[Dict]) -> str:
    symbols_key = ",".join(sorted(symbols))
    # Use the most recent news published_at as part of the key, or len(news) if empty
    latest_ts = str(news[0]["published_at"]) if news and "published_at" in news[0] else str(len(news))
    raw = symbols_key + ":" + latest_ts
    return hashlib.sha256(raw.encode()).hexdigest()

async def get_market_summary(news: List[Dict], symbols: List[str]) -> Tuple[str, str]:
    if not client:
        return "OpenAI API key not set.", ""
    cache_key = _make_cache_key(symbols, news)
    now = time.time()
    # Check cache
    if cache_key in _summary_cache:
        ts, (summary, actions) = _summary_cache[cache_key]
        if now - ts < CACHE_TTL:
            return summary, actions
    # Format news for prompt
    news_str = "\n".join(
        f"- {item.get('title', '')} ({item.get('crypto_topic', '')}): {item.get('chunk_text', '')[:120]}..."
        for item in news
    )
    prompt = f"""You are a crypto portfolio assistant. The user holds: {', '.join(symbols)} (including ETFs if present).
Given the following news headlines and snippets from the last 6 hours, summarize the market sentiment and recommend actions to maximize the portfolio. Be concise and actionable.

News:
{news_str}

Respond with:
Summary:
[...]
Recommended Actions:
[...]
"""
    response = await client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=400
    )
    content = response.choices[0].message.content
    summary, actions = "", ""
    if isinstance(content, str):
        if "Recommended Actions:" in content:
            parts = content.split("Recommended Actions:")
            summary = parts[0].replace("Summary:", "").strip()
            actions = parts[1].strip()
        else:
            summary = content.strip()
    # Store in cache
    _summary_cache[cache_key] = (now, (summary, actions))
    return summary, actions 
