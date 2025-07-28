from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field, SecretStr
from typing import Dict, Any, List
import os
from utils.cost_tracker import track_openai_call

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
        temperature=0.4
    )
    
    parser = JsonOutputParser(pydantic_object=NewsEnrichment)
    
    # Create the chain using the modern pipe syntax
    chain = prompt | llm | parser
    
    return chain

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
