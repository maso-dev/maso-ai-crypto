from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from utils.newsapi import fetch_news_articles
from utils.milvus import insert_news_chunks
from utils.optimized_pipeline import run_optimized_pipeline

router = APIRouter()


class ChunkingConfig(BaseModel):
    method: str = Field(
        ..., description="Chunking method, e.g., 'sentence', 'paragraph', 'fixed'"
    )
    chunk_size: Optional[int] = Field(None, description="Chunk size if applicable")
    overlap: Optional[int] = Field(None, description="Chunk overlap if applicable")


class PopulateRequest(BaseModel):
    terms: List[str]
    chunking: ChunkingConfig
    newsapi_key: Optional[str] = None


class PopulateResponse(BaseModel):
    inserted: int
    updated: int
    errors: Optional[List[str]] = None


@router.post("/populate_crypto_news_rag", response_model=PopulateResponse)
async def populate_crypto_news_rag(
    req: PopulateRequest = Body(...),
) -> PopulateResponse:
    try:
        print(f"=== Starting populate_crypto_news_rag ===")
        print(f"Terms: {req.terms}")
        print(f"Chunking config: {req.chunking}")

        # Step 1: Fetch news articles
        print(f"Step 1: Fetching news articles...")
        articles = await fetch_news_articles(req.terms, req.newsapi_key)
        print(f"✓ Fetched {len(articles)} articles from NewsAPI")

        if not articles:
            print("⚠️ No articles fetched, returning early")
            return PopulateResponse(inserted=0, updated=0, errors=["No articles found"])

        # Step 2: Process articles with optimized pipeline
        print(f"Step 2: Processing articles with optimized pipeline...")
        chunks = []

        # Process all articles through the optimized pipeline
        processed_data = await run_optimized_pipeline(articles)
        vector_data = processed_data["vector_data"]
        summary = processed_data["summary"]

        print(f"✓ Optimized pipeline summary:")
        print(f"   Total processed: {summary['total_processed']}")
        print(f"   Breaking news: {summary['breaking_news']}")
        print(f"   Recent news: {summary['recent_news']}")
        print(f"   Avg sentiment: {summary['avg_sentiment']}")

        # Prepare chunks for Milvus insertion
        for chunk in vector_data:
            # The optimized pipeline already handles temporal context and enrichment
            # Just ensure we have the required fields for Milvus
            if "vector" not in chunk:
                chunk["vector"] = chunk.get("dense_vector", [])
            if "sparse_vector" not in chunk:
                chunk["sparse_vector"] = chunk.get("sparse_vector", {})

            chunks.append(chunk)

        print(f"✓ Total chunks prepared: {len(chunks)}")

        if not chunks:
            print("⚠️ No chunks created, returning early")
            return PopulateResponse(inserted=0, updated=0, errors=["No chunks created"])

        # Step 3: Insert into Milvus
        print(f"Step 3: Inserting into Milvus...")
        inserted, updated, errors = await insert_news_chunks(chunks)
        print(
            f"✓ Milvus result - Inserted: {inserted}, Updated: {updated}, Errors: {errors}"
        )

        print(f"=== Completed populate_crypto_news_rag ===")
        return PopulateResponse(inserted=inserted, updated=updated, errors=errors)

    except Exception as e:
        print(f"❌ Error in populate_crypto_news_rag: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
