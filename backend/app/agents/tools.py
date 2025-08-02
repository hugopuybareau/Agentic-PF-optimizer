# backend/app/agent/tools.py

import logging
import os
from datetime import datetime, timedelta

import requests
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI
from pydantic import SecretStr

from ..models.assets import Asset
from .state.analysis import AnalysisResult
from .state.news import NewsItem
from .utils import safe_json_parse

logger = logging.getLogger(__name__)

class NewsSearchTool:
    def __init__(self):
        self.newsapi_key = os.getenv('NEWS_SEARCH_API_KEY')
        self.bing_subscription_key = os.getenv('BING_SUBSCRIPTION_KEY')
        self.newsapi_endpoint = "https://newsapi.org/v2/everything"
        self.bing_endpoint = "https://api.bing.microsoft.com/v7.0/news/search"

    def search_newsapi(self, query: str, days_back: int = 7, page_size: int = 10) -> list[NewsItem]:
        try:
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

            params = {
                'q': query,
                'from': from_date,
                'sortBy': 'relevancy',
                'pageSize': page_size,
                'language': 'en',
                'apiKey': self.newsapi_key
            }

            response = requests.get(self.newsapi_endpoint, params=params)
            response.raise_for_status()

            data = response.json()
            news_items = []

            for article in data.get('articles', []):
                if article.get('title') and article.get('description'):
                    news_item = NewsItem(
                        title=article['title'],
                        snippet=article['description'],
                        url=article['url'],
                        published_at=datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00')) if article.get('publishedAt') else None,
                        source=article.get('source', {}).get('name', 'NewsAPI')
                    )
                    news_items.append(news_item)

            logger.info(f"Found {len(news_items)} articles for query: {query}")
            return news_items

        except Exception as e:
            logger.error(f"NewsAPI search failed: {e}")
            return []

    def search_bing(self, query: str, count: int = 10) -> list[NewsItem]:
        try:
            if not self.bing_subscription_key:
                logger.warning("Bing subscription key not found, skipping Bing search")
                return []

            headers = {
                'Ocp-Apim-Subscription-Key': self.bing_subscription_key
            }

            params = {
                'q': query,
                'count': count,
                'mkt': 'en-US',
                'freshness': 'Week'
            }

            response = requests.get(self.bing_endpoint, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            news_items = []

            for article in data.get('value', []):
                news_item = NewsItem(
                    title=article['name'],
                    snippet=article['description'],
                    url=article['url'],
                    published_at=datetime.fromisoformat(article['datePublished'].replace('Z', '+00:00')) if article.get('datePublished') else None,
                    source='Bing News'
                )
                news_items.append(news_item)

            logger.info(f"Found {len(news_items)} articles from Bing for query: {query}")
            return news_items

        except Exception as e:
            logger.error(f"Bing search failed: {e}")
            return []

    def search_for_asset(self, asset: Asset, use_bing: bool = False) -> list[NewsItem]:
        query = self._build_asset_query(asset)

        if use_bing:
            return self.search_bing(query)
        else:
            return self.search_newsapi(query)

    def _build_asset_query(self, asset: Asset) -> str:
        if asset.type == "stock":
            return f"{asset.ticker} stock earnings financial news"
        elif asset.type == "crypto":
            return f"{asset.symbol} cryptocurrency bitcoin price news"
        elif asset.type == "real_estate":
            # Extract city/region from address for broader news
            address_parts = asset.address.split(',')
            location = address_parts[-2].strip() if len(address_parts) > 1 else asset.address
            return f"{location} real estate market housing prices"
        elif asset.type == "mortgage":
            return f"mortgage rates housing market {asset.lender}"
        elif asset.type == "cash":
            return f"{asset.currency} currency exchange rates inflation"
        else:
            return f"{asset.type} financial market news"

class ClassificationTool:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_endpoint="https://hugo-mbm3qhjz-swedencentral.cognitiveservices.azure.com/",
            azure_deployment="gpt-4o-mini",
            api_key=SecretStr(os.getenv('AZURE_OPENAI_API_KEY') or ""),
            api_version="2025-01-01-preview",
            temperature=0.1
        )


    def classify_news_item(self, news_item: NewsItem, asset: Asset) -> NewsItem:
        try:
            asset_info = f"{asset.type}: {getattr(asset, 'ticker', '') or getattr(asset, 'symbol', '') or str(asset)}"

            messages: list[BaseMessage] = [
                SystemMessage(content="""You are a financial news classifier. Analyze the given news article and classify it with the following criteria:

                1. SENTIMENT: positive, negative, or neutral
                2. IMPACT: high, medium, or low (how much this could affect the asset price)
                3. RELEVANCE: Score from 0-1 (how relevant this is to the specific asset)
                4. RISK_TYPE: market_risk, regulatory_risk, operational_risk, credit_risk, or other

                Reply **only** with a valid JSON object as described below, and nothing else:
                {
                    "sentiment": "positive/negative/neutral",
                    "impact": "high/medium/low",
                    "relevance_score": 0.0-1.0,
                    "risk_type": "market_risk/regulatory_risk/operational_risk/credit_risk/other",
                    "reasoning": "Brief explanation of your classification"
                }"""),
                HumanMessage(content=f"Asset: {asset_info}\nNews Title: {news_item.title}\nNews Content: {news_item.snippet}")
            ]

            response = self.llm.invoke(messages)

            try:
                classification = safe_json_parse(response.content)
            except Exception:
                logger.error(f"Could not parse LLM response as JSON: {response.content}")
                classification = {}

            sentiment = classification.get('sentiment')
            if not isinstance(sentiment, str) or sentiment not in ["positive", "negative", "neutral"]:
                sentiment = "neutral"
            impact = classification.get('impact')
            if not isinstance(impact, str) or impact not in ["high", "medium", "low"]:
                impact = "low"
            relevance_score = classification.get('relevance_score')
            try:
                if relevance_score is not None:
                    relevance_score = float(relevance_score)
                    if not (0.0 <= relevance_score <= 1.0):
                        relevance_score = 0.5
                else:
                    relevance_score = 0.5
            except Exception:
                relevance_score = 0.5

            news_item.sentiment = sentiment
            news_item.impact = impact
            news_item.relevance_score = relevance_score
            logger.debug(f"Classified news: {news_item.title[:50]}... - {sentiment}/{impact}/{relevance_score}")
            return news_item

        except Exception as e:
            logger.error(f"Classification failed: {e}")
            news_item.sentiment = "neutral"
            news_item.impact = "low"
            news_item.relevance_score = 0.5
            return news_item

