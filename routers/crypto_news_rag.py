from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from utils.newsapi import fetch_news_articles
from utils.embedding import embed_chunks, compute_sparse_vectors
from utils.milvus import insert_news_chunks

router = APIRouter()

class ChunkingConfig(BaseModel):
    method: str = Field(..., description="Chunking method, e.g., 'sentence', 'paragraph', 'fixed'")
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
    req: PopulateRequest = Body(...)
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
        
        # Step 2: Process articles into chunks
        print(f"Step 2: Processing articles into chunks...")
        chunks = []
        for i, article in enumerate(articles):
            print(f"  Processing article {i+1}/{len(articles)}: {article['title'][:50]}...")
            
            # Check if article has content
            if not article.get('content'):
                print(f"    ⚠️ Article {i+1} has no content, skipping")
                continue
                
            article_chunks = await embed_chunks(article, req.chunking.model_dump())
            print(f"    ✓ Created {len(article_chunks)} chunks")
            
            for chunk in article_chunks:
                # Convert published_at from ISO string to Unix timestamp
                try:
                    if isinstance(article['published_at'], str):
                        dt = datetime.fromisoformat(article['published_at'].replace('Z', '+00:00'))
                        published_timestamp = int(dt.timestamp())
                    else:
                        published_timestamp = article['published_at']
                except (ValueError, TypeError):
                    # Fallback to current timestamp if parsing fails
                    published_timestamp = int(datetime.now().timestamp())
                
                chunk['crypto_topic'] = article['crypto_topic']
                chunk['source_url'] = article['source_url']
                chunk['published_at'] = published_timestamp
                chunk['title'] = article['title']
                chunk['vector'] = chunk['dense_vector']
                chunk['sparse_vector'] = compute_sparse_vectors(chunk['chunk_text'])
                chunks.append(chunk)
        
        print(f"✓ Total chunks prepared: {len(chunks)}")
        
        if not chunks:
            print("⚠️ No chunks created, returning early")
            return PopulateResponse(inserted=0, updated=0, errors=["No chunks created"])
        
        # Step 3: Insert into Milvus
        print(f"Step 3: Inserting into Milvus...")
        inserted, updated, errors = await insert_news_chunks(chunks)
        print(f"✓ Milvus result - Inserted: {inserted}, Updated: {updated}, Errors: {errors}")
        
        print(f"=== Completed populate_crypto_news_rag ===")
        return PopulateResponse(inserted=inserted, updated=updated, errors=errors)
        
    except Exception as e:
        print(f"❌ Error in populate_crypto_news_rag: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e)) 
