import logging

from langfuse.decorators import langfuse_context, observe

from ...models import ChatSession, PortfolioBuildingState
from ...models.assets import Asset, Cash, Crypto, Mortgage, RealEstate, Stock
from ...models.responses import FormAssetData, FormSuggestion, PortfolioFormData, UIHints

logger = logging.getLogger(__name__)


class FormPreparer:

    @observe(name="prepare_form_tool")
    def prepare_form(self, session: ChatSession, portfolio_state: PortfolioBuildingState) -> dict:

        form_assets = []
        for asset in portfolio_state.assets:
            if isinstance(asset, Stock):
                form_asset = FormAssetData(
                    type="stock",
                    ticker=asset.ticker,
                    shares=asset.shares
                )
            elif isinstance(asset, Crypto):
                form_asset = FormAssetData(
                    type="crypto",
                    symbol=asset.symbol,
                    amount=asset.amount
                )
            elif isinstance(asset, RealEstate):
                form_asset = FormAssetData(
                    type="real_estate",
                    address=asset.address,
                    market_value=asset.market_value
                )
            elif isinstance(asset, Mortgage):
                form_asset = FormAssetData(
                    type="mortgage",
                    lender=asset.lender,
                    balance=asset.balance,
                    property_address=asset.property_address
                )
            elif isinstance(asset, Cash):
                form_asset = FormAssetData(
                    type="cash",
                    currency=asset.currency,
                    amount=asset.amount
                )
            else:
                continue

            form_assets.append(form_asset)

        response = (
            "Great! I've captured your portfolio so far. Please review the details below "
            "and make any adjustments needed. You can also add any assets I might have missed."
        )

        ui_hints = UIHints(
            show_portfolio_summary=True,
            current_asset_count=len(form_assets)
        )

        suggested_additions = self._suggest_missing_assets(portfolio_state.assets)
        form_data = PortfolioFormData(
            assets=form_assets,
            suggested_additions=suggested_additions
        )

        langfuse_context.update_current_observation(
            metadata={
                "form_prepared": True,
                "asset_count": len(form_assets),
                "asset_types": list(set(a.type for a in form_assets))
            }
        )

        return {
            "show_form": True,
            "form_data": form_data,
            "response": response,
            "ui_hints": ui_hints
        }

    def _suggest_missing_assets(self, current_assets: list[Asset]) -> list[FormSuggestion]:
        current_types = {asset.type for asset in current_assets}
        suggestions = []

        if "cash" not in current_types:
            suggestions.append(FormSuggestion(
                type="cash",
                message="Emergency fund or savings account"
            ))

        if "stock" not in current_types:
            suggestions.append(FormSuggestion(
                type="stock",
                message="401(k) or individual stocks"
            ))

        if "real_estate" not in current_types and "mortgage" in current_types:
            suggestions.append(FormSuggestion(
                type="real_estate",
                message="Your mortgaged property value"
            ))

        return suggestions
