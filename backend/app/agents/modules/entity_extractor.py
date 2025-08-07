import json
import logging
import re
from typing import Any

from langchain.schema import AIMessage, BaseMessage, HumanMessage
from langchain_openai import AzureChatOpenAI
from langfuse.decorators import langfuse_context, observe

from ...config.prompts import prompt_manager
from ..state.chat_state import ChatSession

logger = logging.getLogger(__name__)


class EntityExtractor:
    def __init__(self, llm: AzureChatOpenAI):
        self.llm = llm

    @observe(name="extract_entities_tool")
    def extract_entities(self, session: ChatSession, user_message: str, intent: str) -> dict[str, Any]:
        if intent not in ["add_asset", "modify_asset", "remove_asset"]:
            return {}

        conversation_history: list[BaseMessage] = []
        for msg in session.messages[-6:]:
            if msg.role == "user":
                conversation_history.append(HumanMessage(content=msg.content))
            else:
                conversation_history.append(AIMessage(content=msg.content))

        messages = prompt_manager.build_messages(
            system_prompt_name="chat-entity-extractor",
            user_content=user_message,
            conversation_history=conversation_history
        )

        try:
            response = self.llm.invoke(messages)
            content = response.content

            if isinstance(content, list):
                content = str(content)
            elif not isinstance(content, str):
                content = str(content)

            entities = self._extract_json_from_llm_response(content)

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

    @observe(name="extract_json_from_llm")
    def _extract_json_from_llm_response(self, content: str) -> dict[str, Any] | None:
        try:
            if isinstance(content, dict | list):
                return content if isinstance(content, dict) else {"items": content}

            if not isinstance(content, str):
                content = str(content)

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
