from datetime import datetime
from typing import Any

from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = datetime.now()
    metadata: dict[str, Any] | None = None


class ChatSession(BaseModel):
    session_id: str
    user_id: str | None = None
    messages: list[ChatMessage] = []
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
