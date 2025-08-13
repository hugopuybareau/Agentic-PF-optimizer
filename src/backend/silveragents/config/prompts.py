# backend/app/config/prompts.py

import logging
from typing import Any

from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langfuse.decorators import langfuse_context

from .langfuse import langfuse_config

logger = logging.getLogger(__name__)


class PromptManager:
    def __init__(self):
        self.langfuse = langfuse_config.langfuse
        self._cache: dict[str, Any] = {}

    def get_prompt(self, prompt_name: str, variables: dict[str, Any] | None = None) -> str:
        try:
            if not self.langfuse:
                logger.warning("Langfuse not available, falling back to cached/default prompts")
                return self._get_fallback_prompt(prompt_name, variables)

            prompt = self.langfuse.get_prompt(prompt_name, label="latest")

            if not prompt:
                logger.warning(f"Prompt '{prompt_name}' not found in Langfuse, using fallback")
                return self._get_fallback_prompt(prompt_name, variables)

            prompt_content = prompt.prompt

            if variables:
                try:
                    prompt_content = prompt_content.format(**variables)
                except KeyError as e:
                    logger.warning(f"Variable substitution failed for prompt '{prompt_name}': {e}")

            try:
                langfuse_context.update_current_observation(
                    metadata={
                        "prompt_name": prompt_name,
                        "prompt_version": prompt.version,
                        "variables": variables or {}
                    }
                )
            except Exception as e:
                logger.debug(f"Failed to update Langfuse context: {e}")

            return prompt_content

        except Exception as e:
            logger.error(f"Failed to get prompt '{prompt_name}' from Langfuse: {e}")
            return self._get_fallback_prompt(prompt_name, variables)

    def get_system_message(self, prompt_name: str, variables: dict[str, Any] | None = None) -> SystemMessage:
        content = self.get_prompt(prompt_name, variables)
        return SystemMessage(content=content)

    def get_human_message(self, prompt_name: str, variables: dict[str, Any] | None = None) -> HumanMessage:
        content = self.get_prompt(prompt_name, variables)
        return HumanMessage(content=content)

    def build_messages(
        self,
        system_prompt_name: str,
        user_content: str,
        system_variables: dict[str, Any] | None = None,
        conversation_history: list[BaseMessage] | None = None
    ) -> list[BaseMessage]:
        """
        Build a complete message list with system prompt from Langfuse and user message.

        Args:
            system_prompt_name: Name of the system prompt in Langfuse
            user_content: User message content
            system_variables: Variables for the system prompt
            conversation_history: Optional conversation history to include

        Returns:
            List of messages ready for LLM
        """
        messages: list[BaseMessage] = []

        system_msg = self.get_system_message(system_prompt_name, system_variables)
        messages.append(system_msg)

        if conversation_history:
            messages.extend(conversation_history)

        messages.append(HumanMessage(user_content))

        return messages

    def _get_fallback_prompt(self, prompt_name: str, variables: dict[str, Any] | None = None) -> str:

        fallback_prompts = {
            "chat-intent-classifier":
                """You are a portfolio assistant helping users build their investment portfolio.
                Classify the user's intent into one of these categories:

                1. "add_asset" - User wants to add an asset (stock, crypto, real estate, etc.)
                2. "remove_asset" - User wants to remove an asset
                3. "modify_asset" - User wants to change quantity/details of existing asset
                4. "list_assets" - User wants to see current portfolio
                5. "complete_portfolio" - User indicates they're done adding assets
                6. "ask_question" - General question about portfolio or investing
                7. "greeting" - Initial greeting or general conversation
                8. "unclear" - Intent is not clear

                Consider the conversation history to understand context.
                Return ONLY the intent category, nothing else.""",

            "chat-entity-extractor":
                """Extract investment details from the user message.
                Look for:
                - Asset type (stock, crypto, real_estate, mortgage, cash)
                - Asset identifier (ticker, symbol, address, etc.)
                - Quantity/amount/shares
                - Additional details (currency, lender, etc.)

                Consider the conversation context to understand references like "it", "that", "the same", etc.

                Return ONLY a valid JSON object with extracted information.
                Example outputs:
                {"type": "stock", "ticker": "AAPL", "shares": 100}
                {"type": "crypto", "symbol": "BTC", "amount": 0.5}
                {"type": "real_estate", "address": "123 Main St, NYC", "value": 500000}
                {"type": "cash", "currency": "USD", "amount": 10000}

                If information is missing, include what you found and mark missing fields as null.
                DO NOT include any text outside the JSON object.""",

            "tools-news-classifier":
                """You are a financial news classifier. Analyze the given news article and classify it with the following criteria:

                1. SENTIMENT: positive, negative, or neutral
                2. IMPACT: high, medium, or low (how much this could affect the asset price)
                3. RELEVANCE: Score from 0-1 (how relevant this is to the specific asset)
                4. RISK_TYPE: market_risk, regulatory_risk, operational_risk, credit_risk, or other

                Reply **only** with a valid JSON object as described below, and nothing else:
                {
                    "sentiment": "positive/negative/neutral",
                    "impact": "high/medium/low",
                    "relevance_score": 0.0-1.0,
                    "risk_type": "market_risk/regulatory_risk/operational_risk/credit_risk/other",
                    "reasoning": "Brief explanation of your classification"
                }""",

            "tools-asset-analyzer":
                """You are an expert financial advisor analyzing portfolio assets based on recent news.

                Provide a comprehensive analysis including:
                1. SENTIMENT_SUMMARY: Overall sentiment from the news (2-3 sentences)
                2. RISK_ASSESSMENT: Current risk level and factors (2-3 sentences)
                3. RECOMMENDATIONS: 3-5 specific actionable recommendations
                4. CONFIDENCE_SCORE: Your confidence in this analysis (0-1)

                Be specific, actionable, and focus on risk management and optimization opportunities.
                Consider both short-term news impacts and long-term portfolio health.""",

            "chat-response-generator":
                """You are a friendly portfolio assistant helping users build their investment portfolio.

                Current portfolio state:
                {portfolio_summary}

                User intent: {intent}
                Extracted entities: {entities}

                Guidelines:
                - Be conversational and helpful, your goal to make the user create a complete portfolio in our database.
                - Reference previous conversation when relevant
                - If information is missing, ask for specific details
                - Confirm when assets are added/removed
                - Suggest common asset types if portfolio seems incomplete
                - Keep responses concise but informative
                - Remember what the user has already told you

                Generate an appropriate response based on the conversation history."""
        }

        prompt = fallback_prompts.get(prompt_name, f"Prompt '{prompt_name}' not found")

        if variables:
            try:
                prompt = prompt.format(**variables)
            except KeyError as e:
                logger.warning(f"Variable substitution failed for fallback prompt '{prompt_name}': {e}")

        return prompt

prompt_manager = PromptManager()
