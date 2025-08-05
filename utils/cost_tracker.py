#!/usr/bin/env python3
"""
Cost Tracking System for API Usage
Monitors costs for OpenAI, Tavily, NewsAPI, and other services.
"""

import os
import json
import time
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
from contextlib import asynccontextmanager


@dataclass
class APICall:
    """Represents a single API call with cost tracking."""

    service: str
    endpoint: str
    timestamp: datetime
    tokens_input: Optional[int] = None
    tokens_output: Optional[int] = None
    cost_usd: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CostTracker:
    """Comprehensive cost tracking system for API usage."""

    def __init__(self, db_path: str = "cost_tracking.db"):
        self.db_path = db_path
        self.init_database()

        # Cost rates (per 1K tokens or per call)
        self.cost_rates = {
            "openai": {
                "gpt-4-turbo": {"input": 0.01, "output": 0.03},  # per 1K tokens
                "gpt-4": {"input": 0.03, "output": 0.06},
                "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
                "text-embedding-ada-002": {"input": 0.0001, "output": 0.0},
            },
            "tavily": {"search": {"per_call": 0.01}},  # per search call
            "newsapi": {"everything": {"per_call": 0.001}},  # per API call
            "milvus": {
                "insert": {"per_call": 0.0},  # free tier
                "search": {"per_call": 0.0},
            },
        }

    def init_database(self):
        """Initialize SQLite database for cost tracking."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS api_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                tokens_input INTEGER,
                tokens_output INTEGER,
                cost_usd REAL NOT NULL,
                success BOOLEAN NOT NULL,
                error_message TEXT,
                metadata TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_costs (
                date TEXT PRIMARY KEY,
                total_cost REAL NOT NULL,
                openai_cost REAL NOT NULL,
                tavily_cost REAL NOT NULL,
                newsapi_cost REAL NOT NULL,
                milvus_cost REAL NOT NULL,
                call_count INTEGER NOT NULL
            )
        """
        )

        conn.commit()
        conn.close()

    def calculate_cost(
        self, service: str, model: str, tokens_input: int = 0, tokens_output: int = 0
    ) -> float:
        """Calculate cost for API usage."""
        if service not in self.cost_rates:
            return 0.0

        rates = self.cost_rates[service]
        if model not in rates:
            return 0.0

        model_rates = rates[model]

        if "per_call" in model_rates:
            return model_rates["per_call"]

        input_cost = (tokens_input / 1000) * model_rates.get("input", 0)
        output_cost = (tokens_output / 1000) * model_rates.get("output", 0)

        return input_cost + output_cost

    async def track_call(
        self,
        service: str,
        endpoint: str,
        model: str = "",
        tokens_input: int = 0,
        tokens_output: int = 0,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> APICall:
        """Track an API call and calculate its cost."""
        cost = self.calculate_cost(service, model, tokens_input, tokens_output)

        api_call = APICall(
            service=service,
            endpoint=endpoint,
            timestamp=datetime.now(timezone.utc),
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            cost_usd=cost,
            success=success,
            error_message=error_message,
            metadata=metadata,
        )

        # Store in database
        await self.store_call(api_call)

        return api_call

    async def store_call(self, api_call: APICall):
        """Store API call in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO api_calls 
            (service, endpoint, timestamp, tokens_input, tokens_output, cost_usd, success, error_message, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                api_call.service,
                api_call.endpoint,
                api_call.timestamp.isoformat(),
                api_call.tokens_input,
                api_call.tokens_output,
                api_call.cost_usd,
                api_call.success,
                api_call.error_message,
                json.dumps(api_call.metadata) if api_call.metadata else None,
            ),
        )

        conn.commit()
        conn.close()

    def get_daily_summary(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Get cost summary for a specific date."""
        if date is None:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get daily costs
        cursor.execute(
            """
            SELECT total_cost, openai_cost, tavily_cost, newsapi_cost, milvus_cost, call_count
            FROM daily_costs WHERE date = ?
        """,
            (date,),
        )

        daily_result = cursor.fetchone()

        if not daily_result:
            # Calculate from api_calls table
            cursor.execute(
                """
                SELECT 
                    SUM(cost_usd) as total_cost,
                    COUNT(*) as call_count,
                    SUM(CASE WHEN service = 'openai' THEN cost_usd ELSE 0 END) as openai_cost,
                    SUM(CASE WHEN service = 'tavily' THEN cost_usd ELSE 0 END) as tavily_cost,
                    SUM(CASE WHEN service = 'newsapi' THEN cost_usd ELSE 0 END) as newsapi_cost,
                    SUM(CASE WHEN service = 'milvus' THEN cost_usd ELSE 0 END) as milvus_cost
                FROM api_calls 
                WHERE DATE(timestamp) = ?
            """,
                (date,),
            )

            result = cursor.fetchone()
            if result and result[0]:
                (
                    total_cost,
                    call_count,
                    openai_cost,
                    tavily_cost,
                    newsapi_cost,
                    milvus_cost,
                ) = result

                # Store in daily_costs table
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO daily_costs 
                    (date, total_cost, openai_cost, tavily_cost, newsapi_cost, milvus_cost, call_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        date,
                        total_cost,
                        openai_cost,
                        tavily_cost,
                        newsapi_cost,
                        milvus_cost,
                        call_count,
                    ),
                )

                conn.commit()
                daily_result = (
                    total_cost,
                    openai_cost,
                    tavily_cost,
                    newsapi_cost,
                    milvus_cost,
                    call_count,
                )
            else:
                daily_result = (0.0, 0.0, 0.0, 0.0, 0.0, 0)

        # Get service breakdown
        cursor.execute(
            """
            SELECT service, COUNT(*) as calls, SUM(cost_usd) as cost
            FROM api_calls 
            WHERE DATE(timestamp) = ?
            GROUP BY service
        """,
            (date,),
        )

        service_breakdown = {}
        for service, calls, cost in cursor.fetchall():
            service_breakdown[service] = {"calls": calls, "cost": cost}

        conn.close()

        total_cost, openai_cost, tavily_cost, newsapi_cost, milvus_cost, call_count = (
            daily_result
        )

        return {
            "date": date,
            "total_cost": total_cost,
            "call_count": call_count,
            "service_costs": {
                "openai": openai_cost,
                "tavily": tavily_cost,
                "newsapi": newsapi_cost,
                "milvus": milvus_cost,
            },
            "service_breakdown": service_breakdown,
        }

    def get_monthly_summary(self, year: int, month: int) -> Dict[str, Any]:
        """Get cost summary for a specific month."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 
                SUM(cost_usd) as total_cost,
                COUNT(*) as call_count,
                SUM(CASE WHEN service = 'openai' THEN cost_usd ELSE 0 END) as openai_cost,
                SUM(CASE WHEN service = 'tavily' THEN cost_usd ELSE 0 END) as tavily_cost,
                SUM(CASE WHEN service = 'newsapi' THEN cost_usd ELSE 0 END) as newsapi_cost,
                SUM(CASE WHEN service = 'milvus' THEN cost_usd ELSE 0 END) as milvus_cost
            FROM api_calls 
            WHERE strftime('%Y-%m', timestamp) = ?
        """,
            (f"{year:04d}-{month:02d}",),
        )

        result = cursor.fetchone()
        conn.close()

        if result and result[0]:
            (
                total_cost,
                call_count,
                openai_cost,
                tavily_cost,
                newsapi_cost,
                milvus_cost,
            ) = result
        else:
            total_cost = call_count = openai_cost = tavily_cost = newsapi_cost = (
                milvus_cost
            ) = 0

        return {
            "year": year,
            "month": month,
            "total_cost": total_cost,
            "call_count": call_count,
            "service_costs": {
                "openai": openai_cost,
                "tavily": tavily_cost,
                "newsapi": newsapi_cost,
                "milvus": milvus_cost,
            },
        }

    def get_recent_calls(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent API calls."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT service, endpoint, timestamp, tokens_input, tokens_output, cost_usd, success, error_message
            FROM api_calls 
            ORDER BY timestamp DESC 
            LIMIT ?
        """,
            (limit,),
        )

        calls = []
        for row in cursor.fetchall():
            (
                service,
                endpoint,
                timestamp,
                tokens_input,
                tokens_output,
                cost_usd,
                success,
                error_message,
            ) = row
            calls.append(
                {
                    "service": service,
                    "endpoint": endpoint,
                    "timestamp": timestamp,
                    "tokens_input": tokens_input,
                    "tokens_output": tokens_output,
                    "cost_usd": cost_usd,
                    "success": success,
                    "error_message": error_message,
                }
            )

        conn.close()
        return calls


# Global cost tracker instance
cost_tracker = CostTracker()


@asynccontextmanager
async def track_api_call(
    service: str,
    endpoint: str,
    model: str = "",
    tokens_input: int = 0,
    tokens_output: int = 0,
    metadata: Optional[Dict[str, Any]] = None,
):
    """Context manager for tracking API calls."""
    start_time = time.time()
    success = True
    error_message = None

    try:
        yield
    except Exception as e:
        success = False
        error_message = str(e)
        raise
    finally:
        await cost_tracker.track_call(
            service=service,
            endpoint=endpoint,
            model=model,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            success=success,
            error_message=error_message,
            metadata=metadata,
        )


# Convenience functions for specific services
async def track_openai_call(
    model: str,
    tokens_input: int = 0,
    tokens_output: int = 0,
    metadata: Optional[Dict[str, Any]] = None,
):
    """Track OpenAI API call."""
    return await cost_tracker.track_call(
        service="openai",
        endpoint=model,
        model=model,
        tokens_input=tokens_input,
        tokens_output=tokens_output,
        metadata=metadata,
    )


async def track_tavily_call(
    endpoint: str = "search", metadata: Optional[Dict[str, Any]] = None
):
    """Track Tavily API call."""
    return await cost_tracker.track_call(
        service="tavily", endpoint=endpoint, model="search", metadata=metadata
    )


async def track_newsapi_call(
    endpoint: str = "everything", metadata: Optional[Dict[str, Any]] = None
):
    """Track NewsAPI call."""
    return await cost_tracker.track_call(
        service="newsapi", endpoint=endpoint, model="everything", metadata=metadata
    )


async def track_milvus_call(endpoint: str, metadata: Optional[Dict[str, Any]] = None):
    """Track Milvus API call."""
    return await cost_tracker.track_call(
        service="milvus", endpoint=endpoint, model=endpoint, metadata=metadata
    )
