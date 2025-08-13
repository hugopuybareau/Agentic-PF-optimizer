import asyncio
import json
import logging
import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..agents.chat_agent import ChatAgent
from ..agents.portfolio_agent import PortfolioAgent
from ..agents.services import PortfolioService
from ..auth.dependencies import get_current_user_optional
from ..db.base import get_db
from ..db.models import User
from ..models import (
    ChatConfirmation,
    ChatMessageRequest,
    ChatResponse,
    PortfolioSubmission,
)

logger = logging.getLogger(__name__)

# Initialize agents (in production, use dependency injection)
chat_agent = None
portfolio_agent = None

def get_chat_agent(db: Session | None = None):
    global chat_agent
    if chat_agent is None:
        chat_agent = ChatAgent(db)
    return chat_agent

def get_portfolio_agent():
    global portfolio_agent
    if portfolio_agent is None:
        portfolio_agent = PortfolioAgent()
    return portfolio_agent

chat_router = APIRouter(prefix="/chat", tags=["chat"])

@chat_router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatMessageRequest,
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
    db: Annotated[Session, Depends(get_db)]
):
    try:
        logger.info(f"Received chat message: session={request.session_id}, user={current_user.id if current_user else 'anonymous'}")

        agent = get_chat_agent(db)
        session_id = request.session_id or str(uuid.uuid4())
        user_id = str(current_user.id) if current_user else None

        logger.debug(f"Processing message with session_id={session_id}, user_id={user_id}")

        result = agent.process_message(
            session_id=session_id,
            user_message=request.message,
            user_id=user_id,
            _db=db
        )

        logger.info(f"Chat message processed successfully for session {session_id}")
        return ChatResponse(**result)

    except Exception as e:
        logger.error(f"Chat processing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@chat_router.post("/confirm", response_model=dict)
async def confirm_action(
    request: ChatConfirmation,
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
    db: Annotated[Session, Depends(get_db)]
):
    try:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required for portfolio modifications"
            )

        logger.info(f"Processing confirmation {request.confirmation_id} for session {request.session_id}")

        agent = get_chat_agent(db)

        result = agent.process_confirmation(
            confirmation_id=request.confirmation_id,
            confirmed=request.confirmed,
            user_id=str(current_user.id),
            db=db
        )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message if result.message else "Confirmation failed"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Confirmation processing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


async def stream_chat_response(
    message: str,
    session_id: str,
    user_id: str | None = None,
    db: Session | None = None
) -> AsyncGenerator[str, None]:
    try:
        agent = get_chat_agent(db)

        result = agent.process_message(
            session_id=session_id,
            user_message=message,
            user_id=user_id,
            _db=db
        )

        response_text = result.get("message", "")

        metadata = {k: v for k, v in result.items() if k != "message"}
        metadata["type"] = "metadata"
        yield f"data: {json.dumps(metadata)}\n\n"

        words = response_text.split()
        for i, word in enumerate(words):
            delay = 0.1 if word.endswith(('.', '!', '?', ':')) else 0.05

            chunk_data = {
                'type': 'token',
                'content': word + (' ' if i < len(words) - 1 else ''),
                'index': i,
                'is_final': i == len(words) - 1
            }
            yield f"data: {json.dumps(chunk_data)}\n\n"

            await asyncio.sleep(delay)

        yield f"data: {json.dumps({'type': 'complete'})}\n\n"

    except Exception as e:
        logger.error(f"Streaming failed: {e}")
        error_data = {
            'type': 'error',
            'error': str(e)
        }
        yield f"data: {json.dumps(error_data)}\n\n"


