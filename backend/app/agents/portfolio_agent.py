# backend/app/agents/portfolio_agent.py

import hashlib
import logging
import os
from datetime import datetime
from typing import Any

from langfuse import Langfuse
from langfuse.callback import CallbackHandler
from langfuse.decorators import langfuse_context, observe
from langgraph.graph import END, StateGraph

from ..models.assets import Asset
from ..models.portfolio import Portfolio
from .state.agent import AgentState
from .state.analysis import AnalysisResult
from .state.news import NewsItem
from .tools import AnalysisTool, ClassificationTool, NewsSearchTool, PortfolioSummarizerTool
from .vector_store import VectorStore

logger = logging.getLogger(__name__)

# Initialize Langfuse
langfuse = Langfuse(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
)


class PortfolioAgent:
    def __init__(self):
        # Initialize Langfuse
        self.langfuse_handler = CallbackHandler(
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )

        self.news_search_tool = NewsSearchTool()
        self.classification_tool = ClassificationTool()
        self.analysis_tool = AnalysisTool()
        self.summarizer_tool = PortfolioSummarizerTool()
        self.vector_store = VectorStore()

        self.graph = self._build_graph()

    # def _create_tools(self):
    #     # Tools are now created but used properly to maintain Langfuse tracing
    #     pass

    def _build_graph(self) -> StateGraph:
        logger.info("Building portfolio agent workflow graph")
        workflow = StateGraph(AgentState)

        workflow.add_node("initialize", self._initialize_node)
        workflow.add_node("search_vector_db", self._search_vector_db_node)
        workflow.add_node("search_news", self._search_news_node)
        workflow.add_node("classify_news", self._classify_news_node)
        workflow.add_node("analyze_assets", self._analyze_assets_node)
        workflow.add_node("create_digest", self._create_digest_node)
        workflow.add_node("store_results", self._store_results_node)

        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "search_vector_db")
        workflow.add_conditional_edges(
            "search_vector_db",
            self._should_search_news,
            {
                "search_news": "search_news",
                "analyze": "analyze_assets"
            }
        )
        workflow.add_edge("search_news", "classify_news")
        workflow.add_edge("classify_news", "analyze_assets")
        workflow.add_edge("analyze_assets", "create_digest")
        workflow.add_edge("create_digest", "store_results")
        workflow.add_edge("store_results", END)

        logger.info("Portfolio agent workflow graph compiled successfully")
        return workflow.compile() # type: ignore

    @observe(name="initialize_node")
    def _initialize_node(self, state: AgentState) -> AgentState:
        logger.info("Starting portfolio analysis - Initialize node")
        result = self._initialize_analysis_wrapped(
            portfolio=state["portfolio"],
            task_type=state["task_type"],
            user_query=state.get("user_query", "") or ""
        )
        state["current_step"] = result.get("current_step", "initialize")
        state["assets_to_analyze"] = result.get("assets_to_analyze", [])
        state["processed_assets"] = result.get("processed_assets", [])
        state["raw_news"] = result.get("raw_news", [])
        state["classified_news"] = result.get("classified_news", [])
        state["analysis_results"] = result.get("analysis_results", [])
        state["recommendations"] = result.get("recommendations", [])
        state["risk_alerts"] = result.get("risk_alerts", [])
        state["errors"] = result.get("errors", [])
        logger.info(f"Initialize node completed - {len(state['assets_to_analyze'])} assets to analyze")
        return state

    #nodes
    @observe(name="search_vector_db_node")
    def _search_vector_db_node(self, state: AgentState) -> AgentState:
        logger.info("Searching vector database for existing information")
        result = self._search_vector_db_wrapped(
            assets=state["assets_to_analyze"],
            days_back=7
        )
        state["vector_context"] = result
        found_items = result.get("found_items", 0)
        logger.info(f"Vector DB search completed - Found {found_items} relevant items")
        return state

    @observe(name="search_news_node")
    def _search_news_node(self, state: AgentState) -> AgentState:
        logger.info("Starting news search for assets")
        result = self._search_news_wrapped(
            assets=state["assets_to_analyze"],
            use_bing=False
        )
        state["raw_news"] = result
        logger.info(f"News search completed - Found {len(result)} news items across all assets")
        return state

    @observe(name="classify_news_node")
    def _classify_news_node(self, state: AgentState) -> AgentState:
        logger.info(f"Classifying {len(state['raw_news'])} news items")
        result = self._classify_news_wrapped(
            news_items=state["raw_news"],
            assets=state["assets_to_analyze"]
        )
        state["classified_news"] = result
        logger.info(f"News classification completed - {len(result)} items classified")
        return state

    @observe(name="analyze_assets_node")
    def _analyze_assets_node(self, state: AgentState) -> AgentState:
        logger.info(f"Starting detailed analysis of {len(state['assets_to_analyze'])} assets")
        result = self._analyze_assets_wrapped(
            assets=state["assets_to_analyze"],
            classified_news=state.get("classified_news", [])
        )
        state["analysis_results"] = result
        logger.info(f"Asset analysis completed - Generated {len(result)} analysis results")
        return state

    @observe(name="create_digest_node")
    def _create_digest_node(self, state: AgentState) -> AgentState:
        logger.info("Creating portfolio digest and final response")
        result = self._create_digest_wrapped(
            analysis_results=state["analysis_results"],
            task_type=state["task_type"]
        )
        state["final_response"] = result.get("final_response", "")
        state["recommendations"] = result.get("recommendations", [])
        state["risk_alerts"] = result.get("risk_alerts", [])
        logger.info(f"Digest created - {len(state['recommendations'])} recommendations, {len(state['risk_alerts'])} risk alerts")
        return state

    @observe(name="store_results_node")
    def _store_results_node(self, state: AgentState) -> AgentState:
        logger.info("Storing analysis results to vector database")
        self._store_results_wrapped(
            portfolio=state["portfolio"],
            analysis_summary={
                "type": state["task_type"],
                "summary": state.get("final_response", ""),
                "recommendations": state.get("recommendations", []),
                "risk_alerts": state.get("risk_alerts", [])
            }
        )
        logger.info("Results stored successfully")
        return state

    #tools
    @observe(name="initialize_analysis_tool")
    def _initialize_analysis_wrapped(
        self,
        portfolio: Portfolio,
        task_type: str,
        user_query: str = ""
    ) -> dict[str, Any]:
        """Initialize analysis - wrapped for tool use."""
        logger.info(f"Initializing {task_type} analysis for portfolio with {len(portfolio.assets)} assets")

        # Log asset types for visibility
        asset_types = [asset.type for asset in portfolio.assets]
        asset_summary = {}
        for asset_type in asset_types:
            asset_summary[asset_type] = asset_summary.get(asset_type, 0) + 1

        logger.info(f"Portfolio composition: {asset_summary}")

        langfuse_context.update_current_observation(
            metadata={
                "task_type": task_type,
                "asset_count": len(portfolio.assets),
                "user_query": user_query,
                "asset_types": asset_summary
            }
        )

        return {
            "current_step": "initialize",
            "assets_to_analyze": portfolio.assets,
            "processed_assets": [],
            "raw_news": [],
            "classified_news": [],
            "analysis_results": [],
            "recommendations": [],
            "risk_alerts": [],
            "errors": []
        }

    @observe(name="search_vector_db_tool")
    def _search_vector_db_wrapped(self, assets: list[Asset], days_back: int = 7) -> dict[str, Any]:
        logger.info(f"Searching vector database for existing information (last {days_back} days)")

        try:
            portfolio_queries = []
            asset_keys = []

            for asset in assets:
                if asset.type == "stock":
                    query = f"{asset.ticker} stock analysis news"
                    asset_key = f"stock:{asset.ticker}"
                    logger.debug(f"Added stock query: {query}")
                elif asset.type == "crypto":
                    query = f"{asset.symbol} cryptocurrency price analysis"
                    asset_key = f"crypto:{asset.symbol}"
                    logger.debug(f"Added crypto query: {query}")
                elif asset.type == "real_estate":
                    query = f"real estate market analysis {asset.address}"
                    asset_key = f"real_estate:{asset.address}"
                    logger.debug(f"Added real estate query: {query}")
                elif asset.type == "mortgage":
                    query = "mortgage rates housing market analysis"
                    asset_key = f"mortgage:{asset.lender}"
                    logger.debug(f"Added mortgage query: {query}")
                elif asset.type == "cash":
                    query = f"{asset.currency} currency analysis inflation"
                    asset_key = f"cash:{asset.currency}"
                    logger.debug(f"Added cash query: {query}")
                else:
                    logger.warning(f"Unknown asset type: {asset.type}")
                    continue

                portfolio_queries.append(query)
                asset_keys.append(asset_key)

            logger.info(f"Executing {len(portfolio_queries)} vector database queries")
            vector_results = []
            for i, query in enumerate(portfolio_queries):
                logger.debug(f"Query {i+1}/{len(portfolio_queries)}: {query}")
                results = self.vector_store.search_relevant_news(
                    query=query,
                    asset_keys=asset_keys,
                    days_back=days_back,
                    limit=5
                )
                vector_results.extend(results)
                logger.debug(f"Found {len(results)} items for query {i+1}")

            langfuse_context.update_current_observation(
                metadata={
                    "found_items": len(vector_results),
                    "asset_keys_searched": asset_keys,
                    "queries_executed": len(portfolio_queries)
                }
            )

            logger.info(f"Vector DB search completed: {len(vector_results)} relevant items found")
            return {
                "found_items": len(vector_results),
                "results": vector_results
            }

        except Exception as e:
            logger.error(f"Vector DB search failed: {e}")
            return {"found_items": 0, "results": []}

    @observe(name="search_news_tool")
    def _search_news_wrapped(self, assets: list[Asset], use_bing: bool = False) -> list[NewsItem]:
        news_source = "Bing" if use_bing else "default news API"
        logger.info(f"Searching for news using {news_source} for {len(assets)} assets")

        all_news = []

        for i, asset in enumerate(assets, 1):
            try:
                asset_key = self.analysis_tool._get_asset_key(asset)
                logger.info(f"🔍 Asset {i}/{len(assets)}: Searching news for {asset_key}")

                news_items = self.news_search_tool.search_for_asset(asset, use_bing=use_bing)

                # Add asset relation
                for item in news_items:
                    item.asset_related = asset_key

                all_news.extend(news_items)

                if news_items:
                    logger.info(f"Found {len(news_items)} news items for {asset_key}")
                    self.vector_store.store_news_items(news_items, asset_key)
                    logger.debug(f"Stored {len(news_items)} news items in vector DB for {asset_key}")
                else:
                    logger.warning(f"No news found for {asset_key}")

            except Exception as e:
                logger.error(f"News search failed for {asset}: {e}")

        langfuse_context.update_current_observation(
            metadata={
                "total_news_found": len(all_news),
                "assets_searched": len(assets),
                "news_source": news_source
            }
        )

        logger.info(f"News search completed: {len(all_news)} total news items found across {len(assets)} assets")
        return all_news

    @observe(name="classify_news_tool")
    def _classify_news_wrapped(
        self,
        news_items: list[NewsItem],
        assets: list[Asset]
    ) -> list[NewsItem]:
        logger.info(f"Classifying {len(news_items)} news items for {len(assets)} assets")

        classified_news = []

        # Group by asset
        asset_news_map = {}
        for news_item in news_items:
            asset_key = news_item.asset_related
            if asset_key not in asset_news_map:
                asset_news_map[asset_key] = []
            asset_news_map[asset_key].append(news_item)

        logger.info(f"News distribution: {[(k, len(v)) for k, v in asset_news_map.items()]}")

        for i, asset in enumerate(assets, 1):
            asset_key = self.analysis_tool._get_asset_key(asset)
            items = asset_news_map.get(asset_key, [])

            logger.info(f"Asset {i}/{len(assets)}: Classifying {len(items)} news items for {asset_key}")

            classified_count = 0
            for news_item in items:
                try:
                    classified_item = self.classification_tool.classify_news_item(news_item, asset)
                    classified_news.append(classified_item)
                    classified_count += 1
                except Exception as e:
                    logger.error(f"❌ Classification failed for news item: {e}")
                    classified_news.append(news_item)

            if items:
                logger.info(f"Classified {classified_count}/{len(items)} items for {asset_key}")

        langfuse_context.update_current_observation(
            metadata={
                "classified_count": len(classified_news),
                "classification_rate": len(classified_news) / len(news_items) if news_items else 0,
                "asset_news_distribution": {k: len(v) for k, v in asset_news_map.items()}
            }
        )

        logger.info(f"News classification completed: {len(classified_news)}/{len(news_items)} items classified")
        return classified_news

    @observe(name="analyze_assets_tool")
    def _analyze_assets_wrapped(
        self,
        assets: list[Asset],
        classified_news: list[NewsItem]
    ) -> list[AnalysisResult]:
        logger.info(f"Starting detailed analysis of {len(assets)} assets with {len(classified_news)} classified news items")

        analysis_results = []

        # Group news by asset for easier processing
        news_by_asset = {}
        for item in classified_news:
            if item.asset_related not in news_by_asset:
                news_by_asset[item.asset_related] = []
            news_by_asset[item.asset_related].append(item)

        for i, asset in enumerate(assets, 1):
            try:
                asset_key = self.analysis_tool._get_asset_key(asset)
                asset_news = news_by_asset.get(asset_key, [])

                logger.info(f"Asset {i}/{len(assets)}: Analyzing {asset_key} with {len(asset_news)} news items")

                # Analyze
                analysis_result = self.analysis_tool.analyze_asset(asset, asset_news)
                analysis_results.append(analysis_result)

                logger.info(f"Analysis completed for {asset_key} - Confidence: {analysis_result.confidence_score:.2f}")
                logger.debug(f"Sentiment: {analysis_result.sentiment_summary}")
                logger.debug(f"Recommendations: {len(analysis_result.recommendations)}")

            except Exception as e:
                logger.error(f"Asset analysis failed for {asset}: {e}")

        avg_confidence = sum(r.confidence_score for r in analysis_results) / len(analysis_results) if analysis_results else 0

        langfuse_context.update_current_observation(
            metadata={
                "assets_analyzed": len(analysis_results),
                "average_confidence": avg_confidence,
                "high_confidence_count": sum(1 for r in analysis_results if r.confidence_score > 0.7)
            }
        )

        logger.info(f"Asset analysis completed: {len(analysis_results)} assets analyzed, avg confidence: {avg_confidence:.2f}")
        return analysis_results

    @observe(name="create_digest_tool")
    def _create_digest_wrapped(
        self,
        analysis_results: list[AnalysisResult],
        task_type: str
    ) -> dict[str, Any]:
        logger.info("Creating portfolio digest")

        try:
            digest = self.summarizer_tool.create_portfolio_digest(analysis_results)

            all_recommendations = []
            risk_alerts = []

            for result in analysis_results:
                all_recommendations.extend(result.recommendations)

                if (result.confidence_score > 0.6 and
                    any(keyword in result.risk_assessment.lower()
                        for keyword in ['high risk', 'significant', 'warning', 'concern', 'volatile'])):
                    risk_alerts.append(f"{result.asset_key}: {result.risk_assessment}")

            # Build response
            response_parts = [
                f"# Portfolio Analysis Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "\n## Executive Summary",
                digest.get("summary", "Analysis completed."),
                "\n## Portfolio Overview",
                f"- **Assets Analyzed**: {digest.get('total_assets_analyzed', 0)}",
                f"- **High Confidence Analyses**: {digest.get('high_confidence_analyses', 0)}",
                f"- **Average Confidence**: {digest.get('average_confidence', 0):.2f}",
                f"- **Risk Alerts**: {len(risk_alerts)}"
            ]

            if risk_alerts:
                response_parts.extend([
                    "\n## ⚠️ Risk Alerts",
                    "\n".join(f"- {alert}" for alert in risk_alerts)
                ])

            if digest.get("portfolio_recommendations"):
                response_parts.extend([
                    "\n## 📋 Key Recommendations",
                    "\n".join(f"- {rec}" for rec in digest["portfolio_recommendations"][:5])
                ])

            response_parts.append("\n## 📊 Asset Analysis Summary")
            for result in analysis_results:
                response_parts.extend([
                    f"\n### {result.asset_key}",
                    f"**Sentiment**: {result.sentiment_summary}",
                    f"**Risk Assessment**: {result.risk_assessment}",
                    f"**Top Recommendations**: {', '.join(result.recommendations[:2])}",
                    f"**Confidence**: {result.confidence_score:.2f}"
                ])

            final_response = "\n".join(response_parts)

            langfuse_context.update_current_observation(
                metadata={
                    "digest_created": True,
                    "risk_alerts_count": len(risk_alerts),
                    "recommendations_count": len(set(all_recommendations))
                }
            )

            return {
                "final_response": final_response,
                "recommendations": list(set(all_recommendations)),
                "risk_alerts": risk_alerts
            }

        except Exception as e:
            logger.error(f"Digest creation failed: {e}")
            return {
                "final_response": "Analysis completed with errors. Please check logs.",
                "recommendations": [],
                "risk_alerts": []
            }

    @observe(name="store_results_tool")
    def _store_results_wrapped(
        self,
        portfolio: Portfolio,
        analysis_summary: dict[str, Any]
    ) -> None:
        logger.info("Storing analysis results")

        try:
            # Create portfolio hash
            portfolio_str = str(sorted([str(asset) for asset in portfolio.assets]))
            portfolio_hash = hashlib.md5(portfolio_str.encode()).hexdigest()

            # Add metadata
            analysis_summary["total_assets"] = len(portfolio.assets)
            analysis_summary["timestamp"] = datetime.now().isoformat()

            # Store in vector DB
            self.vector_store.store_analysis_result(analysis_summary, portfolio_hash)

            langfuse_context.update_current_observation(
                metadata={
                    "stored": True,
                    "portfolio_hash": portfolio_hash
                }
            )

            logger.info("Analysis results stored successfully")

        except Exception as e:
            logger.error(f"Failed to store results: {e}")

    #helpers
    @observe(name="should_search_news")
    def _should_search_news(self, state: AgentState) -> str:
        vector_context = state.get("vector_context") or {}
        found_items = vector_context.get("found_items", 0)
        threshold = len(state["assets_to_analyze"]) * 2

        decision = "search_news"
        if found_items >= threshold:
            logger.info(f"🎯 Sufficient recent data found in vector DB ({found_items} >= {threshold}), skipping news search")
            decision = "analyze"
        else:
            logger.info(f"🔍 Insufficient recent data ({found_items} < {threshold}), proceeding with news search")

        langfuse_context.update_current_observation(
            metadata={
                "decision": decision,
                "found_items": found_items,
                "threshold": threshold,
                "assets_count": len(state["assets_to_analyze"])
            }
        )

        return decision

    @observe(name="analyze_portfolio")
    def analyze_portfolio(
        self,
        portfolio: Portfolio,
        task_type: str = "analyze",
        user_query: str = ""
    ) -> dict:
        logger.info(f"🚀 Starting portfolio analysis - Task: {task_type}, Assets: {len(portfolio.assets)}")

        trace = langfuse.trace( # type: ignore
            name="portfolio_analysis",
            metadata={
                "task_type": task_type,
                "asset_count": len(portfolio.assets),
                "user_query": user_query
            },
            input={
                "portfolio": [str(asset) for asset in portfolio.assets],
                "task_type": task_type
            }
        )

        try:
            start_time = datetime.now()
            initial_state = {
                "portfolio": portfolio,
                "user_query": user_query,
                "task_type": task_type,
                "start_time": start_time.isoformat()
            }

            langfuse_context.update_current_observation(
                metadata={
                    "task_type": task_type,
                    "asset_count": len(portfolio.assets),
                    "user_query": user_query,
                    "trace_id": trace.id
                }
            )

            logger.info("Invoking analysis workflow graph")
            result = self.graph.invoke(initial_state) # type: ignore

            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"⏱️ Analysis workflow completed in {execution_time:.2f} seconds")

            response = {
                "success": True,
                "response": result.get("final_response", "Analysis completed"),
                "recommendations": result.get("recommendations", []),
                "risk_alerts": result.get("risk_alerts", []),
                "assets_analyzed": len(result.get("analysis_results", [])),
                "execution_time": execution_time,
                "errors": result.get("errors", [])
            }

            logger.info("Portfolio analysis completed successfully:")
            logger.info(f"   - Assets analyzed: {response['assets_analyzed']}")
            logger.info(f"   - Recommendations: {len(response['recommendations'])}")
            logger.info(f"   - Risk alerts: {len(response['risk_alerts'])}")
            logger.info(f"   - Execution time: {execution_time:.2f}s")

            trace.update(
                output=response,
                metadata={
                    "success": True,
                    "execution_time": response["execution_time"],
                    "recommendations_count": len(response["recommendations"]),
                    "risk_alerts_count": len(response["risk_alerts"])
                }
            )

            return response

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
            logger.error(f"Portfolio analysis failed after {execution_time:.2f}s: {e}")

            error_response = {
                "success": False,
                "error": str(e),
                "response": "Analysis failed due to system error",
                "execution_time": execution_time
            }

            trace.update(
                output=error_response,
                metadata={"success": False, "error": str(e), "execution_time": execution_time}
            )

            return error_response

    def create_scheduled_digest(self, portfolio: Portfolio) -> dict:
        logger.info("Creating scheduled portfolio digest")
        return self.analyze_portfolio(portfolio, task_type="digest")

    def get_portfolio_alerts(self, portfolio: Portfolio) -> dict:
        logger.info("Generating portfolio alerts")
        return self.analyze_portfolio(portfolio, task_type="alert")
