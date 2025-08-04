#!/usr/bin/env python3
"""
Test script for Advanced AI Agent System
Tests LangGraph workflows and ReAct agent patterns.
"""

import asyncio
import os
from typing import Optional
from datetime import datetime, timezone
from langchain_core.runnables import RunnableConfig
from utils.ai_agent import (
    CryptoAIAgent, 
    AgentTask, 
    execute_agent_task,
    analyze_market_sentiment,
    generate_portfolio_recommendations
)

async def test_ai_agent_system():
    """Test the advanced AI agent system."""
    print("🧪 Testing Advanced AI Agent System")
    print("=" * 50)
    
    # Initialize the agent
    agent = CryptoAIAgent()
    print(f"✅ Initialized Crypto AI Agent")
    print(f"   LangGraph workflow: {len(agent.workflow.nodes)} nodes")
    print(f"   LangSmith: {'Enabled' if os.getenv('LANGSMITH_API_KEY') else 'Disabled'}")
    
    # Test 1: Market Analysis
    print("\n📊 Test 1: Market Analysis")
    try:
        result = await analyze_market_sentiment(["Bitcoin", "Ethereum"])
        print(f"   ✅ Market analysis completed")
        print(f"   Confidence: {result.confidence_score:.2f}")
        print(f"   Steps: {len(result.reasoning_steps)}")
        print(f"   Current step: {result.current_step}")
        if result.error:
            print(f"   ⚠️ Error: {result.error}")
    except Exception as e:
        print(f"   ❌ Market analysis failed: {e}")
    
    # Test 2: Portfolio Recommendations
    print("\n💡 Test 2: Portfolio Recommendations")
    try:
        result = await generate_portfolio_recommendations(["Bitcoin", "Ethereum", "Solana"], "moderate")
        print(f"   ✅ Portfolio recommendations completed")
        print(f"   Confidence: {result.confidence_score:.2f}")
        print(f"   Recommendations: {len(result.recommendations)}")
        print(f"   Current step: {result.current_step}")
        if result.error:
            print(f"   ⚠️ Error: {result.error}")
    except Exception as e:
        print(f"   ❌ Portfolio recommendations failed: {e}")
    
    # Test 3: Custom Task Execution
    print("\n🤖 Test 3: Custom Task Execution")
    try:
        result = await execute_agent_task(
            AgentTask.RISK_ASSESSMENT,
            "Assess risk factors for Bitcoin and Ethereum",
            ["Bitcoin", "Ethereum"]
        )
        print(f"   ✅ Custom task completed")
        print(f"   Task: {result.task.value}")
        print(f"   Confidence: {result.confidence_score:.2f}")
        print(f"   Steps: {len(result.reasoning_steps)}")
        if result.error:
            print(f"   ⚠️ Error: {result.error}")
    except Exception as e:
        print(f"   ❌ Custom task failed: {e}")
    
    # Test 4: LangGraph Workflow Steps
    print("\n🔄 Test 4: LangGraph Workflow Steps")
    try:
        result = await analyze_market_sentiment(["Bitcoin"])
        print(f"   ✅ Workflow steps:")
        for i, step in enumerate(result.reasoning_steps[:3]):  # Show first 3 steps
            print(f"   {i+1}. {step['step']}: {step['action']}")
        print(f"   ... and {len(result.reasoning_steps) - 3} more steps")
    except Exception as e:
        print(f"   ❌ Workflow test failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Advanced AI Agent System Tests Complete")

async def test_langsmith_integration():
    """Test LangSmith integration."""
    print("\n🧪 Testing LangSmith Integration")
    print("=" * 30)
    
    if not os.getenv("LANGSMITH_API_KEY"):
        print("⚠️ LANGSMITH_API_KEY not set - skipping LangSmith tests")
        return
    
    try:
        # Test with LangSmith tracing
        config: Optional[RunnableConfig] = {
            "tags": ["test", "ai_agent"],
            "metadata": {
                "test_type": "langsmith_integration",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        
        result = await execute_agent_task(
            AgentTask.MARKET_ANALYSIS,
            "Analyze current crypto market trends",
            ["Bitcoin", "Ethereum"],
            config
        )
        
        print(f"✅ LangSmith traced task completed")
        print(f"   Check LangSmith dashboard for traces")
        print(f"   Task: {result.task.value}")
        print(f"   Confidence: {result.confidence_score:.2f}")
        
    except Exception as e:
        print(f"❌ LangSmith integration failed: {e}")

async def test_agent_capabilities():
    """Test different agent capabilities."""
    print("\n🧪 Testing Agent Capabilities")
    print("=" * 30)
    
    # Test all available tasks
    tasks = [
        (AgentTask.MARKET_ANALYSIS, "market analysis"),
        (AgentTask.PORTFOLIO_RECOMMENDATION, "portfolio recommendation"),
        (AgentTask.NEWS_SENTIMENT_ANALYSIS, "news sentiment analysis"),
        (AgentTask.RISK_ASSESSMENT, "risk assessment"),
        (AgentTask.TRADING_SIGNAL, "trading signal"),
        (AgentTask.RESEARCH_SYNTHESIS, "research synthesis")
    ]
    
    for task, description in tasks:
        try:
            print(f"   Testing {description}...")
            result = await execute_agent_task(
                task,
                f"Test {description} for Bitcoin",
                ["Bitcoin"]
            )
            print(f"   ✅ {description}: {result.current_step}")
        except Exception as e:
            print(f"   ❌ {description}: {e}")

async def main():
    """Run all tests."""
    print("🚀 Starting Advanced AI Agent System Tests")
    print("=" * 60)
    
    await test_ai_agent_system()
    await test_langsmith_integration()
    await test_agent_capabilities()
    
    print("\n🎉 All AI Agent tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 
