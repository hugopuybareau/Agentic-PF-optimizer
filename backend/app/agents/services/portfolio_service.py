import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from langfuse.decorators import observe
from sqlalchemy import and_
from sqlalchemy.orm import Session

from ...db.models import Asset as DBAsset, Portfolio as DBPortfolio, User
from ...models import Asset, Cash, Crypto, Mortgage, Portfolio, RealEstate, Stock

logger = logging.getLogger(__name__)


class PortfolioService:
    """Service layer for portfolio operations with database persistence."""

    def __init__(self, db: Session):
        self.db = db
        logger.debug("PortfolioService initialized with database session")

    @observe(name="get_or_create_portfolio")
    def get_or_create_portfolio(
        self,
        user_id: UUID,
        portfolio_name: str = "Main Portfolio"
    ) -> DBPortfolio:
        """
        Get existing portfolio or create a new one for the user.

        Args:
            user_id: User's UUID
            portfolio_name: Name of the portfolio

        Returns:
            Database portfolio object
        """
        try:
            # Check if user exists
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"User {user_id} not found")
                raise ValueError(f"User {user_id} not found")

            # Get or create portfolio
            portfolio = (
                self.db.query(DBPortfolio)
                .filter(
                    and_(
                        DBPortfolio.user_id == user_id,
                        DBPortfolio.name == portfolio_name
                    )
                )
                .first()
            )

            if not portfolio:
                logger.info(f"Creating new portfolio '{portfolio_name}' for user {user_id}")
                portfolio = DBPortfolio(
                    user_id=user_id,
                    name=portfolio_name
                )
                self.db.add(portfolio)
                self.db.commit()
                self.db.refresh(portfolio)
                logger.info(f"Portfolio created with ID: {portfolio.id}")
            else:
                logger.debug(f"Found existing portfolio {portfolio.id} for user {user_id}")

            return portfolio

        except Exception as e:
            logger.error(f"Failed to get/create portfolio: {e}", exc_info=True)
            self.db.rollback()
            raise

    @observe(name="add_asset_to_portfolio")
    def add_asset(
        self,
        user_id: UUID,
        asset: Asset,
        portfolio_name: str = "Main Portfolio"
    ) -> dict[str, Any]:
        """
        Add an asset to the user's portfolio.

        Args:
            user_id: User's UUID
            asset: Asset object to add
            portfolio_name: Target portfolio name

        Returns:
            Result dictionary with success status and details
        """
        try:
            portfolio = self.get_or_create_portfolio(user_id, portfolio_name)

            # Prepare asset data
            symbol, asset_type, quantity, meta = self._prepare_asset_data(asset)

            # Check if asset already exists
            existing_asset = (
                self.db.query(DBAsset)
                .filter(
                    and_(
                        DBAsset.portfolio_id == portfolio.id,
                        DBAsset.symbol == symbol,
                        DBAsset.asset_type == asset_type
                    )
                )
                .first()
            )

            if existing_asset:
                # Update existing asset quantity
                old_quantity = float(existing_asset.quantity)
                existing_asset.quantity = float(existing_asset.quantity) + quantity
                existing_asset.last_updated = datetime.utcnow()
                action = "updated"
                logger.info(
                    f"Updated {asset_type} {symbol}: {old_quantity} -> {existing_asset.quantity}"
                )
            else:
                # Create new asset
                db_asset = DBAsset(
                    portfolio_id=portfolio.id,
                    symbol=symbol,
                    asset_type=asset_type,
                    quantity=quantity,
                    meta=meta
                )
                self.db.add(db_asset)
                action = "added"
                logger.info(f"Added new {asset_type}: {symbol} (quantity: {quantity})")

            self.db.commit()

            result = {
                "success": True,
                "action": action,
                "asset": {
                    "symbol": symbol,
                    "type": asset_type,
                    "quantity": quantity
                },
                "portfolio_id": str(portfolio.id),
                "message": f"Successfully {action} {symbol} to portfolio"
            }

            logger.info(f"Asset operation successful: {result['message']}")
            return result

        except Exception as e:
            logger.error(f"Failed to add asset: {e}", exc_info=True)
            self.db.rollback()
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to add asset: {e}"
            }

    @observe(name="remove_asset_from_portfolio")
    def remove_asset(
        self,
        user_id: UUID,
        symbol: str,
        asset_type: str,
        quantity: float | None = None,
        portfolio_name: str = "Main Portfolio"
    ) -> dict[str, Any]:
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
                        DBAsset.asset_type == asset_type
                    )
                )
                .first()
            )

            if not asset:
                logger.warning(f"Asset {symbol} not found in portfolio")
                return {
                    "success": False,
                    "message": f"Asset {symbol} not found in portfolio"
                }

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
                remaining = float(asset.quantity)
                logger.info(f"Reduced {symbol}: {current_quantity} -> {remaining}")

            self.db.commit()

            return {
                "success": True,
                "action": action,
                "asset": {
                    "symbol": symbol,
                    "type": asset_type,
                    "previous_quantity": current_quantity,
                    "removed_quantity": quantity or current_quantity,
                    "remaining_quantity": remaining
                },
                "portfolio_id": str(portfolio.id),
                "message": f"Successfully {action} {symbol}"
            }

        except Exception as e:
            logger.error(f"Failed to remove asset: {e}", exc_info=True)
            self.db.rollback()
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to remove asset: {e}"
            }

    @observe(name="update_asset_in_portfolio")
    def update_asset(
        self,
        user_id: UUID,
        symbol: str,
        asset_type: str,
        new_quantity: float,
        portfolio_name: str = "Main Portfolio"
    ) -> dict[str, Any]:
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
                        DBAsset.asset_type == asset_type
                    )
                )
                .first()
            )

            if not asset:
                logger.warning(f"Asset {symbol} not found for update")
                return {
                    "success": False,
                    "message": f"Asset {symbol} not found in portfolio"
                }

            old_quantity = float(asset.quantity)
            asset.quantity = new_quantity
            asset.last_updated = datetime.utcnow()

            self.db.commit()

            logger.info(f"Updated {symbol}: {old_quantity} -> {new_quantity}")

            return {
                "success": True,
                "action": "updated",
                "asset": {
                    "symbol": symbol,
                    "type": asset_type,
                    "previous_quantity": old_quantity,
                    "new_quantity": new_quantity
                },
                "portfolio_id": str(portfolio.id),
                "message": f"Successfully updated {symbol} quantity"
            }

        except Exception as e:
            logger.error(f"Failed to update asset: {e}", exc_info=True)
            self.db.rollback()
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to update asset: {e}"
            }

    @observe(name="get_portfolio")
    def get_portfolio(
        self,
        user_id: UUID,
        portfolio_name: str = "Main Portfolio"
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
                        DBPortfolio.name == portfolio_name
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

            logger.info(f"Retrieved portfolio with {len(assets)} assets for user {user_id}")
            return Portfolio(assets=assets)

        except Exception as e:
            logger.error(f"Failed to get portfolio: {e}", exc_info=True)
            return None

    @observe(name="get_portfolio_summary")
    def get_portfolio_summary(
        self,
        user_id: UUID,
        portfolio_name: str = "Main Portfolio"
    ) -> dict[str, Any]:
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
                return {
                    "exists": False,
                    "asset_count": 0,
                    "assets": []
                }

            # Group assets by type
            by_type: dict[str, list[dict]] = {}
            for asset in portfolio.assets:
                asset_type = asset.type
                if asset_type not in by_type:
                    by_type[asset_type] = []

                asset_dict = self._asset_to_summary_dict(asset)
                by_type[asset_type].append(asset_dict)

            summary = {
                "exists": True,
                "asset_count": len(portfolio.assets),
                "assets": [self._asset_to_summary_dict(a) for a in portfolio.assets],
                "by_type": by_type,
                "last_updated": datetime.utcnow().isoformat()
            }

            logger.debug(f"Generated portfolio summary for user {user_id}")
            return summary

        except Exception as e:
            logger.error(f"Failed to get portfolio summary: {e}", exc_info=True)
            return {
                "exists": False,
                "error": str(e)
            }

    def _prepare_asset_data(self, asset: Asset) -> tuple[str, str, float, dict]:
        """Convert Asset model to database fields."""

        if isinstance(asset, Stock):
            return asset.ticker, "stock", asset.shares, {"ticker": asset.ticker}
        elif isinstance(asset, Crypto):
            return asset.symbol, "crypto", asset.amount, {"symbol": asset.symbol}
        elif isinstance(asset, RealEstate):
            return asset.address, "real_estate", asset.market_value, {
                "address": asset.address,
                "market_value": asset.market_value
            }
        elif isinstance(asset, Mortgage):
            return asset.lender, "mortgage", asset.balance, {
                "lender": asset.lender,
                "property_address": asset.property_address
            }
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
                return RealEstate(
                    address=db_asset.symbol,
                    market_value=quantity
                )
            elif db_asset.asset_type == "mortgage":
                return Mortgage(
                    lender=db_asset.symbol,
                    balance=quantity,
                    property_address=meta.get("property_address")
                )
            elif db_asset.asset_type == "cash":
                return Cash(
                    currency=db_asset.symbol,
                    amount=quantity
                )
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
                "display": f"{asset.ticker} ({asset.shares} shares)"
            }
        elif isinstance(asset, Crypto):
            return {
                "type": "crypto",
                "symbol": asset.symbol,
                "quantity": asset.amount,
                "display": f"{asset.symbol} ({asset.amount})"
            }
        elif isinstance(asset, RealEstate):
            return {
                "type": "real_estate",
                "address": asset.address,
                "value": asset.market_value,
                "display": f"Property: ${asset.market_value:,.0f}"
            }
        elif isinstance(asset, Mortgage):
            return {
                "type": "mortgage",
                "lender": asset.lender,
                "balance": asset.balance,
                "display": f"Mortgage ({asset.lender}): ${asset.balance:,.0f}"
            }
        elif isinstance(asset, Cash):
            return {
                "type": "cash",
                "currency": asset.currency,
                "amount": asset.amount,
                "display": f"Cash: {asset.currency} ${asset.amount:,.2f}"
            }
        else:
            return {"type": "unknown", "display": str(asset)}
