"""
Real Cache System - Actually saves and retrieves data
Replaces the mock cache statistics with real database operations
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a cached data entry."""

    key: str
    data: Dict[str, Any]
    data_type: str  # 'portfolio', 'news', 'signals', 'technical'
    created_at: datetime
    expires_at: datetime
    hit_count: int = 0
    last_accessed: Optional[datetime] = None


class RealCacheSystem:
    """Real cache system that actually saves and retrieves data."""

    def __init__(self, db_path: str = "cache_system.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize the cache database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create cache table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cache_entries (
                key TEXT PRIMARY KEY,
                data_type TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                hit_count INTEGER DEFAULT 0,
                last_accessed TEXT
            )
        """
        )

        # Create cache statistics table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cache_stats (
                id INTEGER PRIMARY KEY,
                total_queries INTEGER DEFAULT 0,
                total_hits INTEGER DEFAULT 0,
                last_updated TEXT
            )
        """
        )

        # Initialize stats if empty
        cursor.execute("SELECT COUNT(*) FROM cache_stats")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                """
                INSERT INTO cache_stats (total_queries, total_hits, last_updated)
                VALUES (0, 0, ?)
            """,
                (datetime.now(timezone.utc).isoformat(),),
            )

        conn.commit()
        conn.close()
        logger.info("Real cache system initialized")

    def _generate_key(self, data_type: str, params: Dict[str, Any]) -> str:
        """Generate a unique cache key."""
        # Create a deterministic string from parameters
        param_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(f"{data_type}:{param_str}".encode(), usedforsecurity=False).hexdigest()

    def get(self, data_type: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get data from cache."""
        key = self._generate_key(data_type, params)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT data, expires_at, hit_count FROM cache_entries 
                WHERE key = ? AND expires_at > ?
            """,
                (key, datetime.now(timezone.utc).isoformat()),
            )

            result = cursor.fetchone()
            if result:
                data, expires_at, hit_count = result

                # Update hit count and last accessed
                cursor.execute(
                    """
                    UPDATE cache_entries 
                    SET hit_count = hit_count + 1, last_accessed = ?
                    WHERE key = ?
                """,
                    (datetime.now(timezone.utc).isoformat(), key),
                )

                # Update total hits in stats
                cursor.execute(
                    """
                    UPDATE cache_stats 
                    SET total_hits = total_hits + 1, last_updated = ?
                """,
                    (datetime.now(timezone.utc).isoformat(),),
                )

                conn.commit()

                logger.info(f"Cache HIT for {data_type}: {key}")
                return json.loads(data)
            else:
                logger.info(f"Cache MISS for {data_type}: {key}")
                return None

        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None
        finally:
            conn.close()

    def set(
        self,
        data_type: str,
        params: Dict[str, Any],
        data: Dict[str, Any],
        ttl_minutes: int = 30,
    ) -> bool:
        """Save data to cache."""
        key = self._generate_key(data_type, params)
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=ttl_minutes)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Check if entry already exists
            cursor.execute("SELECT key FROM cache_entries WHERE key = ?", (key,))
            exists = cursor.fetchone()

            if exists:
                # Update existing entry
                cursor.execute(
                    """
                    UPDATE cache_entries 
                    SET data = ?, expires_at = ?, last_accessed = ?
                    WHERE key = ?
                """,
                    (json.dumps(data), expires_at.isoformat(), now.isoformat(), key),
                )
            else:
                # Insert new entry
                cursor.execute(
                    """
                    INSERT INTO cache_entries (key, data_type, data, created_at, expires_at, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        key,
                        data_type,
                        json.dumps(data),
                        now.isoformat(),
                        expires_at.isoformat(),
                        now.isoformat(),
                    ),
                )

                # Update total queries in stats
                cursor.execute(
                    """
                    UPDATE cache_stats 
                    SET total_queries = total_queries + 1, last_updated = ?
                """,
                    (now.isoformat(),),
                )

            conn.commit()
            logger.info(f"Cache SET for {data_type}: {key}")
            return True

        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
        finally:
            conn.close()

    def get_statistics(self) -> Dict[str, Any]:
        """Get real cache statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Get basic stats
            cursor.execute("SELECT total_queries, total_hits FROM cache_stats")
            total_queries, total_hits = cursor.fetchone()

            # Get current cache entries
            cursor.execute(
                "SELECT COUNT(*) FROM cache_entries WHERE expires_at > ?",
                (datetime.now(timezone.utc).isoformat(),),
            )
            active_queries = cursor.fetchone()[0]

            # Get expired entries
            cursor.execute(
                "SELECT COUNT(*) FROM cache_entries WHERE expires_at <= ?",
                (datetime.now(timezone.utc).isoformat(),),
            )
            expired_queries = cursor.fetchone()[0]

            # Get popular queries
            cursor.execute(
                """
                SELECT data_type, hit_count, last_accessed 
                FROM cache_entries 
                WHERE expires_at > ?
                ORDER BY hit_count DESC 
                LIMIT 5
            """,
                (datetime.now(timezone.utc).isoformat(),),
            )

            popular_queries = []
            for row in cursor.fetchall():
                popular_queries.append(
                    {"data_type": row[0], "hit_count": row[1], "last_accessed": row[2]}
                )

            return {
                "total_cached_queries": total_queries or 0,
                "expired_queries": expired_queries,
                "active_queries": active_queries,
                "total_cache_hits": total_hits or 0,
                "average_hits_per_query": (
                    (total_hits / total_queries)
                    if total_queries and total_queries > 0
                    else 0
                ),
                "popular_queries": popular_queries,
            }

        except Exception as e:
            logger.error(f"Error getting cache statistics: {e}")
            return {
                "total_cached_queries": 0,
                "expired_queries": 0,
                "active_queries": 0,
                "total_cache_hits": 0,
                "average_hits_per_query": 0,
                "popular_queries": [],
            }
        finally:
            conn.close()

    def clear_expired(self) -> int:
        """Clear expired cache entries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "DELETE FROM cache_entries WHERE expires_at <= ?",
                (datetime.now(timezone.utc).isoformat(),),
            )
            cleared_count = cursor.rowcount
            conn.commit()

            logger.info(f"Cleared {cleared_count} expired cache entries")
            return cleared_count

        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}")
            return 0
        finally:
            conn.close()


# Global instance
real_cache = RealCacheSystem()
