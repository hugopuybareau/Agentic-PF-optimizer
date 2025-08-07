import logging

from langchain.schema import AIMessage, BaseMessage, HumanMessage
from langchain_openai import AzureChatOpenAI
from langfuse.decorators import langfuse_context, observe

from ...config.prompts import prompt_manager
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
            response = self.llm.invoke(messages)
            intent_text = response.content

            if isinstance(intent_text, list):
                intent_text = next((item for item in intent_text if isinstance(item, str)), "")
            elif hasattr(intent_text, 'content') and not isinstance(intent_text, str):
                intent_text = intent_text.content

            intent = intent_text.strip().lower()

            langfuse_context.update_current_observation(
                metadata={
                    "intent": intent,
                    "session_id": session.session_id,
                    "message_count": len(session.messages)
                }
            )

            return intent

        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            langfuse_context.update_current_observation(
                metadata={"error": str(e)}
            )
            return "unclear"
