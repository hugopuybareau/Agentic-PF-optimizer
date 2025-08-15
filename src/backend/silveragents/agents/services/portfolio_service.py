import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from langfuse.decorators import observe
from sqlalchemy import and_
from sqlalchemy.orm import Session

from ...db.models import DBAsset, DBPortfolio, User
from ...models import (
    Asset,
    AssetModification,
    Cash,
    Crypto,
    Mortgage,
    Portfolio,
    PortfolioAction,
    PortfolioActionResult,
    PortfolioSummary,
    RealEstate,
    Stock,
)

logger = logging.getLogger(__name__)


class PortfolioService:
    def __init__(self, db: Session):
        self.db = db
        logger.debug(
            "PortfolioService for DB actions initialized with database session"
        )

    @observe(name="get_or_create_portfolio")
    def get_or_create_portfolio(
        self, user_id: UUID, portfolio_name: str = "Main Portfolio"
    ) -> DBPortfolio:
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"User {user_id} not found")
                raise ValueError(f"User {user_id} not found")

            portfolio = (
                self.db.query(DBPortfolio)
                .filter(
                    and_(
                        DBPortfolio.user_id == user_id,
                        DBPortfolio.name == portfolio_name,
                    )
                )
                .first()
            )

            if not portfolio:
                logger.info(
                    f"Creating new portfolio '{portfolio_name}' for user {user_id}"
                )
                portfolio = DBPortfolio(user_id=user_id, name=portfolio_name)
                self.db.add(portfolio)
                self.db.commit()
                self.db.refresh(portfolio)
                logger.info(f"Portfolio created with ID: {portfolio.id}")
            else:
                logger.debug(
                    f"Found existing portfolio {portfolio.id} for user {user_id}"
                )

            return portfolio

        except Exception as e:
            logger.error(f"Failed to get/create portfolio: {e}", exc_info=True)
            self.db.rollback()
            raise

    @observe(name="add_asset_to_portfolio")
    def add_asset(
        self, user_id: UUID, asset: Asset, portfolio_name: str = "Main Portfolio"
    ) -> PortfolioActionResult:
        try:
            portfolio = self.get_or_create_portfolio(user_id, portfolio_name)

            symbol, asset_type, quantity, meta = self._prepare_asset_data(asset)

            existing_asset = (
                self.db.query(DBAsset)
                .filter(
                    and_(
                        DBAsset.portfolio_id == portfolio.id,
                        DBAsset.symbol == symbol,
                        DBAsset.asset_type == asset_type,
                    )
                )
                .first()
            )

            if existing_asset:
                old_quantity = float(existing_asset.quantity)
                existing_asset.quantity = float(existing_asset.quantity) + quantity
                existing_asset.last_updated = datetime.utcnow()
                action = "updated"
                logger.info(
                    f"Updated {asset_type} {symbol}: {old_quantity} -> {existing_asset.quantity}"
                )
            else:
                db_asset = DBAsset(
                    portfolio_id=portfolio.id,
                    symbol=symbol,
                    asset_type=asset_type,
                    quantity=quantity,
                    meta=meta,
                )
                self.db.add(db_asset)
                action = "added"
                logger.info(f"Added new {asset_type}: {symbol} (quantity: {quantity})")

            self.db.commit()

            result = PortfolioActionResult(
                success=True,
                action=PortfolioAction.ADD_ASSET,
                message=f"Successfully {action} {symbol} to portfolio",
                portfolio_updated=True,
                assets_modified=[
                    AssetModification(
                        asset_type=asset_type,  # type: ignore
                        symbol=symbol,
                        previous_quantity=old_quantity if existing_asset else None,
                        new_quantity=quantity
                        if not existing_asset
                        else float(existing_asset.quantity),
                        action_performed=action,
                        display_text=f"{action.title()} {symbol}: {quantity} {asset_type}",
                    )
                ],
            )

            logger.info(f"Asset operation successful: {result.message}")
            return result

        except Exception as e:
            logger.error(f"Failed to add asset: {e}", exc_info=True)
            self.db.rollback()
            return PortfolioActionResult(
                success=False,
                action=PortfolioAction.ADD_ASSET,
                message=f"Failed to add asset: {e}",
                portfolio_updated=False,
                error=str(e),
            )

    @observe(name="remove_asset_from_portfolio")
    def remove_asset(
        self,
        user_id: UUID,
        symbol: str,
        asset_type: str,
        quantity: float | None = None,
        portfolio_name: str = "Main Portfolio",
    ) -> PortfolioActionResult:
        """
        Remove an asset or reduce its quantity in the portfolio.

        Args:
            user_id: User's UUID
            symbol: Asset symbol/identifier
            asset_type: Type of asset
            quantity: Amount to remove (None = remove all)
            portfolio_name: Target portfolio name

        Returns:
            Result dictionary with success status
        """
        try:
            portfolio = self.get_or_create_portfolio(user_id, portfolio_name)

            asset = (
                self.db.query(DBAsset)
                .filter(
                    and_(
                        DBAsset.portfolio_id == portfolio.id,
                        DBAsset.symbol == symbol,
                        DBAsset.asset_type == asset_type,
                    )
                )
                .first()
            )

            if not asset:
                logger.warning(f"Asset {symbol} not found in portfolio")
                return PortfolioActionResult(
                    success=False,
                    action=PortfolioAction.REMOVE_ASSET,
                    message=f"Asset {symbol} not found in portfolio",
                    portfolio_updated=False,
                )

            current_quantity = float(asset.quantity)

            if quantity is None or quantity >= current_quantity:
                # Remove entire asset
                self.db.delete(asset)
                action = "removed"
                remaining = 0
                logger.info(f"Removed entire position: {symbol}")
            else:
                # Reduce quantity
                asset.quantity = current_quantity - quantity
                asset.last_updated = datetime.utcnow()
                action = "reduced"
                remaining = asset.quantity
                logger.info(f"Reduced {symbol}: {current_quantity} -> {remaining}")

            self.db.commit()

            return PortfolioActionResult(
                success=True,
                action=PortfolioAction.REMOVE_ASSET,
                message=f"Successfully {action} {symbol}",
                portfolio_updated=True,
                assets_modified=[
                    AssetModification(
                        asset_type=asset_type,  # type: ignore
                        symbol=symbol,
                        previous_quantity=current_quantity,
                        new_quantity=remaining,
                        action_performed=action,
                        display_text=f"{action.title()} {symbol}: {current_quantity} -> {remaining} {asset_type}",
                    )
                ],
            )

        except Exception as e:
            logger.error(f"Failed to remove asset: {e}", exc_info=True)
            self.db.rollback()
            return PortfolioActionResult(
                success=False,
                action=PortfolioAction.REMOVE_ASSET,
                message=f"Failed to remove asset: {e}",
                portfolio_updated=False,
                error=str(e),
            )

    @observe(name="update_asset_in_portfolio")
    def update_asset(
        self,
        user_id: UUID,
        symbol: str,
        asset_type: str,
        new_quantity: float,
        portfolio_name: str = "Main Portfolio",
    ) -> PortfolioActionResult:
        """
        Update an asset's quantity in the portfolio.

        Args:
            user_id: User's UUID
            symbol: Asset symbol/identifier
            asset_type: Type of asset
            new_quantity: New quantity to set
            portfolio_name: Target portfolio name

        Returns:
            Result dictionary with success status
        """
        try:
            portfolio = self.get_or_create_portfolio(user_id, portfolio_name)

            asset = (
                self.db.query(DBAsset)
                .filter(
                    and_(
                        DBAsset.portfolio_id == portfolio.id,
                        DBAsset.symbol == symbol,
                        DBAsset.asset_type == asset_type,
                    )
                )
                .first()
            )

            if not asset:
                logger.warning(f"Asset {symbol} not found for update")
                return PortfolioActionResult(
                    success=False,
                    action=PortfolioAction.UPDATE_ASSET,
                    message=f"Asset {symbol} not found in portfolio",
                    portfolio_updated=False,
                )

            old_quantity = float(asset.quantity)
            asset.quantity = new_quantity
            asset.last_updated = datetime.utcnow()

            self.db.commit()

            logger.info(f"Updated {symbol}: {old_quantity} -> {new_quantity}")

            return PortfolioActionResult(
                success=True,
                action=PortfolioAction.UPDATE_ASSET,
                message=f"Successfully updated {symbol} quantity",
                portfolio_updated=True,
                assets_modified=[
                    AssetModification(
                        asset_type=asset_type,  # type: ignore
                        symbol=symbol,
                        previous_quantity=old_quantity,
                        new_quantity=new_quantity,
                        action_performed="updated",
                        display_text=f"Updated {symbol}: {old_quantity} -> {new_quantity} {asset_type}",
                    )
                ],
            )

        except Exception as e:
            logger.error(f"Failed to update asset: {e}", exc_info=True)
            self.db.rollback()
            return PortfolioActionResult(
                success=False,
                action=PortfolioAction.UPDATE_ASSET,
                message=f"Failed to update asset: {e}",
                portfolio_updated=False,
                error=str(e),
            )

    @observe(name="get_portfolio")
    def get_portfolio(
        self, user_id: UUID, portfolio_name: str = "Main Portfolio"
    ) -> Portfolio | None:
        """
        Get user's portfolio as a Portfolio model.

                Args:
            user_id: User's UUID
            portfolio_name: Portfolio name

        Returns:
            Portfolio model or None if not found
        """
        try:
            portfolio = (
                self.db.query(DBPortfolio)
                .filter(
                    and_(
                        DBPortfolio.user_id == user_id,
                        DBPortfolio.name == portfolio_name,
                    )
                )
                .first()
            )

            if not portfolio:
                logger.info(f"No portfolio found for user {user_id}")
                return None

            # Convert DB assets to model assets
            assets = []
            for db_asset in portfolio.assets:
                asset = self._db_asset_to_model(db_asset)
                if asset:
                    assets.append(asset)

            logger.info(
                f"Retrieved portfolio with {len(assets)} assets for user {user_id}"
            )
            return Portfolio(assets=assets)

        except Exception as e:
            logger.error(f"Failed to get portfolio: {e}", exc_info=True)
            return None

    @observe(name="get_portfolio_summary")
    def get_portfolio_summary(
        self, user_id: UUID, portfolio_name: str = "Main Portfolio"
    ) -> PortfolioSummary:
        """
        Get a summary of the user's portfolio.

        Args:
            user_id: User's UUID
            portfolio_name: Portfolio name

        Returns:
            Summary dictionary with portfolio details
        """
        try:
            portfolio = self.get_portfolio(user_id, portfolio_name)

            if not portfolio:
                return PortfolioSummary(
                    exists=False,
                    asset_count=0,
                    assets=[],
                    by_type={},
                    last_updated=None,
                    error=None,
                )

            # Group assets by type
            by_type: dict[str, list[Asset]] = {}
            for asset in portfolio.assets:
                asset_type = asset.type
                if asset_type not in by_type:
                    by_type[asset_type] = []

                by_type[asset_type].append(asset)

            summary = PortfolioSummary(
                exists=True,
                asset_count=len(portfolio.assets),
                assets=portfolio.assets,
                by_type=by_type,
                last_updated=datetime.utcnow().isoformat(),
                error=None,
            )

            logger.debug(f"Generated portfolio summary for user {user_id}")
            return summary

        except Exception as e:
            logger.error(f"Failed to get portfolio summary: {e}", exc_info=True)
            return PortfolioSummary(
                exists=False,
                asset_count=0,
                assets=[],
                by_type={},
                last_updated=None,
                error=str(e),
            )

    def _prepare_asset_data(self, asset: Asset) -> tuple[str, str, float, dict]:
        """Convert Asset model to database fields."""

        if isinstance(asset, Stock):
            return asset.ticker, "stock", asset.shares, {"ticker": asset.ticker}
        elif isinstance(asset, Crypto):
            return asset.symbol, "crypto", asset.amount, {"symbol": asset.symbol}
        elif isinstance(asset, RealEstate):
            return (
                asset.address,
                "real_estate",
                asset.market_value,
                {"address": asset.address, "market_value": asset.market_value},
            )
        elif isinstance(asset, Mortgage):
            return (
                asset.lender,
                "mortgage",
                asset.balance,
                {"lender": asset.lender, "property_address": asset.property_address},
            )
        elif isinstance(asset, Cash):
            return asset.currency, "cash", asset.amount, {"currency": asset.currency}
        else:
            raise ValueError(f"Unknown asset type: {type(asset)}")

    def _db_asset_to_model(self, db_asset: DBAsset) -> Asset | None:
        try:
            quantity = float(db_asset.quantity)
            meta = db_asset.meta or {}

            if db_asset.asset_type == "stock":
                return Stock(ticker=db_asset.symbol, shares=quantity)
            elif db_asset.asset_type == "crypto":
                return Crypto(symbol=db_asset.symbol, amount=quantity)
            elif db_asset.asset_type == "real_estate":
                return RealEstate(address=db_asset.symbol, market_value=quantity)
            elif db_asset.asset_type == "mortgage":
                return Mortgage(
                    lender=db_asset.symbol,
                    balance=quantity,
                    property_address=meta.get("property_address"),
                )
            elif db_asset.asset_type == "cash":
                return Cash(currency=db_asset.symbol, amount=quantity)
            else:
                logger.warning(f"Unknown asset type in DB: {db_asset.asset_type}")
                return None

        except Exception as e:
            logger.error(f"Failed to convert DB asset to model: {e}")
            return None

    def _asset_to_summary_dict(self, asset: Asset) -> dict[str, Any]:
        """Convert Asset model to summary dictionary."""
        if isinstance(asset, Stock):
            return {
                "type": "stock",
                "symbol": asset.ticker,
                "quantity": asset.shares,
                "display": f"{asset.ticker} ({asset.shares} shares)",
            }
        elif isinstance(asset, Crypto):
            return {
                "type": "crypto",
                "symbol": asset.symbol,
                "quantity": asset.amount,
                "display": f"{asset.symbol} ({asset.amount})",
            }
        elif isinstance(asset, RealEstate):
            return {
                "type": "real_estate",
                "address": asset.address,
                "value": asset.market_value,
                "display": f"Property: ${asset.market_value:,.0f}",
            }
        elif isinstance(asset, Mortgage):
            return {
                "type": "mortgage",
                "lender": asset.lender,
                "balance": asset.balance,
                "display": f"Mortgage ({asset.lender}): ${asset.balance:,.0f}",
            }
        elif isinstance(asset, Cash):
            return {
                "type": "cash",
                "currency": asset.currency,
                "amount": asset.amount,
                "display": f"Cash: {asset.currency} ${asset.amount:,.2f}",
            }
        else:
            return {"type": "unknown", "display": str(asset)}
