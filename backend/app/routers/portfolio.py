# backend/app/routers/portfolio.py

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..agents.services import PortfolioService
from ..auth.dependencies import get_current_user
from ..db.base import get_db
from ..db.models import User
from ..models import (
    AddAssetRequest,
    Portfolio,
    PortfolioAction,
    PortfolioActionResult,
    PortfolioSnapshot,
    RemoveAssetRequest,
    UpdateAssetRequest,
)

logger = logging.getLogger(__name__)

portfolio_router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@portfolio_router.get("/", response_model=Portfolio)
async def get_portfolio(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    portfolio_name: str = Query(default="Main Portfolio")
):
    """
    Get the current user's portfolio.

    Returns the portfolio with all assets or empty portfolio if none exists.
    """
    try:
        logger.info(f"Getting portfolio for user {current_user.id}")
        service = PortfolioService(db)
        portfolio = service.get_portfolio(current_user.id, portfolio_name)

        if not portfolio:
            logger.info("No portfolio found, returning empty portfolio")
            return Portfolio(assets=[])

        logger.info(f"Retrieved portfolio with {len(portfolio.assets)} assets")
        return portfolio

    except Exception as e:
        logger.error(f"Failed to get portfolio: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@portfolio_router.get("/summary")
async def get_portfolio_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    portfolio_name: str = Query(default="Main Portfolio")
):
    """
    Get a summary of the user's portfolio.

    Returns aggregated data about the portfolio including asset counts and types.
    """
    try:
        logger.info(f"Getting portfolio summary for user {current_user.id}")
        service = PortfolioService(db)
        summary = service.get_portfolio_summary(current_user.id, portfolio_name)

        logger.info(f"Portfolio summary: {summary.get('asset_count', 0)} assets")
        return summary

    except Exception as e:
        logger.error(f"Failed to get portfolio summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@portfolio_router.post("/assets", response_model=PortfolioActionResult)
async def add_asset(
    request: AddAssetRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Add an asset to the portfolio.

    If the asset already exists, its quantity will be increased.
    """
    try:
        logger.info(f"Adding asset to portfolio for user {current_user.id}: {request.asset}")
        service = PortfolioService(db)
        result = service.add_asset(
            user_id=current_user.id,
            asset=request.asset,
            portfolio_name=request.portfolio_name
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Failed to add asset")
            )

        # Get updated portfolio summary
        portfolio_summary = service.get_portfolio_summary(current_user.id, request.portfolio_name)

        return PortfolioActionResult(
            success=True,
            action=PortfolioAction.ADD_ASSET,
            message=result["message"],
            portfolio_updated=True,
            assets_affected=[result["asset"]],
            portfolio_summary=portfolio_summary
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update asset: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@portfolio_router.get("/snapshot", response_model=PortfolioSnapshot)
async def get_portfolio_snapshot(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    portfolio_name: str = Query(default="Main Portfolio")
):
    """
    Get a complete snapshot of the portfolio.

    Returns detailed information about the portfolio including metadata.
    """
    try:
        logger.info(f"Getting portfolio snapshot for user {current_user.id}")
        service = PortfolioService(db)

        # Get or create portfolio to ensure it exists
        db_portfolio = service.get_or_create_portfolio(current_user.id, portfolio_name)

        # Get portfolio data
        portfolio = service.get_portfolio(current_user.id, portfolio_name)
        summary = service.get_portfolio_summary(current_user.id, portfolio_name)

        assets = []
        asset_types = set()

        if portfolio:
            for asset in portfolio.assets:
                asset_dict = service._asset_to_summary_dict(asset)
                assets.append(asset_dict)
                asset_types.add(asset.type)

        snapshot = PortfolioSnapshot(
            portfolio_id=db_portfolio.id,
            user_id=current_user.id,
            name=portfolio_name,
            assets=assets,
            total_assets=len(assets),
            asset_types=list(asset_types),
            last_updated=db_portfolio.last_updated or db_portfolio.created_at,
            metadata={
                "summary": summary,
                "created_at": db_portfolio.created_at.isoformat()
            }
        )

        logger.info(f"Portfolio snapshot generated: {snapshot.total_assets} assets")
        return snapshot

    except Exception as e:
        logger.error(f"Failed to get portfolio snapshot: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@portfolio_router.delete("/clear", response_model=PortfolioActionResult)
async def clear_portfolio(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    portfolio_name: str = Query(default="Main Portfolio"),
    confirm: bool = Query(default=False, description="Safety confirmation flag")
):
    """
    Clear all assets from the portfolio.
    Requires confirm=true parameter for safety.
    """
    try:
        if not confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please set confirm=true to clear the portfolio"
            )

        logger.info(f"Clearing portfolio for user {current_user.id}")
        service = PortfolioService(db)

        # Get current portfolio for reporting
        portfolio = service.get_portfolio(current_user.id, portfolio_name)

        if not portfolio or not portfolio.assets:
            return PortfolioActionResult(
                success=True,
                action=PortfolioAction.CLEAR_PORTFOLIO,
                message="Portfolio is already empty",
                portfolio_updated=False
            )

        removed_assets = []

        # Remove each asset
        for asset in portfolio.assets:
            symbol, asset_type, _, _ = service._prepare_asset_data(asset)
            result = service.remove_asset(
                user_id=current_user.id,
                symbol=symbol,
                asset_type=asset_type,
                portfolio_name=portfolio_name
            )
            if result["success"]:
                removed_assets.append(result["asset"])

        logger.info(f"Cleared {len(removed_assets)} assets from portfolio")

        return PortfolioActionResult(
            success=True,
            action=PortfolioAction.CLEAR_PORTFOLIO,
            message=f"Successfully cleared {len(removed_assets)} assets from portfolio",
            portfolio_updated=True,
            assets_affected=removed_assets,
            portfolio_summary={"asset_count": 0, "assets": []}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear portfolio: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@portfolio_router.delete("/assets", response_model=PortfolioActionResult)
async def remove_asset(
    request: RemoveAssetRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Remove an asset from the portfolio.

    If quantity is specified, only that amount is removed.
    If quantity is None, the entire position is removed.
    """
    try:
        logger.info(f"Removing asset from portfolio for user {current_user.id}: {request.symbol}")
        service = PortfolioService(db)
        result = service.remove_asset(
            user_id=current_user.id,
            symbol=request.symbol,
            asset_type=request.asset_type,
            quantity=request.quantity,
            portfolio_name=request.portfolio_name
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Failed to remove asset")
            )

        # Get updated portfolio summary
        portfolio_summary = service.get_portfolio_summary(current_user.id, request.portfolio_name)

        return PortfolioActionResult(
            success=True,
            action=PortfolioAction.REMOVE_ASSET,
            message=result["message"],
            portfolio_updated=True,
            assets_affected=[result["asset"]],
            portfolio_summary=portfolio_summary
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove asset: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@portfolio_router.put("/assets", response_model=PortfolioActionResult)
async def update_asset(
    request: UpdateAssetRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Update an asset's quantity in the portfolio.

    Sets the asset to the specified new quantity.
    """
    try:
        logger.info(f"Updating asset in portfolio for user {current_user.id}: {request.symbol}")
        service = PortfolioService(db)
        result = service.update_asset(
            user_id=current_user.id,
            symbol=request.symbol,
            asset_type=request.asset_type,
            new_quantity=request.new_quantity,
            portfolio_name=request.portfolio_name
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Failed to update asset")
            )

        # Get updated portfolio summary
        portfolio_summary = service.get_portfolio_summary(current_user.id, request.portfolio_name)

        return PortfolioActionResult(
            success=True,
            action=PortfolioAction.UPDATE_ASSET,
            message=result["message"],
            portfolio_updated=True,
            assets_affected=[result["asset"]],
            portfolio_summary=portfolio_summary
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update asset: {e}", exc_info=True)
