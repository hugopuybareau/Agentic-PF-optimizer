# backend/app/routers/chat.py

import asyncio
import json
import logging
import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..agents.chat_agent import ChatAgent
from ..agents.portfolio_agent import PortfolioAgent
from ..auth.dependencies import get_current_user_optional
from ..db.models import User
from ..models.portfolio import Portfolio

logger = logging.getLogger(__name__)

# Request/Response models
class ChatMessage(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    message: str
    session_id: str
    ui_hints: dict | None = None
    show_form: bool = False
    form_data: dict | None = None
    portfolio_summary: dict | None = None


class PortfolioSubmission(BaseModel):
    session_id: str
    portfolio: Portfolio
    analyze_immediately: bool = True


# Initialize agents
chat_agent = None
portfolio_agent = None


def get_chat_agent():
    global chat_agent
    if chat_agent is None:
        chat_agent = ChatAgent()
    return chat_agent


def get_portfolio_agent():
    global portfolio_agent
    if portfolio_agent is None:
        portfolio_agent = PortfolioAgent()
    return portfolio_agent


chat_router = APIRouter(prefix="/chat", tags=["chat"])


@chat_router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatMessage,
    current_user: Annotated[User | None, Depends(get_current_user_optional)]
):
    try:
        logger.info(f"Received chat message: session={request.session_id}, user={current_user.id if current_user else 'anonymous'}")
        agent = get_chat_agent()
        session_id = request.session_id or str(uuid.uuid4())
        user_id = str(current_user.id) if current_user else None

        logger.debug(f"Processing message with session_id={session_id}, user_id={user_id}")
        result = agent.process_message(
            session_id=session_id,
            user_message=request.message,
            user_id=user_id
        )

        logger.info(f"Chat message processed successfully for session {session_id}")
        return ChatResponse(**result)

    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


async def stream_chat_response(
    message: str,
    session_id: str,
    user_id: str | None = None
) -> AsyncGenerator[str, None]:
    """
    Stream chat response token by token with configurable delays.
    """
    try:
        agent = get_chat_agent()

        # Process the message to get the complete response
        result = agent.process_message(
            session_id=session_id,
            user_message=message,
            user_id=user_id
        )

        # Extract the response text
        response_text = result.get("message", "")

        # Send initial metadata
        yield f"data: {json.dumps({'type': 'metadata', **{k: v for k, v in result.items() if k != 'message'}})}\n\n"

        # Stream the response text token by token
        words = response_text.split()
        for i, word in enumerate(words):
            # Determine delay based on punctuation
            delay = 0.1 if word.endswith(('.', '!', '?', ':')) else 0.05

            # Send the word
            chunk_data = {
                'type': 'token',
                'content': word + (' ' if i < len(words) - 1 else ''),
                'index': i,
                'is_final': i == len(words) - 1
            }
            yield f"data: {json.dumps(chunk_data)}\n\n"

            # Add delay for natural feel (20-50 tokens/sec)
            await asyncio.sleep(delay)

        # Send completion signal
        yield f"data: {json.dumps({'type': 'complete'})}\n\n"

    except Exception as e:
        logger.error(f"Streaming failed: {e}")
        error_data = {
            'type': 'error',
            'error': str(e)
        }
        yield f"data: {json.dumps(error_data)}\n\n"


@chat_router.post("/message/stream")
async def send_message_stream(
    request: ChatMessage,
    current_user: Annotated[User | None, Depends(get_current_user_optional)]
):
    """
    Send a message to the portfolio chat agent with streaming response.
    Returns server-sent events for progressive text rendering.
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        user_id = str(current_user.id) if current_user else None

        # Return streaming response
        return StreamingResponse(
            stream_chat_response(request.message, session_id, user_id),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control",
            }
        )

    except Exception as e:
        logger.error(f"Streaming chat processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


# @chat_router.post("/submit-portfolio")
# async def submit_portfolio(
#     submission: PortfolioSubmission,
#     current_user: Annotated[User | None, Depends(get_current_user_optional)]
# ):
#     """
#     Submit the portfolio built through chat for analysis.
#     This is called when the user confirms their portfolio in the form.
#     """
#     try:
#         chat_agent = get_chat_agent()
#         portfolio_agent = get_portfolio_agent()

#         # Validate session exists
#         session_portfolio = chat_agent.get_session_portfolio(submission.session_id)
#         if not session_portfolio and not submission.portfolio.assets:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="No portfolio found for this session"
#             )

#         # Use submitted portfolio or session portfolio
#         portfolio_to_analyze = submission.portfolio if submission.portfolio.assets else session_portfolio

#         if not portfolio_to_analyze or not getattr(portfolio_to_analyze, "assets", None):
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="No valid portfolio with assets found for analysis"
#             )

#         response = {
#             "success": True,
#             "session_id": submission.session_id,
#             "portfolio_received": {
#                 "asset_count": len(portfolio_to_analyze.assets),
#                 "asset_types": list(set(asset.type for asset in portfolio_to_analyze.assets))
#             }
#         }

#         # Run analysis if requested
#         if submission.analyze_immediately:
#             analysis_result = portfolio_agent.analyze_portfolio(
#                 portfolio=portfolio_to_analyze,
#                 task_type="digest"
#             )

