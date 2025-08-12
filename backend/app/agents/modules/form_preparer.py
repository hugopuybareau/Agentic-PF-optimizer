import logging
from typing import Any

from langfuse.decorators import langfuse_context, observe

from ...models import ChatSession, PortfolioBuildingState
from ...models.assets import Asset, Cash, Crypto, Mortgage, RealEstate, Stock

logger = logging.getLogger(__name__)


class FormPreparer:

    @observe(name="prepare_form_tool")
    def prepare_form(self, session: ChatSession, portfolio_state: PortfolioBuildingState) -> dict[str, Any]:

        form_assets = []
        for asset in portfolio_state.assets:
            asset_dict = {}
            if isinstance(asset, Stock):
                asset_dict = {
                    "type": "stock",
                    "ticker": asset.ticker,
                    "shares": asset.shares
                }
            elif isinstance(asset, Crypto):
                asset_dict = {
                    "type": "crypto",
                    "symbol": asset.symbol,
                    "amount": asset.amount
                }
            elif isinstance(asset, RealEstate):
                asset_dict = {
                    "type": "real_estate",
                    "address": asset.address,
                    "market_value": asset.market_value
                }
            elif isinstance(asset, Mortgage):
                asset_dict = {
                    "type": "mortgage",
                    "lender": asset.lender,
                    "balance": asset.balance,
                    "property_address": asset.property_address
                }
            elif isinstance(asset, Cash):
                asset_dict = {
                    "type": "cash",
                    "currency": asset.currency,
                    "amount": asset.amount
                }

            if asset_dict:
                form_assets.append(asset_dict)

        response = (
            "Great! I've captured your portfolio so far. Please review the details below "
            "and make any adjustments needed. You can also add any assets I might have missed."
        )

        ui_hints = {
            "show_portfolio_form": True,
            "form_mode": "review",
            "can_edit": True,
            "can_analyze": len(form_assets) > 0
        }

        langfuse_context.update_current_observation(
            metadata={
                "form_prepared": True,
                "asset_count": len(form_assets),
                "asset_types": list(set(a["type"] for a in form_assets))
            }
        )

        return {
            "show_form": True,
            "form_data": {
                "assets": form_assets,
                "suggested_additions": self._suggest_missing_assets(portfolio_state.assets)
            },
            "response": response,
            "ui_hints": ui_hints
        }

    def _suggest_missing_assets(self, current_assets: list[Asset]) -> list[dict]:
        current_types = {asset.type for asset in current_assets}
        suggestions = []

        if "cash" not in current_types:
            suggestions.append({
                "type": "cash",
                "message": "Emergency fund or savings account"
            })

        if "stock" not in current_types:
            suggestions.append({
                "type": "stock",
                "message": "401(k) or individual stocks"
            })

        if "real_estate" not in current_types and "mortgage" in current_types:
            suggestions.append({
                "type": "real_estate",
                "message": "Your mortgaged property value"
            })

        return suggestions
