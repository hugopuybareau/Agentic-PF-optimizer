# type: ignore
import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException

from ..agents.portfolio_agent import PortfolioAgent
from ..models.portfolio import PortfolioRequest

logger = logging.getLogger(__name__)

portfolio_agent = None


def get_portfolio_agent():
    global portfolio_agent
    if portfolio_agent is None:
        portfolio_agent = PortfolioAgent()
    return portfolio_agent


digest_router = APIRouter()


@digest_router.post("/digest")
async def run_digest(request: PortfolioRequest):
    try:
        logger.info(
            f"Received portfolio digest request with {len(request.portfolio.assets)} assets"
        )
        agent = get_portfolio_agent()

        result = agent.analyze_portfolio(
            portfolio=request.portfolio, task_type="digest"
        )

        if not result["success"]:
            logger.error(
                f"Portfolio analysis failed: {result.get('error', 'Unknown error')}"
            )
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {result.get('error', 'Unknown error')}",
            )

        logger.info(
            f"Portfolio digest generated successfully - {result['assets_analyzed']} assets analyzed in {result['execution_time']:.2f}s"
        )
        return {
            "success": True,
            "digest": {
                "summary": result["response"],
                "recommendations": result["recommendations"],
                "risk_alerts": result["risk_alerts"],
                "metadata": {
                    "assets_analyzed": result["assets_analyzed"],
                    "execution_time": result["execution_time"],
                    "errors": result["errors"],
                },
            },
        }

    except Exception as exc:
        logger.error(f"Digest generation failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@digest_router.post("/analyze")
async def analyze_portfolio(request: PortfolioRequest, query: str | None = None):
    try:
        agent = get_portfolio_agent()

        result = agent.analyze_portfolio(
            portfolio=request.portfolio,
            task_type="analyze",
            user_query=query if query is not None else "",
        )

        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {result.get('error', 'Unknown error')}",
            )

        return {
            "success": True,
            "analysis": result["response"],
            "recommendations": result["recommendations"],
            "risk_alerts": result["risk_alerts"],
            "execution_time": result["execution_time"],
        }

    except Exception as exc:
        logger.error(f"Portfolio analysis failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@digest_router.post("/alerts")
async def get_portfolio_alerts(request: PortfolioRequest):
    try:
        agent = get_portfolio_agent()

        result = agent.get_portfolio_alerts(request.portfolio)

        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Alert generation failed: {result.get('error', 'Unknown error')}",
            )

        return {
            "success": True,
            "alerts": result["risk_alerts"],
            "summary": result["response"],
            "urgent_count": len(result["risk_alerts"]),
        }

    except Exception as exc:
        logger.error(f"Alert generation failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@digest_router.post("/schedule-digest")
async def schedule_digest(request: PortfolioRequest, background_tasks: BackgroundTasks):
    try:
        logger.info(
            f"Scheduling background digest for portfolio with {len(request.portfolio.assets)} assets"
        )

        def generate_background_digest():
            logger.info("Starting background digest generation")
            agent = get_portfolio_agent()
            result = agent.create_scheduled_digest(request.portfolio)
            logger.info(
                f"Background digest completed: {result.get('assets_analyzed', 0)} assets analyzed"
            )

        background_tasks.add_task(generate_background_digest)

        logger.info("Digest generation task scheduled successfully")
        return {
            "success": True,
            "message": "Digest generation scheduled",
            "status": "processing",
        }

    except Exception as exc:
        logger.error(f"Failed to schedule digest: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@digest_router.get("/health")
async def agent_health():
    try:
        agent = get_portfolio_agent()

        vector_health = True
        try:
            agent.vector_store.client.get_collections()
        except Exception as e:
            vector_health = False
            logger.info(f"Qdrant not reachable: {e}")

        return {
            "agent_initialized": agent is not None,
            "vector_store_healthy": vector_health,
            "components": {
                "news_search": agent.news_search_tool is not None,
                "classification": agent.classification_tool is not None,
                "analysis": agent.analysis_tool is not None,
                "summarizer": agent.summarizer_tool is not None,
            },
        }

    except Exception as exc:
        return {"healthy": False, "error": str(exc)}
