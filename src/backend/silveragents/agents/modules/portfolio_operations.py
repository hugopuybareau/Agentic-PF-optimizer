import logging
from typing import Any

from langfuse.decorators import langfuse_context, observe

from ...models.assets import Asset, Cash, Crypto, Mortgage, RealEstate, Stock
from ...models import ChatSession, Intent

logger = logging.getLogger(__name__)


class PortfolioOperations:

    @observe(name="update_portfolio_tool")
    def update_portfolio(self, session: ChatSession, entities: dict[str, Any], intent: Intent) -> dict[str, Any]:
        ui_hints = {}

        if intent == Intent.ADD_ASSET and entities:
            try:
                asset = self._create_asset_from_entities(entities)
                if asset:
                    session.portfolio_state.assets.append(asset)
                    session.portfolio_state.current_asset_type = None
                    session.portfolio_state.current_asset_data = {}
                    ui_hints["asset_added"] = True

                    logger.info(f"Added asset: {asset}")
                    langfuse_context.update_current_observation(
                        metadata={
                            "asset_added": True,
                            "asset_type": asset.type,
                            "total_assets": len(session.portfolio_state.assets)
                        }
                    )
                else:
                    session.portfolio_state.current_asset_type = entities.get("type")
                    session.portfolio_state.current_asset_data.update(entities)
                    ui_hints["needs_more_info"] = True

            except Exception as e:
                logger.error(f"Failed to create asset: {e}")
                session.portfolio_state.validation_errors.append(str(e))

        elif intent == Intent.REMOVE_ASSET and entities:
            identifier = entities.get("ticker") or entities.get("symbol") or entities.get("address")
            if identifier:
                original_count = len(session.portfolio_state.assets)
                session.portfolio_state.assets = [
                    a for a in session.portfolio_state.assets
                    if not self._asset_matches(a, identifier)
                ]
                if len(session.portfolio_state.assets) < original_count:
                    ui_hints["removed_asset"] = True
                    logger.info(f"Removed asset with identifier: {identifier}")

        elif intent == Intent.COMPLETE_PORTFOLIO:
            session.portfolio_state.is_complete = True
            ui_hints["portfolio_complete"] = True

        return {"ui_hints": ui_hints}

    @observe(name="create_asset")
    def _create_asset_from_entities(self, entities: dict) -> Asset | None:
        asset_type = entities.get("type", "").lower()

        try:
            if asset_type == "stock":
                if entities.get("ticker") and entities.get("shares"):
                    return Stock(
                        ticker=entities["ticker"].upper(),
                        shares=float(entities["shares"])
                    )

            elif asset_type in ["crypto", "cryptocurrency"]:
                if entities.get("symbol") and entities.get("amount"):
                    return Crypto(
                        symbol=entities["symbol"].upper(),
                        amount=float(entities["amount"])
                    )

            elif asset_type in ["real_estate", "realestate", "property"]:
                if entities.get("address") and (entities.get("value") or entities.get("market_value")):
                    value = entities.get("value") or entities.get("market_value")
                    if value is not None:
                        return RealEstate(
                            address=entities["address"],
                            market_value=float(value)
                        )

            elif asset_type == "mortgage":
                if entities.get("lender") and entities.get("balance"):
                    return Mortgage(
                        lender=entities["lender"],
                        balance=float(entities["balance"]),
                        property_address=entities.get("property_address")
                    )

            elif asset_type == "cash":
                if entities.get("amount"):
                    return Cash(
                        currency=entities.get("currency", "USD"),
                        amount=float(entities["amount"])
                    )

        except (ValueError, TypeError) as e:
            logger.error(f"Asset creation failed: {e}")

        return None

    def _asset_matches(self, asset: Asset, identifier: str) -> bool:
        identifier = identifier.upper()

        if isinstance(asset, Stock):
            return asset.ticker == identifier
        elif isinstance(asset, Crypto):
            return asset.symbol == identifier
        elif isinstance(asset, RealEstate):
            return identifier.lower() in asset.address.lower()
        elif isinstance(asset, Mortgage):
            return identifier.lower() in asset.lender.lower()
        return False
