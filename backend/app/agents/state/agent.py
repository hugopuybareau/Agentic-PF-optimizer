# backend/app/agent/state.py

import operator
from typing import Annotated, TypedDict

from ...models.assets import Asset
from ...models.portfolio import Portfolio
from .analysis import AnalysisResult
from .news import NewsItem


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
