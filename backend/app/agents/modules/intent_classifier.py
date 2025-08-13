import logging

from langchain.schema import AIMessage, BaseMessage, HumanMessage
from langchain_openai import AzureChatOpenAI
from langfuse.decorators import langfuse_context, observe
from pydantic import ValidationError

from ...config.prompts import prompt_manager
from ...models import ChatSession, Intent, IntentClassificationResponse

logger = logging.getLogger(__name__)


class IntentClassifier:
    def __init__(self, llm: AzureChatOpenAI):
        self.llm = llm

    @observe(name="classify_intent_tool")
    def classify_intent(self, session: ChatSession, user_message: str) -> Intent:
        conversation_history: list[BaseMessage] = []
        for msg in session.messages[-10:]:
            conversation_history.append(
                HumanMessage(content=msg.content) if msg.role == "user"
                else AIMessage(content=msg.content)
            )

        messages = prompt_manager.build_messages(
            system_prompt_name="chat-intent-classifier",
            user_content=user_message,
            conversation_history=conversation_history
        )

        def _observe(extra: dict):
            langfuse_context.update_current_observation(
                metadata={
                    "session_id": session.session_id,
                    "message_count": len(session.messages),
                    "user_message": user_message,
                    **extra
                    }
                )

        try:
            raw_response = self.llm.with_structured_output(IntentClassificationResponse).invoke(messages, timeout=8)
            try:
                intent_response = IntentClassificationResponse.model_validate(raw_response)
                intent = intent_response.intent
            except ValidationError as ve:
                logger.error(f"Intent validation error: {ve}", exc_info=True)
                _observe({"validation_error": str(ve)})
                intent = Intent.UNCLEAR

            _observe({"intent": intent.value})

            return intent

        except Exception as e:
            logger.error(f"Intent classification failed: {e}", exc_info=True)
            _observe({"error": str(e)})
            return Intent.UNCLEAR
