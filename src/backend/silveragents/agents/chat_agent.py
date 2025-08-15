import logging
import os
import uuid
from datetime import datetime
from uuid import UUID

from langchain_openai import AzureChatOpenAI
from langfuse import Langfuse
from langfuse.callback import CallbackHandler
from langfuse.decorators import langfuse_context, observe
from langgraph.graph import END, StateGraph
from pydantic import SecretStr
from sqlalchemy.orm import Session

from ..models import (
    AssetConfirmation,
    AssetType,
    ChatAgentState,
    ChatSession,
    EntityData,
    Intent,
    Portfolio,
    PortfolioAction,
    PortfolioActionResult,
    PortfolioConfirmationRequest,
    ResponseGenerationResponse,
    UIHints,
    ChatResponse,
    Asset,
    Cash,
    Crypto,
    Mortgage,
    RealEstate,
    Stock,
)
from .modules import (
    EntityExtractor,
    IntentClassifier,
    ResponseGenerator,
    WorkflowUtils,
)
from .services import PortfolioService
from .session_storage import get_session_storage
from .utils import dump

logger = logging.getLogger(__name__)

langfuse = Langfuse(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
)


class ChatAgent:
    def __init__(self, db: Session | None = None):
        self.langfuse_handler = CallbackHandler(
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            host=os.getenv("LANGFUSE_HOST" or ""),
        )

        self.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT" or ""),
            openai_api_key=SecretStr(os.getenv("AZURE_OPENAI_API_KEY") or ""),
            openai_api_version="2025-01-01-preview",
            temperature=0.3,
            callbacks=[self.langfuse_handler],
        )

        self.intent_classifier = IntentClassifier(self.llm)
        self.entity_extractor = EntityExtractor(self.llm)
        self.response_generator = ResponseGenerator(self.llm)
        self.workflow_utils = WorkflowUtils()

        self.session_storage = get_session_storage()

        self.db = db

        self.pending_confirmations: dict[
            str,
            dict[str, PortfolioConfirmationRequest | str | list[EntityData] | Intent],
        ] = {}

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
                "generate_response": "generate_response",
            },
        )

        workflow.add_edge("prepare_confirmation", "generate_response")
        workflow.add_edge("update_portfolio", "generate_response")

        workflow.add_conditional_edges(
            "generate_response",
            self.workflow_utils.should_show_form,
            {"show_form": "prepare_form", "continue": END},
        )

        workflow.add_edge("prepare_form", END)

        logger.info("Enhanced chat agent workflow graph compiled successfully")
        return workflow.compile()  # type: ignore

    def _should_prepare_confirmation(self, state: ChatAgentState) -> str:
        intent = state.intent
        entities = state.entities

        if intent in [Intent.ADD_ASSET, Intent.REMOVE_ASSET, Intent.MODIFY_ASSET]:
            if entities:
                return "prepare_confirmation"
            else:
                return "generate_response"
        elif intent == Intent.COMPLETE_PORTFOLIO:
            return "update_portfolio"
        else:
            return "generate_response"

    @observe(name="classify_intent_node")
    def _classify_intent_node(self, state: ChatAgentState) -> ChatAgentState:
        logger.info("Classifying user intent from message")
        result = self.intent_classifier.classify_intent(
            session=state.session, user_message=state.user_message
        )
        logger.info(f"Intent classified as: {result}")

        try:
            langfuse_context.update_current_observation(metadata={"intent": result})
        except Exception as e:
            logger.error(f"Failed to update Langfuse metadata: {e}")

        return state.model_copy(update={"intent": result})

    @observe(name="extract_entities_node")
    def _extract_entities_node(self, state: ChatAgentState) -> ChatAgentState:
        logger.info(f"Extracting entities for intent: {state.intent}")
        entities_list = self.entity_extractor.extract_entities(
            session=state.session,
            user_message=state.user_message,
            intent=state.intent or Intent.UNCLEAR,
        )
        logger.info(f"Entities extracted: {len(entities_list)} entities")
        return state.model_copy(update={"entities": entities_list})

    @observe(name="prepare_confirmation_node")
    def _prepare_confirmation_node(self, state: ChatAgentState) -> ChatAgentState:
        logger.info("Preparing portfolio action confirmation")

        intent = state.intent
        entities_list = state.entities
        session = state.session

        if not entities_list:
            return state.model_copy(
                update={
                    "response": "I couldn't understand the asset details. Could you please clarify?"
                }
            )

        confirmation_id = f"conf_{uuid.uuid4().hex[:8]}"

        asset_confirmations = []
        for entity_data in entities_list:
            entities_dict = entity_data.model_dump(exclude_none=True)
            asset_conf = self._build_asset_confirmation(entities_dict, intent)
            if asset_conf:
                asset_confirmations.append(asset_conf)

        if not asset_confirmations:
            return state.model_copy(
                update={
                    "response": "I couldn't understand the asset details. Could you please clarify?"
                }
            )

        action_map = {
            Intent.ADD_ASSET: PortfolioAction.ADD_ASSET,
            Intent.REMOVE_ASSET: PortfolioAction.REMOVE_ASSET,
            Intent.MODIFY_ASSET: PortfolioAction.UPDATE_ASSET,
        }

        action = action_map.get(intent or Intent.UNCLEAR, PortfolioAction.ADD_ASSET)

        confirmation_request = PortfolioConfirmationRequest(
            confirmation_id=confirmation_id,
            action=action,
            assets=asset_confirmations,
            message=self._generate_confirmation_message_for_multiple(
                asset_confirmations, action
            ),
            requires_confirmation=True,
            metadata={
                "session_id": session.session_id,
                "user_id": session.user_id,
                "timestamp": datetime.now().isoformat(),
            },
        )

        self.pending_confirmations[confirmation_id] = {
            "request": confirmation_request,
            "session_id": session.session_id,
            "entities": entities_list,
            "intent": intent,
        }

        logger.info(f"Confirmation prepared: {confirmation_id} for {action}")

        updated_ui_hints = (state.ui_hints or UIHints()).model_copy(
            update={"show_portfolio_summary": True}
        )

        return state.model_copy(
            update={
                "confirmation_request": confirmation_request,
                "ui_hints": updated_ui_hints,
            }
        )

    @observe(name="update_portfolio_node")
    def _update_portfolio_node(self, state: ChatAgentState) -> ChatAgentState:
        logger.info(f"Processing portfolio completion intent: {state.intent}")

        # For COMPLETE_PORTFOLIO intent, just update UI hints
        updated_ui_hints = (state.ui_hints or UIHints()).model_copy(
            update={"show_completion_button": True, "show_portfolio_summary": True}
        )

        logger.info("Portfolio completion UI hints updated")
        return state.model_copy(update={"ui_hints": updated_ui_hints})

    @observe(name="generate_response_node")
    def _generate_response_node(self, state: ChatAgentState) -> ChatAgentState:
        logger.info("Generating response to user")

        if hasattr(state, "confirmation_request") and state.confirmation_request:
            return state.model_copy(
                update={
                    "response": ResponseGenerationResponse(
                        response="Please confirm this change."
                    ),
                    "ui_hints": state.ui_hints or UIHints(),
                }
            )
        else:
            result = self.response_generator.generate_response(
                session=state.session,
                user_message=state.user_message,
                intent=state.intent or Intent.UNCLEAR,
                entities=state.entities,
            )

            logger.info(f"Response generated ({len(result.response)} characters)")

            return state.model_copy(update={"response": result})

    @observe(name="prepare_form_node")
    def _prepare_form_node(self, state: ChatAgentState) -> ChatAgentState:
        logger.info(
            "Portfolio form generation no longer needed - using direct confirmation flow"
        )
        return state.model_copy(
            update={
                "show_form": False,
                "response": ResponseGenerationResponse(
                    response="Portfolio action completed"
                ),
            }
        )

    def _build_asset_confirmation(
        self, entities: dict, intent: Intent
    ) -> AssetConfirmation | None:
        try:
            asset_type_raw = entities.get("asset_type")
            if not asset_type_raw:
                return None

            asset_type: AssetType
            if asset_type_raw.lower() == "stock":
                asset_type = "stock"
                return AssetConfirmation(
                    type=asset_type,
                    symbol=entities.get("ticker"),
                    name=entities.get("ticker"),
                    quantity=float(entities.get("shares", 0)),
                    current_quantity=0.0,
                    action=self._intent_to_action(intent),
                    display_text=f"{entities.get('shares')} shares of {entities.get('ticker')}",
                )
            elif asset_type_raw.lower() in ["crypto", "cryptocurrency"]:
                asset_type = "crypto"
                return AssetConfirmation(
                    type=asset_type,
                    symbol=entities.get("symbol"),
                    name=entities.get("symbol"),
                    quantity=float(entities.get("amount", 0)),
                    current_quantity=0.0,
                    action=self._intent_to_action(intent),
                    display_text=f"{entities.get('amount')} {entities.get('symbol')}",
                )
            elif asset_type_raw.lower() in ["real_estate", "realestate", "property"]:
                asset_type = "real_estate"
                return AssetConfirmation(
                    type=asset_type,
                    symbol=entities.get("address"),
                    name=f"Property at {entities.get('address')}",
                    quantity=float(
                        entities.get("value") or entities.get("market_value", 0)
                    ),
                    current_quantity=0.0,
                    action=self._intent_to_action(intent),
                    display_text=f"Property at {entities.get('address')} (${entities.get('value', 0):,.0f})",
                )
            elif asset_type_raw.lower() == "mortgage":
                asset_type = "mortgage"
                return AssetConfirmation(
                    type=asset_type,
                    symbol=entities.get("lender"),
                    name=f"Mortgage from {entities.get('lender')}",
                    quantity=float(entities.get("balance", 0)),
                    current_quantity=0.0,
                    action=self._intent_to_action(intent),
                    display_text=f"Mortgage from {entities.get('lender')} (${entities.get('balance', 0):,.0f})",
                )
            elif asset_type_raw.lower() == "cash":
                asset_type = "cash"
                return AssetConfirmation(
                    type=asset_type,
                    symbol=entities.get("currency", "USD"),
                    name=f"Cash in {entities.get('currency', 'USD')}",
                    quantity=float(entities.get("amount", 0)),
                    current_quantity=0.0,
                    action=self._intent_to_action(intent),
                    display_text=f"${entities.get('amount', 0):,.2f} {entities.get('currency', 'USD')}",
                )

            return None

        except Exception as e:
            logger.error(f"Failed to build asset confirmation: {e}")
            return None

    def _intent_to_action(self, intent: Intent) -> PortfolioAction:
        mapping = {
            Intent.ADD_ASSET: PortfolioAction.ADD_ASSET,
            Intent.REMOVE_ASSET: PortfolioAction.REMOVE_ASSET,
            Intent.MODIFY_ASSET: PortfolioAction.UPDATE_ASSET,
        }
        return mapping.get(intent, PortfolioAction.ADD_ASSET)

    def _generate_confirmation_message(
        self, asset: AssetConfirmation, action: PortfolioAction
    ) -> str:
        if action == PortfolioAction.ADD_ASSET:
            return f"Would you like to add {asset.display_text} to your portfolio?"
        elif action == PortfolioAction.REMOVE_ASSET:
            return f"Would you like to remove {asset.display_text} from your portfolio?"
        elif action == PortfolioAction.UPDATE_ASSET:
            return f"Would you like to update {asset.display_text} in your portfolio?"
        else:
            return "Would you like to proceed with this portfolio change?"

    def _generate_confirmation_message_for_multiple(
        self, assets: list[AssetConfirmation], action: PortfolioAction
    ) -> str:
        if len(assets) == 1:
            return self._generate_confirmation_message(assets[0], action)

        asset_list = ", ".join(asset.display_text for asset in assets)

        if action == PortfolioAction.ADD_ASSET:
            return f"Would you like to add {asset_list} to your portfolio?"
        elif action == PortfolioAction.REMOVE_ASSET:
            return f"Would you like to remove {asset_list} from your portfolio?"
        elif action == PortfolioAction.UPDATE_ASSET:
            return f"Would you like to update {asset_list} in your portfolio?"
        else:
            return f"Would you like to proceed with changes to {asset_list}?"

    @observe(name="process_message")
    def process_message(
        self,
        session_id: str,
        user_message: str,
        user_id: str | None = None,
        _db: Session | None = None,
    ) -> ChatResponse:
        logger.info(
            f"Processing message for session {session_id}: '{user_message[:5]}{'...' if len(user_message) > 5 else ''}'"
        )

        trace = langfuse.trace(
            name="chat_conversation",
            session_id=session_id,
            user_id=user_id,
            metadata={
                "session_id": session_id,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
            },
            input={"user_message": user_message},
        )

        session = self.session_storage.get(session_id)
        if not session:
            logger.info(f"Creating new chat session: {session_id}")
            session = ChatSession(session_id=session_id, user_id=user_id)
        else:
            logger.info(
                f"Resuming existing session: {session_id} (messages: {len(session.messages)})"
            )

        session.add_message("user", user_message)

        initial_state = ChatAgentState(
            session=session,
            user_message=user_message,
            current_step="start",
            intent=Intent.UNCLEAR,
            entities=[],
            response=ResponseGenerationResponse(response=""),
            ui_hints=UIHints(),
            confirmation_request=None,
            show_form=False,
            errors=[],
        )

        try:
            langfuse_context.update_current_observation(
                metadata={
                    "session_id": session_id,
                    "user_id": user_id,
                    "processing_step": "graph_invocation",
                    "trace_id": trace.id,
                }
            )

            logger.info("Invoking chat workflow graph")
            raw_result = self.graph.invoke(initial_state)  # type: ignore
            result = ChatAgentState.model_validate(raw_result)

            message_text = (
                result.response.response
                if result.response
                else "I'm not sure how to respond to that."
            )

            response_metadata = {  # json safe
                "ui_hints": dump(result.ui_hints),
                "show_form": result.show_form,
                **(
                    {"confirmation_request": dump(result.confirmation_request)}
                    if result.confirmation_request
                    else {}
                ),
            }

            session.add_message("assistant", message_text, response_metadata)
            self.session_storage.set(session_id, session)

            # Create ChatResponse with proper Pydantic objects (not dumped versions)
            chat_response = ChatResponse(
                message=message_text,
                session_id=session_id,
                ui_hints=None,  # ChatResponse expects list[EntityData] | None, not UIHints
                show_form=result.show_form,
                confirmation_request=result.confirmation_request,
                requires_confirmation=(
                    result.confirmation_request is not None
                    and getattr(result.confirmation_request, "confirmed", None) is None
                ),
                error=None if not result.errors else "; ".join(result.errors),
            )

            trace.update(
                output=chat_response.model_dump(mode="json"),
                metadata={
                    "success": True,
                    "show_form": result.show_form,
                    "intent": dump(result.intent),
                    "entities_extracted": bool(result.entities),
                    "confirmation_pending": chat_response.requires_confirmation,
                },
            )

            logger.info(
                "Message processed - Confirmation: %s",
                bool(result.confirmation_request),
            )
            return chat_response

        except Exception as e:
            logger.error(
                f"Chat processing failed for session {session_id}: {e}", exc_info=True
            )

            trace.update(
                output={"error": str(e)}, metadata={"success": False, "error": str(e)}
            )

            return ChatResponse(
                message="I'm having trouble processing that. Could you try again?",
                session_id=session_id,
                error=str(e),
            )

    @observe(name="process_confirmation")
    def process_confirmation(
        self, confirmation_id: str, confirmed: bool, user_id: str, db: Session
    ) -> PortfolioActionResult:
        logger.info(f"Processing confirmation {confirmation_id}: confirmed={confirmed}")

        try:
            pending = self.pending_confirmations.get(confirmation_id)
            if not pending:
                logger.warning(f"Confirmation {confirmation_id} not found")
                return PortfolioActionResult(
                    success=False,
                    action=PortfolioAction.ADD_ASSET,
                    message="Confirmation request not found or expired",
                    portfolio_updated=False,
                )

            del self.pending_confirmations[confirmation_id]

            if not confirmed:
                logger.info(f"Confirmation {confirmation_id} rejected by user")
                return PortfolioActionResult(
                    success=True,
                    action=PortfolioAction.ADD_ASSET,
                    message="Action cancelled",
                    portfolio_updated=False,
                )

            request = pending["request"]
            entities = pending["entities"]

            if not isinstance(request, PortfolioConfirmationRequest):
                return PortfolioActionResult(
                    success=False,
                    action=PortfolioAction.ADD_ASSET,
                    message="Invalid confirmation request format",
                    portfolio_updated=False,
                )

            if not isinstance(entities, list):
                return PortfolioActionResult(
                    success=False,
                    action=request.action,
                    message="Invalid entities format",
                    portfolio_updated=False,
                )

            portfolio_service = PortfolioService(db)

            result = self._execute_portfolio_action(
                portfolio_service=portfolio_service,
                user_id=UUID(user_id),
                action=request.action,
                entities=entities,
            )

            if result.success:
                logger.info(f"Portfolio action executed successfully: {result.message}")

                portfolio_summary = portfolio_service.get_portfolio_summary(
                    UUID(user_id)
                )

                return PortfolioActionResult(
                    success=True,
                    action=request.action,
                    message=result.message,
                    portfolio_updated=True,
                    portfolio_summary=portfolio_summary,
                )
            else:
                logger.error(f"Portfolio action failed: {result.error}")
                return PortfolioActionResult(
                    success=False,
                    action=request.action,
                    message=result.message or "Failed to update portfolio",
                    portfolio_updated=False,
                    error=result.error,
                )

        except Exception as e:
            logger.error(f"Confirmation processing failed: {e}", exc_info=True)
            return PortfolioActionResult(
                success=False,
                action=PortfolioAction.ADD_ASSET,
                message="Failed to process confirmation",
                portfolio_updated=False,
                error=str(e),
            )

    def _execute_portfolio_action(
        self,
        portfolio_service: PortfolioService,
        user_id: UUID,
        action: PortfolioAction,
        entities: list[EntityData],
    ) -> PortfolioActionResult:
        try:
            primary_entity = entities[0] if entities else None
            if not primary_entity:
                return PortfolioActionResult(
                    success=False,
                    action=action,
                    message="No entity data provided",
                    portfolio_updated=False,
                )

            asset = self._create_asset_from_entity(primary_entity)

            if not asset:
                return PortfolioActionResult(
                    success=False,
                    action=action,
                    message="Could not create asset from provided information",
                    portfolio_updated=False,
                )

            if action == PortfolioAction.ADD_ASSET:
                return portfolio_service.add_asset(user_id, asset)
            elif action == PortfolioAction.REMOVE_ASSET:
                symbol, asset_type, _, _ = portfolio_service._prepare_asset_data(asset)
                return portfolio_service.remove_asset(
                    user_id=user_id, symbol=symbol, asset_type=asset_type
                )
            elif action == PortfolioAction.UPDATE_ASSET:
                symbol, asset_type, quantity, _ = portfolio_service._prepare_asset_data(
                    asset
                )
                return portfolio_service.update_asset(
                    user_id=user_id,
                    symbol=symbol,
                    asset_type=asset_type,
                    new_quantity=quantity,
                )
            else:
                return PortfolioActionResult(
                    success=False,
                    action=action,
                    message=f"Unknown action: {action}",
                    portfolio_updated=False,
                )

        except Exception as e:
            logger.error(f"Portfolio action execution failed: {e}", exc_info=True)
            return PortfolioActionResult(
                success=False,
                action=action,
                message=f"Failed to execute portfolio action: {e}",
                portfolio_updated=False,
                error=str(e),
            )

    def _create_asset_from_entity(self, entity: EntityData) -> Asset | None:
        """Create an Asset object from extracted entity data."""
        if not entity.asset_type:
            return None

        asset_type = entity.asset_type.lower()

        try:
            if asset_type == "stock":
                if entity.ticker and entity.shares:
                    return Stock(
                        ticker=entity.ticker.upper(), shares=float(entity.shares)
                    )

            elif asset_type in ["crypto", "cryptocurrency"]:
                if entity.symbol and entity.amount:
                    return Crypto(
                        symbol=entity.symbol.upper(), amount=float(entity.amount)
                    )

            elif asset_type in ["real_estate", "realestate", "property"]:
                if entity.address and entity.market_value:
                    return RealEstate(
                        address=entity.address, market_value=float(entity.market_value)
                    )

            elif asset_type == "mortgage":
                if entity.lender and entity.balance:
                    return Mortgage(
                        lender=entity.lender,
                        balance=float(entity.balance),
                        property_address=getattr(entity, "property_address", None),
                    )

            elif asset_type == "cash":
                if entity.amount:
                    return Cash(
                        currency=entity.currency or "USD", amount=float(entity.amount)
                    )

        except (ValueError, TypeError) as e:
            logger.error(f"Asset creation failed: {e}")

        return None

    def get_session_portfolio(self, session_id: str) -> Portfolio | None:
        logger.debug(
            f"Portfolio state removed from sessions - no in-memory portfolio available for session: {session_id}"
        )
        return None

    def clear_session(self, session_id: str):
        logger.info(f"Clearing session: {session_id}")
        self.session_storage.delete(session_id)
        logger.info(f"Session cleared: {session_id}")
