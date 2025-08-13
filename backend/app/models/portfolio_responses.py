from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from .assets import Asset, AssetType
from .portfolio_requests import PortfolioAction, PortfolioConfirmationRequest


class AssetModification(BaseModel):
    asset_type: AssetType = Field(description="Type of asset that was modified")
    symbol: str = Field(description="Asset symbol/identifier")
    previous_quantity: float | None = Field(None, description="Quantity before modification")
    new_quantity: float = Field(description="Quantity after modification")
    action_performed: str = Field(description="Action that was performed (added, updated, removed)")
    display_text: str = Field(description="Human-readable description of the modification")

class PortfolioSummary(BaseModel):
    exists: bool = Field(description="Whether the portfolio exists")
    asset_count: int = Field(default=0, description="Total number of assets")
    assets: list[Asset] = Field(default_factory=list, description="List of assets in portfolio")
    by_type: dict[str, list[Asset]] = Field(default_factory=dict, description="Assets grouped by type")
    last_updated: str | None = Field(None, description="ISO timestamp of last update")
    error: str | None = Field(None, description="Error message if summary failed")

class PortfolioActionResult(BaseModel):
    success: bool
    action: PortfolioAction
    message: str
    portfolio_updated: bool = Field(description="Whether the portfolio was modified")
    assets_modified: list[AssetModification] = Field(default_factory=list, description="Assets that were modified")
    portfolio_summary: PortfolioSummary | None = None
    error: str | None = None


class ChatPortfolioUpdate(BaseModel):
    session_id: str
    confirmation_request: PortfolioConfirmationRequest | None = None
    immediate_action: bool = Field(
        default=False,
        description="If true, skip confirmation and execute immediately"
    )


class PortfolioSnapshot(BaseModel):
    portfolio_id: UUID
    user_id: UUID
    name: str
    assets: list[dict[str, Any]]
    total_assets: int
    asset_types: list[str]
    last_updated: datetime
    metadata: dict[str, Any] | None = None


class PortfolioEventType(StrEnum):
    ASSET_ADDED = "asset_added"
    ASSET_REMOVED = "asset_removed"
    ASSET_UPDATED = "asset_updated"
    PORTFOLIO_CLEARED = "portfolio_cleared"
    CONFIRMATION_PENDING = "confirmation_pending"
    CONFIRMATION_COMPLETED = "confirmation_completed"


class PortfolioEvent(BaseModel):
    event_type: PortfolioEventType
    portfolio_id: UUID
    user_id: UUID
    session_id: str | None = None
    data: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
