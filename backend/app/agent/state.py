# backend/app/agent/state.py

import operator
from datetime import datetime
from typing import Annotated, TypedDict

from pydantic import BaseModel

from ..models.assets import Asset
from ..models.portfolio import Portfolio


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

class AgentState(TypedDict):
    portfolio: Portfolio
    user_query: str | None
    task_type: str  # "analyze", "digest", "alert"

    # processing
    current_step: str
    assets_to_analyze: list[Asset]
    processed_assets: Annotated[list[str], operator.add]

    # news and analysis
    raw_news: Annotated[list[NewsItem], operator.add]
    classified_news: Annotated[list[NewsItem], operator.add]
    analysis_results: Annotated[list[AnalysisResult], operator.add]

    vector_context: dict | None

    # output
    final_response: str | None
    recommendations: Annotated[list[str], operator.add]
    risk_alerts: Annotated[list[str], operator.add]

    # meta
    execution_time: float | None
    errors: Annotated[list[str], operator.add]
