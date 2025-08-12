from datetime import datetime
from typing import Any

from pydantic import BaseModel

from .assets import Asset, AssetType


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = datetime.now()
    metadata: dict[str, Any] | None = None


class PortfolioBuildingState(BaseModel):
    # Incrementally built portfolio
    assets: list[Asset] = []
    # Current asset being discussed
    current_asset_type: AssetType | None = None
    current_asset_data: dict[str, Any] = {}
    # Validation errors
    validation_errors: list[str] = []
    # Whether portfolio is complete
    is_complete: bool = False
    # Suggested next questions
    next_questions: list[str] = []


class ChatSession(BaseModel):
    session_id: str
    user_id: str | None = None
    messages: list[ChatMessage] = []
    portfolio_state: PortfolioBuildingState = PortfolioBuildingState()
    context: dict[str, Any] = {}
    created_at: datetime = datetime.now()
    last_activity: datetime = datetime.now()

    def add_message(self, role: str, content: str, metadata: dict | None = None):
        self.messages.append(ChatMessage(
            role=role,
            content=content,
            metadata=metadata or {}
        ))
        self.last_activity = datetime.now()
