import logging

from langfuse.decorators import langfuse_context, observe

from ...models import ChatSession, Intent
from ...models.assets import Asset, Cash, Crypto, Mortgage, RealEstate, Stock
from ...models.responses import EntityData, UIHints

logger = logging.getLogger(__name__)


class PortfolioOperations:

    @observe(name="update_portfolio_tool")
    def update_portfolio(self, session: ChatSession, entities: list[EntityData], intent: Intent) -> UIHints:
        ui_hints = UIHints()

        if intent == Intent.ADD_ASSET and entities:
            try:
                primary_entity = entities[0] if entities else None
                if primary_entity:
                    asset = self._create_asset_from_entity(primary_entity)
                    if asset:
                        session.portfolio_state.assets.append(asset)
                        session.portfolio_state.current_asset_type = None
                        session.portfolio_state.current_asset_data = {}
                        ui_hints.show_portfolio_summary = True
                        ui_hints.current_asset_count = len(session.portfolio_state.assets)

                        logger.info(f"Added asset: {asset}")
                        langfuse_context.update_current_observation(
                            metadata={
                                "asset_added": True,
                                "asset_type": asset.type,
                                "total_assets": len(session.portfolio_state.assets)
                            }
                        )
                    else:
                        session.portfolio_state.current_asset_type = primary_entity.asset_type
                        session.portfolio_state.current_asset_data.update(primary_entity.model_dump(exclude_none=True))
                        ui_hints.highlight_missing_info = True

            except Exception as e:
                logger.error(f"Failed to create asset: {e}")
                session.portfolio_state.validation_errors.append(str(e))

        elif intent == Intent.REMOVE_ASSET and entities:
            primary_entity = entities[0] if entities else None
            if primary_entity:
                identifier = primary_entity.ticker or primary_entity.symbol or primary_entity.address
                if identifier:
                    original_count = len(session.portfolio_state.assets)
                    session.portfolio_state.assets = [
                        a for a in session.portfolio_state.assets
                        if not self._asset_matches(a, identifier)
                    ]
                    if len(session.portfolio_state.assets) < original_count:
                        ui_hints.show_portfolio_summary = True
                        ui_hints.current_asset_count = len(session.portfolio_state.assets)
                        logger.info(f"Removed asset with identifier: {identifier}")

        elif intent == Intent.COMPLETE_PORTFOLIO:
            session.portfolio_state.is_complete = True
            ui_hints.show_completion_button = True
            ui_hints.show_portfolio_summary = True
            ui_hints.current_asset_count = len(session.portfolio_state.assets)

        return ui_hints

    @observe(name="create_asset")
    def _create_asset_from_entity(self, entity: EntityData) -> Asset | None:
        if not entity.asset_type:
            return None

        asset_type = entity.asset_type.lower()

        try:
            if asset_type == "stock":
                if entity.ticker and entity.shares:
                    return Stock(
                        ticker=entity.ticker.upper(),
                        shares=float(entity.shares)
                    )

            elif asset_type in ["crypto", "cryptocurrency"]:
                if entity.symbol and entity.amount:
                    return Crypto(
                        symbol=entity.symbol.upper(),
                        amount=float(entity.amount)
                    )

            elif asset_type in ["real_estate", "realestate", "property"]:
                if entity.address and entity.market_value:
                    return RealEstate(
                        address=entity.address,
                        market_value=float(entity.market_value)
                    )

            elif asset_type == "mortgage":
                if entity.lender and entity.balance:
                    return Mortgage(
                        lender=entity.lender,
                        balance=float(entity.balance),
                        property_address=getattr(entity, 'property_address', None)
                    )

            elif asset_type == "cash":
                if entity.amount:
                    return Cash(
                        currency=entity.currency or "USD",
                        amount=float(entity.amount)
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
