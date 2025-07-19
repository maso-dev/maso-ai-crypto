import os
from typing import Dict, List, Any
import openai
from sklearn.feature_extraction.text import TfidfVectorizer

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Simple chunking by fixed size (can be extended)
def chunk_text(text: str, chunk_size: int = 200, overlap: int = 0) -> List[str]:
    if overlap is None:
        overlap = 0
    if chunk_size is None:
        chunk_size = 200
    words = text.split()
    chunks = []
    step = chunk_size - overlap if chunk_size > overlap else chunk_size
    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i+chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

async def embed_chunks(article: Dict[str, Any], chunking: Dict[str, Any]) -> List[Dict[str, Any]]:
    text = article["content"]
    chunk_size = chunking.get("chunk_size", 200)
    overlap = chunking.get("overlap", 0)
    if overlap is None:
        overlap = 0
    chunks = chunk_text(text, chunk_size, overlap)
    results = []
    for chunk in chunks:
        if not client:
            continue
        try:
            resp = await client.embeddings.create(
                model="text-embedding-ada-002",
                input=chunk
            )
            dense_vector = resp.data[0].embedding
            results.append({
                "chunk_text": chunk,
                "dense_vector": dense_vector
            })
        except Exception as e:
            print(f"Error getting embedding: {e}")
    return results

def compute_sparse_vectors(text: str) -> Dict[str, float]:
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform([text])
    # Convert sparse matrix to dense array for processing
    tfidf = X.toarray()[0]  # type: ignore
    return {str(i): float(tfidf[i]) for i in range(len(tfidf)) if tfidf[i] > 0} 
