import os
import asyncio
from utils.newsapi import fetch_news_articles

# Set your NewsAPI key - replace with your actual key
os.environ["NEWSAPI_KEY"] = "a0c5583adee74b778f59b894c1f2687a"

async def test_newsapi():
    print("Testing NewsAPI...")
    try:
        articles = await fetch_news_articles(["bitcoin"])
        print(f"Fetched {len(articles)} articles")
        for i, article in enumerate(articles[:3]):  # Show first 3
            print(f"\nArticle {i+1}:")
            print(f"  Title: {article['title']}")
            print(f"  URL: {article['source_url']}")
            print(f"  Content length: {len(article['content'])} chars")
            print(f"  Topic: {article['crypto_topic']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_newsapi()) 
