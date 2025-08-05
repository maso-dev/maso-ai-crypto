#!/usr/bin/env python3
"""
Data Quality Filter for News Processing
Filters out noise, clickbait, and unverified sources using AI-powered analysis.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
import re
from urllib.parse import urlparse

# Import centralized config
from utils.config import get_api_key, is_api_available

logger = logging.getLogger(__name__)


@dataclass
class QualityMetrics:
    """Quality metrics for news articles."""

    overall_score: float  # 0.0 to 1.0
    source_reliability: float  # 0.0 to 1.0
    content_quality: float  # 0.0 to 1.0
    clickbait_score: float  # 0.0 to 1.0 (lower is better)
    relevance_score: float  # 0.0 to 1.0
    verification_score: float  # 0.0 to 1.0
    is_verified: bool
    is_clickbait: bool
    is_relevant: bool
    quality_level: str  # "high", "medium", "low"
    issues: List[str]
    recommendations: List[str]


@dataclass
class FilteredArticle:
    """Filtered news article with quality metrics."""

    original_article: Dict[str, Any]
    quality_metrics: QualityMetrics
    is_approved: bool
    rejection_reason: Optional[str] = None
    filtered_at: Optional[datetime] = None


class DataQualityFilter:
    """AI-powered data quality filter for news articles."""

    def __init__(self):
        self.openai_available = is_api_available("openai")
        self.quality_threshold = 0.6  # Minimum quality score for approval
        self.clickbait_threshold = 0.7  # Maximum clickbait score allowed
        self.relevance_threshold = 0.5  # Minimum relevance score

        # Known reliable sources (whitelist)
        self.reliable_sources = {
            "reuters.com",
            "bloomberg.com",
            "cnbc.com",
            "wsj.com",
            "ft.com",
            "coindesk.com",
            "cointelegraph.com",
            "bitcoin.com",
            "decrypt.co",
            "theblock.co",
            "cryptonews.com",
            "ambcrypto.com",
            "newsbtc.com",
            "cryptoslate.com",
            "bitcoinist.com",
            "livebitcoinnews.com",
        }

        # Known unreliable sources (blacklist)
        self.unreliable_sources = {
            "cryptodaily.co.uk",
            "cryptonewsz.com",
            "cryptopolitan.com",
            "cryptonews.com",
            "cryptoslate.com",
            "bitcoinist.com",
        }

        # Clickbait patterns
        self.clickbait_patterns = [
            r"\b(breaking|urgent|shocking|amazing|incredible|unbelievable)\b",
            r"\b(you won't believe|this will shock you|number \d+ will surprise you)\b",
            r"\b(going to the moon|mooning|pumping|dumping|exploding)\b",
            r"\b(100x|1000x|millionaire|billionaire)\b",
            r"\b(secret|hidden|exposed|revealed)\b",
            r"\b(buy now|sell now|act fast|limited time)\b",
            r"\b(guaranteed|promised|assured)\b",
            r"\b(revolutionary|game-changing|disruptive)\b",
        ]

        logger.info("DataQualityFilter initialized")

    async def filter_articles(
        self, articles: List[Dict[str, Any]], symbols: Optional[List[str]] = None
    ) -> List[FilteredArticle]:
        """
        Filter a list of news articles for quality.

        Args:
            articles: List of news articles to filter
            symbols: List of cryptocurrency symbols for relevance checking

        Returns:
            List of FilteredArticle objects
        """
        if not articles:
            return []

        logger.info(f"Filtering {len(articles)} articles for quality")

        filtered_articles = []
        for article in articles:
            try:
                filtered_article = await self._filter_single_article(article, symbols)
                filtered_articles.append(filtered_article)
            except Exception as e:
                logger.error(
                    f"Error filtering article {article.get('title', 'Unknown')}: {e}"
                )
                # Create a rejected article with error
                quality_metrics = QualityMetrics(
                    overall_score=0.0,
                    source_reliability=0.0,
                    content_quality=0.0,
                    clickbait_score=1.0,
                    relevance_score=0.0,
                    verification_score=0.0,
                    is_verified=False,
                    is_clickbait=True,
                    is_relevant=False,
                    quality_level="low",
                    issues=["Processing error"],
                    recommendations=["Review manually"],
                )
                filtered_articles.append(
                    FilteredArticle(
                        original_article=article,
                        quality_metrics=quality_metrics,
                        is_approved=False,
                        rejection_reason="Processing error",
                        filtered_at=datetime.now(timezone.utc),
                    )
                )

        approved_count = sum(1 for article in filtered_articles if article.is_approved)
        logger.info(
            f"Quality filtering complete: {approved_count}/{len(articles)} articles approved"
        )

        return filtered_articles

    async def _filter_single_article(
        self, article: Dict[str, Any], symbols: Optional[List[str]] = None
    ) -> FilteredArticle:
        """Filter a single news article."""
        title = article.get("title", "")
        description = article.get("description", "")
        content = article.get("content", "")
        source = article.get("source", {}).get("name", "")
        url = article.get("url", "")

        # Combine text for analysis
        full_text = f"{title}\n{description}\n{content}".strip()

        # Calculate quality metrics
        quality_metrics = await self._calculate_quality_metrics(
            title, description, content, source, url, full_text, symbols
        )

        # Determine if article is approved
        is_approved = self._evaluate_approval(quality_metrics)
        rejection_reason = (
            None if is_approved else self._get_rejection_reason(quality_metrics)
        )

        return FilteredArticle(
            original_article=article,
            quality_metrics=quality_metrics,
            is_approved=is_approved,
            rejection_reason=rejection_reason,
            filtered_at=datetime.now(timezone.utc),
        )

    async def _calculate_quality_metrics(
        self,
        title: str,
        description: str,
        content: str,
        source: str,
        url: str,
        full_text: str,
        symbols: Optional[List[str]] = None,
    ) -> QualityMetrics:
        """Calculate comprehensive quality metrics for an article."""

        # 1. Source reliability check
        source_reliability = self._check_source_reliability(source, url)

        # 2. Clickbait detection
        clickbait_score = self._detect_clickbait(title, description, content)

        # 3. Content quality analysis
        content_quality = self._analyze_content_quality(title, description, content)

        # 4. Relevance check
        relevance_score = self._check_relevance(full_text, symbols)

        # 5. Verification score
        verification_score = self._calculate_verification_score(
            source_reliability, content_quality, clickbait_score
        )

        # 6. AI-powered analysis (if OpenAI is available)
        ai_analysis = (
            await self._ai_quality_analysis(full_text, source)
            if self.openai_available
            else None
        )

        # Combine metrics
        overall_score = self._calculate_overall_score(
            source_reliability,
            content_quality,
            clickbait_score,
            relevance_score,
            verification_score,
            ai_analysis,
        )

        # Determine quality level
        quality_level = self._determine_quality_level(overall_score)

        # Identify issues and recommendations
        issues, recommendations = self._identify_issues_and_recommendations(
            source_reliability,
            content_quality,
            clickbait_score,
            relevance_score,
            verification_score,
            ai_analysis,
        )

        return QualityMetrics(
            overall_score=overall_score,
            source_reliability=source_reliability,
            content_quality=content_quality,
            clickbait_score=clickbait_score,
            relevance_score=relevance_score,
            verification_score=verification_score,
            is_verified=verification_score >= 0.7,
            is_clickbait=clickbait_score >= self.clickbait_threshold,
            is_relevant=relevance_score >= self.relevance_threshold,
            quality_level=quality_level,
            issues=issues,
            recommendations=recommendations,
        )

    def _check_source_reliability(self, source: str, url: str) -> float:
        """Check the reliability of the news source."""
        if not source and not url:
            return 0.0

        # Extract domain from URL
        domain = ""
        if url:
            try:
                parsed_url = urlparse(url)
                domain = parsed_url.netloc.lower()
            except:
                pass

        # Check whitelist
        if domain in self.reliable_sources or source.lower() in [
            s.split(".")[0] for s in self.reliable_sources
        ]:
            return 0.9

        # Check blacklist
        if domain in self.unreliable_sources or source.lower() in [
            s.split(".")[0] for s in self.unreliable_sources
        ]:
            return 0.1

        # Check for common reliable patterns
        reliable_patterns = [
            r"reuters",
            r"bloomberg",
            r"cnbc",
            r"wsj",
            r"ft",
            r"coindesk",
            r"cointelegraph",
            r"bitcoin\.com",
            r"decrypt",
            r"theblock",
            r"cryptonews",
            r"ambcrypto",
            r"newsbtc",
        ]

        for pattern in reliable_patterns:
            if re.search(pattern, domain, re.IGNORECASE) or re.search(
                pattern, source, re.IGNORECASE
            ):
                return 0.8

        # Check for suspicious patterns
        suspicious_patterns = [
            r"crypto.*daily",
            r"crypto.*news",
            r"bitcoin.*news",
            r"crypto.*slate",
            r"crypto.*ist",
            r"live.*bitcoin",
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, domain, re.IGNORECASE) or re.search(
                pattern, source, re.IGNORECASE
            ):
                return 0.3

        # Default score for unknown sources
        return 0.5

    def _detect_clickbait(self, title: str, description: str, content: str) -> float:
        """Detect clickbait patterns in the article."""
        text = f"{title} {description} {content}".lower()

        clickbait_score = 0.0
        pattern_matches = 0

        for pattern in self.clickbait_patterns:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            if matches > 0:
                pattern_matches += matches
                clickbait_score += 0.1 * matches

        # Normalize score
        clickbait_score = min(1.0, clickbait_score)

        # Additional checks
        if len(title) > 100:  # Very long titles are often clickbait
            clickbait_score += 0.1

        if title.count("!") > 2:  # Too many exclamation marks
            clickbait_score += 0.2

        if title.count("?") > 1:  # Multiple questions
            clickbait_score += 0.1

        return min(1.0, clickbait_score)

    def _analyze_content_quality(
        self, title: str, description: str, content: str
    ) -> float:
        """Analyze the quality of the article content."""
        quality_score = 0.5  # Base score

        # Check content length
        total_length = len(title) + len(description) + len(content)
        if total_length > 500:
            quality_score += 0.2
        elif total_length > 200:
            quality_score += 0.1
        else:
            quality_score -= 0.2

        # Check for proper structure
        if title and description and content:
            quality_score += 0.1

        # Check for technical terms (indicates crypto knowledge)
        crypto_terms = [
            "blockchain",
            "cryptocurrency",
            "bitcoin",
            "ethereum",
            "defi",
            "nft",
            "smart contract",
            "mining",
            "staking",
            "yield",
            "liquidity",
            "volatility",
            "market cap",
            "trading volume",
        ]

        text = f"{title} {description} {content}".lower()
        term_count = sum(1 for term in crypto_terms if term in text)
        if term_count >= 3:
            quality_score += 0.2
        elif term_count >= 1:
            quality_score += 0.1

        # Check for numbers and data (indicates factual content)
        number_pattern = r"\d+(?:\.\d+)?%?"
        numbers = re.findall(number_pattern, text)
        if len(numbers) >= 3:
            quality_score += 0.1

        return min(1.0, max(0.0, quality_score))

    def _check_relevance(self, text: str, symbols: List[str] = None) -> float:
        """Check if the article is relevant to the specified symbols."""
        if not symbols:
            return 0.7  # Default relevance if no symbols specified

        text_lower = text.lower()
        relevance_score = 0.0

        for symbol in symbols:
            if symbol.lower() in text_lower:
                relevance_score += 0.3

        # Check for general crypto terms
        crypto_terms = ["crypto", "cryptocurrency", "bitcoin", "ethereum", "blockchain"]
        for term in crypto_terms:
            if term in text_lower:
                relevance_score += 0.1

        return min(1.0, relevance_score)

    def _calculate_verification_score(
        self, source_reliability: float, content_quality: float, clickbait_score: float
    ) -> float:
        """Calculate verification score based on multiple factors."""
        # Weighted average
        verification_score = (
            source_reliability * 0.4
            + content_quality * 0.3
            + (1.0 - clickbait_score) * 0.3
        )

        return verification_score

    async def _ai_quality_analysis(
        self, text: str, source: str
    ) -> Optional[Dict[str, Any]]:
        """Use AI to analyze article quality."""
        if not self.openai_available:
            return None

        try:
            from utils.openai_utils import get_openai_client

            client = get_openai_client()

            if not client:
                return None

            prompt = f"""
            Analyze the following news article for quality and reliability:
            
            Source: {source}
            Text: {text[:1000]}...
            
            Please provide a JSON response with the following fields:
            - quality_score (0.0 to 1.0)
            - reliability_score (0.0 to 1.0)
            - is_clickbait (true/false)
            - is_verified (true/false)
            - issues (list of quality issues)
            - recommendations (list of improvements)
            
            Focus on:
            1. Factual accuracy and verification
            2. Source credibility
            3. Clickbait detection
            4. Relevance to cryptocurrency/blockchain
            5. Professional writing quality
            """

            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3,
            )

            # Parse AI response (simplified)
            ai_content = response.choices[0].message.content

            # Extract scores from AI response
            quality_score = 0.7  # Default
            reliability_score = 0.7  # Default
            is_clickbait = False
            is_verified = False

            # Simple parsing (in production, use proper JSON parsing)
            if "quality_score" in ai_content:
                try:
                    quality_match = re.search(
                        r'quality_score["\s:]+([0-9.]+)', ai_content
                    )
                    if quality_match:
                        quality_score = float(quality_match.group(1))
                except:
                    pass

            if "reliability_score" in ai_content:
                try:
                    reliability_match = re.search(
                        r'reliability_score["\s:]+([0-9.]+)', ai_content
                    )
                    if reliability_match:
                        reliability_score = float(reliability_match.group(1))
                except:
                    pass

            if "is_clickbait" in ai_content:
                is_clickbait = "true" in ai_content.lower()

            if "is_verified" in ai_content:
                is_verified = "true" in ai_content.lower()

            return {
                "quality_score": quality_score,
                "reliability_score": reliability_score,
                "is_clickbait": is_clickbait,
                "is_verified": is_verified,
                "ai_analysis": ai_content,
            }

        except Exception as e:
            logger.warning(f"AI quality analysis failed: {e}")
            return None

    def _calculate_overall_score(
        self,
        source_reliability: float,
        content_quality: float,
        clickbait_score: float,
        relevance_score: float,
        verification_score: float,
        ai_analysis: Optional[Dict[str, Any]] = None,
    ) -> float:
        """Calculate overall quality score."""

        # Base score from rule-based analysis
        base_score = (
            source_reliability * 0.25
            + content_quality * 0.20
            + (1.0 - clickbait_score) * 0.20
            + relevance_score * 0.15
            + verification_score * 0.20
        )

        # Adjust with AI analysis if available
        if ai_analysis:
            ai_quality = ai_analysis.get("quality_score", 0.7)
            ai_reliability = ai_analysis.get("reliability_score", 0.7)

            # Weighted combination
            overall_score = (base_score * 0.7) + (
                (ai_quality + ai_reliability) / 2 * 0.3
            )
        else:
            overall_score = base_score

        return min(1.0, max(0.0, overall_score))

    def _determine_quality_level(self, overall_score: float) -> str:
        """Determine quality level based on overall score."""
        if overall_score >= 0.8:
            return "high"
        elif overall_score >= 0.6:
            return "medium"
        else:
            return "low"

    def _identify_issues_and_recommendations(
        self,
        source_reliability: float,
        content_quality: float,
        clickbait_score: float,
        relevance_score: float,
        verification_score: float,
        ai_analysis: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[str], List[str]]:
        """Identify issues and provide recommendations."""
        issues = []
        recommendations = []

        if source_reliability < 0.5:
            issues.append("Low source reliability")
            recommendations.append("Verify source credibility")

        if content_quality < 0.5:
            issues.append("Poor content quality")
            recommendations.append("Improve content depth and accuracy")

        if clickbait_score > 0.7:
            issues.append("High clickbait score")
            recommendations.append("Avoid sensationalist language")

        if relevance_score < 0.5:
            issues.append("Low relevance to crypto")
            recommendations.append("Focus on crypto-related content")

        if verification_score < 0.6:
            issues.append("Low verification score")
            recommendations.append("Include verifiable facts and sources")

        if not issues:
            issues.append("No major issues detected")
            recommendations.append("Article meets quality standards")

        return issues, recommendations

    def _evaluate_approval(self, quality_metrics: QualityMetrics) -> bool:
        """Evaluate whether an article should be approved."""
        return (
            quality_metrics.overall_score >= self.quality_threshold
            and quality_metrics.clickbait_score < self.clickbait_threshold
            and quality_metrics.relevance_score >= self.relevance_threshold
        )

    def _get_rejection_reason(self, quality_metrics: QualityMetrics) -> str:
        """Get the reason for rejection."""
        if quality_metrics.overall_score < self.quality_threshold:
            return f"Low overall quality score ({quality_metrics.overall_score:.2f})"
        elif quality_metrics.clickbait_score >= self.clickbait_threshold:
            return f"High clickbait score ({quality_metrics.clickbait_score:.2f})"
        elif quality_metrics.relevance_score < self.relevance_threshold:
            return f"Low relevance score ({quality_metrics.relevance_score:.2f})"
        else:
            return "Unknown rejection reason"


# Global instance
data_quality_filter = DataQualityFilter()


# Convenience functions
async def filter_news_articles(
    articles: List[Dict[str, Any]], symbols: List[str] = None
) -> List[FilteredArticle]:
    """Filter news articles for quality."""
    return await data_quality_filter.filter_articles(articles, symbols)


async def get_quality_metrics(
    article: Dict[str, Any], symbols: List[str] = None
) -> QualityMetrics:
    """Get quality metrics for a single article."""
    filtered_article = await data_quality_filter._filter_single_article(
        article, symbols
    )
    return filtered_article.quality_metrics
