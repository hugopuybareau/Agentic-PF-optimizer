# backend/test/mock_tools.py

from ..models.assets import Asset

def mock_search_tool(asset: Asset):
    # Demo: only mock news for stocks and cryptos
    if asset.type == "stock":
        return [{"title": f"{asset.ticker} surges!", "snippet": f"Shares of {asset.ticker} went up...", "url": "https://example.com/stock"}]
    elif asset.type == "crypto":
        return [{"title": f"{asset.symbol} new all-time high!", "snippet": f"Crypto {asset.symbol} is in the news...", "url": "https://example.com/crypto"}]
    else:
        return []

def mock_classify_tool(news_item):
    return {**news_item, "impact": "positive", "sentiment": "bullish"}

def mock_summarize_tool(news_items):
    if not news_items:
        return "No news found."
    headlines = [item["title"] for item in news_items]
    return f"Summary: {', '.join(headlines)}"

# Used to test the digest endpoint