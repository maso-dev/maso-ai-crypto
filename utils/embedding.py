import os
import re
from typing import Dict, List, Any
import openai
from collections import Counter

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
    """Simple word frequency-based sparse vector (replaces TF-IDF for Vercel size optimization)"""
    # Clean and tokenize text
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'his', 'hers', 'ours', 'theirs'}
    words = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Count word frequencies
    word_counts = Counter(words)
    
    # Create sparse vector (word -> frequency)
    sparse_vector = {}
    for word, count in word_counts.most_common(100):  # Limit to top 100 words
        sparse_vector[word] = float(count)
    
    return sparse_vector

async def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Get embeddings for a list of texts using OpenAI's text-embedding-ada-002 model.
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        List of embedding vectors (each vector is a list of floats)
    """
    if not client:
        print("⚠️ OpenAI client not available - returning empty embeddings")
        return [[0.0] * 1536 for _ in texts]  # text-embedding-ada-002 has 1536 dimensions
    
    embeddings = []
    for text in texts:
        try:
            response = await client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            embeddings.append(response.data[0].embedding)
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Return zero vector as fallback
            embeddings.append([0.0] * 1536)
    
    return embeddings 
