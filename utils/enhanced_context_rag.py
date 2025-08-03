#!/usr/bin/env python3
"""
Enhanced Context RAG System
Provides useful, actionable context for frontend UI with portfolio insights and market analysis.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from enum import Enum

# Import existing utilities
from .intelligent_news_cache import get_portfolio_news, get_cached_news_for_symbols
from .vector_rag import EnhancedVectorRAG, VectorQuery, QueryType, intelligent_search
from .hybrid_rag import HybridRAGSystem, HybridQuery, HybridQueryType
from .binance_client import get_portfolio_data
from .ai_agent import CryptoAIAgent, AgentTask
from .enrichment import enrich_news_articles

class ContextType(Enum):
    """Types of context for frontend UI."""
    PORTFOLIO_INSIGHTS = "portfolio_insights"
    MARKET_ANALYSIS = "market_analysis"
    TRADING_OPPORTUNITIES = "trading_opportunities"
    RISK_ASSESSMENT = "risk_assessment"
    NEWS_SENTIMENT = "news_sentiment"
    TECHNICAL_ANALYSIS = "technical_analysis"
    FUNDAMENTAL_ANALYSIS = "fundamental_analysis"
    SOCIAL_SENTIMENT = "social_sentiment"

@dataclass
class PortfolioInsight:
    """Portfolio-specific insight for frontend."""
    symbol: str
    insight_type: str  # "performance", "risk", "opportunity", "warning"
    title: str
    description: str
    confidence_score: float
    actionable: bool
    recommended_action: Optional[str] = None
    supporting_data: Dict[str, Any] = None
    timestamp: datetime = None

@dataclass
class MarketContext:
    """Market context for frontend UI."""
    context_type: ContextType
    title: str
    summary: str
    key_points: List[str]
    supporting_articles: List[Dict[str, Any]]
    sentiment_score: float
    confidence_score: float
    actionable_insights: List[str]
    risk_level: str  # "low", "medium", "high", "critical"
    timestamp: datetime = None

class EnhancedContextRAG:
    """
    Enhanced RAG system that provides useful, actionable context for frontend UI.
    Focuses on portfolio insights, market analysis, and trading opportunities.
    """
    
    def __init__(self):
        self.vector_rag = EnhancedVectorRAG()
        self.hybrid_rag = HybridRAGSystem()
        self.ai_agent = CryptoAIAgent()
        self.news_cache = None  # Will be initialized when needed
        
        print("🧠 Enhanced Context RAG System initialized")
        print(f"   Vector RAG: {'✅' if self.vector_rag else '❌'}")
        print(f"   Hybrid RAG: {'✅' if self.hybrid_rag else '❌'}")
        print(f"   AI Agent: {'✅' if self.ai_agent else '❌'}")
    
    async def get_portfolio_context(
        self,
        include_news: bool = True,
        include_analysis: bool = True,
        include_opportunities: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive portfolio context for frontend UI.
        
        Args:
            include_news: Include news sentiment analysis
            include_analysis: Include AI analysis
            include_opportunities: Include trading opportunities
            
        Returns:
            Dictionary with portfolio context data
        """
        print("🎯 Generating comprehensive portfolio context...")
        
        # Get portfolio data
        portfolio_data = await get_portfolio_data()
        
        if not portfolio_data:
            return {
                "error": "No portfolio data available",
                "portfolio_context": {},
                "market_context": {},
                "opportunities": [],
                "insights": []
            }
        
        # Initialize results
        results = {
            "portfolio_summary": self._create_portfolio_summary(portfolio_data),
            "portfolio_insights": [],
            "market_context": {},
            "trading_opportunities": [],
            "risk_assessment": {},
            "news_sentiment": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Get portfolio symbols
        portfolio_symbols = [asset.asset for asset in portfolio_data.assets if asset.total > 0]
        
        # 1. Portfolio Insights
        if include_analysis:
            print("   📊 Generating portfolio insights...")
            portfolio_insights = await self._generate_portfolio_insights(portfolio_data)
            results["portfolio_insights"] = portfolio_insights
        
        # 2. News Sentiment Analysis
        if include_news:
            print("   📰 Analyzing news sentiment...")
            news_sentiment = await self._analyze_news_sentiment(portfolio_symbols)
            results["news_sentiment"] = news_sentiment
        
        # 3. Market Context
        print("   🌍 Gathering market context...")
        market_context = await self._get_market_context(portfolio_symbols)
        results["market_context"] = market_context
        
        # 4. Trading Opportunities
        if include_opportunities:
            print("   💡 Identifying trading opportunities...")
            opportunities = await self._identify_trading_opportunities(portfolio_symbols)
            results["trading_opportunities"] = opportunities
        
        # 5. Risk Assessment
        print("   ⚠️ Assessing portfolio risk...")
        risk_assessment = await self._assess_portfolio_risk(portfolio_data)
        results["risk_assessment"] = risk_assessment
        
        print("✅ Portfolio context generated successfully")
        return results
    
    def _create_portfolio_summary(self, portfolio_data) -> Dict[str, Any]:
        """Create a summary of portfolio data."""
        total_value = portfolio_data.total_value_usdt
        total_cost = portfolio_data.total_cost_basis
        total_roi = portfolio_data.total_roi_percentage
        
        # Calculate top performers and underperformers
        assets_with_roi = [
            {
                "symbol": asset.asset,
                "value": asset.usdt_value,
                "roi": asset.roi_percentage,
                "weight": (asset.usdt_value / total_value) * 100 if total_value > 0 else 0
            }
            for asset in portfolio_data.assets if asset.total > 0
        ]
        
        assets_with_roi.sort(key=lambda x: x["roi"], reverse=True)
        
        return {
            "total_value_usdt": total_value,
            "total_cost_basis": total_cost,
            "total_roi_percentage": total_roi,
            "total_roi_usdt": total_value - total_cost,
            "asset_count": len([a for a in portfolio_data.assets if a.total > 0]),
            "top_performers": assets_with_roi[:3],
            "underperformers": assets_with_roi[-3:],
            "largest_positions": sorted(assets_with_roi, key=lambda x: x["value"], reverse=True)[:3],
            "portfolio_health": self._calculate_portfolio_health(assets_with_roi)
        }
    
    def _calculate_portfolio_health(self, assets_with_roi: List[Dict]) -> str:
        """Calculate overall portfolio health."""
        if not assets_with_roi:
            return "unknown"
        
        avg_roi = sum(asset["roi"] for asset in assets_with_roi) / len(assets_with_roi)
        positive_assets = sum(1 for asset in assets_with_roi if asset["roi"] > 0)
        positive_ratio = positive_assets / len(assets_with_roi)
        
        if avg_roi > 20 and positive_ratio > 0.7:
            return "excellent"
        elif avg_roi > 10 and positive_ratio > 0.5:
            return "good"
        elif avg_roi > 0:
            return "fair"
        else:
            return "poor"
    
    async def _generate_portfolio_insights(self, portfolio_data) -> List[PortfolioInsight]:
        """Generate AI-powered portfolio insights."""
        insights = []
        
        for asset in portfolio_data.assets:
            if asset.total <= 0:
                continue
            
            # Analyze individual asset performance
            insight = await self._analyze_asset_performance(asset)
            if insight:
                insights.append(insight)
        
        # Generate portfolio-level insights
        portfolio_insights = await self._analyze_portfolio_composition(portfolio_data)
        insights.extend(portfolio_insights)
        
        return insights
    
    async def _analyze_asset_performance(self, asset) -> Optional[PortfolioInsight]:
        """Analyze individual asset performance."""
        try:
            # Use AI agent to analyze asset
            analysis = await self.ai_agent.execute_task(
                task=AgentTask.MARKET_ANALYSIS,
                query=f"Analyze {asset.asset} performance and provide actionable insights",
                symbols=[asset.asset]
            )
            
            if analysis.error:
                return None
            
            # Extract insights from analysis
            roi = asset.roi_percentage
            weight = (asset.usdt_value / 100000) * 100  # Assuming 100k portfolio for weight calculation
            
            if roi > 50:
                insight_type = "performance"
                title = f"Strong Performance: {asset.asset}"
                description = f"{asset.asset} is performing exceptionally well with {roi:.1f}% ROI"
                confidence_score = 0.9
                actionable = True
                recommended_action = "Consider taking partial profits or rebalancing"
            elif roi > 20:
                insight_type = "opportunity"
                title = f"Good Performance: {asset.asset}"
                description = f"{asset.asset} shows solid performance with {roi:.1f}% ROI"
                confidence_score = 0.7
                actionable = False
                recommended_action = "Monitor for continued strength"
            elif roi < -20:
                insight_type = "warning"
                title = f"Poor Performance: {asset.asset}"
                description = f"{asset.asset} is underperforming with {roi:.1f}% ROI"
                confidence_score = 0.8
                actionable = True
                recommended_action = "Consider stop-loss or rebalancing"
            else:
                insight_type = "neutral"
                title = f"Stable Performance: {asset.asset}"
                description = f"{asset.asset} shows stable performance with {roi:.1f}% ROI"
                confidence_score = 0.6
                actionable = False
                recommended_action = None
            
            return PortfolioInsight(
                symbol=asset.asset,
                insight_type=insight_type,
                title=title,
                description=description,
                confidence_score=confidence_score,
                actionable=actionable,
                recommended_action=recommended_action,
                supporting_data={
                    "roi_percentage": roi,
                    "usdt_value": asset.usdt_value,
                    "weight_percentage": weight,
                    "analysis_summary": analysis.analysis_results.get("summary", "")
                },
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            print(f"Error analyzing {asset.asset}: {e}")
            return None
    
    async def _analyze_portfolio_composition(self, portfolio_data) -> List[PortfolioInsight]:
        """Analyze overall portfolio composition."""
        insights = []
        
        try:
            # Analyze portfolio diversification
            total_value = portfolio_data.total_value_usdt
            assets = [a for a in portfolio_data.assets if a.total > 0]
            
            if len(assets) < 3:
                insights.append(PortfolioInsight(
                    symbol="PORTFOLIO",
                    insight_type="warning",
                    title="Low Diversification",
                    description=f"Portfolio has only {len(assets)} assets, consider diversifying",
                    confidence_score=0.9,
                    actionable=True,
                    recommended_action="Add more assets to reduce concentration risk",
                    supporting_data={"asset_count": len(assets)},
                    timestamp=datetime.now(timezone.utc)
                ))
            
            # Analyze concentration risk
            largest_position = max(assets, key=lambda x: x.usdt_value)
            largest_weight = (largest_position.usdt_value / total_value) * 100
            
            if largest_weight > 50:
                insights.append(PortfolioInsight(
                    symbol="PORTFOLIO",
                    insight_type="warning",
                    title="High Concentration Risk",
                    description=f"{largest_position.asset} represents {largest_weight:.1f}% of portfolio",
                    confidence_score=0.8,
                    actionable=True,
                    recommended_action="Consider reducing position size to manage risk",
                    supporting_data={"largest_position": largest_position.asset, "weight": largest_weight},
                    timestamp=datetime.now(timezone.utc)
                ))
            
            # Overall portfolio performance
            if portfolio_data.total_roi_percentage > 30:
                insights.append(PortfolioInsight(
                    symbol="PORTFOLIO",
                    insight_type="performance",
                    title="Excellent Portfolio Performance",
                    description=f"Portfolio showing strong performance with {portfolio_data.total_roi_percentage:.1f}% ROI",
                    confidence_score=0.9,
                    actionable=False,
                    recommended_action="Continue current strategy",
                    supporting_data={"total_roi": portfolio_data.total_roi_percentage},
                    timestamp=datetime.now(timezone.utc)
                ))
            
        except Exception as e:
            print(f"Error analyzing portfolio composition: {e}")
        
        return insights
    
    async def _analyze_news_sentiment(self, symbols: List[str]) -> Dict[str, Any]:
        """Analyze news sentiment for portfolio symbols."""
        try:
            # Get news for portfolio symbols
            news_data = await get_cached_news_for_symbols(symbols, hours_back=24)
            
            if not news_data:
                return {"error": "No news data available"}
            
            # Analyze sentiment for each symbol
            sentiment_analysis = {}
            
            for symbol in symbols:
                symbol_news = [article for article in news_data if article.get("symbol") == symbol]
                
                if symbol_news:
                    # Use AI agent for sentiment analysis
                    sentiment_result = await self.ai_agent.execute_task(
                        task=AgentTask.NEWS_SENTIMENT_ANALYSIS,
                        query=f"Analyze sentiment for {symbol} based on recent news",
                        symbols=[symbol]
                    )
                    
                    sentiment_analysis[symbol] = {
                        "article_count": len(symbol_news),
                        "sentiment_score": sentiment_result.analysis_results.get("sentiment_score", 0.0),
                        "sentiment_label": sentiment_result.analysis_results.get("sentiment_label", "neutral"),
                        "key_themes": sentiment_result.analysis_results.get("key_themes", []),
                        "recent_headlines": [article["title"] for article in symbol_news[:3]]
                    }
            
            return {
                "overall_sentiment": self._calculate_overall_sentiment(sentiment_analysis),
                "symbol_sentiments": sentiment_analysis,
                "news_count": len(news_data)
            }
            
        except Exception as e:
            print(f"Error analyzing news sentiment: {e}")
            return {"error": f"Sentiment analysis failed: {str(e)}"}
    
    def _calculate_overall_sentiment(self, sentiment_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall sentiment across all symbols."""
        if not sentiment_analysis:
            return {"score": 0.0, "label": "neutral"}
        
        scores = [data["sentiment_score"] for data in sentiment_analysis.values()]
        avg_score = sum(scores) / len(scores)
        
        if avg_score > 0.6:
            label = "positive"
        elif avg_score < 0.4:
            label = "negative"
        else:
            label = "neutral"
        
        return {
            "score": avg_score,
            "label": label,
            "symbol_count": len(sentiment_analysis)
        }
    
    async def _get_market_context(self, symbols: List[str]) -> Dict[str, Any]:
        """Get market context for portfolio symbols."""
        try:
            # Get market analysis from AI agent
            market_analysis = await self.ai_agent.execute_task(
                task=AgentTask.MARKET_ANALYSIS,
                query="Provide comprehensive market analysis for current crypto market conditions",
                symbols=symbols
            )
            
            # Get recent news for market context
            market_news = await get_cached_news_for_symbols(symbols, hours_back=48)
            
            return {
                "market_summary": market_analysis.analysis_results.get("summary", ""),
                "key_trends": market_analysis.analysis_results.get("trends", []),
                "market_sentiment": market_analysis.analysis_results.get("sentiment", "neutral"),
                "risk_factors": market_analysis.analysis_results.get("risks", []),
                "opportunities": market_analysis.analysis_results.get("opportunities", []),
                "recent_news_count": len(market_news),
                "analysis_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            print(f"Error getting market context: {e}")
            return {"error": f"Market context analysis failed: {str(e)}"}
    
    async def _identify_trading_opportunities(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Identify trading opportunities for portfolio symbols."""
        opportunities = []
        
        try:
            # Get portfolio news for opportunity analysis
            news_data = await get_portfolio_news(
                include_alpha_portfolio=True,
                include_opportunity_tokens=True,
                include_personal_portfolio=True,
                hours_back=24
            )
            
            # Analyze opportunities using AI agent
            opportunity_analysis = await self.ai_agent.execute_task(
                task=AgentTask.TRADING_SIGNAL,
                query="Identify trading opportunities based on current market conditions and news",
                symbols=symbols
            )
            
            # Extract opportunities from analysis
            if opportunity_analysis.recommendations:
                for rec in opportunity_analysis.recommendations:
                    opportunities.append({
                        "symbol": rec.get("symbol", "Unknown"),
                        "opportunity_type": rec.get("type", "unknown"),
                        "description": rec.get("description", ""),
                        "confidence_score": rec.get("confidence", 0.0),
                        "risk_level": rec.get("risk", "medium"),
                        "recommended_action": rec.get("action", ""),
                        "supporting_evidence": rec.get("evidence", []),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
            
        except Exception as e:
            print(f"Error identifying trading opportunities: {e}")
        
        return opportunities
    
    async def _assess_portfolio_risk(self, portfolio_data) -> Dict[str, Any]:
        """Assess overall portfolio risk."""
        try:
            # Use AI agent for risk assessment
            risk_analysis = await self.ai_agent.execute_task(
                task=AgentTask.RISK_ASSESSMENT,
                query="Assess portfolio risk and provide risk management recommendations",
                symbols=[asset.asset for asset in portfolio_data.assets if asset.total > 0]
            )
            
            return {
                "overall_risk_level": risk_analysis.analysis_results.get("risk_level", "medium"),
                "risk_factors": risk_analysis.analysis_results.get("risk_factors", []),
                "risk_score": risk_analysis.analysis_results.get("risk_score", 0.5),
                "recommendations": risk_analysis.recommendations,
                "diversification_score": self._calculate_diversification_score(portfolio_data),
                "concentration_risk": self._calculate_concentration_risk(portfolio_data),
                "assessment_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            print(f"Error assessing portfolio risk: {e}")
            return {"error": f"Risk assessment failed: {str(e)}"}
    
    def _calculate_diversification_score(self, portfolio_data) -> float:
        """Calculate portfolio diversification score (0-1)."""
        assets = [a for a in portfolio_data.assets if a.total > 0]
        if len(assets) < 2:
            return 0.0
        
        total_value = portfolio_data.total_value_usdt
        weights = [(a.usdt_value / total_value) for a in assets]
        
        # Calculate Herfindahl-Hirschman Index (HHI)
        hhi = sum(w * w for w in weights)
        
        # Convert to diversification score (lower HHI = higher diversification)
        diversification_score = 1 - hhi
        
        return max(0.0, min(1.0, diversification_score))
    
    def _calculate_concentration_risk(self, portfolio_data) -> Dict[str, Any]:
        """Calculate concentration risk metrics."""
        assets = [a for a in portfolio_data.assets if a.total > 0]
        total_value = portfolio_data.total_value_usdt
        
        if not assets:
            return {"risk_level": "unknown", "largest_position": 0.0}
        
        weights = [(a.usdt_value / total_value) * 100 for a in assets]
        largest_weight = max(weights)
        
        if largest_weight > 50:
            risk_level = "high"
        elif largest_weight > 30:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "risk_level": risk_level,
            "largest_position": largest_weight,
            "top_3_concentration": sum(sorted(weights, reverse=True)[:3])
        }
    
    async def get_symbol_context(self, symbol: str) -> Dict[str, Any]:
        """Get detailed context for a specific symbol."""
        try:
            # Get news for symbol
            news_data = await get_cached_news_for_symbols([symbol], hours_back=24)
            
            # Get AI analysis
            analysis = await self.ai_agent.execute_task(
                task=AgentTask.MARKET_ANALYSIS,
                query=f"Provide comprehensive analysis for {symbol}",
                symbols=[symbol]
            )
            
            return {
                "symbol": symbol,
                "news_count": len(news_data),
                "recent_news": news_data[:5],
                "analysis": analysis.analysis_results,
                "recommendations": analysis.recommendations,
                "sentiment": analysis.analysis_results.get("sentiment", "neutral"),
                "confidence_score": analysis.confidence_score,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            print(f"Error getting context for {symbol}: {e}")
            return {"error": f"Context analysis failed for {symbol}: {str(e)}"}

# Global instance
enhanced_context_rag = EnhancedContextRAG()

# Convenience functions
async def get_portfolio_context(
    include_news: bool = True,
    include_analysis: bool = True,
    include_opportunities: bool = True
) -> Dict[str, Any]:
    """Get comprehensive portfolio context."""
    return await enhanced_context_rag.get_portfolio_context(
        include_news=include_news,
        include_analysis=include_analysis,
        include_opportunities=include_opportunities
    )

async def get_symbol_context(symbol: str) -> Dict[str, Any]:
    """Get detailed context for a specific symbol."""
    return await enhanced_context_rag.get_symbol_context(symbol) 
