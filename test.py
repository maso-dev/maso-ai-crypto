import asyncio
from utils.openai_utils import enrich_news_metadata

async def main():
    article = {
        "title": "Bitcoin surges as ETF inflows hit record highs",
        "content": "Bitcoin price jumped 10% today after several major ETFs reported record inflows. Analysts say this could signal a new bull run...",
        "source_name": "CoinDesk"
    }
    meta = await enrich_news_metadata(article)
    print("Enriched Metadata:")
    print(meta)

if __name__ == "__main__":
    asyncio.run(main())
