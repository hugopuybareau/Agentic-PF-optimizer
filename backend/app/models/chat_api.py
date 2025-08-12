from pydantic import BaseModel

from .portfolio import Portfolio


class ChatMessageRequest(BaseModel):
    """Request model for chat API endpoint"""
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    """Response model for chat API endpoint"""
    message: str
    session_id: str
    ui_hints: dict | None = None
    show_form: bool = False
    form_data: dict | None = None
    portfolio_summary: dict | None = None
    confirmation_request: dict | None = None
    requires_confirmation: bool = False


class PortfolioSubmission(BaseModel):
    """Model for submitting a completed portfolio"""
    session_id: str
    portfolio: Portfolio
    analyze_immediately: bool = True


class ChatConfirmation(BaseModel):
    """Model for confirming chat actions"""
    session_id: str
    confirmation_id: str
    confirmed: bool