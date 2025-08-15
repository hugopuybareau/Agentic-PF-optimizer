from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from .assets import Asset, AssetType


class AddAssetRequest(BaseModel):
    asset: Asset
    portfolio_name: str = "Main Portfolio"


class RemoveAssetRequest(BaseModel):
    symbol: str
    asset_type: str
    quantity: float | None = None
    portfolio_name: str = "Main Portfolio"


class UpdateAssetRequest(BaseModel):
    symbol: str
    asset_type: str
    new_quantity: float
    portfolio_name: str = "Main Portfolio"


class PortfolioAction(StrEnum):
    ADD_ASSET = "add_asset"
    REMOVE_ASSET = "remove_asset"
    UPDATE_ASSET = "update_asset"
    CLEAR_PORTFOLIO = "clear_portfolio"
    CONFIRMATION_PROCESSED = "confirmation_processed"


class AssetConfirmation(BaseModel):
    type: AssetType
    symbol: str | None = None
    name: str | None = None
    quantity: float
    current_quantity: float | None = None
    action: PortfolioAction
    display_text: str


class PortfolioConfirmationRequest(BaseModel):
    confirmation_id: str = Field(description="Unique ID for this confirmation")
    action: PortfolioAction
    assets: list[AssetConfirmation] = Field(description="Assets involved in the action")
    message: str = Field(description="Confirmation message to display")
    requires_confirmation: bool = Field(default=True)
    metadata: dict[str, Any] | None = Field(None, description="Additional context")
