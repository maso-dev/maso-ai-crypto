from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field, SecretStr
from typing import Dict, Any, List
import os
from utils.cost_tracker import track_openai_call

# LangSmith configuration
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
if LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "masonic-enrichment"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_ORGANIZATION"] = "703f12b7-8da7-455d-9870-c0dd95d12d7d"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Define the output schema using Pydantic
class NewsEnrichment(BaseModel):
    sentiment: float = Field(description="Sentiment score between 0.01 and 1.0")
    trust: float = Field(description="Trust score between 0.01 and 1.0")
    categories: List[str] = Field(description="List of relevant categories")
    macro_category: str = Field(description="Primary macro category")
    summary: str = Field(description="Brief summary of the article")
    urgency_score: float = Field(description="Urgency score between 0.01 and 1.0 based on time sensitivity")
    market_impact: str = Field(description="Expected market impact: 'high', 'medium', 'low'")
    time_relevance: str = Field(description="Time relevance: 'breaking', 'recent', 'historical'")

# Define the prompt template for enrichment
ENRICHMENT_PROMPT = """
Given the following crypto news article, extract the following fields:
Title: {title}
Content: {content}
Source: {source_name}
Published: {published_at}

Analyze the sentiment, trustworthiness, categorize the content, and provide a summary.
Consider the publication time for urgency and market impact assessment.

IMPORTANT: Respond with ONLY a valid JSON object containing these exact fields:
- sentiment: float between 0.01 and 1.0
- trust: float between 0.01 and 1.0  
- categories: array of strings
- macro_category: string
- summary: string
- urgency_score: float between 0.01 and 1.0 (higher for breaking news, time-sensitive events)
- market_impact: string ('high', 'medium', 'low')
- time_relevance: string ('breaking' for <2 hours, 'recent' for <24 hours, 'historical' for older)

Do not include any explanation or text before or after the JSON.
"""

prompt = ChatPromptTemplate.from_template(ENRICHMENT_PROMPT)

def get_enrichment_chain():
    """
    Returns a LangChain chain for news enrichment using modern patterns.
    Input: dict with keys 'title', 'content', 'source_name', 'published_at'.
    Output: NewsEnrichment object with structured metadata including temporal context.
    """
    if not OPENAI_API_KEY:
        print("⚠️ OpenAI API key not configured - enrichment disabled")
        return None
    
    llm = ChatOpenAI(
        api_key=SecretStr(OPENAI_API_KEY),
        model="gpt-4-turbo",
        temperature=0.4,
        tags=["enrichment", "news", "crypto"] if LANGSMITH_API_KEY else None
    )
    
    parser = JsonOutputParser(pydantic_object=NewsEnrichment)
    
    # Create the chain using the modern pipe syntax with LangSmith metadata
    chain = prompt | llm | parser
    
    # Add LangSmith metadata if available
    if LANGSMITH_API_KEY:
        chain = chain.with_config({
            "tags": ["enrichment", "news", "crypto"],
            "metadata": {
                "component": "news_enrichment",
                "version": "1.0.0",
                "model": "gpt-4-turbo"
            }
        })
    
    return chain

async def enrich_news_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enrich a list of news articles with AI-generated metadata.
    
    Args:
        articles: List of article dictionaries with 'title', 'content', 'source_name', 'published_at'
    
    Returns:
        List of enriched articles with additional metadata
    """
    chain = get_enrichment_chain()
    if not chain:
        print("⚠️ Enrichment chain not available - returning original articles")
        return articles
    
    enriched_articles = []
    
    for i, article in enumerate(articles):
        try:
            print(f"   Enriching article {i+1}/{len(articles)}: {article.get('title', 'Unknown')[:50]}...")
            
            # Add default published_at if not present
            if 'published_at' not in article:
                article['published_at'] = "2024-01-15T00:00:00Z"
            
            # Run enrichment with LangSmith tracing
            enrichment_result = chain.invoke(article)
            
            # Combine original article with enrichment data
            enriched_article = {
                **article,
                "enrichment": {
                    "sentiment": enrichment_result.get('sentiment', 0.5),
                    "trust": enrichment_result.get('trust', 0.5),
                    "categories": enrichment_result.get('categories', []),
                    "macro_category": enrichment_result.get('macro_category', 'Unknown'),
                    "summary": enrichment_result.get('summary', ''),
                    "urgency_score": enrichment_result.get('urgency_score', 0.5),
                    "market_impact": enrichment_result.get('market_impact', 'medium'),
                    "time_relevance": enrichment_result.get('time_relevance', 'recent')
                }
            }
            
            enriched_articles.append(enriched_article)
            
        except Exception as e:
            print(f"   ⚠️ Failed to enrich article {i+1}: {e}")
            # Add article without enrichment
            enriched_articles.append(article)
    
    return enriched_articles

# Example usage (for testing):
if __name__ == "__main__":
    chain = get_enrichment_chain()
    if chain:
        article = {
            "title": "Bitcoin surges as ETF inflows hit record highs",
            "content": "Bitcoin price jumped 10% today after several major ETFs reported record inflows. Analysts say this could signal a new bull run...",
            "source_name": "CoinDesk"
        }
        result = chain.invoke(article)
        print("Enrichment result:", result)
    else:
        print("OpenAI API key not configured - cannot test enrichment") 
