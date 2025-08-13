import logging
import re

from langchain.schema import AIMessage, BaseMessage, HumanMessage
from langchain_openai import AzureChatOpenAI
from langfuse.decorators import langfuse_context, observe
from pydantic import ValidationError

from ...config.prompts import prompt_manager
from ...models import ChatSession, EntityData, EntityExtractionResponse, Intent

logger = logging.getLogger(__name__)


class EntityExtractor:
    def __init__(self, llm: AzureChatOpenAI):
        self.llm = llm

    @observe(name="extract_entities_tool")
    def extract_entities(self, session: ChatSession, user_message: str, intent: Intent) -> list[EntityData]:
        if intent not in [Intent.ADD_ASSET, Intent.MODIFY_ASSET, Intent.REMOVE_ASSET]:
            return []

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

                # Process all entities and resolve references
                resolved_entities = []

                if entity_data:  # Primary entity
                    resolved_entity = self.resolve_references(entity_data, session)
                    resolved_entities.append(resolved_entity)

                # Process additional entities from the list
                for additional_entity in entity_response.entities:
                    if additional_entity != entity_data:  # Avoid duplicating primary entity
                        resolved_entity = self.resolve_references(additional_entity, session)
                        resolved_entities.append(resolved_entity)

                if resolved_entities:
                    logger.info(f"Successfully extracted and resolved {len(resolved_entities)} entities")
                    _observe({
                        "entities_extracted": True,
                        "entity_count": len(resolved_entities),
                        "entities": [e.model_dump(exclude_none=True) for e in resolved_entities]
                    })
                    return resolved_entities
                else:
                    logger.warning("No entities extracted from response")
                    _observe({"entities_extracted": False})
                    return []
            except ValidationError as ve:
                logger.error(f"Entity validation error: {ve}", exc_info=True)
                _observe({"validation_error": str(ve)})
                return []

        except Exception as e:
            logger.error(f"Entity extraction failed: {e}", exc_info=True)
            _observe({"error": str(e)})
            return []


    @observe(name="resolve_references")
    def resolve_references(self, entity_data: EntityData, session: ChatSession) -> EntityData:
        if session.portfolio_state.current_asset_type and not entity_data.asset_type:
            entity_data.asset_type = session.portfolio_state.current_asset_type

        # Extract recent numerical values from conversation history for reference resolution
        if session.messages:
            recent_amounts = []
            for msg in session.messages[-4:]:
                if msg.role == "assistant":
                    continue
                numbers = re.findall(r'\b\d+(?:\.\d+)?\b', msg.content)
                recent_amounts.extend(numbers)

            # Resolve missing amount/shares from recent conversation
            if not entity_data.amount and not entity_data.shares and recent_amounts:
                if entity_data.asset_type == "stock":
                    entity_data.shares = int(float(recent_amounts[-1]))
                else:
                    entity_data.amount = float(recent_amounts[-1])

        return entity_data
