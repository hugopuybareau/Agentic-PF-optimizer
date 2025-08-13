# backend/app/test_agent.py

import asyncio
import logging
import os
import sys

import pytest
from app.models.assets import Cash, Crypto, Stock
from app.models.portfolio import Portfolio
from logs.config import setup_logging

from backend.app.agents.portfolio_agent import PortfolioAgent

setup_logging()
logger = logging.getLogger(__name__)
logger.info("Setting up Agentic Portfolio Optimizer tests...")


@pytest.mark.asyncio
async def test_agent():
    # Create a test portfolio
    test_portfolio = Portfolio(assets=[
        Stock(ticker="AAPL", shares=10),
        Stock(ticker="GOOGL", shares=5),
        Crypto(symbol="BTC", amount=0.5),
        Cash(currency="USD", amount=10000)
    ])

    logger.info("🚀 Testing Agentic Portfolio Optimizer")
    logger.info(f"📊 Test Portfolio: {len(test_portfolio.assets)} assets")
    logger.info("-" * 50)

    try:
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

            logger.info("\n" + "="*50)
            logger.info("📋 ANALYSIS RESULT:")
            logger.info("="*50)
            logger.info(result["response"])

            if result["errors"]:
                logger.info(f"\n⚠️  Errors encountered: {len(result['errors'])}")
                for error in result["errors"]:
                    logger.info(f"   - {error}")

        else:
            logger.info(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        logger.info(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

def test_news_search():
    logger.info("\n🔍 Testing news search...")

    try:
        from app.agents.tools import NewsSearchTool
        from app.models.assets import Stock

        news_tool = NewsSearchTool()
        test_stock = Stock(ticker="AAPL", shares=1)

        news_items = news_tool.search_for_asset(test_stock)
        logger.info(f"✅ Found {len(news_items)} news items for AAPL")

        if news_items:
            logger.info(f"📰 Sample news: {news_items[0].title}")

    except Exception as e:
        logger.info(f"❌ News search test failed: {e}")

def test_vector_store():
    logger.info("\n🗄️  Testing vector store...")

    try:
        from backend.app.agents.services.vector_store import VectorStoreService as VectorStore

        vector_store = VectorStore()
        logger.info("✅ Vector store initialized successfully")

        collections = vector_store.client.get_collections()
        logger.info(f"✅ Qdrant connection healthy, found collections: {collections}")

    except Exception as e:
        logger.info(f"❌ Vector store test failed: {e}")

if __name__ == "__main__":
    logger.info("🧪 Running Agent Tests")
    logger.info("=" * 50)

    required_vars = ['AZURE_OPENAI_API_KEY', 'NEWS_SEARCH_API_KEY', 'BING_SUBSCRIPTION_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.info(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        logger.info("Please set these in your .env file")
        sys.exit(1)

    logger.info("✅ Environment variables configured")

    # Run tests
    test_vector_store()
    test_news_search()
    asyncio.run(test_agent())

    logger.info("\n" + "="*50)
    logger.info("🎉 Testing completed!")
    logger.info("="*50)