class AnalysisTool:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_endpoint="https://hugo-mbm3qhjz-swedencentral.cognitiveservices.azure.com/",
            azure_deployment="gpt-4o-mini",
            api_key=SecretStr(os.getenv('AZURE_OPENAI_API_KEY') or ""),
            api_version="2025-01-01-preview",
            temperature=0.3
        )


    def analyze_asset(self, asset: Asset, classified_news: list[NewsItem]) -> AnalysisResult:
        try:
            asset_key = self._get_asset_key(asset)

            news_summary = self._prepare_news_summary(classified_news)
            asset_info = self._get_asset_info(asset)

            messages: list[BaseMessage] = [
                SystemMessage(content="""You are an expert financial advisor analyzing portfolio assets based on recent news.

                Provide a comprehensive analysis including:
                1. SENTIMENT_SUMMARY: Overall sentiment from the news (2-3 sentences)
                2. RISK_ASSESSMENT: Current risk level and factors (2-3 sentences)
                3. RECOMMENDATIONS: 3-5 specific actionable recommendations
                4. CONFIDENCE_SCORE: Your confidence in this analysis (0-1)

                Be specific, actionable, and focus on risk management and optimization opportunities.
                Consider both short-term news impacts and long-term portfolio health."""),
                HumanMessage(content=f"""Asset: {asset_info}
                Recent News Analysis:
                {news_summary}

                Please provide your analysis in JSON format:
                {{
                    "sentiment_summary": "...",
                    "risk_assessment": "...",
                    "recommendations": ["rec1", "rec2", "rec3"],
                    "confidence_score": 0.0-1.0
                }}""")
            ]

            response = self.llm.invoke(messages)

            analysis = safe_json_parse(response.content)
            result = AnalysisResult(
                asset_key=asset_key,
                asset=asset,
                news_items=classified_news,
                sentiment_summary=analysis['sentiment_summary'],
                risk_assessment=analysis['risk_assessment'],
                recommendations=analysis['recommendations'],
                confidence_score=analysis['confidence_score']
            )

            logger.info(f"Analysis completed for {asset_key} - Confidence: {analysis['confidence_score']}")
            return result

        except Exception as e:
            logger.error(f"Analysis failed for {asset}: {e}")
            # Return default analysis
            return AnalysisResult(
                asset_key=self._get_asset_key(asset),
                asset=asset,
                news_items=classified_news,
                sentiment_summary="Insufficient data for analysis.",
                risk_assessment="Unable to assess risk due to limited information.",
                recommendations=["Monitor for more news updates"],
                confidence_score=0.1
            )

    def _get_asset_key(self, asset: Asset) -> str:
        if asset.type == "stock":
            return f"stock:{asset.ticker}"
        elif asset.type == "crypto":
            return f"crypto:{asset.symbol}"
        elif asset.type == "real_estate":
            return f"real_estate:{asset.address}"
        elif asset.type == "mortgage":
            return f"mortgage:{asset.lender}"
        elif asset.type == "cash":
            return f"cash:{asset.currency}"
        else:
            return f"unknown:{str(asset)}"

    def _get_asset_info(self, asset: Asset) -> str:
        if asset.type == "stock":
            return f"Stock: {asset.ticker} ({asset.shares} shares)"
        elif asset.type == "crypto":
            return f"Cryptocurrency: {asset.symbol} ({asset.amount} units)"
        elif asset.type == "real_estate":
            return f"Real Estate: {asset.address} (${asset.market_value:,.2f})"
        elif asset.type == "mortgage":
            return f"Mortgage: {asset.lender} (${asset.balance:,.2f} balance)"
        elif asset.type == "cash":
            return f"Cash: {asset.currency} (${asset.amount:,.2f})"
        else:
            return f"Asset: {asset.type}"

    def _prepare_news_summary(self, news_items: list[NewsItem]) -> str:
        if not news_items:
            return "No recent news found."

        summary_parts = []
        for item in news_items[:10]:  # Limit to top 10 items
            sentiment_emoji = {"positive": "📈", "negative": "📉", "neutral": "📊"}.get(item.sentiment or "neutral", "📊")
            impact_text = f"[{item.impact.upper()} IMPACT]" if item.impact else ""

            summary_parts.append(
                f"{sentiment_emoji} {impact_text} {item.title}\n"
                f"   Summary: {item.snippet[:200]}...\n"
                f"   Relevance: {item.relevance_score:.2f}\n"
            )

        return "\n".join(summary_parts)

