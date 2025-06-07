# backend/app/models/models.py

from pydantic import BaseModel
from typing import List

from .assets import Asset

class Portfolio(BaseModel):
    assets: List[Asset]

class PortfolioRequest(BaseModel):
    portfolio: Portfolio

    