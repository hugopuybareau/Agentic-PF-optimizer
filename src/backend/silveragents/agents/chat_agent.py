# backend/app/agents/chat_agent_v2.py

import logging
import os
import uuid
from datetime import datetime

from langchain_openai import AzureChatOpenAI
from langfuse import Langfuse
from langfuse.callback import CallbackHandler
from langfuse.decorators import langfuse_context, observe
from langgraph.graph import END, StateGraph
from pydantic import SecretStr
from sqlalchemy.orm import Session

from ..models import ChatAgentState, ChatSession, Intent
from ..models.portfolio import Portfolio
from ..models.portfolio_responses import (
    AssetConfirmation,
    PortfolioAction,
    PortfolioConfirmationRequest,
)
from .modules.entity_extractor import EntityExtractor
from .modules.form_preparer import FormPreparer
from .modules.intent_classifier import IntentClassifier
from .modules.portfolio_operations import PortfolioOperations
from .modules.response_generator import ResponseGenerator
from .modules.workflow_utils import WorkflowUtils
from .services.portfolio_service import PortfolioService
from .session_storage import get_session_storage

logger = logging.getLogger(__name__)

langfuse = Langfuse(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
)


class ChatAgent:

    def __init__(self, db: Session | None = None):
        # Initialize Langfuse callback handler for LLM only
        self.langfuse_handler = CallbackHandler(
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            host=os.getenv("LANGFUSE_HOST" or "")
        )

        self.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT" or ""),
            api_key=SecretStr(os.getenv('AZURE_OPENAI_API_KEY') or ""),
            api_version="2025-01-01-preview",
            temperature=0.3,
            callbacks=[self.langfuse_handler]
        )

        self.intent_classifier = IntentClassifier(self.llm)
        self.entity_extractor = EntityExtractor(self.llm)
        self.portfolio_operations = PortfolioOperations()
        self.response_generator = ResponseGenerator(self.llm)
        self.form_preparer = FormPreparer()
        self.workflow_utils = WorkflowUtils()

        self.session_storage = get_session_storage()

        self.db = db

        self.pending_confirmations: dict[str, dict] = {}

        self.graph = self._build_graph()

        logger.info("ChatAgent initialized")

    def _build_graph(self) -> StateGraph:
        logger.info("Building enhanced chat agent workflow graph")
        workflow = StateGraph(ChatAgentState)

        workflow.add_node("classify_intent", self._classify_intent_node)
        workflow.add_node("extract_entities", self._extract_entities_node)
        workflow.add_node("prepare_confirmation", self._prepare_confirmation_node)
        workflow.add_node("update_portfolio", self._update_portfolio_node)
        workflow.add_node("generate_response", self._generate_response_node)
        workflow.add_node("prepare_form", self._prepare_form_node)

        workflow.set_entry_point("classify_intent")
        workflow.add_edge("classify_intent", "extract_entities")

        # Add conditional routing based on intent
        workflow.add_conditional_edges(
            "extract_entities",
            self._should_prepare_confirmation,
            {
                "prepare_confirmation": "prepare_confirmation",
                "update_portfolio": "update_portfolio",
                "generate_response": "generate_response"
            }
        )

        workflow.add_edge("prepare_confirmation", "generate_response")
        workflow.add_edge("update_portfolio", "generate_response")

        workflow.add_conditional_edges(
            "generate_response",
            self.workflow_utils.should_show_form,
            {
                "show_form": "prepare_form",
                "continue": END
            }
        )

        workflow.add_edge("prepare_form", END)

        logger.info("Enhanced chat agent workflow graph compiled successfully")
        return workflow.compile()  # type: ignore

    # Conditional routing functions
    def _should_prepare_confirmation(self, state: ChatAgentState) -> str:
        """Determine if confirmation is needed for the action."""
        intent = state.get("intent")
        entities = state.get("entities", {})

        # Portfolio modification intents need confirmation
        if intent in [Intent.ADD_ASSET, Intent.REMOVE_ASSET, Intent.MODIFY_ASSET]:
            if entities:  # Only if we extracted valid entities
                return "prepare_confirmation"
            else:
                return "generate_response"  # Ask for more info
        elif intent == Intent.COMPLETE_PORTFOLIO:
            return "update_portfolio"  # Direct to portfolio update
        else:
            return "generate_response"  # Other intents

    # Node implementations
    @observe(name="classify_intent_node")
    def _classify_intent_node(self, state: ChatAgentState) -> ChatAgentState:
        logger.info("Classifying user intent from message")
        result = self.intent_classifier.classify_intent(
            session=state["session"],
            user_message=state["user_message"]
        )
        state["intent"] = result
        logger.info(f"Intent classified as: {result}")

        try:
            langfuse_context.update_current_observation(
                metadata={"intent": result}
            )
        except Exception as e:
            logger.error(f"Failed to update Langfuse metadata: {e}")
        return state

    @observe(name="extract_entities_node")
    def _extract_entities_node(self, state: ChatAgentState) -> ChatAgentState:
        logger.info(f"Extracting entities for intent: {state['intent']}")
        entities = self.entity_extractor.extract_entities(
            session=state["session"],
            user_message=state["user_message"],
            intent=state["intent"] or Intent.UNCLEAR
        )
        # Handle context-aware references
        result = self.entity_extractor.resolve_references(entities, state["session"])
        state["entities"] = result
        logger.info(f"Entities extracted: {list(result.keys()) if result else 'none'}")
        return state

    @observe(name="prepare_confirmation_node")
    def _prepare_confirmation_node(self, state: ChatAgentState) -> ChatAgentState:
        """Prepare confirmation request for portfolio changes."""
        logger.info("Preparing portfolio action confirmation")

        intent = state["intent"]
        entities = state["entities"]
        session = state["session"]

        # Create confirmation request
        confirmation_id = f"conf_{uuid.uuid4().hex[:8]}"

        # Build asset confirmation
        asset_conf = self._build_asset_confirmation(entities, intent)

        if not asset_conf:
            state["response"] = "I couldn't understand the asset details. Could you please clarify?"
            return state

        # Map intent to action
        action_map = {
            Intent.ADD_ASSET: PortfolioAction.ADD_ASSET,
            Intent.REMOVE_ASSET: PortfolioAction.REMOVE_ASSET,
            Intent.MODIFY_ASSET: PortfolioAction.UPDATE_ASSET
        }

        action = action_map.get(intent, PortfolioAction.ADD_ASSET)

        # Create confirmation request
        confirmation_request = PortfolioConfirmationRequest(
            confirmation_id=confirmation_id,
            action=action,
            assets=[asset_conf],
            message=self._generate_confirmation_message(asset_conf, action),
            requires_confirmation=True,
            metadata={
                "session_id": session.session_id,
                "user_id": session.user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        # Store pending confirmation
        self.pending_confirmations[confirmation_id] = {
            "request": confirmation_request,
            "session_id": session.session_id,
            "entities": entities,
            "intent": intent
        }

        # Add to state for response generation
        state["confirmation_request"] = confirmation_request.model_dump()
        state["ui_hints"]["confirmation_pending"] = True
        state["ui_hints"]["confirmation_id"] = confirmation_id

        logger.info(f"Confirmation prepared: {confirmation_id} for {action}")

        return state

    @observe(name="update_portfolio_node")
    def _update_portfolio_node(self, state: ChatAgentState) -> ChatAgentState:
        """Update the in-memory portfolio state (form preparation flow)."""
        logger.info(f"Updating in-memory portfolio based on intent: {state['intent']}")
        current_assets_count = len(state["session"].portfolio_state.assets)

        result = self.portfolio_operations.update_portfolio(
            session=state["session"],
            entities=state["entities"],
            intent=state["intent"] or Intent.UNCLEAR
        )

        state["ui_hints"] = result.get("ui_hints", {})
        new_assets_count = len(state["session"].portfolio_state.assets)

        if new_assets_count != current_assets_count:
            logger.info(f"In-memory portfolio updated: {current_assets_count} → {new_assets_count} assets")
        else:
            logger.info("Portfolio state unchanged")

        return state

    @observe(name="generate_response_node")
    def _generate_response_node(self, state: ChatAgentState) -> ChatAgentState:
        """Generate response with confirmation request if needed."""
        logger.info("Generating response to user")

        # Check if we have a confirmation request
        if state.get("confirmation_request"):
            conf_req = state["confirmation_request"]
            state["response"] = conf_req["message"]
            state["ui_hints"]["show_confirmation"] = True
            state["ui_hints"]["confirmation_data"] = conf_req
        else:
            # Regular response generation
            result = self.response_generator.generate_response(
                session=state["session"],
                user_message=state["user_message"],
                intent=state["intent"] or Intent.UNCLEAR,
                entities=state["entities"],
                portfolio_state=state["session"].portfolio_state
            )
            state["response"] = result["response"]
            state["ui_hints"].update(result["ui_hints"])

        logger.info(f"Response generated ({len(state['response'])} characters)")
        return state

    @observe(name="prepare_form_node")
    def _prepare_form_node(self, state: ChatAgentState) -> ChatAgentState:
        """Prepare portfolio form for user review."""
        logger.info("Preparing portfolio form for user review")
        result = self.form_preparer.prepare_form(
            session=state["session"],
            portfolio_state=state["session"].portfolio_state
        )
        state["show_form"] = result.get("show_form", False)
        state["form_data"] = result.get("form_data")
        state["response"] = result.get("response", "")
        state["ui_hints"] = result.get("ui_hints", {})
        logger.info(f"Form prepared with {len(result.get('form_data', {}).get('assets', []))} assets")
        return state

    def _build_asset_confirmation(self, entities: dict, intent: Intent) -> AssetConfirmation | None:
        """Build asset confirmation from extracted entities."""
        try:
            asset_type = entities.get("type", "").lower()

            if asset_type == "stock":
                return AssetConfirmation(
                    type="stock",
                    symbol=entities.get("ticker"),
                    quantity=float(entities.get("shares", 0)),
                    action=self._intent_to_action(intent),
                    display_text=f"{entities.get('shares')} shares of {entities.get('ticker')}"
                )
            elif asset_type in ["crypto", "cryptocurrency"]:
                return AssetConfirmation(
                    type="crypto",
                    symbol=entities.get("symbol"),
                    quantity=float(entities.get("amount", 0)),
                    action=self._intent_to_action(intent),
                    display_text=f"{entities.get('amount')} {entities.get('symbol')}"
                )
            elif asset_type in ["real_estate", "realestate", "property"]:
                return AssetConfirmation(
                    type="real_estate",
                    symbol=entities.get("address"),
                    quantity=float(entities.get("value") or entities.get("market_value", 0)),
                    action=self._intent_to_action(intent),
                    display_text=f"Property at {entities.get('address')} (${entities.get('value', 0):,.0f})"
                )
            elif asset_type == "mortgage":
                return AssetConfirmation(
                    type="mortgage",
                    symbol=entities.get("lender"),
                    quantity=float(entities.get("balance", 0)),
                    action=self._intent_to_action(intent),
                    display_text=f"Mortgage from {entities.get('lender')} (${entities.get('balance', 0):,.0f})"
                )
            elif asset_type == "cash":
                return AssetConfirmation(
                    type="cash",
                    symbol=entities.get("currency", "USD"),
                    quantity=float(entities.get("amount", 0)),
                    action=self._intent_to_action(intent),
                    display_text=f"${entities.get('amount', 0):,.2f} {entities.get('currency', 'USD')}"
                )

            return None

        except Exception as e:
            logger.error(f"Failed to build asset confirmation: {e}")
            return None

    def _intent_to_action(self, intent: Intent) -> PortfolioAction:
        """Convert intent to portfolio action."""
        mapping = {
            Intent.ADD_ASSET: PortfolioAction.ADD_ASSET,
            Intent.REMOVE_ASSET: PortfolioAction.REMOVE_ASSET,
            Intent.MODIFY_ASSET: PortfolioAction.UPDATE_ASSET
        }
        return mapping.get(intent, PortfolioAction.ADD_ASSET)

    def _generate_confirmation_message(self, asset: AssetConfirmation, action: PortfolioAction) -> str:
        """Generate user-friendly confirmation message."""
        if action == PortfolioAction.ADD_ASSET:
            return f"Would you like to add {asset.display_text} to your portfolio?"
        elif action == PortfolioAction.REMOVE_ASSET:
            return f"Would you like to remove {asset.display_text} from your portfolio?"
        elif action == PortfolioAction.UPDATE_ASSET:
            return f"Would you like to update {asset.display_text} in your portfolio?"
        else:
            return "Would you like to proceed with this portfolio change?"

    @observe(name="process_message_v2")
    def process_message(
        self,
        session_id: str,
        user_message: str,
        user_id: str | None = None,
        db: Session | None = None
    ) -> dict:
        """Process message with portfolio persistence support."""
        logger.info(f"Processing message for session {session_id}: '{user_message[:50]}{'...' if len(user_message) > 50 else ''}'")

        trace = langfuse.trace(  # type: ignore
            name="chat_conversation_v2",
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
            result = self.graph.invoke(initial_state)  # type: ignore

            # Prepare response with confirmation if needed
            response_metadata = {
                "ui_hints": result.get("ui_hints", {}),
                "show_form": result.get("show_form", False)
            }

            # Add confirmation request to metadata if present
            if result.get("confirmation_request"):
                response_metadata["confirmation_request"] = result["confirmation_request"]

            session.add_message("assistant", result["response"], response_metadata)
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

            # Add confirmation request to response if present
            if result.get("confirmation_request"):
                response["confirmation_request"] = result["confirmation_request"]
                response["requires_confirmation"] = True

            if result.get("errors"):
                response["errors"] = result["errors"]

            trace.update(
                output=response,
                metadata={
                    "success": True,
                    "asset_count": len(session.portfolio_state.assets),
                    "show_form": result.get("show_form", False),
                    "intent": result.get("intent"),
                    "entities_extracted": bool(result.get("entities")),
                    "confirmation_pending": bool(result.get("confirmation_request"))
                }
            )

            logger.info(f"Message processed - Assets: {len(session.portfolio_state.assets)}, Confirmation: {bool(result.get('confirmation_request'))}")
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

    @observe(name="process_confirmation")
    def process_confirmation(
        self,
        confirmation_id: str,
        confirmed: bool,
        user_id: str,
        db: Session
    ) -> dict:
        """Process confirmation response and update database if confirmed."""
        logger.info(f"Processing confirmation {confirmation_id}: confirmed={confirmed}")

        try:
            # Get pending confirmation
            pending = self.pending_confirmations.get(confirmation_id)
            if not pending:
                logger.warning(f"Confirmation {confirmation_id} not found")
                return {
                    "success": False,
                    "message": "Confirmation request not found or expired"
                }

            # Remove from pending
            del self.pending_confirmations[confirmation_id]

            if not confirmed:
                logger.info(f"Confirmation {confirmation_id} rejected by user")
                return {
                    "success": True,
                    "confirmed": False,
                    "message": "Action cancelled"
                }

            # Process the confirmed action
            request = pending["request"]
            entities = pending["entities"]
            intent = pending["intent"]

            # Initialize portfolio service
            portfolio_service = PortfolioService(db)

            # Execute the action
            result = self._execute_portfolio_action(
                portfolio_service=portfolio_service,
                user_id=UUID(user_id),
                action=request.action,
                entities=entities
            )

            if result["success"]:
                logger.info(f"Portfolio action executed successfully: {result['message']}")

                # Get updated portfolio summary
                portfolio_summary = portfolio_service.get_portfolio_summary(UUID(user_id))

                return {
                    "success": True,
                    "confirmed": True,
                    "message": result["message"],
                    "portfolio_updated": True,
                    "portfolio_summary": portfolio_summary,
                    "action_result": result
                }
            else:
                logger.error(f"Portfolio action failed: {result.get('error')}")
                return {
                    "success": False,
                    "message": result.get("message", "Failed to update portfolio"),
                    "error": result.get("error")
                }

        except Exception as e:
            logger.error(f"Confirmation processing failed: {e}", exc_info=True)
            return {
                "success": False,
                "message": "Failed to process confirmation",
                "error": str(e)
            }

    def _execute_portfolio_action(
        self,
        portfolio_service: PortfolioService,
        user_id: UUID,
        action: PortfolioAction,
        entities: dict
    ) -> dict:
        """Execute the portfolio action in the database."""

        try:
            # Create asset from entities
            asset = self.portfolio_operations._create_asset_from_entities(entities)

            if not asset:
                return {
                    "success": False,
                    "message": "Could not create asset from provided information"
                }

            if action == PortfolioAction.ADD_ASSET:
                return portfolio_service.add_asset(user_id, asset)
            elif action == PortfolioAction.REMOVE_ASSET:
                symbol, asset_type, _, _ = portfolio_service._prepare_asset_data(asset)
                return portfolio_service.remove_asset(
                    user_id=user_id,
                    symbol=symbol,
                    asset_type=asset_type
                )
            elif action == PortfolioAction.UPDATE_ASSET:
                symbol, asset_type, quantity, _ = portfolio_service._prepare_asset_data(asset)
                return portfolio_service.update_asset(
                    user_id=user_id,
                    symbol=symbol,
                    asset_type=asset_type,
                    new_quantity=quantity
                )
            else:
                return {
                    "success": False,
                    "message": f"Unknown action: {action}"
                }

        except Exception as e:
            logger.error(f"Portfolio action execution failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute portfolio action: {e}"
            }

    def get_session_portfolio(self, session_id: str) -> Portfolio | None:
        """Get the in-memory portfolio for a session."""
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
        """Clear a chat session."""
        logger.info(f"Clearing session: {session_id}")
        self.session_storage.delete(session_id)
        logger.info(f"Session cleared: {session_id}")
