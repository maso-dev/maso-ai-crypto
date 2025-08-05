import os
import httpx
from typing import List, Dict, Tuple, Optional

MILVUS_URI = os.getenv(
    "MILVUS_URI",
    "https://in03-9f01d93b384a0f7.serverless.gcp-us-west1.cloud.zilliz.com",
)
MILVUS_TOKEN = os.getenv("MILVUS_TOKEN")
MILVUS_CLUSTER_NAME = os.getenv("MILVUS_CLUSTER_NAME", "elmaso-free")
MILVUS_COLLECTION_NAME = os.getenv("MILVUS_COLLECTION_NAME", "crypto_news_rag")


async def insert_news_chunks(chunks: List[Dict]) -> Tuple[int, int, List[str]]:
    print(f"=== Milvus Insertion Debug ===")
    print(f"Cluster: {MILVUS_CLUSTER_NAME}")
    print(f"Collection: {MILVUS_COLLECTION_NAME}")
    print(f"Collection Name: {MILVUS_COLLECTION_NAME}")
    print(f"Chunks to insert: {len(chunks)}")

    url = f"{MILVUS_URI}/v2/vectordb/entities/insert"
    inserted = 0
    updated = 0
    errors = []
    seen_urls = set()
    data = []

    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}")
        if chunk["source_url"] in seen_urls:
            print(f"  ⚠️ Duplicate URL, skipping: {chunk['source_url'][:50]}...")
            updated += 1
            continue
        seen_urls.add(chunk["source_url"])

        # Prepare chunk data
        chunk_data = {
            "chunk_text": chunk["chunk_text"],
            "crypto_topic": chunk["crypto_topic"],
            "source_url": chunk["source_url"],
            "published_at": chunk["published_at"],
            "title": chunk["title"],
            "vector": chunk["vector"],
            "sparse_vector": chunk["sparse_vector"],
        }
        data.append(chunk_data)
        print(f"  ✓ Added chunk: {chunk['title'][:30]}...")

    print(f"Prepared {len(data)} unique chunks for insertion")

    payload = {"collectionName": MILVUS_COLLECTION_NAME, "data": data}

    headers = {}
    if MILVUS_TOKEN:
        headers["Authorization"] = f"Bearer {MILVUS_TOKEN}"

    print(f"Sending request to: {url}")
    print(f"Headers: {headers}")
    print(f"Payload keys: {list(payload.keys())}")
    print(f"Data count: {len(payload['data'])}")

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json=payload, headers=headers)
            print(f"Response status: {resp.status_code}")
            print(f"Response headers: {dict(resp.headers)}")

            if resp.status_code == 200:
                result = resp.json()
                print(f"Response body: {result}")
                inserted = len(data)
                print(f"✓ Successfully inserted {inserted} chunks")
            else:
                error_text = resp.text
                print(f"❌ Error response: {error_text}")
                errors.append(f"HTTP {resp.status_code}: {error_text}")

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Exception during insertion: {error_msg}")
            errors.append(error_msg)

    print(f"=== Milvus Insertion Complete ===")
    print(f"Inserted: {inserted}, Updated: {updated}, Errors: {errors}")
    return inserted, updated, errors


async def query_news_for_symbols(symbols: List[str], limit: int = 20) -> List[Dict]:
    """
    Query Milvus for the latest news where crypto_topic matches any of the given symbols.
    Returns a list of news dicts sorted by published_at descending.
    """
    if not symbols:
        return []
    headers = {"Content-Type": "application/json"}
    if MILVUS_TOKEN:
        headers["Authorization"] = f"Bearer {MILVUS_TOKEN}"

    # Build filter for crypto_topic in symbols
    filter_expr = " or ".join([f"crypto_topic == '{symbol}'" for symbol in symbols])
    query_data = {
        "collectionName": MILVUS_COLLECTION_NAME,
        "limit": limit,
        "outputFields": [
            "chunk_text",
            "crypto_topic",
            "title",
            "source_url",
            "published_at",
        ],
        "filter": filter_expr,
        "sort": [{"field": "published_at", "order": "desc"}],
    }
    url = f"{MILVUS_URI}/v1/vector/search"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=query_data, headers=headers)
        if resp.status_code == 200:
            result = resp.json()
            return result.get("data", [])
        else:
            print(f"Milvus query error: {resp.status_code} {resp.text}")
            return []
