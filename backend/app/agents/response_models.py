from typing import Any, Literal

from pydantic import BaseModel, Field


class IntentClassificationResponse(BaseModel):
    intent: Literal[
        "add_asset", "remove_asset", "modify_asset", "complete_portfolio",
        "view_portfolio", "start_over", "unclear", "general_question"
    ] = Field(description="The classified intent from user message")


class EntityExtractionResponse(BaseModel):
    ticker: str | None = Field(None, description="Stock ticker symbol if mentioned")
    symbol: str | None = Field(None, description="Cryptocurrency symbol if mentioned")
    amount: float | None = Field(None, description="Dollar amount or quantity")
    shares: int | None = Field(None, description="Number of shares for stocks")
    asset_type: Literal["stock", "crypto", "real_estate", "mortgage", "cash"] | None = Field(
        None, description="Type of asset being discussed"
    )
    currency: str | None = Field(None, description="Currency code (USD, EUR, etc.)")
    address: str | None = Field(None, description="Real estate address")
    lender: str | None = Field(None, description="Mortgage lender name")
    market_value: float | None = Field(None, description="Market value of real estate")
    balance: float | None = Field(None, description="Outstanding mortgage balance")


class ResponseGenerationResponse(BaseModel):
    response: str = Field(description="The generated conversational response")
    ui_hints: dict[str, Any] = Field(
        default_factory=dict,
        description="UI hints for frontend display"
    )


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
