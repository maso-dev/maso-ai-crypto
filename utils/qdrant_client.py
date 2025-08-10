#!/usr/bin/env python3
"""
Qdrant Vector Database Integration
Provides vector search functionality using Qdrant cloud service
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance,
        VectorParams,
        PointStruct,
        Filter,
        FieldCondition,
        MatchValue,
        CreateCollection,
        CollectionInfo,
    )

    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logging.warning(
        "Qdrant client not available. Install with: pip install qdrant-client"
    )

logger = logging.getLogger(__name__)


@dataclass
class QdrantDocument:
    """Document structure for Qdrant storage"""

    id: str
    content: str
    metadata: Dict[str, Any]
    vector: List[float] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class QdrantVectorSearch:
    """Qdrant vector search implementation"""

    def __init__(self, collection_name: str = "crypto_news"):
        self.collection_name = collection_name
        self.client = None
        self.is_connected = False

        if not QDRANT_AVAILABLE:
            raise ImportError("Qdrant client not available")

        self._connect()
        self._ensure_collection()

    def _connect(self):
        """Connect to Qdrant cloud service"""
        try:
            # Get API key from environment
            api_key = os.getenv("QDRANT_VECTOR_API")
            if not api_key:
                raise ValueError("QDRANT_VECTOR_API environment variable not set")

            # Connect to your cluster
            self.client = QdrantClient(
                url="https://068fa68a-6308-444f-81bb-5cc091e4f988.us-west-2-0.aws.cloud.qdrant.io:6333",
                api_key=api_key,
            )

            # Test connection
            if self.client:
                info = self.client.get_collections()
                self.is_connected = True
                logger.info(
                    f"✅ Connected to Qdrant cloud service. Collections: {len(info.collections)}"
                )
            else:
                raise ConnectionError("Failed to create Qdrant client")

        except Exception as e:
            logger.error(f"❌ Failed to connect to Qdrant: {e}")
            self.is_connected = False
            raise

    def _ensure_collection(self):
        """Ensure the collection exists with proper schema"""
        try:
            if not self.client:
                raise ConnectionError("Qdrant client not initialized")

            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]

            if self.collection_name not in collection_names:
                # Create collection with proper vector configuration
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=28,  # Match simple_vectorize output dimension
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"✅ Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(
                    f"✅ Using existing Qdrant collection: {self.collection_name}"
                )

        except Exception as e:
            logger.error(f"❌ Failed to ensure collection: {e}")
            raise

    def add_document(
        self, content: str, metadata: Dict[str, Any], vector: List[float]
    ) -> str:
        """Add a document to Qdrant"""
        try:
            if not self.is_connected:
                raise ConnectionError("Not connected to Qdrant")

            # Generate document ID - Qdrant requires integer or UUID
            import uuid

            doc_id = str(uuid.uuid4())

            # Create point for Qdrant
            point = PointStruct(
                id=doc_id,
                vector=vector,
                payload={
                    "content": content,
                    "metadata": metadata,
                    "timestamp": datetime.now().isoformat(),
                    "symbols": metadata.get("symbols", []),
                    "category": metadata.get("category", "unknown"),
                    "sentiment": metadata.get("sentiment", "neutral"),
                    "original_symbol": (
                        metadata.get("symbols", ["unknown"])[0]
                        if metadata.get("symbols")
                        else "unknown"
                    ),
                },
            )

            # Insert into collection
            self.client.upsert(collection_name=self.collection_name, points=[point])

            logger.info(f"✅ Document added to Qdrant: {doc_id}")
            return doc_id

        except Exception as e:
            logger.error(f"❌ Failed to add document to Qdrant: {e}")
            raise

    def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        symbols: Optional[List[str]] = None,
        min_score: float = 0.1,
    ) -> List[Dict[str, Any]]:
        """Search for similar documents in Qdrant"""
        try:
            if not self.is_connected:
                raise ConnectionError("Not connected to Qdrant")

            # Prepare search parameters
            search_params = {
                "collection_name": self.collection_name,
                "query_vector": query_vector,
                "limit": limit,
                "score_threshold": min_score,
            }

            # Add symbol filter if specified
            if symbols:
                search_params["query_filter"] = Filter(
                    must=[
                        FieldCondition(
                            key="symbols",
                            match=MatchValue(
                                value=symbols[0]
                            ),  # Use first symbol for now
                        )
                    ]
                )

            # Perform search
            results = self.client.search(**search_params)

            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append(
                    {
                        "id": result.id,
                        "score": result.score,
                        "content": result.payload.get("content", ""),
                        "metadata": result.payload.get("metadata", {}),
                        "symbols": result.payload.get("symbols", []),
                        "category": result.payload.get("category", "unknown"),
                        "sentiment": result.payload.get("sentiment", "neutral"),
                        "timestamp": result.payload.get("timestamp", ""),
                    }
                )

            logger.info(f"✅ Qdrant search returned {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            logger.error(f"❌ Qdrant search failed: {e}")
            return []

    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection statistics and info"""
        try:
            if not self.is_connected:
                return {"error": "Not connected"}

            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": getattr(info, "vectors_count", 0),
                "points_count": getattr(info, "points_count", 0),
                "segments_count": getattr(info, "segments_count", 0),
                "config": {
                    "vector_size": getattr(info.config.params.vectors, "size", 28),
                    "distance": str(
                        getattr(info.config.params.vectors, "distance", "COSINE")
                    ),
                },
            }

        except Exception as e:
            return {"error": str(e)}

    def cleanup_old_documents(self, days_old: int = 30):
        """Clean up old documents (placeholder for future implementation)"""
        logger.info(
            f"🔄 Cleanup of documents older than {days_old} days not yet implemented"
        )
        # TODO: Implement cleanup using Qdrant's filtering capabilities


def get_qdrant_client() -> QdrantVectorSearch:
    """Get Qdrant client instance"""
    try:
        return QdrantVectorSearch()
    except Exception as e:
        logger.error(f"Failed to create Qdrant client: {e}")
        raise


def is_qdrant_available() -> bool:
    """Check if Qdrant is available and configured"""
    try:
        api_key = os.getenv("QDRANT_VECTOR_API")
        return bool(api_key) and QDRANT_AVAILABLE
    except:
        return False


def test_qdrant_connection() -> Dict[str, Any]:
    """Test Qdrant connection and return status"""
    try:
        if not is_qdrant_available():
            return {
                "status": "not_available",
                "error": "QDRANT_VECTOR_API not set or client not installed",
            }

        client = get_qdrant_client()
        info = client.get_collection_info()

        return {
            "status": "connected",
            "collection_info": info,
            "is_operational": client.is_connected,
        }

    except Exception as e:
        return {"status": "error", "error": str(e), "is_operational": False}
