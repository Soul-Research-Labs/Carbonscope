"""PCAF (Partnership for Carbon Accounting Financials) service.

Calculates financed emissions using the attribution approach:
  financed_emissions = (outstanding_amount / total_equity_debt) * investee_emissions
"""

from __future__ import annotations

from typing import Any


def calculate_attribution_factor(outstanding_amount: float, total_equity_debt: float) -> float:
    """Calculate PCAF attribution factor."""
    if total_equity_debt <= 0:
        return 0.0
    return outstanding_amount / total_equity_debt


def calculate_financed_emissions(
    outstanding_amount: float,
    total_equity_debt: float,
    investee_emissions_tco2e: float,
) -> tuple[float, float]:
    """Return (attribution_factor, financed_emissions_tco2e)."""
    af = calculate_attribution_factor(outstanding_amount, total_equity_debt)
    return af, round(af * investee_emissions_tco2e, 4)


def summarise_portfolio(assets: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate portfolio-level PCAF metrics from a list of asset dicts."""
    total_financed = 0.0
    total_outstanding = 0.0
    weighted_dq_num = 0.0
    by_class: dict[str, dict[str, float]] = {}

    for a in assets:
        fe = a.get("financed_emissions_tco2e") or 0.0
        oa = a.get("outstanding_amount", 0.0)
        dq = a.get("data_quality_score", 3)
        ac = a.get("asset_class", "unknown")

        total_financed += fe
        total_outstanding += oa
        weighted_dq_num += dq * oa

        bucket = by_class.setdefault(ac, {"financed_emissions_tco2e": 0.0, "outstanding_amount": 0.0, "count": 0})
        bucket["financed_emissions_tco2e"] += fe
        bucket["outstanding_amount"] += oa
        bucket["count"] += 1

    weighted_dq = round(weighted_dq_num / total_outstanding, 2) if total_outstanding > 0 else 0.0

    return {
        "total_financed_emissions_tco2e": round(total_financed, 2),
        "total_outstanding": round(total_outstanding, 2),
        "weighted_data_quality": weighted_dq,
        "asset_count": len(assets),
        "by_asset_class": {k: {kk: round(vv, 2) if isinstance(vv, float) else vv for kk, vv in v.items()} for k, v in by_class.items()},
    }
