# backend/app/agent/state.py

from typing import Dict, List, Optional, TypedDict, Annotated
from pydantic import BaseModel
from datetime import datetime
import operator

from ..models.portfolio import Portfolio
from ..models.assets import Asset

class NewsItem(BaseModel):
    title: str
    snippet: str
    url: str
    published_at: Optional[datetime] = None
    source: Optional[str] = None
    sentiment: Optional[str] = None
    impact: Optional[str] = None
    relevance_score: Optional[float] = None
    asset_related: Optional[str] = None

class AnalysisResult(BaseModel):
    asset_key: str
    asset: Asset
    news_items: List[NewsItem]
    sentiment_summary: str
    risk_assessment: str
    recommendations: List[str]
    confidence_score: float

class AgentState(TypedDict):
    portfolio: Portfolio
    user_query: Optional[str]
    task_type: str  # "analyze", "digest", "alert"
    
    # processing
    current_step: str
    assets_to_analyze: List[Asset]
    processed_assets: Annotated[List[str], operator.add]
    
    # news and analysis
    raw_news: Annotated[List[NewsItem], operator.add]
    classified_news: Annotated[List[NewsItem], operator.add]
    analysis_results: Annotated[List[AnalysisResult], operator.add]
    
    vector_context: Optional[Dict]
    
    # output
    final_response: Optional[str]
    recommendations: Annotated[List[str], operator.add]
    risk_alerts: Annotated[List[str], operator.add]
    
    # meta
    execution_time: Optional[float]
    errors: Annotated[List[str], operator.add]