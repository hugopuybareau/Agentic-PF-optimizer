# backend/app/agent/state/global.py

from datetime import datetime

from pydantic import BaseModel


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
