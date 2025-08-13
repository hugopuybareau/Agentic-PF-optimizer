from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from .assets import AssetType


class Intent(StrEnum):
    START = "start"
    ADD_ASSET = "add_asset"
    REMOVE_ASSET = "remove_asset"
    MODIFY_ASSET = "modify_asset"
    COMPLETE_PORTFOLIO = "complete_portfolio"
    VIEW_PORTFOLIO = "view_portfolio"
    START_OVER = "start_over"
    UNCLEAR = "unclear"
    GENERAL_QUESTION = "general_question"


class IntentClassificationResponse(BaseModel):
    intent: Intent = Field(description="The classified intent from user message")


class EntityData(BaseModel):
    ticker: str | None = Field(None, description="Stock ticker symbol if mentioned")
    symbol: str | None = Field(None, description="Cryptocurrency symbol if mentioned")
    amount: float | None = Field(None, description="Dollar amount or quantity")
    shares: int | None = Field(None, description="Number of shares for stocks")
    asset_type: AssetType | None = Field(
        None, description="Type of asset being discussed"
    )
    currency: str | None = Field(None, description="Currency code (USD, EUR, etc.)")
    address: str | None = Field(None, description="Real estate address")
    lender: str | None = Field(None, description="Mortgage lender name")
    market_value: float | None = Field(None, description="Market value of real estate")
    balance: float | None = Field(None, description="Outstanding mortgage balance")


class EntityExtractionResponse(BaseModel):
    entities: list[EntityData] = Field(
        default_factory=list,
        description="List of extracted entities from the user message"
    )
    primary_entity: EntityData | None = Field(
        None,
        description="The main entity being discussed if multiple are found"
    )


class UIHints(BaseModel):
    show_portfolio_summary: bool = Field(
        default=False,
        description="Whether to show portfolio summary in UI"
    )
    suggest_asset_types: bool = Field(
        default=False,
        description="Whether to suggest asset types to user"
    )
    current_asset_count: int = Field(
        default=0,
        description="Current number of assets in portfolio"
    )
    show_completion_button: bool = Field(
        default=False,
        description="Whether to show portfolio completion button"
    )
    highlight_missing_info: bool = Field(
        default=False,
        description="Whether to highlight missing asset information"
    )


class ResponseGenerationResponse(BaseModel):
    response: str = Field(description="The generated conversational response")


class NewsClassificationResponse(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"] = Field(
        description="Sentiment of news towards the asset"
    )
    impact: Literal["high", "medium", "low"] = Field(
        description="Expected impact level on asset price"
    )
    relevance_score: float = Field(
        ge=0.0, le=1.0,
        description="Relevance score between 0-1"
    )


class AssetAnalysisResponse(BaseModel):
    sentiment_summary: str = Field(description="Summary of overall sentiment from news")
    risk_assessment: str = Field(description="Risk assessment for the asset")
    recommendations: list[str] = Field(description="List of actionable recommendations")
    confidence_score: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score in the analysis between 0-1"
    )


class PortfolioDigestResponse(BaseModel):
    executive_summary: str = Field(description="2-3 sentence overview of portfolio health")
    key_risks: list[str] = Field(description="Top 3-5 portfolio-wide risks")
    opportunities: list[str] = Field(description="2-3 optimization opportunities")
    immediate_actions: list[str] = Field(description="Priority actions to take now")
    overall_sentiment: Literal["positive", "negative", "neutral", "mixed"] = Field(
        description="Overall market sentiment affecting portfolio"
    )
    risk_score: int = Field(
        ge=1, le=10,
        description="Overall portfolio risk score (1-10, 10 is highest risk)"
    )


class FormAssetData(BaseModel):
    type: AssetType = Field(description="Type of asset")
    ticker: str | None = Field(None, description="Stock ticker symbol")
    shares: int | None = Field(None, description="Number of shares for stocks")
    symbol: str | None = Field(None, description="Cryptocurrency symbol")
    amount: float | None = Field(None, description="Amount for crypto or cash")
    address: str | None = Field(None, description="Real estate address")
    market_value: float | None = Field(None, description="Market value of real estate")
    lender: str | None = Field(None, description="Mortgage lender name")
    balance: float | None = Field(None, description="Outstanding mortgage balance")
    property_address: str | None = Field(None, description="Property address for mortgage")
    currency: str | None = Field(None, description="Currency code for cash")


class FormSuggestion(BaseModel):
    type: AssetType = Field(description="Type of suggested asset")
    message: str = Field(description="Suggestion message to display")


class PortfolioFormData(BaseModel):
    assets: list[FormAssetData] = Field(description="List of assets in portfolio")
    suggested_additions: list[FormSuggestion] = Field(
        default_factory=list,
        description="Suggested asset additions"
    )


class FormPreparerResponse(BaseModel):
    show_form: bool = Field(description="Whether to show the portfolio form")
    form_data: PortfolioFormData = Field(description="Portfolio form data")
    response: str = Field(description="Response message to display")
    ui_hints: UIHints = Field(description="UI hints for frontend")

    class Config:
        json_schema_extra = {
            "example": {
                "show_form": True,
                "form_data": {
                    "assets": [
                        {
                            "type": "stock",
                            "ticker": "AAPL",
                            "shares": 100
                        },
                        {
                            "type": "cash",
                            "currency": "USD",
                            "amount": 5000.0
                        }
                    ],
                    "suggested_additions": [
                        {
                            "type": "crypto",
                            "message": "Consider adding cryptocurrency for diversification"
                        }
                    ]
                },
                "response": "Please review your portfolio details below",
                "ui_hints": {
                    "show_portfolio_summary": True,
                    "current_asset_count": 2
                }
            }
        }
