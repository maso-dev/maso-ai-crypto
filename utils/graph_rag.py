#!/usr/bin/env python3
"""
Neo4j Graph Database Integration for Hybrid RAG System
Implements graph-based knowledge storage and relationship queries.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

# Neo4j imports
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError

# Local imports
from .cost_tracker import track_openai_call

# Neo4j configuration
NEO4J_URI = os.getenv("NEO4J_URI", os.getenv("AURA_INSTANCEI", "bolt://localhost:7687"))
NEO4J_USER = os.getenv("NEO4J_USERNAME", os.getenv("NEO4J_USER", "neo4j"))
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


class NodeType(Enum):
    """Types of nodes in the knowledge graph."""

    NEWS_ARTICLE = "NewsArticle"
    CRYPTO_SYMBOL = "CryptoSymbol"
    ENTITY = "Entity"
    TOPIC = "Topic"
    SENTIMENT = "Sentiment"
    EVENT = "Event"


class RelationshipType(Enum):
    """Types of relationships in the knowledge graph."""

    MENTIONS = "MENTIONS"
    RELATED_TO = "RELATED_TO"
    HAS_SENTIMENT = "HAS_SENTIMENT"
    TRIGGERS = "TRIGGERS"
    IMPACTS = "IMPACTS"
    SIMILAR_TO = "SIMILAR_TO"
    PART_OF = "PART_OF"


@dataclass
class GraphNode:
    """Represents a node in the knowledge graph."""

    id: str
    type: NodeType
    properties: Dict[str, Any]
    labels: Optional[List[str]] = None


@dataclass
class GraphRelationship:
    """Represents a relationship in the knowledge graph."""

    source_id: str
    target_id: str
    type: RelationshipType
    properties: Optional[Dict[str, Any]] = None


@dataclass
class GraphQuery:
    """Represents a graph query."""

    query_type: str
    parameters: Dict[str, Any]
    limit: int = 10


class Neo4jGraphRAG:
    """
    Neo4j Graph Database integration for hybrid RAG system.
    Implements graph-based knowledge storage and relationship queries.
    """

    def __init__(self):
        """Initialize Graph RAG with Neo4j connection."""
        self.uri = os.getenv("NEO4J_URI")
        self.username = os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")

        self.driver = None
        self.connected = False

        if self.uri and self.password:
            try:
                self.driver = GraphDatabase.driver(
                    self.uri,
                    auth=(self.username, self.password)
                )
                # Test connection
                with self.driver.session(database=self.database) as session:
                    result = session.run("RETURN 1 as test")
                    result.single()
                self.connected = True
                print(f"✅ Connected to Neo4j at {self.uri}")

                # Initialize schema
                self._initialize_schema()

            except Exception as e:
                print(f"❌ Neo4j connection failed: {e}")
                self.connected = False
        else:
            print("⚠️ Neo4j credentials not found, using mock mode")

    def _initialize_schema(self):
        """Initialize Neo4j schema with required labels and properties."""
        if not self.connected:
            return

        try:
            with self.driver.session(database=self.database) as session:
                # Create constraints and indexes
                schema_queries = [
                    "CREATE CONSTRAINT news_id IF NOT EXISTS FOR (n:NewsArticle) REQUIRE n.id IS UNIQUE",
                    "CREATE CONSTRAINT symbol_name IF NOT EXISTS FOR (s:CryptoSymbol) REQUIRE s.name IS UNIQUE",
                    "CREATE CONSTRAINT entity_name IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE",
                    "CREATE INDEX news_title IF NOT EXISTS FOR (n:NewsArticle) ON (n.title)",
                    "CREATE INDEX news_content IF NOT EXISTS FOR (n:NewsArticle) ON (n.content)",
                ]

                for query in schema_queries:
                    try:
                        session.run(query)
                    except Exception as e:
                        print(f"Schema query warning: {e}")

                # Create sample data if database is empty
                result = session.run("MATCH (n:NewsArticle) RETURN count(n) as count")
                count = result.single()["count"]

                if count == 0:
                    self._create_sample_data(session)

        except Exception as e:
            print(f"Schema initialization error: {e}")

    def _create_sample_data(self, session):
        """Create sample data for demonstration."""
        try:
            sample_queries = [
                """
                CREATE (n:NewsArticle {
                    id: 'sample-1',
                    title: 'Bitcoin Reaches New Heights',
                    content: 'Bitcoin continues its upward trajectory as institutional adoption grows.',
                    source_url: 'https://example.com/bitcoin-news',
                    published_at: datetime()
                })
                """,
                """
                CREATE (s:CryptoSymbol {name: 'BTC', full_name: 'Bitcoin'})
                """,
                """
                CREATE (e:Entity {name: 'institutional_adoption', type: 'trend'})
                """,
                """
                MATCH (n:NewsArticle {id: 'sample-1'}), (s:CryptoSymbol {name: 'BTC'})
                CREATE (n)-[:MENTIONS]->(s)
                """,
                """
                MATCH (n:NewsArticle {id: 'sample-1'}), (e:Entity {name: 'institutional_adoption'})
                CREATE (n)-[:MENTIONS]->(e)
                """
            ]

            for query in sample_queries:
                session.run(query)

            print("✅ Sample data created in Neo4j")

        except Exception as e:
            print(f"Sample data creation error: {e}")


    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()

    async def create_constraints(self):
        """Create database constraints and indexes."""
        if not self.connected or not self.driver:
            return

        constraints = [
            "CREATE CONSTRAINT news_id IF NOT EXISTS FOR (n:NewsArticle) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT symbol_name IF NOT EXISTS FOR (s:CryptoSymbol) REQUIRE s.name IS UNIQUE",
            "CREATE CONSTRAINT entity_name IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE",
            "CREATE INDEX news_published IF NOT EXISTS FOR (n:NewsArticle) ON (n.published_at)",
            "CREATE INDEX symbol_mentions IF NOT EXISTS FOR (s:CryptoSymbol) ON (s.mention_count)",
            "CREATE INDEX sentiment_score IF NOT EXISTS FOR (n:NewsArticle) ON (n.sentiment_score)",
        ]

        try:
            with self.driver.session() as session:
                for constraint in constraints:
                    session.run(constraint)
            print("✅ Neo4j constraints and indexes created")
        except Exception as e:
            print(f"⚠️ Failed to create constraints: {e}")

    async def insert_news_article(self, article_data: Dict[str, Any]) -> Optional[str]:
        """Insert a news article into the graph."""
        if not self.connected or not self.driver:
            return f"mock_article_{datetime.now().timestamp()}"

        try:
            with self.driver.session() as session:
                # Create news article node
                result = session.run(
                    """
                    MERGE (n:NewsArticle {id: $id})
                    SET n.title = $title,
                        n.content = $content,
                        n.source_url = $source_url,
                        n.published_at = $published_at,
                        n.sentiment_score = $sentiment_score,
                        n.crypto_topic = $crypto_topic,
                        n.relevance_score = $relevance_score,
                        n.updated_at = datetime()
                    RETURN n.id
                """,
                    article_data,
                )

                result_record = result.single()
                if not result_record:
                    return None
                article_id = result_record["n.id"]

                # Create crypto symbol nodes and relationships
                symbols = article_data.get("symbols", [])
                for symbol in symbols:
                    session.run(
                        """
                        MERGE (s:CryptoSymbol {name: $symbol})
                        SET s.mention_count = COALESCE(s.mention_count, 0) + 1,
                            s.last_mentioned = datetime()
                    """,
                        {"symbol": symbol},
                    )

                    session.run(
                        """
                        MATCH (n:NewsArticle {id: $article_id})
                        MATCH (s:CryptoSymbol {name: $symbol})
                        MERGE (n)-[r:MENTIONS]->(s)
                        SET r.weight = COALESCE(r.weight, 0) + 1
                    """,
                        {"article_id": article_id, "symbol": symbol},
                    )

                # Create sentiment relationship
                if article_data.get("sentiment_score"):
                    sentiment = (
                        "positive"
                        if article_data["sentiment_score"] > 0.1
                        else (
                            "negative"
                            if article_data["sentiment_score"] < -0.1
                            else "neutral"
                        )
                    )
                    session.run(
                        """
                        MATCH (n:NewsArticle {id: $article_id})
                        MERGE (sent:Sentiment {type: $sentiment})
                        MERGE (n)-[r:HAS_SENTIMENT]->(sent)
                        SET r.score = $score
                    """,
                        {
                            "article_id": article_id,
                            "sentiment": sentiment,
                            "score": article_data["sentiment_score"],
                        },
                    )

                return article_id

        except Exception as e:
            print(f"❌ Failed to insert news article: {e}")
            return None

    async def insert_entities(self, article_id: str, entities: List[Dict[str, Any]]):
        """Insert entities and their relationships."""
        if not self.connected or not self.driver or not entities:
            return

        try:
            with self.driver.session() as session:
                for entity in entities:
                    # Create entity node
                    session.run(
                        """
                        MERGE (e:Entity {name: $name})
                        SET e.type = $type,
                            e.mention_count = COALESCE(e.mention_count, 0) + 1
                    """,
                        {"name": entity["name"], "type": entity.get("type", "unknown")},
                    )

                    # Create relationship to article
                    session.run(
                        """
                        MATCH (n:NewsArticle {id: $article_id})
                        MATCH (e:Entity {name: $entity_name})
                        MERGE (n)-[r:MENTIONS]->(e)
                        SET r.weight = COALESCE(r.weight, 0) + 1
                    """,
                        {"article_id": article_id, "entity_name": entity["name"]},
                    )

                    # Create relationships between entities and crypto symbols
                    if entity.get("related_symbols"):
                        for symbol in entity["related_symbols"]:
                            session.run(
                                """
                                MATCH (e:Entity {name: $entity_name})
                                MATCH (s:CryptoSymbol {name: $symbol})
                                MERGE (e)-[r:RELATED_TO]->(s)
                                SET r.weight = COALESCE(r.weight, 0) + 1
                            """,
                                {"entity_name": entity["name"], "symbol": symbol},
                            )

        except Exception as e:
            print(f"❌ Failed to insert entities: {e}")

    async def graph_search(self, query: GraphQuery) -> List[Dict[str, Any]]:
        """Perform graph-based search queries."""
        if not self.connected or not self.driver:
            return self._mock_graph_search(query)

        try:
            with self.driver.session() as session:
                if query.query_type == "related_articles":
                    return await self._search_related_articles(session, query)
                elif query.query_type == "entity_network":
                    return await self._search_entity_network(session, query)
                elif query.query_type == "sentiment_analysis":
                    return await self._search_sentiment_analysis(session, query)
                elif query.query_type == "trending_topics":
                    return await self._search_trending_topics(session, query)
                else:
                    return await self._search_general(session, query)

        except Exception as e:
            print(f"❌ Graph search failed: {e}")
            return []

    async def _search_related_articles(
        self, session, query: GraphQuery
    ) -> List[Dict[str, Any]]:
        """Search for articles related to specific symbols."""
        symbols = query.parameters.get("symbols", [])
        limit = query.limit

        result = session.run(
            """
            MATCH (n:NewsArticle)-[:MENTIONS]->(s:CryptoSymbol)
            WHERE s.name IN $symbols
            WITH n, s, n.sentiment_score as sentiment
            ORDER BY n.published_at DESC
            LIMIT $limit
            RETURN n.id as id, n.title as title, n.content as content,
                   n.source_url as source_url, n.published_at as published_at,
                   n.sentiment_score as sentiment_score, n.crypto_topic as crypto_topic,
                   collect(s.name) as symbols
        """,
            {"symbols": symbols, "limit": limit},
        )

        return [dict(record) for record in result]

    async def _search_entity_network(
        self, session, query: GraphQuery
    ) -> List[Dict[str, Any]]:
        """Search for entity relationships and networks."""
        entity_name = query.parameters.get("entity_name", "")
        depth = query.parameters.get("depth", 2)

        result = session.run(
            """
            MATCH path = (e:Entity {name: $entity_name})-[*1..$depth]-(related)
            WHERE related:Entity OR related:CryptoSymbol OR related:NewsArticle
            RETURN DISTINCT related.name as name, labels(related) as type,
                   length(path) as distance
            ORDER BY distance, related.mention_count DESC
            LIMIT $limit
        """,
            {"entity_name": entity_name, "depth": depth, "limit": query.limit},
        )

        return [dict(record) for record in result]

    async def _search_sentiment_analysis(
        self, session, query: GraphQuery
    ) -> List[Dict[str, Any]]:
        """Search for sentiment patterns."""
        symbols = query.parameters.get("symbols", [])
        time_range = query.parameters.get("time_range_hours", 24)

        result = session.run(
            """
            MATCH (n:NewsArticle)-[:MENTIONS]->(s:CryptoSymbol)-[:HAS_SENTIMENT]->(sent:Sentiment)
            WHERE s.name IN $symbols
            AND n.published_at > datetime() - duration({hours: $time_range})
            RETURN s.name as symbol, sent.type as sentiment,
                   count(n) as article_count,
                   avg(n.sentiment_score) as avg_sentiment
            ORDER BY article_count DESC
        """,
            {"symbols": symbols, "time_range": time_range},
        )

        return [dict(record) for record in result]

    async def _search_trending_topics(
        self, session, query: GraphQuery
    ) -> List[Dict[str, Any]]:
        """Search for trending topics and entities."""
        time_range = query.parameters.get("time_range_hours", 24)

        result = session.run(
            """
            MATCH (n:NewsArticle)-[:MENTIONS]->(e:Entity)
            WHERE n.published_at > datetime() - duration({hours: $time_range})
            WITH e, count(n) as mention_count
            ORDER BY mention_count DESC
            LIMIT $limit
            RETURN e.name as name, e.type as type, mention_count
        """,
            {"time_range": time_range, "limit": query.limit},
        )

        return [dict(record) for record in result]

    async def _search_general(self, session, query: GraphQuery) -> List[Dict[str, Any]]:
        """General graph search."""
        search_term = query.parameters.get("search_term", "")

        result = session.run(
            """
            MATCH (n:NewsArticle)
            WHERE n.title CONTAINS $search_term OR n.content CONTAINS $search_term
            WITH n
            OPTIONAL MATCH (n)-[:MENTIONS]->(s:CryptoSymbol)
            OPTIONAL MATCH (n)-[:MENTIONS]->(e:Entity)
            RETURN n.id as id, n.title as title, n.content as content,
                   n.source_url as source_url, n.published_at as published_at,
                   collect(DISTINCT s.name) as symbols,
                   collect(DISTINCT e.name) as entities
            ORDER BY n.published_at DESC
            LIMIT $limit
        """,
            {"search_term": search_term, "limit": query.limit},
        )

        return [dict(record) for record in result]

    def _mock_graph_search(self, query: GraphQuery) -> List[Dict[str, Any]]:
        """Mock graph search for when Neo4j is not available."""
        print("🔄 Using mock graph search")

        if query.query_type == "related_articles":
            return [
                {
                    "id": "mock_article_1",
                    "title": "Bitcoin Price Analysis",
                    "content": "Bitcoin shows strong momentum...",
                    "source_url": "https://example.com/bitcoin-analysis",
                    "published_at": datetime.now(timezone.utc).isoformat(),
                    "sentiment_score": 0.7,
                    "crypto_topic": "Bitcoin",
                    "symbols": ["Bitcoin"],
                }
            ]
        elif query.query_type == "entity_network":
            return [{"name": "Elon Musk", "type": ["Entity"], "distance": 1}]
        else:
            return []

    async def get_graph_stats(self) -> Dict[str, Any]:
        """Get graph database statistics."""
        if not self.connected or not self.driver:
            return {
                "connected": False,
                "total_nodes": 0,
                "total_relationships": 0,
                "node_types": {},
                "relationship_types": {},
            }

        try:
            with self.driver.session() as session:
                # Get node counts by type
                node_stats = session.run(
                    """
                    MATCH (n)
                    RETURN labels(n) as labels, count(n) as count
                """
                )

                node_types = {}
                for record in node_stats:
                    labels = record["labels"]
                    if labels:
                        label = labels[0]  # Take first label
                        node_types[label] = record["count"]

                # Get relationship counts by type
                rel_stats = session.run(
                    """
                    MATCH ()-[r]->()
                    RETURN type(r) as type, count(r) as count
                """
                )

                relationship_types = {}
                for record in rel_stats:
                    relationship_types[record["type"]] = record["count"]

                # Get total counts
                total_nodes = sum(node_types.values())
                total_relationships = sum(relationship_types.values())

                return {
                    "connected": True,
                    "total_nodes": total_nodes,
                    "total_relationships": total_relationships,
                    "node_types": node_types,
                    "relationship_types": relationship_types,
                }

        except Exception as e:
            print(f"❌ Failed to get graph stats: {e}")
            return {"connected": False, "error": str(e)}


# Global instance
graph_rag = Neo4jGraphRAG()


# Convenience functions
async def insert_news_to_graph(
    article_data: Dict[str, Any], entities: Optional[List[Dict[str, Any]]] = None
) -> Optional[str]:
    """Insert news article and entities into the graph."""
    article_id = await graph_rag.insert_news_article(article_data)
    if article_id and entities:
        await graph_rag.insert_entities(article_id, entities)
    return article_id


async def search_graph(
    query_type: str, parameters: Dict[str, Any], limit: int = 10
) -> List[Dict[str, Any]]:
    """Search the knowledge graph."""
    query = GraphQuery(query_type=query_type, parameters=parameters, limit=limit)
    return await graph_rag.graph_search(query)


async def get_graph_statistics() -> Dict[str, Any]:
    """Get graph database statistics."""
    return await graph_rag.get_graph_stats()