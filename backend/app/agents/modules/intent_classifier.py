import logging

from langchain.schema import AIMessage, BaseMessage, HumanMessage
from langchain_openai import AzureChatOpenAI
from langfuse.decorators import langfuse_context, observe
from pydantic import ValidationError

from ...config.prompts import prompt_manager
from ..response_models import IntentClassificationResponse
from ..state.chat_state import ChatSession

logger = logging.getLogger(__name__)


class IntentClassifier:
    def __init__(self, llm: AzureChatOpenAI):
        self.llm = llm

    @observe(name="classify_intent_tool")
    def classify_intent(self, session: ChatSession, user_message: str) -> str:
        conversation_history: list[BaseMessage] = []
        for msg in session.messages[-10:]:
            if msg.role == "user":
                conversation_history.append(HumanMessage(content=msg.content))
            else:
                conversation_history.append(AIMessage(content=msg.content))

        messages = prompt_manager.build_messages(
            system_prompt_name="chat-intent-classifier",
            user_content=user_message,
            conversation_history=conversation_history
        )

        try:
            raw_response = self.llm.with_structured_output(IntentClassificationResponse).invoke(messages, timeout=8)
            try:
                intent_response = IntentClassificationResponse.model_validate(raw_response)
                intent = intent_response.intent
            except ValidationError as ve:
                logger.error(f"Intent validation error: {ve}", exc_info=True)
                langfuse_context.update_current_observation(
                    metadata={
                        "error": f"Validation error: {ve}",
                        "user_message": user_message,
                        "session_id": session.session_id,
                    }
                )
                intent = "unclear"

            langfuse_context.update_current_observation(
                metadata={
                    "intent": intent,
                    "session_id": session.session_id,
                    "message_count": len(session.messages)
                }
            )

            return intent

        except Exception as e:
            logger.error(f"Intent classification failed: {e}", exc_info=True)
            langfuse_context.update_current_observation(
                metadata={
                    "error": f"Exception: {e}",
                    "user_message": user_message,
                    "session_id": session.session_id
                }
            )
            return "unclear"
