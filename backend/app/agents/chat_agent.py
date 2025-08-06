# backend/app/agents/chat_agent.py

import json
import logging
import os
import re
from datetime import datetime
from typing import Any

from langchain.schema import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI
from langfuse import Langfuse
from langfuse.callback import CallbackHandler
from langfuse.decorators import langfuse_context, observe
from langgraph.graph import END, StateGraph
from pydantic import SecretStr

from ..models.assets import Asset, Cash, Crypto, Mortgage, RealEstate, Stock
from ..models.portfolio import Portfolio
from .session_storage import get_session_storage
from .state.chat_state import ChatAgentState, ChatSession, PortfolioBuildingState

logger = logging.getLogger(__name__)

# Initialize Langfuse
langfuse = Langfuse(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
)


class ChatAgent:
    def __init__(self):
        # Initialize Langfuse callback handler for LLM only
        self.langfuse_handler = CallbackHandler(
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            host=os.getenv("LANGFUSE_HOST" or "")
        )

        # LLM with Langfuse callback - this will handle LLM call tracing
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT" or ""),
            api_key=SecretStr(os.getenv('AZURE_OPENAI_API_KEY') or ""),
            api_version="2025-01-01-preview",
            temperature=0.3,
            callbacks=[self.langfuse_handler]
        )

        # self._create_tools()

        self.graph = self._build_graph()
        self.session_storage = get_session_storage()

    # def _create_tools(self):
    #     """Create LangChain tools from our methods for better observability."""
    #     # Tools are now created but used properly to maintain Langfuse tracing
    #     pass

    def _build_graph(self) -> StateGraph:
        logger.info("Building chat agent workflow graph")
        workflow = StateGraph(ChatAgentState)

        # Use the tool-wrapped versions in the graph
        workflow.add_node("classify_intent", self._classify_intent_node)
        workflow.add_node("extract_entities", self._extract_entities_node)
        workflow.add_node("update_portfolio", self._update_portfolio_node)
        workflow.add_node("generate_response", self._generate_response_node)
        workflow.add_node("prepare_form", self._prepare_form_node)

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

        logger.info("Chat agent workflow graph compiled successfully")
        return workflow.compile() # type: ignore

    # Nodes
    @observe(name="classify_intent_node")
    def _classify_intent_node(self, state: ChatAgentState) -> ChatAgentState:
        logger.info("Classifying user intent from message")
        result = self._classify_intent_wrapped(
            session=state["session"],
            user_message=state["user_message"]
        )
        state["intent"] = result
        logger.info(f"Intent classified as: {result}")
        return state

    @observe(name="extract_entities_node")
    def _extract_entities_node(self, state: ChatAgentState) -> ChatAgentState:
        logger.info(f"Extracting entities for intent: {state['intent']}")
        result = self._extract_entities_wrapped(
            session=state["session"],
            user_message=state["user_message"],
            intent=state["intent"] or "unclear"
        )
        state["entities"] = result
        logger.info(f"Entities extracted: {list(result.keys()) if result else 'none'}")
        return state

    @observe(name="update_portfolio_node")
    def _update_portfolio_node(self, state: ChatAgentState) -> ChatAgentState:
        logger.info(f"Updating portfolio based on intent: {state['intent']}")
        current_assets_count = len(state["session"].portfolio_state.assets)
        result = self._update_portfolio_wrapped(
            session=state["session"],
            entities=state["entities"],
            intent=state["intent"] or "unclear"
        )
        state["ui_hints"] = result.get("ui_hints", {})
        new_assets_count = len(state["session"].portfolio_state.assets)
        if new_assets_count != current_assets_count:
            logger.info(f"Portfolio updated: {current_assets_count} → {new_assets_count} assets")
        else:
            logger.info("Portfolio state unchanged")
        return state

    @observe(name="generate_response_node")
    def _generate_response_node(self, state: ChatAgentState) -> ChatAgentState:
        logger.info("Generating response to user")
        result = self._generate_response_wrapped(
            session=state["session"],
            user_message=state["user_message"],
            intent=state["intent"] or "unclear",
            entities=state["entities"],
            portfolio_state=state["session"].portfolio_state
        )
        state["response"] = result["response"]
        state["ui_hints"] = result["ui_hints"]
        logger.info(f"Response generated ({len(result['response'])} characters)")
        return state

    @observe(name="prepare_form_node")
    def _prepare_form_node(self, state: ChatAgentState) -> ChatAgentState:
        logger.info("Preparing portfolio form for user review")
        result = self._prepare_form_wrapped(
            session=state["session"],
            portfolio_state=state["session"].portfolio_state
        )
        state["show_form"] = result.get("show_form", False)
        state["form_data"] = result.get("form_data")
        state["response"] = result.get("response", "")
        state["ui_hints"] = result.get("ui_hints", {})
        logger.info(f"Form prepared with {len(result.get('form_data', {}).get('assets', []))} assets")
        return state

    # tools
    @observe(name="classify_intent_tool")
    def _classify_intent_wrapped(self, session: ChatSession, user_message: str) -> str:
        messages: list[BaseMessage] = [
            SystemMessage(content="""You are a portfolio assistant helping users build their investment portfolio.
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
            Return ONLY the intent category, nothing else.""")
        ]

        for msg in session.messages[-10:]:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            else:
                messages.append(AIMessage(content=msg.content))

        messages.append(HumanMessage(content=user_message))

        try:
            response = self.llm.invoke(messages)
            intent_text = response.content

            if isinstance(intent_text, list):
                intent_text = next((item for item in intent_text if isinstance(item, str)), "")
            elif hasattr(intent_text, 'content'):
                intent_text = intent_text.content # type: ignore

            intent = intent_text.strip().lower()

            # Update Langfuse context
            langfuse_context.update_current_observation(
                metadata={
                    "intent": intent,
                    "session_id": session.session_id,
                    "message_count": len(session.messages)
                }
            )

            logger.info(f"Classified intent: {intent}")
            return intent

        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            langfuse_context.update_current_observation(
                metadata={"error": str(e)}
            )
            return "unclear"

    @observe(name="extract_entities_tool")
    def _extract_entities_wrapped(self, session: ChatSession, user_message: str, intent: str) -> dict[str, Any]:
        if intent not in ["add_asset", "modify_asset", "remove_asset"]:
            return {}

        messages: list[BaseMessage] = [
            SystemMessage(content="""Extract investment details from the user message.
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
            DO NOT include any text outside the JSON object.""")
        ]

        for msg in session.messages[-6:]:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            else:
                messages.append(AIMessage(content=msg.content))

        messages.append(HumanMessage(content=user_message))

        try:
            response = self.llm.invoke(messages)
            content = response.content

            entities = self._extract_json_from_llm_response(content) # type: ignore

            if entities:
                logger.info(f"Successfully extracted entities: {entities}")
                langfuse_context.update_current_observation(
                    metadata={
                        "entities_extracted": True,
                        "entity_count": len(entities),
                        "entities": entities
                    }
                )
            else:
                logger.warning("No entities extracted from response")
                entities = {}

            return entities

        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            langfuse_context.update_current_observation(
                metadata={"error": str(e)}
            )
            return {}

    @observe(name="update_portfolio_tool")
    def _update_portfolio_wrapped(self, session: ChatSession, entities: dict[str, Any], intent: str) -> dict[str, Any]:
        ui_hints = {}

        # Handle context-aware references
        entities = self._resolve_references(entities, session)

        if intent == "add_asset" and entities:
            try:
                asset = self._create_asset_from_entities(entities)
                if asset:
                    session.portfolio_state.assets.append(asset)
                    session.portfolio_state.current_asset_type = None
                    session.portfolio_state.current_asset_data = {}
                    ui_hints["asset_added"] = True

                    logger.info(f"Added asset: {asset}")
                    langfuse_context.update_current_observation(
                        metadata={
                            "asset_added": True,
                            "asset_type": asset.type,
                            "total_assets": len(session.portfolio_state.assets)
                        }
                    )
                else:
                    # Incomplete data
                    session.portfolio_state.current_asset_type = entities.get("type")
                    session.portfolio_state.current_asset_data.update(entities)
                    ui_hints["needs_more_info"] = True

            except Exception as e:
                logger.error(f"Failed to create asset: {e}")
                session.portfolio_state.validation_errors.append(str(e))

        elif intent == "remove_asset" and entities:
            identifier = entities.get("ticker") or entities.get("symbol") or entities.get("address")
            if identifier:
                original_count = len(session.portfolio_state.assets)
                session.portfolio_state.assets = [
                    a for a in session.portfolio_state.assets
                    if not self._asset_matches(a, identifier)
                ]
                if len(session.portfolio_state.assets) < original_count:
                    ui_hints["removed_asset"] = True
                    logger.info(f"Removed asset with identifier: {identifier}")

        elif intent == "complete_portfolio":
            session.portfolio_state.is_complete = True
            ui_hints["portfolio_complete"] = True

        return {"ui_hints": ui_hints}

    @observe(name="generate_response_tool")
    def _generate_response_wrapped(
        self,
        session: ChatSession,
        user_message: str,
        intent: str,
        entities: dict[str, Any],
        portfolio_state: PortfolioBuildingState
    ) -> dict[str, Any]:

        messages: list[BaseMessage] = [
            SystemMessage(content=f"""You are a friendly portfolio assistant helping users build their investment portfolio.

            Current portfolio state:
            {self._get_portfolio_summary(portfolio_state)}

            User intent: {intent}
            Extracted entities: {json.dumps(entities)}

            Guidelines:
            - Be conversational and helpful
            - Reference previous conversation when relevant
            - If information is missing, ask for specific details
            - Confirm when assets are added/removed
            - Suggest common asset types if portfolio seems incomplete
            - Keep responses concise but informative
            - Remember what the user has already told you

            Generate an appropriate response based on the conversation history.""")
        ]

        for msg in session.messages[-8:]:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            else:
                messages.append(AIMessage(content=msg.content))

        messages.append(HumanMessage(content=user_message))

        try:
            response = self.llm.invoke(messages)
            content = response.content

            if isinstance(content, list):
                content = " ".join(str(item) for item in content if isinstance(item, str | dict))
            elif hasattr(content, 'content'):
                content = content.content # type: ignore

            if not isinstance(content, str):
                content = str(content)

            ui_hints = {
                "show_portfolio_summary": len(portfolio_state.assets) > 0,
                "suggest_asset_types": len(portfolio_state.assets) < 2,
                "current_asset_count": len(portfolio_state.assets)
            }

            langfuse_context.update_current_observation(
                metadata={
                    "response_length": len(content),
                    "ui_hints": ui_hints
                }
            )

            return {
                "response": content,
                "ui_hints": ui_hints
            }

        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return {
                "response": "I encountered an error processing your request. Could you please rephrase?",
                "ui_hints": {}
            }

    @observe(name="prepare_form_tool")
    def _prepare_form_wrapped(self, session: ChatSession, portfolio_state: PortfolioBuildingState) -> dict[str, Any]:

        # Convert assets to form-friendly format
        form_assets = []
        for asset in portfolio_state.assets:
            asset_dict = {}
            if isinstance(asset, Stock):
                asset_dict = {
                    "type": "stock",
                    "ticker": asset.ticker,
                    "shares": asset.shares
                }
            elif isinstance(asset, Crypto):
                asset_dict = {
                    "type": "crypto",
                    "symbol": asset.symbol,
                    "amount": asset.amount
                }
            elif isinstance(asset, RealEstate):
                asset_dict = {
                    "type": "real_estate",
                    "address": asset.address,
                    "market_value": asset.market_value
                }
            elif isinstance(asset, Mortgage):
                asset_dict = {
                    "type": "mortgage",
                    "lender": asset.lender,
                    "balance": asset.balance,
                    "property_address": asset.property_address
                }
            elif isinstance(asset, Cash):
                asset_dict = {
                    "type": "cash",
                    "currency": asset.currency,
                    "amount": asset.amount
                }

            if asset_dict:
                form_assets.append(asset_dict)

        response = (
            "Great! I've captured your portfolio so far. Please review the details below "
            "and make any adjustments needed. You can also add any assets I might have missed."
        )

        ui_hints = {
            "show_portfolio_form": True,
            "form_mode": "review",
            "can_edit": True,
            "can_analyze": len(form_assets) > 0
        }

        langfuse_context.update_current_observation(
            metadata={
                "form_prepared": True,
                "asset_count": len(form_assets),
                "asset_types": list(set(a["type"] for a in form_assets))
            }
        )

        return {
            "show_form": True,
            "form_data": {
                "assets": form_assets,
                "suggested_additions": self._suggest_missing_assets(portfolio_state.assets)
            },
            "response": response,
            "ui_hints": ui_hints
        }

    # helpers
    @observe(name="extract_json_from_llm")
    def _extract_json_from_llm_response(self, content: str) -> dict[str, Any] | None:
        try:
            # If content is already a dict/list, return it
            if isinstance(content, dict | list):
                return content if isinstance(content, dict) else {"items": content}

            # Convert to string if needed
            if not isinstance(content, str):
                content = str(content)

            # Try to parse as-is first
            try:
                parsed = json.loads(content)
                if isinstance(parsed, dict):
                    return parsed
                elif isinstance(parsed, list) and len(parsed) > 0:
                    return parsed[0] if isinstance(parsed[0], dict) else {"items": parsed}
                else:
                    return {"data": parsed}
            except json.JSONDecodeError:
                pass

            # Try to extract JSON from markdown code blocks
            json_pattern = r'```(?:json)?\s*(\{[\s\S]*?\}|\[[\s\S]*?\])\s*```'
            matches = re.findall(json_pattern, content, re.MULTILINE)

            if matches:
                for match in matches:
                    try:
                        parsed = json.loads(match)
                        if isinstance(parsed, dict):
                            return parsed
                        elif isinstance(parsed, list):
                            if len(parsed) > 0:
                                return parsed[0] if isinstance(parsed[0], dict) else {"items": parsed}
                            else:
                                return {"items": parsed}
                        else:
                            return {"data": parsed}
                    except json.JSONDecodeError:
                        continue

            # Try to find JSON without code blocks
            json_like_pattern = r'(\{[^{}]*\}|\[[^\[\]]*\])'
            matches = re.findall(json_like_pattern, content)

            for match in matches:
                try:
                    parsed = json.loads(match)
                    if isinstance(parsed, dict):
                        return parsed
                    elif isinstance(parsed, list) and len(parsed) > 0:
                        return parsed[0] if isinstance(parsed[0], dict) else {"items": parsed}
                    else:
                        return {"data": parsed}
                except json.JSONDecodeError:
                    continue

            return None

        except Exception as e:
            logger.error(f"Failed to extract JSON from LLM response: {e}")
            return None

    @observe(name="should_show_form")
    def _should_show_form(self, state: ChatAgentState) -> str:
        session = state["session"]

        decision = "continue"
        reason = "not_ready"

        if session.portfolio_state.is_complete:
            decision = "show_form"
            reason = "portfolio_complete"
        elif len(session.portfolio_state.assets) >= 2:
            keywords = ["done", "finish", "complete", "review", "that's all", "that's it", "show me", "see my"]
            user_msg_lower = state["user_message"].lower()
            if any(keyword in user_msg_lower for keyword in keywords):
                decision = "show_form"
                reason = "user_indicated_completion"

        langfuse_context.update_current_observation(
            metadata={
                "decision": decision,
                "reason": reason,
                "asset_count": len(session.portfolio_state.assets)
            }
        )

        return decision

    @observe(name="create_asset")
    def _create_asset_from_entities(self, entities: dict) -> Asset | None:
        asset_type = entities.get("type", "").lower()

        try:
            if asset_type == "stock":
                if entities.get("ticker") and entities.get("shares"):
                    return Stock(
                        ticker=entities["ticker"].upper(),
                        shares=float(entities["shares"])
                    )

            elif asset_type in ["crypto", "cryptocurrency"]:
                if entities.get("symbol") and entities.get("amount"):
                    return Crypto(
                        symbol=entities["symbol"].upper(),
                        amount=float(entities["amount"])
                    )

            elif asset_type in ["real_estate", "realestate", "property"]:
                if entities.get("address") and (entities.get("value") or entities.get("market_value")):
                    value = entities.get("value") or entities.get("market_value")
                    if value is not None:
                        return RealEstate(
                            address=entities["address"],
                            market_value=float(value)
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
        if session.portfolio_state.current_asset_type and not entities.get("type"):
            entities["type"] = session.portfolio_state.current_asset_type

        if session.messages:
            recent_amounts = []
            for msg in session.messages[-4:]:
                if msg.role == "assistant":
                    continue
                numbers = re.findall(r'\b\d+(?:\.\d+)?\b', msg.content)
                recent_amounts.extend(numbers)

            if not entities.get("amount") and not entities.get("shares") and recent_amounts:
                if entities.get("type") == "stock":
                    entities["shares"] = float(recent_amounts[-1])
                else:
                    entities["amount"] = float(recent_amounts[-1])

        return entities

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

    def _suggest_missing_assets(self, current_assets: list[Asset]) -> list[dict]: #to enhance
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

    @observe(name="process_message")
    def process_message(self, session_id: str, user_message: str, user_id: str | None = None) -> dict:
        logger.info(f"Processing message for session {session_id}: '{user_message[:50]}{'...' if len(user_message) > 50 else ''}'")

        trace = langfuse.trace( # type: ignore
            name="chat_conversation",
            session_id=session_id,
            user_id=user_id,
            metadata={
                "session_id": session_id,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            },
            input={"user_message": user_message}
        )

        session = self.session_storage.get(session_id)
        if not session:
            logger.info(f"Creating new chat session: {session_id}")
            session = ChatSession(
                session_id=session_id,
                user_id=user_id
            )
        else:
            logger.info(f"Resuming existing session: {session_id} (messages: {len(session.messages)})")

        session.add_message("user", user_message)

        initial_state: ChatAgentState = {
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
            langfuse_context.update_current_observation(
                metadata={
                    "session_id": session_id,
                    "user_id": user_id,
                    "processing_step": "graph_invocation",
                    "trace_id": trace.id
                }
            )

            logger.info("Invoking chat workflow graph")
            result = self.graph.invoke(initial_state) # type: ignore

            session.add_message("assistant", result["response"], {
                "ui_hints": result.get("ui_hints", {}),
                "show_form": result.get("show_form", False)
            })

            self.session_storage.set(session_id, session)

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

            trace.update(
                output=response,
                metadata={
                    "success": True,
                    "asset_count": len(session.portfolio_state.assets),
                    "show_form": result.get("show_form", False),
                    "intent": result.get("intent"),
                    "entities_extracted": bool(result.get("entities"))
                }
            )

            logger.info(f"Message processed successfully - Assets: {len(session.portfolio_state.assets)}, Show form: {result.get('show_form', False)}")
            return response

        except Exception as e:
            logger.error(f"Chat processing failed for session {session_id}: {e}", exc_info=True)

            trace.update(
                output={"error": str(e)},
                metadata={"success": False, "error": str(e)}
            )

            return {
                "message": "I'm having trouble processing that. Could you try again?",
                "session_id": session_id,
                "error": str(e)
            }

    def get_session_portfolio(self, session_id: str) -> Portfolio | None:
        logger.debug(f"Retrieving portfolio for session: {session_id}")
        session = self.session_storage.get(session_id)
        if not session:
            logger.warning(f"No session found for ID: {session_id}")
            return None

        if session.portfolio_state.assets:
            logger.info(f"Found portfolio with {len(session.portfolio_state.assets)} assets for session {session_id}")
            return Portfolio(assets=session.portfolio_state.assets)
        logger.info(f"No assets found in portfolio for session {session_id}")
        return None

    def clear_session(self, session_id: str):
        logger.info(f"Clearing session: {session_id}")
        self.session_storage.delete(session_id)
        logger.info(f"Session cleared: {session_id}")
