# backend/app/agent/graph.py

import logging
import hashlib
from typing import Dict, List
from datetime import datetime
from langgraph.graph import StateGraph, END
# from langchain.tools import ToolExecutor

from .state import AgentState
from .tools import NewsSearchTool, ClassificationTool, AnalysisTool, PortfolioSummarizerTool
from .vector_store import VectorStore
from ..models.portfolio import Portfolio

logger = logging.getLogger(__name__)

class PortfolioAgent:
    def __init__(self):
        self.news_search_tool = NewsSearchTool()
        self.classification_tool = ClassificationTool()
        self.analysis_tool = AnalysisTool()
        self.summarizer_tool = PortfolioSummarizerTool()
        self.vector_store = VectorStore()
        
        # Build the agent graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        
        # Define nodes
        workflow.add_node("initialize", self._initialize_analysis)
        workflow.add_node("search_vector_db", self._search_vector_db)
        workflow.add_node("search_news", self._search_news)
        workflow.add_node("classify_news", self._classify_news)
        workflow.add_node("analyze_assets", self._analyze_assets)
        workflow.add_node("create_digest", self._create_digest)
        workflow.add_node("store_results", self._store_results)
        
        # Define edges
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
        
        return workflow.compile()
    
    def _initialize_analysis(self, state: AgentState) -> AgentState:
        logger.info(f"Starting {state['task_type']} for portfolio with {len(state['portfolio'].assets)} assets")
        
        state["current_step"] = "initialize"
        state["assets_to_analyze"] = state["portfolio"].assets
        state["processed_assets"] = []
        state["raw_news"] = []
        state["classified_news"] = []
        state["analysis_results"] = []
        state["recommendations"] = []
        state["risk_alerts"] = []
        state["errors"] = []
        
        return state
    
    def _search_vector_db(self, state: AgentState) -> AgentState:
        logger.info("Searching vector database for existing information")
        state["current_step"] = "search_vector_db"
        
        try:
            portfolio_queries = []
            asset_keys = []
            
            for asset in state["assets_to_analyze"]:
                if asset.type == "stock":
                    query = f"{asset.ticker} stock analysis news"
                    asset_key = f"stock:{asset.ticker}"
                elif asset.type == "crypto":
                    query = f"{asset.symbol} cryptocurrency price analysis"
                    asset_key = f"crypto:{asset.symbol}"
                elif asset.type == "real_estate":
                    query = f"real estate market analysis {asset.address}"
                    asset_key = f"real_estate:{asset.address}"
                elif asset.type == "mortgage":
                    query = f"mortgage rates housing market analysis"
                    asset_key = f"mortgage:{asset.lender}"
                elif asset.type == "cash":
                    query = f"{asset.currency} currency analysis inflation"
                    asset_key = f"cash:{asset.currency}"
                else:
                    continue
                
                portfolio_queries.append(query)
                asset_keys.append(asset_key)
            
            vector_results = []
            for query in portfolio_queries:
                results = self.vector_store.search_relevant_news(
                    query=query,
                    asset_keys=asset_keys,
                    days_back=7,
                    limit=5
                )
                vector_results.extend(results)
            
            state["vector_context"] = {
                "found_items": len(vector_results),
                "results": vector_results
            }
            
            logger.info(f"Found {len(vector_results)} relevant items in vector database")
            
        except Exception as e:
            logger.error(f"Vector DB search failed: {e}")
            state["errors"].append(f"Vector DB search error: {str(e)}")
            state["vector_context"] = {"found_items": 0, "results": []}
        
        return state
    
    def _should_search_news(self, state: AgentState) -> str:
        vector_context = state.get("vector_context", {})
        found_items = vector_context.get("found_items", 0)
        
        if found_items >= len(state["assets_to_analyze"]) * 2:
            logger.info("Sufficient recent data found in vector DB, skipping news search")
            return "analyze"
        else:
            logger.info("Insufficient recent data, proceeding with news search")
            return "search_news"
    
    def _search_news(self, state: AgentState) -> AgentState:
        logger.info("Searching for news for each asset")
        state["current_step"] = "search_news"
        
        all_news = []
        
        for asset in state["assets_to_analyze"]:
            try:
                news_items = self.news_search_tool.search_for_asset(asset, use_bing=False)
                
                for item in news_items:
                    item.asset_related = self.analysis_tool._get_asset_key(asset)
                
                all_news.extend(news_items)
                
                if news_items:
                    asset_key = self.analysis_tool._get_asset_key(asset)
                    self.vector_store.store_news_items(news_items, asset_key)
                
                logger.info(f"Found {len(news_items)} news items for {asset.type}")
                
            except Exception as e:
                logger.error(f"News search failed for {asset}: {e}")
                state["errors"].append(f"News search error for {asset}: {str(e)}")
        
        state["raw_news"] = all_news
        logger.info(f"Total news items found: {len(all_news)}")
        
        return state
    
    def _classify_news(self, state: AgentState) -> AgentState:
        logger.info("Classifying news items")
        state["current_step"] = "classify_news"
        
        classified_news = []
        
        # group by asset
        asset_news_map = {}
        for news_item in state["raw_news"]:
            asset_key = news_item.asset_related
            if asset_key not in asset_news_map:
                asset_news_map[asset_key] = []
            asset_news_map[asset_key].append(news_item)
        
        for asset in state["assets_to_analyze"]:
            asset_key = self.analysis_tool._get_asset_key(asset)
            news_items = asset_news_map.get(asset_key, [])
            
            for news_item in news_items:
                try:
                    classified_item = self.classification_tool.classify_news_item(news_item, asset)
                    classified_news.append(classified_item)
                except Exception as e:
                    logger.error(f"Classification failed for news item: {e}")
                    state["errors"].append(f"Classification error: {str(e)}")
                    classified_news.append(news_item)  # unclassified
        
        state["classified_news"] = classified_news
        logger.info(f"Classified {len(classified_news)} news items")
        
        return state
    
    def _analyze_assets(self, state: AgentState) -> AgentState:
        logger.info("Analyzing assets")
        state["current_step"] = "analyze_assets"
        
        analysis_results = []
        
        for asset in state["assets_to_analyze"]:
            try:
                asset_key = self.analysis_tool._get_asset_key(asset)
                
                asset_news = [
                    item for item in state["classified_news"] 
                    if item.asset_related == asset_key
                ]
                
                analysis_result = self.analysis_tool.analyze_asset(asset, asset_news)
                analysis_results.append(analysis_result)
                
                state["processed_assets"].append(asset_key)
                logger.info(f"Analysis completed for {asset_key}")
                
            except Exception as e:
                logger.error(f"Asset analysis failed for {asset}: {e}")
                state["errors"].append(f"Analysis error for {asset}: {str(e)}")
        
        state["analysis_results"] = analysis_results
        logger.info(f"Completed analysis for {len(analysis_results)} assets")
        
        return state
    
    def _create_digest(self, state: AgentState) -> AgentState:
        logger.info("Creating portfolio digest")
        state["current_step"] = "create_digest"
        
        try:
            digest = self.summarizer_tool.create_portfolio_digest(state["analysis_results"])
            
            all_recommendations = []
            risk_alerts = []
            
            for result in state["analysis_results"]:
                all_recommendations.extend(result.recommendations)
                
                # high risk check
                if (result.confidence_score > 0.6 and 
                    any(keyword in result.risk_assessment.lower() 
                        for keyword in ['high risk', 'significant', 'warning', 'concern', 'volatile'])):
                    risk_alerts.append(f"{result.asset_key}: {result.risk_assessment}")
            
            response_parts = [
                f"# Portfolio Analysis Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                f"\n## Executive Summary",
                digest.get("summary", "Analysis completed."),
                f"\n## Portfolio Overview",
                f"- **Assets Analyzed**: {digest.get('total_assets_analyzed', 0)}",
                f"- **High Confidence Analyses**: {digest.get('high_confidence_analyses', 0)}",
                f"- **Average Confidence**: {digest.get('average_confidence', 0):.2f}",
                f"- **Risk Alerts**: {len(risk_alerts)}"
            ]
            
            if risk_alerts:
                response_parts.extend([
                    f"\n## ⚠️ Risk Alerts",
                    "\n".join(f"- {alert}" for alert in risk_alerts)
                ])
            
            if digest.get("portfolio_recommendations"):
                response_parts.extend([
                    f"\n## 📋 Key Recommendations",
                    "\n".join(f"- {rec}" for rec in digest["portfolio_recommendations"][:5])
                ])
            
            response_parts.append(f"\n## 📊 Asset Analysis Summary")
            for result in state["analysis_results"]:
                response_parts.extend([
                    f"\n### {result.asset_key}",
                    f"**Sentiment**: {result.sentiment_summary}",
                    f"**Risk Assessment**: {result.risk_assessment}",
                    f"**Top Recommendations**: {', '.join(result.recommendations[:2])}",
                    f"**Confidence**: {result.confidence_score:.2f}"
                ])
            
            state["final_response"] = "\n".join(response_parts)
            state["recommendations"] = list(set(all_recommendations))
            state["risk_alerts"] = risk_alerts
            
            logger.info("Portfolio digest created successfully")
            
        except Exception as e:
            logger.error(f"Digest creation failed: {e}")
            state["errors"].append(f"Digest creation error: {str(e)}")
            state["final_response"] = f"Analysis completed with errors. Please check logs."
        
        return state
    
    def _store_results(self, state: AgentState) -> AgentState:
        logger.info("Storing analysis results")
        state["current_step"] = "store_results"
        
        try:
            portfolio_str = str(sorted([str(asset) for asset in state["portfolio"].assets]))
            portfolio_hash = hashlib.md5(portfolio_str.encode()).hexdigest()
            
            analysis_summary = {
                "type": state["task_type"],
                "summary": state.get("final_response", ""),
                "recommendations": state.get("recommendations", []),
                "risk_alerts": state.get("risk_alerts", []),
                "total_assets": len(state["portfolio"].assets),
                "confidence": sum(r.confidence_score for r in state["analysis_results"]) / len(state["analysis_results"]) if state["analysis_results"] else 0,
                "risk_level": "high" if state.get("risk_alerts") else "medium" if len(state.get("recommendations", [])) > 3 else "low"
            }
            
            self.vector_store.store_analysis_result(analysis_summary, portfolio_hash)
            
            state["execution_time"] = (datetime.now() - datetime.fromisoformat(state.get("start_time", datetime.now().isoformat()))).total_seconds()
            
            logger.info(f"Analysis results stored successfully. Execution time: {state.get('execution_time', 0):.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to store results: {e}")
            state["errors"].append(f"Storage error: {str(e)}")
        
        return state
    
    def analyze_portfolio(self, portfolio: Portfolio, task_type: str = "analyze", user_query: str = None) -> Dict:
        try:
            initial_state = {
                "portfolio": portfolio,
                "user_query": user_query,
                "task_type": task_type,
                "start_time": datetime.now().isoformat()
            }
            
            result = self.graph.invoke(initial_state)
            
            return {
                "success": True,
                "response": result.get("final_response", "Analysis completed"),
                "recommendations": result.get("recommendations", []),
                "risk_alerts": result.get("risk_alerts", []),
                "assets_analyzed": len(result.get("processed_assets", [])),
                "execution_time": result.get("execution_time", 0),
                "errors": result.get("errors", [])
            }
            
        except Exception as e:
            logger.error(f"Portfolio analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "Analysis failed due to system error"
            }
    
    def create_scheduled_digest(self, portfolio: Portfolio) -> Dict:
        return self.analyze_portfolio(portfolio, task_type="digest")
    
    def get_portfolio_alerts(self, portfolio: Portfolio) -> Dict:
        return self.analyze_portfolio(portfolio, task_type="alert")