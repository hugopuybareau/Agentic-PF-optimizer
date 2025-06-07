# backend/app/models/assets.py

from pydantic import BaseModel, Field
from typing import List, Union, Optional, Literal

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
    property_address: Optional[str] = None

class Cash(BaseModel):
    type: Literal["cash"] = "cash"
    currency: str = Field(default="USD")
    amount: float

Asset = Union[Stock, Crypto, RealEstate, Mortgage, Cash]
