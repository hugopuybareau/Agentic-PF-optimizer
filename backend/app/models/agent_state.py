import operator
from typing import Annotated

from pydantic import BaseModel, Field

from .analysis import AnalysisResult, NewsItem
from .assets import Asset
from .chat import ChatSession
from .portfolio import Portfolio
from .portfolio_requests import PortfolioConfirmationRequest
from .responses import EntityData, Intent, ResponseGenerationResponse, UIHints


class ChatAgentState(BaseModel):
    session: ChatSession
    user_message: str
    current_step: str = "classify_intent"
    intent: Intent
    entities: list[EntityData] = Field(default_factory=list)
    response: ResponseGenerationResponse | None = None
    ui_hints: UIHints | None = None
    confirmation_request: PortfolioConfirmationRequest | None = None
    show_form: bool = False
    errors: list[str] = Field(default_factory=list)


class PortfolioAgentState(BaseModel):
    portfolio: Portfolio
    user_query: str | None
    task_type: str

    # processing
    current_step: str
    assets_to_analyze: list[Asset]
    processed_assets: Annotated[list[str], operator.add]

    # news and analysis
    raw_news: Annotated[list[NewsItem], operator.add]
    classified_news: Annotated[list[NewsItem], operator.add]
    analysis_results: Annotated[list[AnalysisResult], operator.add]

    vector_context: dict | None = None

    # output
    final_response: str | None = None
    recommendations: Annotated[list[str], operator.add]
    risk_alerts: Annotated[list[str], operator.add]

    # meta
    execution_time: float | None = None
    errors: Annotated[list[str], operator.add]
