import logging

import pytest
from silveragents.agents.portfolio_agent import PortfolioAgent
from silveragents.logs.config import setup_logging
from silveragents.models.assets import Cash, Crypto, Stock
from silveragents.models.portfolio import Portfolio
from silveragents.agents.services import VectorStoreService as VectorStore
from silveragents.agents.tools import NewsSearchTool

setup_logging()
logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_agent():
    # Create a test portfolio
    test_portfolio = Portfolio(
        assets=[
            Stock(ticker="AAPL", shares=10),
            Stock(ticker="GOOGL", shares=5),
            Crypto(symbol="BTC", amount=0.5),
            Cash(currency="USD", amount=10000),
        ]
    )

    # Initialize agent
    logger.info("🤖 Initializing agent...")
    agent = PortfolioAgent()
    logger.info("✅ Agent initialized successfully")

    # Test portfolio analysis
    logger.info("📈 Running portfolio analysis...")
    result = agent.analyze_portfolio(test_portfolio, task_type="analyze")

    if result["success"]:
        logger.info("✅ Analysis completed successfully!")
        logger.info(f"⏱️  Execution time: {result['execution_time']:.2f}s")
        logger.info(f"🎯 Assets analyzed: {result['assets_analyzed']}")
        logger.info(f"⚠️  Risk alerts: {len(result['risk_alerts'])}")
        logger.info(f"💡 Recommendations: {len(result['recommendations'])}")

        logger.info("\n" + "=" * 50)
        logger.info("📋 ANALYSIS RESULT:")
        logger.info("=" * 50)
        logger.info(result["response"])

        if result["errors"]:
            logger.info(f"\n⚠️  Errors encountered: {len(result['errors'])}")
            for error in result["errors"]:
                logger.info(f"   - {error}")

    else:
        logger.info(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")


def test_news_search():
    news_tool = NewsSearchTool()
    test_stock = Stock(ticker="AAPL", shares=1)

    news_items = news_tool.search_for_asset(test_stock)
    logger.info(f"✅ Found {len(news_items)} news items for AAPL")

    if news_items:
        logger.info(f"📰 Sample news: {news_items[0].title}")


def test_vector_store():
    # TODO: modify test to add assertions and check if collections exist
    vector_store = VectorStore()
    collections = vector_store.client.get_collections()
