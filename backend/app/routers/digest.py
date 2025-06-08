# backend/app/endpoints/digest

from fastapi import APIRouter, HTTPException, Query

from ..models.portfolio import PortfolioRequest
from ..tools.mock_tools import mock_classify_tool, mock_search_tool, mock_summarize_tool

digest_router = APIRouter()

@digest_router.post("/digest")
async def run_digest(request: PortfolioRequest):
    digest = {}
    for asset in request.portfolio.assets:
        news = mock_search_tool(asset)
        classified_news = [mock_classify_tool(item) for item in news]
        summary = mock_summarize_tool(classified_news)
        digest_key = ""
        if asset.type == "stock":
            digest_key = f"stock:{asset.ticker}"
        elif asset.type == "crypto":
            digest_key = f"crypto:{asset.symbol}"
        elif asset.type == "real_estate":
            digest_key = f"real_estate:{asset.address}"
        elif asset.type == "mortgage":
            digest_key = f"mortgage:{asset.lender}"
        elif asset.type == "cash":
            digest_key = f"cash:{asset.currency}"
        else:
            digest_key = "unknown"
        digest[digest_key] = {
            "asset": asset,
            "news": classified_news,
            "summary": summary,
        }
        
    return {"digest": digest}