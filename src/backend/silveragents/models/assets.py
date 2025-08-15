from typing import Literal

from pydantic import BaseModel, Field

AssetType = Literal["stock", "crypto", "real_estate", "mortgage", "cash"]


class Stock(BaseModel):
    type: Literal["stock"] = "stock"
    ticker: str
    shares: float


class Crypto(BaseModel):
    type: Literal["crypto"] = "crypto"
    symbol: str
    amount: float


class RealEstate(BaseModel):
    type: Literal["real_estate"] = "real_estate"
    address: str
    market_value: float


class Mortgage(BaseModel):
    type: Literal["mortgage"] = "mortgage"
    lender: str
    balance: float
    property_address: str | None = None


class Cash(BaseModel):
    type: Literal["cash"] = "cash"
    currency: str = Field(default="USD")
    amount: float


Asset = Stock | Crypto | RealEstate | Mortgage | Cash
