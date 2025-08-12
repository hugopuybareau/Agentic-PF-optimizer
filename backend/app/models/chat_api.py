from pydantic import BaseModel

from .portfolio import Portfolio


class ChatMessageRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    message: str
    session_id: str
    ui_hints: dict | None = None
    show_form: bool = False
    form_data: dict | None = None
    portfolio_summary: dict | None = None
    confirmation_request: dict | None = None
    requires_confirmation: bool = False


class PortfolioSubmission(BaseModel):
    session_id: str
    portfolio: Portfolio
    analyze_immediately: bool = True


class ChatConfirmation(BaseModel):
    session_id: str
    confirmation_id: str
    confirmed: bool