@chat_router.post("/message/stream", response_class=StreamingResponse)
async def send_message_stream(
    request: ChatMessageRequest,
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Send a message to the portfolio chat agent with streaming response.

    Returns server-sent events for progressive text rendering.
    Includes confirmation requests in the metadata if portfolio actions are detected.
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        user_id = str(current_user.id) if current_user else None

        # Return streaming response
        return StreamingResponse(
            stream_chat_response(request.message, session_id, user_id, db),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control",
                "X-Accel-Buffering": "no"
            }
        )

    except Exception as e:
        logger.error(f"Streaming chat processing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@chat_router.post("/submit-portfolio")
async def submit_portfolio(
    submission: PortfolioSubmission,
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
    db: Annotated[Session, Depends(get_db)]
):
    try:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to save portfolio"
            )

        chat_agent = get_chat_agent(db)
        portfolio_agent = get_portfolio_agent()
        portfolio_service = PortfolioService(db)

        session_portfolio = chat_agent.get_session_portfolio(submission.session_id)
        if not session_portfolio and not submission.portfolio.assets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No portfolio found for this session"
            )

        portfolio_to_save = submission.portfolio if submission.portfolio.assets else session_portfolio

        if not portfolio_to_save or not portfolio_to_save.assets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid portfolio with assets found"
            )

        saved_count = 0
        failed_count = 0

        for asset in portfolio_to_save.assets:
            result = portfolio_service.add_asset(
                user_id=current_user.id,
                asset=asset
            )
            if result.success:
                saved_count += 1
            else:
                failed_count += 1
                logger.error(f"Failed to save asset: {asset}")

        response = {
            "success": saved_count > 0,
            "session_id": submission.session_id,
            "portfolio_saved": {
                "assets_saved": saved_count,
                "assets_failed": failed_count,
                "total_assets": len(portfolio_to_save.assets)
            }
        }

        # Run analysis if requested and save was successful
        if submission.analyze_immediately and saved_count > 0:
            analysis_result = portfolio_agent.analyze_portfolio(
                portfolio=portfolio_to_save,
                task_type="digest"
            )

            if analysis_result["success"]:
                response["analysis"] = {
                    "digest": analysis_result["response"],
                    "recommendations": analysis_result["recommendations"],
                    "risk_alerts": analysis_result["risk_alerts"],
                    "execution_time": analysis_result["execution_time"]
                }
            else:
                response["analysis_error"] = analysis_result.get("error", "Analysis failed")

        # Clear the chat session after successful submission
        if saved_count > 0:
            chat_agent.clear_session(submission.session_id)
            logger.info(f"Portfolio saved and session cleared: {submission.session_id}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Portfolio submission failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e

@chat_router.get("/session/{session_id}")
async def get_session(
    session_id: str,
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Get the current chat session including messages and portfolio state.

    Also returns the user's saved portfolio from the database if authenticated.
    """
    try:
        agent = get_chat_agent(db)
        session = agent.session_storage.get(session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or expired"
            )

        response = {
            "session_id": session.session_id,
            "messages": [
                {
                    "id": f"{i}",
                    "text": msg.content,
                    "isUser": msg.role == "user",
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.metadata
                }
                for i, msg in enumerate(session.messages)
            ],
            "in_memory_portfolio": {
                "assets": [asset.model_dump() for asset in session.portfolio_state.assets],
                "asset_count": len(session.portfolio_state.assets),
                "is_complete": session.portfolio_state.is_complete
            } if session.portfolio_state.assets else None,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat()
        }

        # Add saved portfolio if user is authenticated
        if current_user:
            service = PortfolioService(db)
            saved_portfolio = service.get_portfolio_summary(current_user.id)
            response["saved_portfolio"] = saved_portfolio

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e

@chat_router.delete("/session/{session_id}")
async def clear_session(
    session_id: str,
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
    db: Annotated[Session, Depends(get_db)]
):
    """Clear a chat session and start fresh."""
    try:
        agent = get_chat_agent(db)
        agent.clear_session(session_id)

        return {
            "success": True,
            "message": "Session cleared successfully",
            "session_id": session_id
        }

    except Exception as e:
        logger.error(f"Failed to clear session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e