class PortfolioSummarizerTool:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_endpoint="https://hugo-mbm3qhjz-swedencentral.cognitiveservices.azure.com/",
            azure_deployment="gpt-4o-mini",
            api_key=SecretStr(os.getenv('AZURE_OPENAI_API_KEY') or ""),
            api_version="2025-01-01-preview",
            temperature=0.2
        )


    def create_portfolio_digest(self, analysis_results: list[AnalysisResult]) -> dict:
        try:
            # prepare analysis summary
            analysis_summary = self._prepare_analysis_summary(analysis_results)

            messages: list[BaseMessage] = [
                SystemMessage(content="""You are a senior portfolio manager providing a comprehensive portfolio digest.

                Synthesize the individual asset analyses into:
                1. EXECUTIVE_SUMMARY: 2-3 sentence overview of portfolio health
                2. KEY_RISKS: Top 3-5 portfolio-wide risks identified
                3. OPPORTUNITIES: 2-3 optimization opportunities
                4. IMMEDIATE_ACTIONS: Priority actions to take now
                5. OVERALL_SENTIMENT: Current market sentiment affecting the portfolio
                6. RISK_SCORE: Overall portfolio risk score (1-10, where 10 is highest risk)

                Be concise but actionable. Focus on portfolio-level insights, not individual assets."""),
                HumanMessage(content=f"""Portfolio Analysis Results:
                {analysis_summary}

                Please provide a comprehensive portfolio digest.""")
            ]

            response = self.llm.invoke(messages)

            digest_content = response.content

            all_recommendations = []
            high_risk_alerts = []

            for result in analysis_results:
                all_recommendations.extend(result.recommendations)
                if any(keyword in result.risk_assessment.lower() for keyword in ['high risk', 'significant risk', 'warning', 'concern']):
                    high_risk_alerts.append(f"{result.asset_key}: {result.risk_assessment}")

            digest = {
                "summary": digest_content,
                "total_assets_analyzed": len(analysis_results),
                "high_confidence_analyses": len([r for r in analysis_results if r.confidence_score > 0.7]),
                "portfolio_recommendations": list(set(all_recommendations)),  # duplicates
                "risk_alerts": high_risk_alerts,
                "generated_at": datetime.now().isoformat(),
                "average_confidence": sum(r.confidence_score for r in analysis_results) / len(analysis_results) if analysis_results else 0
            }

            logger.info(f"Portfolio digest created for {len(analysis_results)} assets")
            return digest

        except Exception as e:
            logger.error(f"Failed to create portfolio digest: {e}")
            return {
                "summary": "Unable to generate portfolio digest due to processing error.",
                "total_assets_analyzed": len(analysis_results),
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }

    def _prepare_analysis_summary(self, analysis_results: list[AnalysisResult]) -> str:
        summary_parts = []

        for result in analysis_results:
            summary_parts.append(
                f"=== {result.asset_key} ===\n"
                f"Sentiment: {result.sentiment_summary}\n"
                f"Risk: {result.risk_assessment}\n"
                f"Recommendations: {', '.join(result.recommendations[:3])}\n"
                f"Confidence: {result.confidence_score:.2f}\n"
                f"News Items: {len(result.news_items)}\n"
            )

        return "\n".join(summary_parts)
