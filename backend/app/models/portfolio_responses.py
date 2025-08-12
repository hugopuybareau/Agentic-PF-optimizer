from datetime import datetime
from enum import StrEnum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from .assets import AssetType


class PortfolioAction(StrEnum):
    ADD_ASSET = "add_asset"
    REMOVE_ASSET = "remove_asset"
    UPDATE_ASSET = "update_asset"
    CLEAR_PORTFOLIO = "clear_portfolio"
    CONFIRMATION_PROCESSED = "confirmation_processed"


class AssetConfirmation(BaseModel):
    """Asset details for confirmation."""
    type: AssetType
    symbol: str | None = Field(None, description="Ticker/Symbol for stocks/crypto")
    name: str | None = Field(None, description="Human-readable name")
    quantity: float = Field(description="Amount/shares to add/remove")
    current_quantity: float | None = Field(None, description="Current quantity in portfolio")
    action: PortfolioAction
    display_text: str = Field(description="Formatted text for display")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "stock",
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "quantity": 100,
                "current_quantity": 50,
                "action": "add_asset",
                "display_text": "Add 100 shares of AAPL (Apple Inc.)"
            }
        }


class PortfolioConfirmationRequest(BaseModel):
    """Request for portfolio action confirmation."""
    confirmation_id: str = Field(description="Unique ID for this confirmation")
    action: PortfolioAction
    assets: list[AssetConfirmation] = Field(description="Assets involved in the action")
    message: str = Field(description="Confirmation message to display")
    requires_confirmation: bool = Field(default=True)
    metadata: dict[str, Any] | None = Field(None, description="Additional context")

    class Config:
        json_schema_extra = {
            "example": {
                "confirmation_id": "conf_abc123",
                "action": "add_asset",
                "assets": [{
                    "type": "stock",
                    "symbol": "AAPL",
                    "quantity": 100,
                    "action": "add_asset",
                    "display_text": "100 shares of AAPL"
                }],
                "message": "Would you like to add 100 shares of AAPL to your portfolio?",
                "requires_confirmation": True
            }
        }


class PortfolioConfirmationResponse(BaseModel):
    """Response to a portfolio confirmation request."""
    confirmation_id: str
    confirmed: bool
    user_id: UUID | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "confirmation_id": "conf_abc123",
                "confirmed": True,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class PortfolioActionResult(BaseModel):
    """Result of a portfolio action after confirmation."""
    success: bool
    action: PortfolioAction
    message: str
    portfolio_updated: bool = Field(description="Whether the portfolio was modified")
    assets_affected: list[dict[str, Any]] = Field(default_factory=list)
    portfolio_summary: dict[str, Any] | None = None
    error: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "action": "add_asset",
                "message": "Successfully added 100 shares of AAPL to your portfolio",
                "portfolio_updated": True,
                "assets_affected": [{
                    "symbol": "AAPL",
                    "type": "stock",
                    "quantity": 100
                }],
                "portfolio_summary": {
                    "total_assets": 5,
                    "asset_types": ["stock", "crypto", "cash"]
                }
            }
        }


class ChatPortfolioUpdate(BaseModel):
    """Portfolio update event for chat responses."""
    session_id: str
    confirmation_request: PortfolioConfirmationRequest | None = None
    immediate_action: bool = Field(
        default=False,
        description="If true, skip confirmation and execute immediately"
    )
    portfolio_state: dict[str, Any] | None = Field(
        None,
        description="Current portfolio state after update"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_xyz789",
                "confirmation_request": {
                    "confirmation_id": "conf_abc123",
                    "action": "add_asset",
                    "assets": [{
                        "type": "stock",
                        "symbol": "AAPL",
                        "quantity": 100,
                        "action": "add_asset",
                        "display_text": "100 shares of AAPL"
                    }],
                    "message": "Add 100 shares of AAPL?",
                    "requires_confirmation": True
                },
                "immediate_action": False
            }
        }


class PortfolioSnapshot(BaseModel):
    """Current state of a portfolio."""
    portfolio_id: UUID
    user_id: UUID
    name: str
    assets: list[dict[str, Any]]
    total_assets: int
    asset_types: list[str]
    last_updated: datetime
    metadata: dict[str, Any] | None = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "portfolio_id": "456e7890-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Main Portfolio",
                "assets": [
                    {
                        "type": "stock",
                        "symbol": "AAPL",
                        "quantity": 100,
                        "display": "AAPL (100 shares)"
                    },
                    {
                        "type": "crypto",
                        "symbol": "BTC",
                        "quantity": 0.5,
                        "display": "BTC (0.5)"
                    }
                ],
                "total_assets": 2,
                "asset_types": ["stock", "crypto"],
                "last_updated": "2024-01-15T10:30:00Z"
            }
        }


class PortfolioEventType(StrEnum):
    ASSET_ADDED = "asset_added"
    ASSET_REMOVED = "asset_removed"
    ASSET_UPDATED = "asset_updated"
    PORTFOLIO_CLEARED = "portfolio_cleared"
    CONFIRMATION_PENDING = "confirmation_pending"
    CONFIRMATION_COMPLETED = "confirmation_completed"


class PortfolioEvent(BaseModel):
    """Event emitted when portfolio changes."""
    event_type: PortfolioEventType
    portfolio_id: UUID
    user_id: UUID
    session_id: str | None = None
    data: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "asset_added",
                "portfolio_id": "456e7890-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "session_id": "sess_xyz789",
                "data": {
                    "asset": {
                        "type": "stock",
                        "symbol": "AAPL",
                        "quantity": 100
                    },
                    "action": "added",
                    "portfolio_summary": {
                        "total_assets": 5
                    }
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
