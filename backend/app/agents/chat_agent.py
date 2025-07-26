# backend/app/agent/chat_agent.py

import json
import logging
import os

from langchain.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, StateGraph
from pydantic import SecretStr

from ..models.assets import Asset, Cash, Crypto, Mortgage, RealEstate, Stock
from ..models.portfolio import Portfolio
from .session_storage import get_session_storage
from .state.chat_state import ChatAgentState, ChatSession, PortfolioBuildingState
from .utils import safe_json_parse

logger = logging.getLogger(__name__)


class ChatAgent:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            base_url="https://hugo-mbm3qhjz-swedencentral.cognitiveservices.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2025-01-01-preview",
            api_key=SecretStr(os.getenv('AZURE_OPENAI_API_KEY') or ""),
            api_version="2025-01-01-preview",
            temperature=0.3
        )
        self.graph = self._build_graph()
        self.session_storage = get_session_storage()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(ChatAgentState)

        # Define nodes
        workflow.add_node("classify_intent", self._classify_intent)
        workflow.add_node("extract_entities", self._extract_entities)
        workflow.add_node("update_portfolio", self._update_portfolio)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("prepare_form", self._prepare_form)

        # Define edges
        workflow.set_entry_point("classify_intent")
        workflow.add_edge("classify_intent", "extract_entities")
        workflow.add_edge("extract_entities", "update_portfolio")
        workflow.add_conditional_edges(
            "update_portfolio",
            self._should_show_form,
            {
                "show_form": "prepare_form",
                "continue": "generate_response"
            }
        )
        workflow.add_edge("prepare_form", END)
        workflow.add_edge("generate_response", END)

        return workflow.compile() # type: ignore

    def _classify_intent(self, state: ChatAgentState) -> ChatAgentState:
        """Classify user intent from their message"""

        session = state["session"]

        # Build conversation history
        messages = [
            ("system", """You are a portfolio assistant helping users build their investment portfolio.
            Classify the user's intent into one of these categories:\n\n

            1. "add_asset" - User wants to add an asset (stock, crypto, real estate, etc.)
            2. "remove_asset" - User wants to remove an asset
            3. "modify_asset" - User wants to change quantity/details of existing asset
            4. "list_assets" - User wants to see current portfolio
            5. "complete_portfolio" - User indicates they're done adding assets
            6. "ask_question" - General question about portfolio or investing
            7. "greeting" - Initial greeting or general conversation
            8. "unclear" - Intent is not clear\n\n

            Consider the conversation history to understand context.
            Return ONLY the intent category, nothing else.""")
        ]

        # Add recent conversation history (last 10 messages)
        for msg in session.messages[-10:]:
            if msg.role == "user":
                messages.append(("human", msg.content))
            else:
                messages.append(("assistant", msg.content))

        # Add current message
        messages.append(("human", state["user_message"]))

        intent_prompt = ChatPromptTemplate.from_messages(messages)

        try:
            response = self.llm.invoke(intent_prompt.format_messages())
            # If response.content is a list, extract the first string element
            intent_text = response.content
            if isinstance(intent_text, list):
                # Find the first string in the list
                intent_text = next((item for item in intent_text if isinstance(item, str)), "")
            state["intent"] = intent_text.strip().lower()
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            state["intent"] = "unclear"

        return state

    def _extract_entities(self, state: ChatAgentState) -> ChatAgentState:
        """Extract relevant entities based on intent"""

        if state["intent"] not in ["add_asset", "modify_asset", "remove_asset"]:
            state["entities"] = {}
            return state

        session = state["session"]

        # Build messages with conversation history
        messages = [
            ("system", """Extract investment details from the user message.
            Look for:
            - Asset type (stock, crypto, real_estate, mortgage, cash)
            - Asset identifier (ticker, symbol, address, etc.)
            - Quantity/amount/shares
            - Additional details (currency, lender, etc.)\n\n

            Consider the conversation context to understand references like "it", "that", "the same", etc.\n\n

            Return a JSON object with extracted information.
            Example outputs:
            {"type": "stock", "ticker": "AAPL", "shares": 100}
            {"type": "crypto", "symbol": "BTC", "amount": 0.5}
            {"type": "real_estate", "address": "123 Main St, NYC", "value": 500000}\n\n

            If information is missing, include what you found and mark missing fields as null.""")
        ]

        # Add recent conversation history for context
        for msg in session.messages[-6:]:
            if msg.role == "user":
                messages.append(("human", msg.content))
            else:
                messages.append(("assistant", msg.content))

        # Add current message
        messages.append(("human", state["user_message"]))

        entity_prompt = ChatPromptTemplate.from_messages(messages)

        try:
            response = self.llm.invoke(entity_prompt.format_messages())
            entities = safe_json_parse(response.content)
            state["entities"] = entities
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            state["entities"] = {}

        return state

    def _update_portfolio(self, state: ChatAgentState) -> ChatAgentState:
        """Update the portfolio based on extracted entities"""

        session = state["session"]
        entities = state["entities"]
        intent = state["intent"]

        # Handle context-aware references
        entities = self._resolve_references(entities, session)

        if intent == "add_asset" and entities:
            try:
                asset = self._create_asset_from_entities(entities)
                if asset:
                    session.portfolio_state.assets.append(asset)
                    session.portfolio_state.current_asset_type = None
                    session.portfolio_state.current_asset_data = {}
                else:
                    # Incomplete data, store for progressive collection
                    session.portfolio_state.current_asset_type = entities.get("type")
                    session.portfolio_state.current_asset_data.update(entities)
            except Exception as e:
                logger.error(f"Failed to create asset: {e}")
                session.portfolio_state.validation_errors.append(str(e))

        elif intent == "remove_asset" and entities:
            # Find and remove matching asset
            identifier = entities.get("ticker") or entities.get("symbol") or entities.get("address")
            if identifier:
                original_count = len(session.portfolio_state.assets)
                session.portfolio_state.assets = [
                    a for a in session.portfolio_state.assets
                    if not self._asset_matches(a, identifier)
                ]
                if len(session.portfolio_state.assets) < original_count:
                    state["ui_hints"]["removed_asset"] = True

        elif intent == "complete_portfolio":
            session.portfolio_state.is_complete = True

        return state

    def _should_show_form(self, state: ChatAgentState) -> str:
        """Decide whether to show form or continue conversation"""

        session = state["session"]

        # Show form if user indicated completion or has enough assets
        if (session.portfolio_state.is_complete or
            (len(session.portfolio_state.assets) >= 3 and state["intent"] == "add_asset")):
            return "show_form"

        return "continue"

    def _prepare_form(self, state: ChatAgentState) -> ChatAgentState:
        """Prepare form data for frontend"""

        session = state["session"]

        # Convert assets to form-friendly format
        form_assets = []
        for asset in session.portfolio_state.assets:
            if isinstance(asset, Stock):
                form_assets.append({
                    "type": "stock",
                    "ticker": asset.ticker,
                    "shares": asset.shares
                })
            elif isinstance(asset, Crypto):
                form_assets.append({
                    "type": "crypto",
                    "symbol": asset.symbol,
                    "amount": asset.amount
                })
            elif isinstance(asset, RealEstate):
                form_assets.append({
                    "type": "real_estate",
                    "address": asset.address,
                    "market_value": asset.market_value
                })
            elif isinstance(asset, Mortgage):
                form_assets.append({
                    "type": "mortgage",
                    "lender": asset.lender,
                    "balance": asset.balance,
                    "property_address": asset.property_address
                })
            elif isinstance(asset, Cash):
                form_assets.append({
                    "type": "cash",
                    "currency": asset.currency,
                    "amount": asset.amount
                })

        state["show_form"] = True
        state["form_data"] = {
            "assets": form_assets,
            "suggested_additions": self._suggest_missing_assets(session.portfolio_state.assets)
        }

        state["response"] = (
            "Great! I've captured your portfolio so far. Please review the details below "
            "and make any adjustments needed. You can also add any assets I might have missed."
        )

        state["ui_hints"] = {
            "show_portfolio_form": True,
            "form_mode": "review",
            "can_edit": True,
            "can_analyze": len(form_assets) > 0
        }

        return state

    def _generate_response(self, state: ChatAgentState) -> ChatAgentState:
        """Generate conversational response"""

        session = state["session"]
        intent = state["intent"]

        # Build conversation history
        messages = [
            ("system", """You are a friendly portfolio assistant helping users build their investment portfolio.

            Current portfolio state:
            {portfolio_state}\n\n

            User intent: {intent}
            Extracted entities: {entities}\n\n

            Guidelines:
            - Be conversational and helpful
            - Reference previous conversation when relevant
            - If information is missing, ask for specific details
            - Confirm when assets are added/removed
            - Suggest common asset types if portfolio seems incomplete
            - Keep responses concise but informative
            - Remember what the user has already told you\n\n

            Generate an appropriate response based on the conversation history.""")
        ]

        # Add conversation history
        for msg in session.messages[-8:]:
            if msg.role == "user":
                messages.append(("human", msg.content))
            else:
                messages.append(("assistant", msg.content))

        # Add current message
        messages.append(("human", state["user_message"]))

        try:
            portfolio_summary = self._get_portfolio_summary(session.portfolio_state)

            # Format the system message with current state
            formatted_messages = []
            for role, content in messages:
                if role == "system":
                    content = content.format(
                        portfolio_state=portfolio_summary,
                        intent=intent,
                        entities=json.dumps(state["entities"])
                    )
                formatted_messages.append((role, content))

            response = self.llm.invoke(
                ChatPromptTemplate.from_messages(formatted_messages).format_messages()
            )

            # Ensure response.content is always a string
            content = response.content
            if isinstance(content, list):
                # Join list elements as string, or extract first string if possible
                content = " ".join(str(item) for item in content if isinstance(item, str | dict))
                if not isinstance(content, str):
                    content = str(content)
            state["response"] = content

            # Add UI hints based on context
            state["ui_hints"] = {
                "show_portfolio_summary": len(session.portfolio_state.assets) > 0,
                "suggest_asset_types": len(session.portfolio_state.assets) < 2,
                "current_asset_count": len(session.portfolio_state.assets)
            }

        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            state["response"] = "I encountered an error processing your request. Could you please rephrase?"

        return state

    def _create_asset_from_entities(self, entities: dict) -> Asset | None:
        """Create appropriate asset object from extracted entities"""

        asset_type = entities.get("type", "").lower()

        try:
            if asset_type == "stock":
                if entities.get("ticker") and entities.get("shares"):
                    return Stock(
                        ticker=entities["ticker"].upper(),
                        shares=float(entities["shares"])
                    )

            elif asset_type == "crypto":
                if entities.get("symbol") and entities.get("amount"):
                    return Crypto(
                        symbol=entities["symbol"].upper(),
                        amount=float(entities["amount"])
                    )

            elif asset_type == "real_estate":
                if entities.get("address") and entities.get("value"):
                    return RealEstate(
                        address=entities["address"],
                        market_value=float(entities["value"])
                    )

            elif asset_type == "mortgage":
                if entities.get("lender") and entities.get("balance"):
                    return Mortgage(
                        lender=entities["lender"],
                        balance=float(entities["balance"]),
                        property_address=entities.get("property_address")
                    )

            elif asset_type == "cash":
                if entities.get("amount"):
                    return Cash(
                        currency=entities.get("currency", "USD"),
                        amount=float(entities["amount"])
                    )

        except (ValueError, TypeError) as e:
            logger.error(f"Asset creation failed: {e}")

        return None

    def _asset_matches(self, asset: Asset, identifier: str) -> bool:
        """Check if asset matches the given identifier"""

        identifier = identifier.upper()

        if isinstance(asset, Stock):
            return asset.ticker == identifier
        elif isinstance(asset, Crypto):
            return asset.symbol == identifier
        elif isinstance(asset, RealEstate):
            return identifier.lower() in asset.address.lower()
        elif isinstance(asset, Mortgage):
            return identifier.lower() in asset.lender.lower()
        return False

    def _resolve_references(self, entities: dict, session: ChatSession) -> dict:
        """Resolve context-aware references like 'the same amount', 'it', etc."""

        # If user is continuing from previous asset discussion
        if session.portfolio_state.current_asset_type and not entities.get("type"):
            entities["type"] = session.portfolio_state.current_asset_type

        # Check for references to previous amounts
        if session.messages:
            # Look for patterns like "the same" in recent context
            recent_amounts = []
            for msg in session.messages[-4:]:
                if msg.role == "assistant":
                    continue
                # Extract numbers from recent messages
                import re
                numbers = re.findall(r'\b\d+(?:\.\d+)?\b', msg.content)
                recent_amounts.extend(numbers)

            # If entities missing amount but user said "the same", use recent amount
            if not entities.get("amount") and not entities.get("shares") and recent_amounts:
                if entities.get("type") == "stock":
                    entities["shares"] = float(recent_amounts[-1])
                else:
                    entities["amount"] = float(recent_amounts[-1])

        return entities

    def _get_portfolio_summary(self, portfolio_state: PortfolioBuildingState) -> str:
        """Generate human-readable portfolio summary"""

        if not portfolio_state.assets:
            return "No assets in portfolio yet"

        summary_parts = []

        # Group by type
        by_type = {}
        for asset in portfolio_state.assets:
            asset_type = asset.type
            if asset_type not in by_type:
                by_type[asset_type] = []
            by_type[asset_type].append(asset)

        for asset_type, assets in by_type.items():
            if asset_type == "stock":
                stocks = [f"{a.ticker} ({a.shares} shares)" for a in assets]
                summary_parts.append(f"Stocks: {', '.join(stocks)}")
            elif asset_type == "crypto":
                cryptos = [f"{a.symbol} ({a.amount})" for a in assets]
                summary_parts.append(f"Crypto: {', '.join(cryptos)}")
            elif asset_type == "real_estate":
                summary_parts.append(f"Real Estate: {len(assets)} properties")
            elif asset_type == "mortgage":
                summary_parts.append(f"Mortgages: {len(assets)} loans")
            elif asset_type == "cash":
                total_cash = sum(a.amount for a in assets)
                summary_parts.append(f"Cash: ${total_cash:,.2f}")

        return "\n".join(summary_parts)

    def _suggest_missing_assets(self, current_assets: list[Asset]) -> list[dict]:
        """Suggest common asset types that might be missing"""

        current_types = {asset.type for asset in current_assets}
        suggestions = []

        if "cash" not in current_types:
            suggestions.append({
                "type": "cash",
                "message": "Emergency fund or savings account"
            })

        if "stock" not in current_types:
            suggestions.append({
                "type": "stock",
                "message": "401(k) or individual stocks"
            })

        if "real_estate" not in current_types and "mortgage" in current_types:
            suggestions.append({
                "type": "real_estate",
                "message": "Your mortgaged property value"
            })

        return suggestions

    def process_message(self, session_id: str, user_message: str, user_id: str | None = None) -> dict:
        """Process a chat message and return response"""

        # Get or create session
        session = self.session_storage.get(session_id)
        if not session:
            session = ChatSession(
                session_id=session_id,
                user_id=user_id
            )

        session.add_message("user", user_message)

        # Run the graph
        initial_state = {
            "session": session,
            "user_message": user_message,
            "current_step": "start",
            "intent": None,
            "entities": {},
            "response": "",
            "ui_hints": {},
            "show_form": False,
            "form_data": None,
            "errors": []
        }

        try:
            result = self.graph.invoke(initial_state) # type: ignore

            # Add assistant message to session
            session.add_message("assistant", result["response"], {
                "ui_hints": result.get("ui_hints", {}),
                "show_form": result.get("show_form", False)
            })

            # Save session
            self.session_storage.set(session_id, session)

            # Prepare response
            response = {
                "message": result["response"],
                "session_id": session_id,
                "ui_hints": result.get("ui_hints", {}),
                "show_form": result.get("show_form", False),
                "form_data": result.get("form_data"),
                "portfolio_summary": {
                    "assets": len(session.portfolio_state.assets),
                    "is_complete": session.portfolio_state.is_complete
                }
            }

            if result.get("errors"):
                response["errors"] = result["errors"]

            return response

        except Exception as e:
            logger.error(f"Chat processing failed: {e}")
            return {
                "message": "I'm having trouble processing that. Could you try again?",
                "session_id": session_id,
                "error": str(e)
            }

    def get_session_portfolio(self, session_id: str) -> Portfolio | None:
        """Get the current portfolio for a session"""

        session = self.session_storage.get(session_id)
        if not session:
            return None

        if session.portfolio_state.assets:
            return Portfolio(assets=session.portfolio_state.assets)

        return None

    def clear_session(self, session_id: str):
        """Clear a chat session"""

        self.session_storage.delete(session_id)
