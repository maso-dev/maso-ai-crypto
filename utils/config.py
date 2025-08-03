#!/usr/bin/env python3
"""
Centralized Configuration Module
Single source of truth for all API keys, settings, and environment variables.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class APIConfig:
    """API configuration settings."""
    name: str
    key_name: str
    key_value: Optional[str]
    base_url: str
    is_required: bool = True
    description: str = ""
    icon: str = "🔧"
    category: str = "external"

@dataclass
class ServiceConfig:
    """Service configuration settings."""
    name: str
    description: str
    icon: str
    category: str
    endpoints: list
    dependencies: list
    health_check_url: Optional[str] = None

class ConfigManager:
    """Centralized configuration manager."""
    
    def __init__(self):
        self.api_configs = {
            "openai": APIConfig(
                name="OpenAI",
                key_name="OPENAI_API_KEY",
                key_value=os.getenv("OPENAI_API_KEY"),
                base_url="https://api.openai.com/v1",
                description="AI language model and embeddings",
                icon="🤖",
                category="ai"
            ),
            "binance": APIConfig(
                name="Binance",
                key_name="BINANCE_API_KEY",
                key_value=os.getenv("BINANCE_API_KEY"),
                base_url="https://api.binance.com",
                description="Cryptocurrency trading and portfolio data",
                icon="💰",
                category="trading"
            ),
            "newsapi": APIConfig(
                name="NewsAPI",
                key_name="NEWSAPI_KEY",
                key_value=os.getenv("NEWSAPI_KEY"),
                base_url="https://newsapi.org/v2",
                description="News and market sentiment data",
                icon="📰",
                category="news"
            ),
            "livecoinwatch": APIConfig(
                name="LiveCoinWatch",
                key_name="LIVECOINWATCH_API_KEY",
                key_value=os.getenv("LIVECOINWATCH_API_KEY"),
                base_url="https://api.livecoinwatch.com",
                description="Real-time cryptocurrency price data",
                icon="🪙",
                category="pricing"
            ),
            "langsmith": APIConfig(
                name="LangSmith",
                key_name="LANGSMITH_API_KEY",
                key_value=os.getenv("LANGSMITH_API_KEY"),
                base_url="https://api.smith.langchain.com",
                description="AI workflow tracing and monitoring",
                icon="🔍",
                category="monitoring"
            ),
            "neo4j": APIConfig(
                name="Neo4j",
                key_name="NEO4J_URI",
                key_value=os.getenv("NEO4J_URI"),
                base_url="bolt://localhost:7687",
                description="Graph database for knowledge graphs",
                icon="🕸️",
                category="database"
            )
        }
        
        self.service_configs = {
            "ai_agent": ServiceConfig(
                name="AI Agent System",
                description="LangGraph-based AI agent for crypto analysis",
                icon="🧠",
                category="backend",
                endpoints=["/api/dream-team", "/api/opportunities"],
                dependencies=["openai", "langsmith"],
                health_check_url="/api/health"
            ),
            "vector_rag": ServiceConfig(
                name="Vector RAG",
                description="Vector-based retrieval augmented generation",
                icon="📊",
                category="backend",
                endpoints=["/api/news-briefing"],
                dependencies=["openai"],
                health_check_url="/api/health"
            ),
            "hybrid_rag": ServiceConfig(
                name="Hybrid RAG",
                description="Combined vector and graph search",
                icon="🔗",
                category="backend",
                endpoints=["/api/context"],
                dependencies=["openai", "neo4j"],
                health_check_url="/api/health"
            ),
            "livecoinwatch_processor": ServiceConfig(
                name="LiveCoinWatch Processor",
                description="Real-time crypto data collection and analysis",
                icon="🪙",
                category="backend",
                endpoints=["/livecoinwatch/health", "/livecoinwatch/latest-prices"],
                dependencies=["livecoinwatch"],
                health_check_url="/livecoinwatch/health"
            ),
            "realtime_data": ServiceConfig(
                name="Real-time Data",
                description="Live market data streaming",
                icon="⚡",
                category="backend",
                endpoints=["/api/portfolio", "/api/top-movers"],
                dependencies=["binance"],
                health_check_url="/api/health"
            )
        }
    
    def get_api_config(self, name: str) -> Optional[APIConfig]:
        """Get API configuration by name."""
        return self.api_configs.get(name)
    
    def get_service_config(self, name: str) -> Optional[ServiceConfig]:
        """Get service configuration by name."""
        return self.service_configs.get(name)
    
    def get_all_api_configs(self) -> Dict[str, APIConfig]:
        """Get all API configurations."""
        return self.api_configs
    
    def get_all_service_configs(self) -> Dict[str, ServiceConfig]:
        """Get all service configurations."""
        return self.service_configs
    
    def is_api_configured(self, name: str) -> bool:
        """Check if API is properly configured."""
        config = self.get_api_config(name)
        if not config:
            return False
        return bool(config.key_value)
    
    def get_missing_apis(self) -> list:
        """Get list of missing API configurations."""
        missing = []
        for name, config in self.api_configs.items():
            if config.is_required and not config.key_value:
                missing.append(name)
        return missing
    
    def get_configured_apis(self) -> list:
        """Get list of configured APIs."""
        configured = []
        for name, config in self.api_configs.items():
            if config.key_value:
                configured.append(name)
        return configured
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get comprehensive configuration summary."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_apis": len(self.api_configs),
            "configured_apis": len(self.get_configured_apis()),
            "missing_apis": len(self.get_missing_apis()),
            "total_services": len(self.service_configs),
            "apis": {
                name: {
                    "name": config.name,
                    "configured": bool(config.key_value),
                    "category": config.category,
                    "icon": config.icon,
                    "description": config.description
                }
                for name, config in self.api_configs.items()
            },
            "services": {
                name: {
                    "name": config.name,
                    "category": config.category,
                    "icon": config.icon,
                    "description": config.description,
                    "endpoints": config.endpoints,
                    "dependencies": config.dependencies
                }
                for name, config in self.service_configs.items()
            }
        }

# Global instance
config_manager = ConfigManager()

# Convenience functions
def get_api_key(name: str) -> Optional[str]:
    """Get API key by service name."""
    config = config_manager.get_api_config(name)
    return config.key_value if config else None

def is_api_available(name: str) -> bool:
    """Check if API is available (configured and working)."""
    return config_manager.is_api_configured(name)

def get_config_summary() -> Dict[str, Any]:
    """Get configuration summary."""
    return config_manager.get_config_summary() 
