from pydantic import BaseModel

from .assets import Asset


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


class ConfirmActionRequest(BaseModel):
    confirmation_id: str
    confirmed: bool