#             if analysis_result["success"]:
#                 response["analysis"] = {
#                     "digest": analysis_result["response"],
#                     "recommendations": analysis_result["recommendations"],
#                     "risk_alerts": analysis_result["risk_alerts"],
#                     "execution_time": analysis_result["execution_time"]
#                 }
#             else:
#                 response["analysis_error"] = analysis_result.get("error", "Analysis failed")

#         # Clear the chat session after successful submission
#         chat_agent.clear_session(submission.session_id)

#         return response

#     except Exception as e:
#         logger.error(f"Portfolio submission failed: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         ) from e


@chat_router.get("/session/{session_id}")
async def get_session(
    session_id: str,
    current_user: Annotated[User | None, Depends(get_current_user_optional)]
):
    try:
        agent = get_chat_agent()
        session = agent.session_storage.get(session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or expired"
            )

        return {
            "session_id": session.session_id,
            "messages": [
                {
                    "id": f"{i}",
                    "text": msg.content,
                    "isUser": msg.role == "user",
                    "timestamp": msg.timestamp.isoformat()
                }
                for i, msg in enumerate(session.messages)
            ],
            "portfolio": {
                "assets": [asset.model_dump() for asset in session.portfolio_state.assets],
                "asset_count": len(session.portfolio_state.assets),
                "is_complete": session.portfolio_state.is_complete
            } if session.portfolio_state.assets else None,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


# @chat_router.get("/session/{session_id}/portfolio")
# async def get_session_portfolio(
#     session_id: str,
#     current_user: Annotated[User | None, Depends(get_current_user_optional)]
# ):
#     """
#     Get the current portfolio being built in a chat session.
#     Useful for the frontend to sync state.
#     """
#     try:
#         agent = get_chat_agent()
#         portfolio = agent.get_session_portfolio(session_id)

#         if not portfolio:
#             return {
#                 "session_id": session_id,
#                 "portfolio": None,
#                 "asset_count": 0
#             }

#         return {
#             "session_id": session_id,
#             "portfolio": portfolio,
#             "asset_count": len(portfolio.assets),
#             "asset_types": list(set(asset.type for asset in portfolio.assets))
#         }

#     except Exception as e:
#         logger.error(f"Failed to get session portfolio: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         ) from e


@chat_router.delete("/session/{session_id}")
async def clear_session(
    session_id: str,
    current_user: Annotated[User | None, Depends(get_current_user_optional)]
):
    """
    Clear a chat session and start fresh.
    """
    try:
        agent = get_chat_agent()
        agent.clear_session(session_id)

        return {
            "success": True,
            "message": "Session cleared successfully",
            "session_id": session_id
        }

    except Exception as e:
        logger.error(f"Failed to clear session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


# @chat_router.get("/suggestions")
# async def get_asset_suggestions(
#     current_user: Annotated[User | None, Depends(get_current_user_optional)],
#     asset_type: str | None = None
# ):
#     """
#     Get common asset suggestions to help users.
#     """
#     suggestions = {
#         "stock": [
#             {"ticker": "AAPL", "name": "Apple Inc."},
#             {"ticker": "MSFT", "name": "Microsoft Corporation"},
#             {"ticker": "GOOGL", "name": "Alphabet Inc."},
#             {"ticker": "AMZN", "name": "Amazon.com Inc."},
#             {"ticker": "TSLA", "name": "Tesla, Inc."}
#         ],
#         "crypto": [
#             {"symbol": "BTC", "name": "Bitcoin"},
#             {"symbol": "ETH", "name": "Ethereum"},
#             {"symbol": "BNB", "name": "Binance Coin"},
#             {"symbol": "SOL", "name": "Solana"},
#             {"symbol": "ADA", "name": "Cardano"}
#         ],
#         "popular_etfs": [
#             {"ticker": "SPY", "name": "SPDR S&P 500 ETF"},
#             {"ticker": "VOO", "name": "Vanguard S&P 500 ETF"},
#             {"ticker": "QQQ", "name": "Invesco QQQ Trust"},
#             {"ticker": "VTI", "name": "Vanguard Total Stock Market ETF"}
#         ]
#     }

#     if asset_type and asset_type in suggestions:
#         return {
#             "asset_type": asset_type,
#             "suggestions": suggestions[asset_type]
#         }

#     return {
#         "all_suggestions": suggestions,
#         "quick_start_templates": [
#             {
#                 "name": "Conservative Portfolio",
#                 "description": "60% stocks, 40% bonds",
#                 "assets": [
#                     {"type": "stock", "ticker": "VOO", "shares": 100},
#                     {"type": "stock", "ticker": "BND", "shares": 80},
#                     {"type": "cash", "currency": "USD", "amount": 10000}
#                 ]
#             },
#             {
#                 "name": "Growth Portfolio",
#                 "description": "Tech-focused with crypto allocation",
#                 "assets": [
#                     {"type": "stock", "ticker": "QQQ", "shares": 50},
#                     {"type": "stock", "ticker": "TSLA", "shares": 20},
#                     {"type": "crypto", "symbol": "BTC", "amount": 0.1},
#                     {"type": "crypto", "symbol": "ETH", "amount": 2}
#                 ]
#             }
#         ]
#     }
