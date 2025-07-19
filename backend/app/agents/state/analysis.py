# backend/app/agent/state/analysis.py

from pydantic import BaseModel

from ...models.assets import Asset
from .news import NewsItem


class AnalysisResult(BaseModel):
    asset_key: str
    asset: Asset
    news_items: list[NewsItem]
    sentiment_summary: str
    risk_assessment: str
    recommendations: list[str]
    confidence_score: float
