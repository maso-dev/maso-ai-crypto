#!/usr/bin/env python3
"""
Local Vector Search Fallback System
Provides vector search functionality without external dependencies
"""

import hashlib
import json
import math
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import sqlite3
from pathlib import Path


@dataclass
class VectorDocument:
    """Simple document with vector representation"""

    id: str
    content: str
    metadata: Dict[str, Any]
    vector: List[float] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class LocalVectorSearch:
    """Local in-memory vector search with SQLite persistence"""

    def __init__(self, db_path: str = "data/local_vectors.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for vector storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS vectors (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    vector TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_timestamp ON vectors(timestamp)"
            )
            conn.commit()

    def simple_vectorize(self, text: str) -> List[float]:
        """Simple vectorization using character frequency and basic features"""
        # Simple character frequency vector (basic but effective)
        char_freq = {}
        for char in text.lower():
            if char.isalnum():
                char_freq[char] = char_freq.get(char, 0) + 1

        # Normalize to 0-1 range
        max_freq = max(char_freq.values()) if char_freq else 1
        vector = [char_freq.get(chr(i), 0) / max_freq for i in range(97, 123)]  # a-z

        # Add length and word count features
        words = text.split()
        vector.append(min(len(words) / 100, 1.0))  # Word count (normalized)
        vector.append(min(len(text) / 1000, 1.0))  # Character count (normalized)

        # Pad to 128 dimensions to match Qdrant collection
        while len(vector) < 128:
            vector.append(0.0)

        # Ensure exactly 128 dimensions
        return vector[:128]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def add_document(self, content: str, metadata: Dict[str, Any]) -> str:
        """Add a document to the local vector store"""
        doc_id = hashlib.md5(
            f"{content}{datetime.now().isoformat()}".encode(), usedforsecurity=False
        ).hexdigest()
        vector = self.simple_vectorize(content)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO vectors (id, content, metadata, vector, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    doc_id,
                    content,
                    json.dumps(metadata),
                    json.dumps(vector),
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()

        return doc_id

    def search(
        self, query: str, limit: int = 10, min_similarity: float = 0.1
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        query_vector = self.simple_vectorize(query)
        results = []

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id, content, metadata, vector, timestamp FROM vectors"
            )

            for row in cursor.fetchall():
                doc_id, content, metadata, vector_str, timestamp = row
                vector = json.loads(vector_str)
                metadata = json.loads(metadata)

                similarity = self._cosine_similarity(query_vector, vector)

                if similarity >= min_similarity:
                    results.append(
                        {
                            "id": doc_id,
                            "content": content,
                            "metadata": metadata,
                            "similarity": similarity,
                            "timestamp": timestamp,
                        }
                    )

        # Sort by similarity and limit results
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:limit]

    def search_by_metadata(
        self, filters: Dict[str, Any], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search documents by metadata filters"""
        results = []

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id, content, metadata, vector, timestamp FROM vectors"
            )

            for row in cursor.fetchall():
                doc_id, content, metadata, vector_str, timestamp = row
                metadata = json.loads(metadata)

                # Check if document matches all filters
                matches = True
                for key, value in filters.items():
                    if key not in metadata or metadata[key] != value:
                        matches = False
                        break

                if matches:
                    results.append(
                        {
                            "id": doc_id,
                            "content": content,
                            "metadata": metadata,
                            "timestamp": timestamp,
                        }
                    )

        return results[:limit]

    def cleanup_old_documents(self, days_old: int = 30):
        """Remove documents older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM vectors WHERE timestamp < ?", (cutoff_date.isoformat(),)
            )
            conn.commit()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the local vector store"""
        with sqlite3.connect(self.db_path) as conn:
            total_docs = conn.execute("SELECT COUNT(*) FROM vectors").fetchone()[0]
            oldest_doc = conn.execute("SELECT MIN(timestamp) FROM vectors").fetchone()[
                0
            ]
            newest_doc = conn.execute("SELECT MAX(timestamp) FROM vectors").fetchone()[
                0
            ]

        return {
            "total_documents": total_docs,
            "oldest_document": oldest_doc,
            "newest_document": newest_doc,
            "storage_path": str(self.db_path),
            "type": "local_fallback",
        }


# Global instance for easy access
_local_vector_search = None


def get_local_vector_search() -> LocalVectorSearch:
    """Get or create global local vector search instance"""
    global _local_vector_search
    if _local_vector_search is None:
        _local_vector_search = LocalVectorSearch()
    return _local_vector_search


def add_document_to_local_store(content: str, metadata: Dict[str, Any]) -> str:
    """Add document to local vector store"""
    return get_local_vector_search().add_document(content, metadata)


def search_local_vectors(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search local vector store"""
    return get_local_vector_search().search(query, limit)


def get_local_vector_stats() -> Dict[str, Any]:
    """Get local vector store statistics"""
    return get_local_vector_search().get_stats()


def simple_vectorize(text: str) -> List[float]:
    """Standalone function for simple text vectorization"""
    search = get_local_vector_search()
    return search.simple_vectorize(text)
