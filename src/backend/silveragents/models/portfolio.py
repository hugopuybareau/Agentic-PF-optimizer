from pydantic import BaseModel

from .assets import Asset


class Portfolio(BaseModel):
    assets: list[Asset]


class PortfolioRequest(BaseModel):
    portfolio: Portfolio
