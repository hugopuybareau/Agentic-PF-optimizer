import logging

from langfuse.decorators import langfuse_context, observe

from ...models import ChatAgentState

logger = logging.getLogger(__name__)


class WorkflowUtils:

    @observe(name="should_show_form")
    def should_show_form(self, state: ChatAgentState) -> str:
        session = state["session"]

        decision = "continue"
        reason = "not_ready"

        if session.portfolio_state.is_complete:
            decision = "show_form"
            reason = "portfolio_complete"
        elif len(session.portfolio_state.assets) >= 2:
            keywords = ["done", "finish", "complete", "review", "that's all", "that's it", "show me", "see my"]
            user_msg_lower = state["user_message"].lower()
            if any(keyword in user_msg_lower for keyword in keywords):
                decision = "show_form"
                reason = "user_indicated_completion"

        langfuse_context.update_current_observation(
            metadata={
                "decision": decision,
                "reason": reason,
                "asset_count": len(session.portfolio_state.assets)
            }
        )

        return decision
