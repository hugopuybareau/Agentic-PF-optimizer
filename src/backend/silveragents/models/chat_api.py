from pydantic import BaseModel

from .portfolio import Portfolio
from .portfolio_requests import PortfolioConfirmationRequest
from .responses import EntityData, PortfolioFormData


class ChatMessageRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    message: str
    session_id: str
    ui_hints: list[EntityData] | None = None
    show_form: bool = False
    form_data: PortfolioFormData | None = None
    portfolio_summary: dict | None = None
    confirmation_request: PortfolioConfirmationRequest | None = None
    requires_confirmation: bool = False
    error: str | None = None


class PortfolioSubmission(BaseModel):
    session_id: str
    portfolio: Portfolio
    analyze_immediately: bool = True


class UserConfirmationResponse(BaseModel):
    session_id: str
    confirmation_id: str
    confirmed: bool
