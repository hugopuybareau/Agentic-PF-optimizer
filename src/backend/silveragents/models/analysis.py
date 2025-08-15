from datetime import datetime

from pydantic import BaseModel

from .assets import Asset


class NewsItem(BaseModel):
    title: str
    snippet: str
    url: str
    published_at: datetime | None = None
    source: str | None = None
    sentiment: str | None = None
    impact: str | None = None
    relevance_score: float | None = None
    asset_related: str | None = None


class AnalysisResult(BaseModel):
    asset_key: str
    asset: Asset
    news_items: list[NewsItem]
    sentiment_summary: str
    risk_assessment: str
    recommendations: list[str]
    confidence_score: float
