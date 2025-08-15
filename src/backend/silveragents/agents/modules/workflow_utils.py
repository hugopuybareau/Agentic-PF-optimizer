import logging

from langfuse.decorators import langfuse_context, observe

from ...models import ChatAgentState

logger = logging.getLogger(__name__)


class WorkflowUtils:
    @observe(name="should_show_form")
    def should_show_form(self, state: ChatAgentState) -> str:
        decision = "continue"
        reason = "not_ready"

        if state.confirmation_request:
            decision = "show_form"
            reason = "confirmation_ready"
        else:
            if state.entities:
                keywords = [
                    "done",
                    "finish",
                    "complete",
                    "review",
                    "that's all",
                    "that's it",
                    "show me",
                    "see my",
                ]
                user_msg = state.user_message
                user_msg_str = str(user_msg)
                if any(keyword in user_msg_str.lower() for keyword in keywords):
                    decision = "show_form"
                    reason = "user_indicated_completion"

        langfuse_context.update_current_observation(
            metadata={
                "decision": decision,
                "reason": reason,
                "entity_count": len(state.entities) if state.entities else 0,
                "has_confirmation_request": bool(state.confirmation_request),
            }
        )

        return decision
