import operator
from typing import Annotated, Any, TypedDict

from langchain.schema import HumanMessage

from .analysis import AnalysisResult, NewsItem
from .assets import Asset
from .chat import ChatSession
from .chat_api import ChatResponse
from .portfolio import Portfolio
from .portfolio_requests import ConfirmActionRequest
from .responses import EntityData, Intent


class ChatAgentState(TypedDict):
    # Current session
    session: ChatSession
    # Last user message
    user_message: HumanMessage
    # Current step in the flow
    current_step: str
    # Intent classification
    intent: Intent
    # Extracted entities
    entities: list[EntityData]
    # Response to send
    response: ChatResponse
    # UI hints for frontend
    ui_hints: dict[str, Any]
    # Pending confirmations
    confirmation_request: ConfirmActionRequest
    # Whether to show form
    show_form: bool
    # Form data if applicable
    form_data: dict[str, Any] | None
    # Errors
    errors: Annotated[list[str], lambda x, y: x + y]


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
