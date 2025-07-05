# backend/app/test_agent.py

import logging

import os
import sys
import asyncio

from logs.config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)
logger.info("Setting up Agentic Portfolio Optimizer tests...")

from app.models.portfolio import Portfolio
from app.models.assets import Stock, Crypto, Cash
from app.agent.graph import PortfolioAgent


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
        logger.info("\n📈 Running portfolio analysis...")
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
        from app.agent.tools import NewsSearchTool
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
        from app.agent.vector_store import VectorStore
        
        vector_store = VectorStore()
        logger.info("✅ Vector store initialized successfully")
        
        # Test connection
        vector_store.client.heartbeat()
        logger.info("✅ ChromaDB connection healthy")
        
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