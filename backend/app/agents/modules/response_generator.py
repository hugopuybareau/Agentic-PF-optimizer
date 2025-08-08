import json
import logging
from typing import Any

from langchain.schema import AIMessage, BaseMessage, HumanMessage
from langchain_openai import AzureChatOpenAI
from langfuse.decorators import langfuse_context, observe
from pydantic import ValidationError

from ...config.prompts import prompt_manager
from ...models.assets import Asset, Cash, Crypto, Stock
from ..response_models import ResponseGenerationResponse
from ..state.chat_state import ChatSession, PortfolioBuildingState

logger = logging.getLogger(__name__)


class ResponseGenerator:
    def __init__(self, llm: AzureChatOpenAI):
        self.llm = llm

    @observe(name="generate_response_tool")
    def generate_response(
        self,
        session: ChatSession,
        user_message: str,
        intent: str,
        entities: dict[str, Any],
        portfolio_state: PortfolioBuildingState
    ) -> dict[str, Any]:
        conversation_history: list[BaseMessage] = []
        for msg in session.messages[-8:]:
            if msg.role == "user":
                conversation_history.append(HumanMessage(content=msg.content))
            else:
                conversation_history.append(AIMessage(content=msg.content))

        prompt_variables = {
            "portfolio_summary": self._get_portfolio_summary(portfolio_state),
            "intent": intent,
            "entities": json.dumps(entities)
        }

        messages = prompt_manager.build_messages(
            system_prompt_name="chat-response-generator",
            user_content=user_message,
            system_variables=prompt_variables,
            conversation_history=conversation_history
        )

        ui_hints = {
            "show_portfolio_summary": len(portfolio_state.assets) > 0,
            "suggest_asset_types": len(portfolio_state.assets) < 2,
            "current_asset_count": len(portfolio_state.assets)
        }

        try:
            try:
                raw_response = self.llm.with_structured_output(ResponseGenerationResponse).invoke(messages, timeout=10)
                response = ResponseGenerationResponse.model_validate(raw_response)
            except ValidationError as ve:
                langfuse_context.update_current_observation(metadata={
                    "error": f"Validation error in response generation: {ve}",
                    "user_message": user_message
                })
                logger.error(f"Validation error: {ve}", exc_info=True)
                response = ResponseGenerationResponse(
                    response="I encountered an error processing your request. Could you please rephrase?",
                    ui_hints=ui_hints
                )

            langfuse_context.update_current_observation(
                metadata={
                    "response_length": len(response.response),
                    "ui_hints": response.ui_hints,
                    "user_message": user_message
                }
            )

            return response.model_dump(exclude_unset=True)

        except Exception as e:
            logger.error(f"Response generation failed: {e}", exc_info=True)
            langfuse_context.update_current_observation(metadata={
                "error": f"Unexpected error: {e}",
                "user_message": user_message
            })
            return {
                "response": "I encountered an error processing your request. Could you please rephrase?",
                "ui_hints": {}
            }


    def _get_portfolio_summary(self, portfolio_state: PortfolioBuildingState) -> str:
        if not portfolio_state.assets:
            return "No assets in portfolio yet"

        summary_parts = []
        by_type: dict[str, list[Asset]] = {}

        for asset in portfolio_state.assets:
            asset_type = asset.type
            if asset_type not in by_type:
                by_type[asset_type] = []
            by_type[asset_type].append(asset)

        for asset_type, assets in by_type.items():
            if asset_type == "stock":
                stocks = [f"{a.ticker} ({a.shares} shares)" for a in assets if isinstance(a, Stock)]
                summary_parts.append(f"Stocks: {', '.join(stocks)}")
            elif asset_type == "crypto":
                cryptos = [f"{a.symbol} ({a.amount})" for a in assets if isinstance(a, Crypto)]
                summary_parts.append(f"Crypto: {', '.join(cryptos)}")
            elif asset_type == "real_estate":
                summary_parts.append(f"Real Estate: {len(assets)} properties")
            elif asset_type == "mortgage":
                summary_parts.append(f"Mortgages: {len(assets)} loans")
            elif asset_type == "cash":
                total_cash = sum(a.amount for a in assets if isinstance(a, Cash))
                summary_parts.append(f"Cash: ${total_cash:,.2f}")

        return "\n".join(summary_parts)
