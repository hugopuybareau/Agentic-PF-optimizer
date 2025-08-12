import logging
import os
from datetime import datetime

from langchain_openai import AzureChatOpenAI
from langfuse import Langfuse
from langfuse.callback import CallbackHandler
from langfuse.decorators import langfuse_context, observe
from langgraph.graph import END, StateGraph
from pydantic import SecretStr

from ..models.portfolio import Portfolio
from .modules.entity_extractor import EntityExtractor
from .modules.form_preparer import FormPreparer
from .modules.intent_classifier import IntentClassifier
from ..models import Intent
from .modules.portfolio_operations import PortfolioOperations
from .modules.response_generator import ResponseGenerator
from .modules.workflow_utils import WorkflowUtils
from .session_storage import get_session_storage
from ..models import ChatAgentState, ChatSession

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

        # Initialize modular components
        self.intent_classifier = IntentClassifier(self.llm)
        self.entity_extractor = EntityExtractor(self.llm)
        self.portfolio_operations = PortfolioOperations()
        self.response_generator = ResponseGenerator(self.llm)
        self.form_preparer = FormPreparer()
        self.workflow_utils = WorkflowUtils()

        self.graph = self._build_graph()
        self.session_storage = get_session_storage()

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
            self.workflow_utils.should_show_form,
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

    @observe(name="update_portfolio_node")
    def _update_portfolio_node(self, state: ChatAgentState) -> ChatAgentState:
        logger.info(f"Updating portfolio based on intent: {state['intent']}")
        current_assets_count = len(state["session"].portfolio_state.assets)
        result = self.portfolio_operations.update_portfolio(
            session=state["session"],
            entities=state["entities"],
            intent=state["intent"] or Intent.UNCLEAR
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
        result = self.response_generator.generate_response(
            session=state["session"],
            user_message=state["user_message"],
            intent=state["intent"] or Intent.UNCLEAR,
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
