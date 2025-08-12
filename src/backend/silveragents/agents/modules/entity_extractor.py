import logging
import re
from typing import Any

from langchain.schema import AIMessage, BaseMessage, HumanMessage
from langchain_openai import AzureChatOpenAI
from langfuse.decorators import langfuse_context, observe
from pydantic import ValidationError

from ...config.prompts import prompt_manager
from ..response_models import EntityExtractionResponse, Intent
from ..state.chat_state import ChatSession

logger = logging.getLogger(__name__)


class EntityExtractor:
    def __init__(self, llm: AzureChatOpenAI):
        self.llm = llm

    @observe(name="extract_entities_tool")
    def extract_entities(self, session: ChatSession, user_message: str, intent: Intent) -> dict[str, Any]:
        if intent not in [Intent.ADD_ASSET, Intent.MODIFY_ASSET, Intent.REMOVE_ASSET]:
            return {}

        conversation_history: list[BaseMessage] = []
        for msg in session.messages[-6:]:
            conversation_history.append(
                HumanMessage(content=msg.content) if msg.role == "user"
                else AIMessage(content=msg.content)
            )

        messages = prompt_manager.build_messages(
            system_prompt_name="chat-entity-extractor",
            user_content=user_message,
            conversation_history=conversation_history
        )

        def _observe(extra: dict):
            langfuse_context.update_current_observation(
                metadata={
                    "session_id": session.session_id,
                    "message_count": len(session.messages),
                    "user_message": user_message,
                    "intent": intent,
                    **extra
                }
            )

        try:
            raw_response = self.llm.with_structured_output(EntityExtractionResponse).invoke(messages, timeout=8)
            try:
                entity_response = EntityExtractionResponse.model_validate(raw_response)
                entity_data = entity_response.primary_entity or (entity_response.entities[0] if entity_response.entities else None)

                if entity_data:
                    entities = entity_data.model_dump(exclude_none=True)
                    if "asset_type" in entities:
                        entities["type"] = entities.pop("asset_type")
                else:
                    entities = {}
            except ValidationError as ve:
                logger.error(f"Entity validation error: {ve}", exc_info=True)
                _observe({"validation_error": str(ve)})
                entities = {}

            if entities:
                logger.info(f"Successfully extracted entities: {entities}")
                _observe({
                    "entities_extracted": True,
                    "entity_count": len(entities),
                    "entities": entities
                })
            else:
                logger.warning("No entities extracted from response")
                _observe({"entities_extracted": False})

            return entities

        except Exception as e:
            logger.error(f"Entity extraction failed: {e}", exc_info=True)
            _observe({"error": str(e)})
            return {}


    @observe(name="resolve_references")
    def resolve_references(self, entities: dict, session: ChatSession) -> dict:
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
