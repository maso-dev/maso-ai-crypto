#!/usr/bin/env python3
"""
REACT Validation System for Crypto News
Uses Tavily search to fact-check news articles and validate data.
"""

import os
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from tavily import TavilyClient
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field, SecretStr

# Initialize Tavily client
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
tavily_client = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None

# Initialize OpenAI client for validation
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = None  # Will be initialized in __init__ if API key is available


class ValidationResult(BaseModel):
    """Result of news article validation."""

    is_verified: bool = Field(description="Whether the article claims are verified")
    confidence_score: float = Field(description="Confidence in verification (0.0-1.0)")
    verification_summary: str = Field(description="Summary of verification findings")
    conflicting_sources: List[str] = Field(
        description="Sources that conflict with claims"
    )
    supporting_sources: List[str] = Field(description="Sources that support claims")
    fact_check_notes: List[str] = Field(description="Specific fact-checking notes")
    risk_level: str = Field(description="Risk level: 'low', 'medium', 'high'")
    recommendation: str = Field(description="Recommendation for handling this article")


class REACTValidationSystem:
    """REACT (Reasoning and Acting) validation system for crypto news."""

    def __init__(self):
        self.validation_prompt = ChatPromptTemplate.from_template(
            """
You are a crypto news fact-checker. Analyze the following news article against search results to validate claims.

Article Title: {title}
Article Content: {content}
Article Source: {source_name}
Published: {published_at}

Search Results for Fact-Checking:
{search_results}

Instructions:
1. Compare the article claims against the search results
2. Identify any conflicting or supporting information
3. Assess the credibility and accuracy of claims
4. Provide a confidence score and risk assessment

Return a JSON object with these exact fields:
- is_verified: boolean (true if claims are supported by reliable sources)
- confidence_score: float between 0.0 and 1.0
- verification_summary: string describing verification findings
- conflicting_sources: array of strings (sources that contradict claims)
- supporting_sources: array of strings (sources that support claims)
- fact_check_notes: array of strings (specific fact-checking observations)
- risk_level: string ('low', 'medium', 'high')
- recommendation: string (recommendation for handling this article)

Be thorough and objective in your analysis.
"""
        )

        self.parser = JsonOutputParser(pydantic_object=ValidationResult)

        # Initialize LLM and chain if API key is available
        if OPENAI_API_KEY:
            self.llm = ChatOpenAI(
                api_key=SecretStr(OPENAI_API_KEY), model="gpt-4-turbo", temperature=0.1
            )
            self.validation_chain = self.validation_prompt | self.llm | self.parser
        else:
            self.llm = None
            self.validation_chain = None

    async def search_for_validation(
        self, query: str, max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for information to validate news claims."""
        if not tavily_client:
            return []

        try:
            # Create a focused search query for fact-checking
            search_query = f"fact check crypto news: {query}"

            response = tavily_client.search(
                query=search_query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=[
                    "coindesk.com",
                    "cointelegraph.com",
                    "reuters.com",
                    "bloomberg.com",
                    "wsj.com",
                    "ft.com",
                ],
                exclude_domains=["twitter.com", "reddit.com", "4chan.org"],
            )

            return response.get("results", [])
        except Exception as e:
            print(f"Tavily search error: {e}")
            return []

    async def validate_article(self, article: Dict[str, Any]) -> ValidationResult:
        """Validate a single news article using REACT methodology."""
        if not self.validation_chain:
            return ValidationResult(
                is_verified=False,
                confidence_score=0.0,
                verification_summary="Validation system not configured",
                conflicting_sources=[],
                supporting_sources=[],
                fact_check_notes=["Tavily API key or OpenAI API key not configured"],
                risk_level="high",
                recommendation="Configure API keys for validation",
            )

        try:
            # Step 1: Extract key claims for validation
            claims = self._extract_claims(article)

            # Step 2: Search for validation data
            search_results = await self.search_for_validation(claims)

            # Step 3: Format search results for analysis
            formatted_results = self._format_search_results(search_results)

            # Step 4: Run validation analysis
            validation_input = {
                "title": article.get("title", ""),
                "content": article.get("content", ""),
                "source_name": article.get("source_name", ""),
                "published_at": article.get("published_at", ""),
                "search_results": formatted_results,
            }

            result = await self.validation_chain.ainvoke(validation_input)
            return ValidationResult(**result)

        except Exception as e:
            print(f"Validation error: {e}")
            return ValidationResult(
                is_verified=False,
                confidence_score=0.0,
                verification_summary=f"Validation failed: {str(e)}",
                conflicting_sources=[],
                supporting_sources=[],
                fact_check_notes=[f"Error during validation: {str(e)}"],
                risk_level="high",
                recommendation="Manual review required",
            )

    def _extract_claims(self, article: Dict[str, Any]) -> str:
        """Extract key claims from article for validation."""
        title = article.get("title", "")
        content = article.get("content", "")

        # Focus on specific claims that can be fact-checked
        claims = []

        # Extract price-related claims
        if any(
            word in title.lower()
            for word in ["price", "surge", "drop", "high", "low", "$"]
        ):
            claims.append("price movements")

        # Extract regulatory claims
        if any(
            word in title.lower()
            for word in ["regulation", "sec", "ban", "approval", "legal"]
        ):
            claims.append("regulatory developments")

        # Extract institutional claims
        if any(
            word in title.lower()
            for word in ["institutional", "etf", "blackrock", "fidelity", "adoption"]
        ):
            claims.append("institutional adoption")

        # Extract technical claims
        if any(
            word in title.lower()
            for word in ["technology", "upgrade", "fork", "scaling"]
        ):
            claims.append("technical developments")

        # If no specific claims found, use general crypto news
        if not claims:
            claims.append("cryptocurrency market developments")

        return f"{title} - {', '.join(claims)}"

    def _format_search_results(self, search_results: List[Dict[str, Any]]) -> str:
        """Format search results for validation analysis."""
        if not search_results:
            return "No search results available for validation."

        formatted = []
        for i, result in enumerate(search_results[:5], 1):
            title = result.get("title", "No title")
            content = result.get("content", "No content")
            url = result.get("url", "No URL")
            published_date = result.get("published_date", "Unknown date")

            formatted.append(
                f"""
Result {i}:
Title: {title}
Content: {content[:300]}...
Source: {url}
Date: {published_date}
---"""
            )

        return "\n".join(formatted)

    async def validate_articles_batch(
        self, articles: List[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """Validate multiple articles in batch."""
        print(f"🔍 Starting REACT validation for {len(articles)} articles...")

        validation_results = []
        for i, article in enumerate(articles, 1):
            print(
                f"  Validating article {i}/{len(articles)}: {article.get('title', '')[:50]}..."
            )

            try:
                result = await self.validate_article(article)
                validation_results.append(result)

                # Add validation metadata to article
                article["validation"] = {
                    "is_verified": result.is_verified,
                    "confidence_score": result.confidence_score,
                    "risk_level": result.risk_level,
                    "verification_summary": result.verification_summary,
                }

                print(
                    f"    ✅ Validation complete - Risk: {result.risk_level}, Confidence: {result.confidence_score:.2f}"
                )

            except Exception as e:
                print(f"    ❌ Validation failed: {e}")
                # Add error result
                error_result = ValidationResult(
                    is_verified=False,
                    confidence_score=0.0,
                    verification_summary=f"Validation error: {str(e)}",
                    conflicting_sources=[],
                    supporting_sources=[],
                    fact_check_notes=[f"Error: {str(e)}"],
                    risk_level="high",
                    recommendation="Manual review required",
                )
                validation_results.append(error_result)

                article["validation"] = {
                    "is_verified": False,
                    "confidence_score": 0.0,
                    "risk_level": "high",
                    "verification_summary": f"Validation error: {str(e)}",
                }

        print(
            f"🎉 REACT validation completed: {len(validation_results)} articles processed"
        )
        return validation_results

    def get_validation_summary(
        self, validation_results: List[ValidationResult]
    ) -> Dict[str, Any]:
        """Generate summary statistics from validation results."""
        if not validation_results:
            return {"total_validated": 0}

        total = len(validation_results)
        verified = sum(1 for r in validation_results if r.is_verified)
        avg_confidence = sum(r.confidence_score for r in validation_results) / total

        risk_distribution = {}
        for result in validation_results:
            risk = result.risk_level
            risk_distribution[risk] = risk_distribution.get(risk, 0) + 1

        return {
            "total_validated": total,
            "verified_count": verified,
            "verification_rate": verified / total if total > 0 else 0,
            "avg_confidence": avg_confidence,
            "risk_distribution": risk_distribution,
            "high_risk_count": risk_distribution.get("high", 0),
            "medium_risk_count": risk_distribution.get("medium", 0),
            "low_risk_count": risk_distribution.get("low", 0),
        }


# Global instance
react_validator = REACTValidationSystem()


async def validate_news_articles(
    articles: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Convenience function to validate news articles and return enhanced articles with validation data."""
    validation_results = await react_validator.validate_articles_batch(articles)
    summary = react_validator.get_validation_summary(validation_results)
    return articles, summary
