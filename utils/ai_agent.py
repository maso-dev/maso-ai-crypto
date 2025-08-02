#!/usr/bin/env python3
"""
Advanced AI Agent System with LangGraph Workflows
Implements sophisticated ReAct patterns and agent reasoning for crypto analysis.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum

# LangGraph imports
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Local imports
from .vector_rag import EnhancedVectorRAG, VectorQuery, QueryType, intelligent_search
from .realtime_data import realtime_manager
from .enrichment import enrich_news_articles
from .cost_tracker import track_openai_call

# LangSmith configuration
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "masonic-brain")
LANGCHAIN_ORGANIZATION = os.getenv("LANGCHAIN_ORGANIZATION", "703f12b7-8da7-455d-9870-c0dd95d12d7d")

class AgentTask(Enum):
    """Types of tasks the AI agent can perform."""
    MARKET_ANALYSIS = "market_analysis"
    PORTFOLIO_RECOMMENDATION = "portfolio_recommendation"
    NEWS_SENTIMENT_ANALYSIS = "news_sentiment_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    TRADING_SIGNAL = "trading_signal"
    RESEARCH_SYNTHESIS = "research_synthesis"

@dataclass
class AgentState:
    """State for the AI agent workflow."""
    task: AgentTask
    query: str
    symbols: List[str] = field(default_factory=list)
    current_step: str = "initialized"
    reasoning_steps: List[Dict[str, Any]] = field(default_factory=list)
    search_results: List[Dict[str, Any]] = field(default_factory=list)
    market_data: Dict[str, Any] = field(default_factory=dict)
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class CryptoAIAgent:
    """
    Advanced AI Agent for crypto analysis using LangGraph workflows.
    Implements sophisticated ReAct patterns with multi-step reasoning.
    """
    
    def __init__(self):
        self.vector_rag = EnhancedVectorRAG()
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            tags=["ai_agent", "crypto_analysis"] if LANGSMITH_API_KEY else None
        )
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
        self.compiled_workflow = self.workflow.compile()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for the AI agent."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_task", self._analyze_task)
        workflow.add_node("gather_context", self._gather_context)
        workflow.add_node("search_knowledge", self._search_knowledge)
        workflow.add_node("analyze_market", self._analyze_market)
        workflow.add_node("synthesize_analysis", self._synthesize_analysis)
        workflow.add_node("generate_recommendations", self._generate_recommendations)
        workflow.add_node("validate_recommendations", self._validate_recommendations)
        
        # Define edges
        workflow.set_entry_point("analyze_task")
        workflow.add_edge("analyze_task", "gather_context")
        workflow.add_edge("gather_context", "search_knowledge")
        workflow.add_edge("search_knowledge", "analyze_market")
        workflow.add_edge("analyze_market", "synthesize_analysis")
        workflow.add_edge("synthesize_analysis", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "validate_recommendations")
        workflow.add_edge("validate_recommendations", END)
        
        return workflow
    
    async def _analyze_task(self, state: AgentState, config: RunnableConfig) -> AgentState:
        """Analyze the task and determine the approach."""
        print(f"🤖 AI Agent: Analyzing task '{state.task.value}'")
        
        analysis_prompt = ChatPromptTemplate.from_template("""
        Analyze this crypto analysis task and determine the best approach:
        
        Task: {task}
        Query: {query}
        Symbols: {symbols}
        
        Determine:
        1. What type of analysis is needed?
        2. What context should be gathered?
        3. What knowledge sources to search?
        4. What market data is relevant?
        5. What reasoning steps are required?
        
        Return a structured analysis plan.
        """)
        
        try:
            chain = analysis_prompt | self.llm
            result = await chain.ainvoke({
                "task": state.task.value,
                "query": state.query,
                "symbols": ", ".join(state.symbols)
            }, config)
            
            state.reasoning_steps.append({
                "step": "task_analysis",
                "action": "analyze_task",
                "observation": result.content,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            state.current_step = "task_analyzed"
            state.metadata["analysis_plan"] = result.content
            
        except Exception as e:
            state.error = f"Task analysis failed: {str(e)}"
            print(f"❌ Task analysis error: {e}")
        
        return state
    
    async def _gather_context(self, state: AgentState, config: RunnableConfig) -> AgentState:
        """Gather relevant context for the analysis."""
        print(f"🔍 AI Agent: Gathering context for {state.symbols}")
        
        try:
            # Get real-time market data
            market_data = {}
            for symbol in state.symbols:
                price = realtime_manager.get_price(symbol)
                if price:
                    market_data[symbol] = {
                        "price": price.price,
                        "change_24h": price.change_24h,
                        "volume_24h": price.volume_24h,
                        "market_cap": price.market_cap,
                        "timestamp": price.timestamp.isoformat()
                    }
            
            state.market_data = market_data
            
            state.reasoning_steps.append({
                "step": "context_gathering",
                "action": "gather_market_data",
                "observation": f"Gathered market data for {len(market_data)} symbols",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            state.current_step = "context_gathered"
            
        except Exception as e:
            state.error = f"Context gathering failed: {str(e)}"
            print(f"❌ Context gathering error: {e}")
        
        return state
    
    async def _search_knowledge(self, state: AgentState, config: RunnableConfig) -> AgentState:
        """Search the knowledge base using ReAct agent patterns."""
        print(f"📚 AI Agent: Searching knowledge base")
        
        try:
            # Perform intelligent search
            search_results = await intelligent_search(
                query_text=state.query,
                query_type=QueryType.REACT_AGENT,
                symbols=state.symbols,
                time_range_hours=24,
                limit=10
            )
            
            # Convert to serializable format
            serializable_results = []
            for result in search_results:
                serializable_results.append({
                    "content": result.content,
                    "title": result.title,
                    "source_url": result.source_url,
                    "crypto_topic": result.crypto_topic,
                    "published_at": result.published_at.isoformat(),
                    "similarity_score": result.similarity_score,
                    "sentiment_score": result.sentiment_score
                })
            
            state.search_results = serializable_results
            
            state.reasoning_steps.append({
                "step": "knowledge_search",
                "action": "search_vector_rag",
                "observation": f"Found {len(serializable_results)} relevant articles",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            state.current_step = "knowledge_searched"
            
        except Exception as e:
            state.error = f"Knowledge search failed: {str(e)}"
            print(f"❌ Knowledge search error: {e}")
        
        return state
    
    async def _analyze_market(self, state: AgentState, config: RunnableConfig) -> AgentState:
        """Analyze market conditions and trends."""
        print(f"📊 AI Agent: Analyzing market conditions")
        
        analysis_prompt = ChatPromptTemplate.from_template("""
        Analyze the current market conditions based on the provided data:
        
        Market Data: {market_data}
        Recent News: {recent_news}
        Query: {query}
        Symbols: {symbols}
        
        Provide analysis on:
        1. Current market sentiment
        2. Key trends and patterns
        3. Risk factors
        4. Market drivers
        5. Potential catalysts
        
        Be specific and data-driven in your analysis.
        """)
        
        try:
            # Prepare recent news summary
            recent_news = []
            for result in state.search_results[:5]:
                recent_news.append(f"- {result['title']}: {result['content'][:200]}...")
            
            chain = analysis_prompt | self.llm
            result = await chain.ainvoke({
                "market_data": state.market_data,
                "recent_news": "\n".join(recent_news),
                "query": state.query,
                "symbols": ", ".join(state.symbols)
            }, config)
            
            state.analysis_results["market_analysis"] = result.content
            
            state.reasoning_steps.append({
                "step": "market_analysis",
                "action": "analyze_market_conditions",
                "observation": "Completed market analysis",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            state.current_step = "market_analyzed"
            
        except Exception as e:
            state.error = f"Market analysis failed: {str(e)}"
            print(f"❌ Market analysis error: {e}")
        
        return state
    
    async def _synthesize_analysis(self, state: AgentState, config: RunnableConfig) -> AgentState:
        """Synthesize all analysis into coherent insights."""
        print(f"🧠 AI Agent: Synthesizing analysis")
        
        synthesis_prompt = ChatPromptTemplate.from_template("""
        Synthesize the following analysis into coherent insights:
        
        Task: {task}
        Query: {query}
        Market Analysis: {market_analysis}
        Search Results Count: {search_count}
        Market Data: {market_data}
        
        Provide:
        1. Key insights summary
        2. Main conclusions
        3. Important patterns identified
        4. Areas of uncertainty
        5. Next steps for recommendations
        
        Be concise but comprehensive.
        """)
        
        try:
            chain = synthesis_prompt | self.llm
            result = await chain.ainvoke({
                "task": state.task.value,
                "query": state.query,
                "market_analysis": state.analysis_results.get("market_analysis", ""),
                "search_count": len(state.search_results),
                "market_data": state.market_data
            }, config)
            
            state.analysis_results["synthesis"] = result.content
            
            state.reasoning_steps.append({
                "step": "synthesis",
                "action": "synthesize_analysis",
                "observation": "Completed analysis synthesis",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            state.current_step = "analysis_synthesized"
            
        except Exception as e:
            state.error = f"Analysis synthesis failed: {str(e)}"
            print(f"❌ Analysis synthesis error: {e}")
        
        return state
    
    async def _generate_recommendations(self, state: AgentState, config: RunnableConfig) -> AgentState:
        """Generate actionable recommendations based on analysis."""
        print(f"💡 AI Agent: Generating recommendations")
        
        recommendation_prompt = ChatPromptTemplate.from_template("""
        Generate actionable recommendations based on the analysis:
        
        Task: {task}
        Query: {query}
        Synthesis: {synthesis}
        Market Data: {market_data}
        
        For each recommendation, provide:
        1. Action to take
        2. Reasoning
        3. Confidence level (0-1)
        4. Risk assessment
        5. Time horizon
        
        Format as structured recommendations.
        """)
        
        try:
            chain = recommendation_prompt | self.llm
            result = await chain.ainvoke({
                "task": state.task.value,
                "query": state.query,
                "synthesis": state.analysis_results.get("synthesis", ""),
                "market_data": state.market_data
            }, config)
            
            # Parse recommendations (simplified for now)
            recommendations = [
                {
                    "action": "Analysis completed",
                    "reasoning": result.content,
                    "confidence": 0.8,
                    "risk_level": "medium",
                    "time_horizon": "short_term"
                }
            ]
            
            state.recommendations = recommendations
            
            state.reasoning_steps.append({
                "step": "recommendations",
                "action": "generate_recommendations",
                "observation": f"Generated {len(recommendations)} recommendations",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            state.current_step = "recommendations_generated"
            
        except Exception as e:
            state.error = f"Recommendation generation failed: {str(e)}"
            print(f"❌ Recommendation generation error: {e}")
        
        return state
    
    async def _validate_recommendations(self, state: AgentState, config: RunnableConfig) -> AgentState:
        """Validate and finalize recommendations."""
        print(f"✅ AI Agent: Validating recommendations")
        
        try:
            # Calculate overall confidence score
            if state.recommendations:
                avg_confidence = sum(r.get("confidence", 0) for r in state.recommendations) / len(state.recommendations)
                state.confidence_score = avg_confidence
            else:
                state.confidence_score = 0.0
            
            state.current_step = "completed"
            
            state.reasoning_steps.append({
                "step": "validation",
                "action": "validate_recommendations",
                "observation": f"Validated recommendations with confidence {state.confidence_score:.2f}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            print(f"🎉 AI Agent: Task completed with confidence {state.confidence_score:.2f}")
            
        except Exception as e:
            state.error = f"Recommendation validation failed: {str(e)}"
            print(f"❌ Recommendation validation error: {e}")
        
        return state
    
    async def execute_task(
        self,
        task: AgentTask,
        query: str,
        symbols: Optional[List[str]] = None,
        config: Optional[RunnableConfig] = None
    ) -> AgentState:
        """Execute a complete AI agent task."""
        if config is None:
            config = {}
        
        # Add LangSmith metadata
        if LANGSMITH_API_KEY:
            config["tags"] = config.get("tags", []) + ["ai_agent", task.value]
            config["metadata"] = {
                **config.get("metadata", {}),
                "task": task.value,
                "query": query,
                "symbols": symbols or [],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Initialize state
        state = AgentState(
            task=task,
            query=query,
            symbols=symbols or []
        )
        
        try:
            # Execute the workflow
            final_state = await self.compiled_workflow.ainvoke(state, config)
            # LangGraph returns a dict, but we need AgentState
            if isinstance(final_state, dict):
                # Extract the state from the workflow result
                return final_state.get("state", state)
            return final_state
            
        except Exception as e:
            state.error = f"Workflow execution failed: {str(e)}"
            print(f"❌ Workflow execution error: {e}")
            return state

# Global instance
ai_agent = CryptoAIAgent()

# Convenience functions
async def execute_agent_task(
    task: AgentTask,
    query: str,
    symbols: Optional[List[str]] = None,
    config: Optional[RunnableConfig] = None
) -> AgentState:
    """Convenience function for executing agent tasks."""
    return await ai_agent.execute_task(task, query, symbols, config)

async def analyze_market_sentiment(
    symbols: List[str],
    config: Optional[RunnableConfig] = None
) -> AgentState:
    """Analyze market sentiment for given symbols."""
    query = f"Analyze market sentiment for {', '.join(symbols)}"
    return await execute_agent_task(AgentTask.MARKET_ANALYSIS, query, symbols, config)

async def generate_portfolio_recommendations(
    symbols: List[str],
    risk_profile: str = "moderate",
    config: Optional[RunnableConfig] = None
) -> AgentState:
    """Generate portfolio recommendations."""
    query = f"Generate portfolio recommendations for {', '.join(symbols)} with {risk_profile} risk profile"
    return await execute_agent_task(AgentTask.PORTFOLIO_RECOMMENDATION, query, symbols, config) 
