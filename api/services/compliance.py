"""Automated compliance reporting service.

Generates structured reports aligned with major frameworks:
- GHG Protocol Corporate Standard inventory
- CDP Climate Change Questionnaire (key modules)
- TCFD recommended disclosures
- SBTi baseline and target pathway
- CSRD (Corporate Sustainability Reporting Directive) — ESRS E1
- ISSB (IFRS S2 Climate-related Disclosures)
- SECR (Streamlined Energy and Carbon Reporting — UK)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


def generate_ghg_inventory(
    company_name: str,
    industry: str,
    region: str,
    year: int,
    scope1: float,
    scope2: float,
    scope3: float,
    total: float,
    breakdown: dict | None,
    sources: list | None,
    assumptions: list | None,
    confidence: float,
) -> dict[str, Any]:
    """Generate a GHG Protocol Corporate Standard inventory report."""
    breakdown = breakdown or {}

    s1_detail = breakdown.get("scope1_detail", {})
    s2_detail = breakdown.get("scope2_detail", {})
    s3_detail = breakdown.get("scope3_detail", {})

    return {
        "framework": "GHG Protocol Corporate Standard",
        "version": "Revised Edition (2004, updated 2015)",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "reporting_period": f"{year}-01-01 to {year}-12-31",
        "organization": {
            "name": company_name,
            "industry_sector": industry,
            "region": region,
        },
        "organizational_boundary": {
            "approach": "Operational Control",
            "description": f"{company_name} reports GHG emissions from all operations under its operational control.",
        },
        "emissions_summary": {
            "total_tco2e": total,
            "scope1_tco2e": scope1,
            "scope2_location_tco2e": s2_detail.get("location_based", scope2),
            "scope2_market_tco2e": s2_detail.get("market_based", scope2),
            "scope3_tco2e": scope3,
            "unit": "metric tonnes of CO2 equivalent (tCO2e)",
            "gwp_source": "IPCC AR6",
            "gases_included": ["CO2", "CH4", "N2O", "HFCs"],
        },
        "scope1_detail": {
            "stationary_combustion": s1_detail.get("stationary_combustion", 0) + s1_detail.get("natural_gas", 0),
            "mobile_combustion": s1_detail.get("mobile_combustion", 0),
            "fugitive_emissions": s1_detail.get("fugitive_emissions", 0),
            "process_emissions": 0,
        },
        "scope2_detail": {
            "location_based_method": s2_detail.get("location_based", scope2),
            "market_based_method": s2_detail.get("market_based", scope2),
            "grid_region": region,
        },
        "scope3_categories": _build_scope3_categories(s3_detail),
        "data_quality": {
            "confidence_score": confidence,
            "data_sources": sources or [],
            "assumptions": assumptions or [],
            "verification_status": "Self-assessed" if confidence < 0.8 else "Ready for third-party verification",
        },
        "methodology_notes": [
            "Emission factors sourced from EPA, eGRID, IEA, and DEFRA databases.",
            "Scope 3 categories without primary data estimated using industry benchmarks.",
            "GWP values from IPCC Sixth Assessment Report (AR6).",
        ],
    }


def _build_scope3_categories(s3_detail: dict) -> list[dict[str, Any]]:
    """Map internal Scope 3 details to GHG Protocol's 15 categories."""
    cat_map = [
        (1, "Purchased goods and services", "cat1_purchased_goods"),
        (2, "Capital goods", "cat2_capital_goods"),
        (3, "Fuel- and energy-related activities", "cat3_fuel_energy"),
        (4, "Upstream transportation and distribution", "cat4_upstream_transport"),
        (5, "Waste generated in operations", "cat5_waste"),
        (6, "Business travel", "cat6_business_travel"),
        (7, "Employee commuting", "cat7_commuting"),
        (8, "Upstream leased assets", "cat8_leased_assets"),
        (9, "Downstream transportation and distribution", "cat9_downstream_transport"),
        (10, "Processing of sold products", "cat10_processing"),
        (11, "Use of sold products", "cat11_use_products"),
        (12, "End-of-life treatment of sold products", "cat12_end_of_life"),
        (13, "Downstream leased assets", "cat13_downstream_leased"),
        (14, "Franchises", "cat14_franchises"),
        (15, "Investments", "cat15_investments"),
    ]

    categories = []
    for num, name, key in cat_map:
        value = s3_detail.get(key, 0)
        method = "Activity-based" if value > 0 and key in s3_detail else "Not estimated"
        if key not in s3_detail and value > 0:
            method = "Industry-default"

        # Check default-filled keys
        default_keys = {k for k in s3_detail if k.startswith("cat") and k not in
                       ["cat1_purchased_goods", "cat4_upstream_transport", "cat5_waste",
                        "cat6_business_travel", "cat7_commuting"]}
        if key in default_keys:
            method = "Industry-default"

        categories.append({
            "category_number": num,
            "category_name": name,
            "tco2e": round(value, 2),
            "method": method,
            "relevant": value > 0,
        })

    return categories


def generate_cdp_responses(
    company_name: str,
    industry: str,
    year: int,
    scope1: float,
    scope2: float,
    scope3: float,
    total: float,
    breakdown: dict | None,
    confidence: float,
) -> dict[str, Any]:
    """Generate key CDP Climate Change questionnaire responses."""
    s2_detail = (breakdown or {}).get("scope2_detail", {})

    return {
        "framework": "CDP Climate Change Questionnaire",
        "reporting_year": year,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "modules": {
            "C0_introduction": {
                "C0.1": company_name,
                "C0.2": f"Reporting period: {year}-01-01 to {year}-12-31",
                "C0.3": "Operational control",
            },
            "C1_governance": {
                "C1.1": "Yes — Board-level oversight of climate-related issues",
                "C1.2": "Climate risk is integrated into overall risk management",
            },
            "C4_targets": {
                "C4.1": "Absolute emissions reduction target",
                "C4.1a": {
                    "base_year": year,
                    "base_year_emissions": total,
                    "target_year": year + 5,
                    "target_reduction_pct": 30,
                    "target_emissions": round(total * 0.7, 2),
                },
            },
            "C6_emissions": {
                "C6.1_scope1": scope1,
                "C6.3_scope2_location": s2_detail.get("location_based", scope2),
                "C6.3_scope2_market": s2_detail.get("market_based", scope2),
                "C6.5_scope3": scope3,
                "C6.10_methodology": "GHG Protocol Corporate Standard",
                "C6.10_gwp_source": "IPCC AR6",
            },
            "C7_emissions_breakdown": {
                "by_scope": {
                    "scope1_pct": round(scope1 / max(total, 1) * 100, 1),
                    "scope2_pct": round(scope2 / max(total, 1) * 100, 1),
                    "scope3_pct": round(scope3 / max(total, 1) * 100, 1),
                },
            },
        },
    }


def generate_tcfd_disclosure(
    company_name: str,
    industry: str,
    year: int,
    scope1: float,
    scope2: float,
    scope3: float,
    total: float,
    recommendations: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Generate TCFD-aligned disclosure framework."""
    return {
        "framework": "Task Force on Climate-related Financial Disclosures (TCFD)",
        "reporting_year": year,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pillars": {
            "governance": {
                "description": "Board oversight and management role in climate-related risks and opportunities.",
                "board_oversight": "The Board receives quarterly updates on climate-related performance and risks.",
                "management_role": "A dedicated sustainability team monitors emissions and implements reduction strategies.",
            },
            "strategy": {
                "description": "Climate-related risks and opportunities impact on strategy and financial planning.",
                "risks": [
                    {
                        "type": "Transition",
                        "risk": "Carbon pricing / emissions trading",
                        "impact": "Potential cost increase of $10-50 per tCO2e on Scope 1 emissions",
                        "time_horizon": "Medium-term (2-5 years)",
                    },
                    {
                        "type": "Physical",
                        "risk": "Extreme weather events disrupting operations",
                        "impact": "Supply chain disruptions, facility damage",
                        "time_horizon": "Long-term (5+ years)",
                    },
                ],
                "opportunities": [
                    {
                        "type": "Resource efficiency",
                        "description": "Energy efficiency improvements reducing costs",
                        "financial_impact": "Potential 10-25% reduction in energy costs",
                    },
                    {
                        "type": "Market",
                        "description": "Growing demand for low-carbon products and services",
                        "financial_impact": "Revenue growth from sustainable offerings",
                    },
                ],
            },
            "risk_management": {
                "description": "Processes for identifying, assessing, and managing climate risks.",
                "process": "Climate risk assessment integrated into enterprise risk management framework.",
                "integration": "Climate metrics included in operational KPIs and investment decisions.",
            },
            "metrics_and_targets": {
                "emissions": {
                    "scope1_tco2e": scope1,
                    "scope2_tco2e": scope2,
                    "scope3_tco2e": scope3,
                    "total_tco2e": total,
                },
                "intensity_metrics": {
                    "note": "Revenue-normalized and employee-normalized intensities available via dashboard.",
                },
                "targets": {
                    "short_term": f"Reduce absolute emissions 15% by {year + 3}",
                    "medium_term": f"Reduce absolute emissions 30% by {year + 5}",
                    "long_term": f"Achieve net-zero by {year + 25}",
                    "science_based": "Aligned with 1.5°C pathway (SBTi)",
                },
                "key_reduction_strategies": [
                    r["title"] for r in (recommendations or [])[:5]
                ],
            },
        },
    }


def generate_sbti_pathway(
    company_name: str,
    year: int,
    scope1: float,
    scope2: float,
    scope3: float,
    total: float,
) -> dict[str, Any]:
    """Generate SBTi-aligned baseline and target pathway."""
    # SBTi requires 4.2% annual reduction for 1.5°C pathway (Scope 1+2)
    # and 2.5% for well-below 2°C (Scope 3)
    s12 = scope1 + scope2
    target_years = list(range(year, year + 11))
    s12_annual_reduction = 0.042
    s3_annual_reduction = 0.025

    pathway = []
    for i, y in enumerate(target_years):
        s12_projected = s12 * ((1 - s12_annual_reduction) ** i)
        s3_projected = scope3 * ((1 - s3_annual_reduction) ** i)
        pathway.append({
            "year": y,
            "scope1_2_tco2e": round(s12_projected, 1),
            "scope3_tco2e": round(s3_projected, 1),
            "total_tco2e": round(s12_projected + s3_projected, 1),
        })

    return {
        "framework": "Science Based Targets initiative (SBTi)",
        "base_year": year,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "baseline": {
            "scope1_tco2e": scope1,
            "scope2_tco2e": scope2,
            "scope3_tco2e": scope3,
            "total_tco2e": total,
        },
        "target": {
            "ambition": "1.5°C aligned",
            "scope1_2_annual_reduction_pct": s12_annual_reduction * 100,
            "scope3_annual_reduction_pct": s3_annual_reduction * 100,
            "target_year": year + 10,
            "scope1_2_target_tco2e": round(s12 * ((1 - s12_annual_reduction) ** 10), 1),
            "scope3_target_tco2e": round(scope3 * ((1 - s3_annual_reduction) ** 10), 1),
        },
        "pathway": pathway,
        "notes": [
            "Scope 1+2: 4.2% annual absolute reduction (1.5°C pathway, SBTi corporate manual v2.1).",
            "Scope 3: 2.5% annual absolute reduction (SBTi Scope 3 minimum ambition).",
            "Pathway assumes linear year-over-year reductions from the base year.",
        ],
    }


# ── CSRD — ESRS E1 Climate Change ──────────────────────────────────


def generate_csrd_report(
    company_name: str,
    industry: str,
    region: str,
    year: int,
    scope1: float,
    scope2: float,
    scope3: float,
    total: float,
    breakdown: dict | None,
    sources: list | None,
    assumptions: list | None,
    confidence: float,
    employee_count: int | None = None,
    revenue_usd: float | None = None,
) -> dict[str, Any]:
    """Generate a CSRD-aligned disclosure covering ESRS E1 (Climate Change)."""
    breakdown = breakdown or {}
    s2_detail = breakdown.get("scope2_detail", {})
    s3_detail = breakdown.get("scope3_detail", {})

    # Intensity metrics when denominators are available
    intensity: dict[str, Any] = {}
    if revenue_usd and revenue_usd > 0:
        intensity["tco2e_per_million_revenue"] = round(total / (revenue_usd / 1_000_000), 2)
    if employee_count and employee_count > 0:
        intensity["tco2e_per_employee"] = round(total / employee_count, 2)

    return {
        "framework": "CSRD — ESRS E1 Climate Change",
        "version": "ESRS Set 1 (Delegated Act 2023/2772)",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "reporting_period": f"{year}-01-01 to {year}-12-31",
        "organization": {
            "name": company_name,
            "industry_sector": industry,
            "region": region,
        },
        "E1_1_transition_plan": {
            "has_transition_plan": True,
            "description": (
                f"{company_name} is committed to reducing GHG emissions in line with the "
                "Paris Agreement 1.5°C target. A phased decarbonisation plan covers energy "
                "transition, supply chain engagement, and operational efficiency."
            ),
            "alignment": "Paris Agreement 1.5°C",
        },
        "E1_4_targets": {
            "target_type": "Absolute GHG emission reduction",
            "base_year": year,
            "base_year_emissions_tco2e": total,
            "short_term_target": {
                "year": year + 5,
                "reduction_pct": 30,
                "target_tco2e": round(total * 0.70, 1),
            },
            "long_term_target": {
                "year": year + 25,
                "reduction_pct": 90,
                "target_tco2e": round(total * 0.10, 1),
                "net_zero_year": year + 25,
            },
        },
        "E1_6_gross_ghg_emissions": {
            "scope1_tco2e": scope1,
            "scope2_location_tco2e": s2_detail.get("location_based", scope2),
            "scope2_market_tco2e": s2_detail.get("market_based", scope2),
            "scope3_tco2e": scope3,
            "total_tco2e": total,
            "gwp_source": "IPCC AR6",
            "consolidation_approach": "Operational Control",
        },
        "E1_7_ghg_removals_and_offsets": {
            "carbon_removals_tco2e": 0,
            "carbon_credits_retired_tco2e": 0,
            "note": "No offsets claimed — gross figures reported.",
        },
        "E1_8_internal_carbon_pricing": {
            "has_internal_carbon_price": False,
            "price_per_tco2e": None,
            "note": "Internal carbon pricing under evaluation.",
        },
        "E1_9_energy": {
            "total_energy_mwh": breakdown.get("total_energy_mwh"),
            "renewable_share_pct": breakdown.get("renewable_share_pct"),
            "note": "Detailed energy breakdown available in operational data.",
        },
        "intensity_metrics": intensity,
        "scope3_categories": _build_scope3_categories(s3_detail),
        "data_quality": {
            "confidence_score": confidence,
            "data_sources": sources or [],
            "assumptions": assumptions or [],
            "external_assurance": "Limited" if confidence >= 0.8 else "Not yet assured",
        },
    }


# ── ISSB — IFRS S2 Climate-related Disclosures ─────────────────────


def generate_issb_report(
    company_name: str,
    industry: str,
    region: str,
    year: int,
    scope1: float,
    scope2: float,
    scope3: float,
    total: float,
    breakdown: dict | None,
    sources: list | None,
    confidence: float,
    employee_count: int | None = None,
    revenue_usd: float | None = None,
    recommendations: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Generate an IFRS S2 Climate-related Disclosures report."""
    breakdown = breakdown or {}
    s2_detail = breakdown.get("scope2_detail", {})

    cross_industry_metrics: list[dict[str, Any]] = [
        {"metric": "Scope 1 GHG emissions (tCO2e)", "value": scope1},
        {"metric": "Scope 2 GHG emissions — location-based (tCO2e)", "value": s2_detail.get("location_based", scope2)},
        {"metric": "Scope 2 GHG emissions — market-based (tCO2e)", "value": s2_detail.get("market_based", scope2)},
        {"metric": "Scope 3 GHG emissions (tCO2e)", "value": scope3},
        {"metric": "Total GHG emissions (tCO2e)", "value": total},
    ]
    if revenue_usd and revenue_usd > 0:
        cross_industry_metrics.append({
            "metric": "GHG intensity — per $M revenue (tCO2e/$M)",
            "value": round(total / (revenue_usd / 1_000_000), 2),
        })
    if employee_count and employee_count > 0:
        cross_industry_metrics.append({
            "metric": "GHG intensity — per employee (tCO2e/FTE)",
            "value": round(total / employee_count, 2),
        })

    return {
        "framework": "IFRS S2 Climate-related Disclosures",
        "version": "ISSB Standards (June 2023)",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "reporting_period": f"{year}-01-01 to {year}-12-31",
        "organization": {
            "name": company_name,
            "industry_sector": industry,
            "region": region,
        },
        "governance": {
            "paragraph_6": (
                "The Board maintains oversight of climate-related risks and opportunities "
                "through quarterly sustainability committee reviews."
            ),
            "paragraph_7": (
                "Management responsibility for climate matters is assigned to the Chief "
                "Sustainability Officer, who reports directly to the CEO."
            ),
        },
        "strategy": {
            "paragraph_10_risks_and_opportunities": [
                {
                    "type": "Transition risk",
                    "description": "Increased carbon pricing or emissions regulation",
                    "time_horizon": "Medium-term (2-5 years)",
                    "financial_impact": "Potential increase in operating costs",
                },
                {
                    "type": "Physical risk",
                    "description": "Acute weather events disrupting operations or supply chain",
                    "time_horizon": "Long-term (5+ years)",
                    "financial_impact": "Asset impairment and business interruption costs",
                },
                {
                    "type": "Opportunity",
                    "description": "Revenue growth from low-carbon products and services",
                    "time_horizon": "Short-term (0-2 years)",
                    "financial_impact": "Incremental revenue from sustainability offerings",
                },
            ],
            "paragraph_14_transition_plan": {
                "has_plan": True,
                "alignment": "Paris Agreement 1.5°C pathway",
                "key_actions": [r["title"] for r in (recommendations or [])[:5]],
            },
        },
        "risk_management": {
            "paragraph_25": (
                "Climate-related risks are identified through an annual risk assessment "
                "covering transition, physical, and regulatory axes."
            ),
            "paragraph_26_integration": (
                "Climate risk is embedded in the enterprise risk management framework."
            ),
        },
        "metrics_and_targets": {
            "paragraph_29_cross_industry_metrics": cross_industry_metrics,
            "paragraph_33_targets": {
                "target_type": "Absolute emission reduction",
                "base_year": year,
                "target_year": year + 10,
                "reduction_pct": 42,
                "methodology": "SBTi 1.5°C pathway",
            },
            "ghg_measurement_approach": {
                "standard": "GHG Protocol Corporate Standard",
                "gwp_source": "IPCC AR6",
                "consolidation": "Operational Control",
            },
        },
        "data_quality": {
            "confidence_score": confidence,
            "data_sources": sources or [],
        },
    }


# ── SECR — UK Streamlined Energy and Carbon Reporting ───────────────


def generate_secr_report(
    company_name: str,
    industry: str,
    region: str,
    year: int,
    scope1: float,
    scope2: float,
    scope3: float,
    total: float,
    breakdown: dict | None,
    sources: list | None,
    confidence: float,
    employee_count: int | None = None,
    revenue_usd: float | None = None,
) -> dict[str, Any]:
    """Generate a UK SECR-compliant GHG and energy report."""
    breakdown = breakdown or {}
    s2_detail = breakdown.get("scope2_detail", {})

    # Intensity ratio (revenue-based is mandatory under SECR)
    intensity_ratio: dict[str, Any] = {"chosen_metric": "tCO2e per £M turnover"}
    if revenue_usd and revenue_usd > 0:
        # Approximate GBP (SECR uses sterling) — we note USD conversion
        intensity_ratio["value"] = round(total / (revenue_usd / 1_000_000), 2)
        intensity_ratio["unit"] = "tCO2e per $M revenue (USD equivalent)"
    else:
        intensity_ratio["value"] = None
        intensity_ratio["note"] = "Revenue data required for intensity ratio calculation."

    # Estimate energy from breakdown if available
    energy_kwh = breakdown.get("total_energy_kwh")

    return {
        "framework": "UK Streamlined Energy and Carbon Reporting (SECR)",
        "version": "Companies (Directors' Report) Regulations 2018, Schedule 7",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "reporting_period": f"01 April {year} to 31 March {year + 1}",
        "organization": {
            "name": company_name,
            "industry_sector": industry,
            "region": region,
        },
        "uk_ghg_emissions": {
            "scope1_tco2e": scope1,
            "scope2_location_tco2e": s2_detail.get("location_based", scope2),
            "total_scope1_and_2_tco2e": round(scope1 + scope2, 2),
            "scope3_tco2e_voluntary": scope3,
            "global_total_tco2e": total,
        },
        "energy_consumption": {
            "total_kwh": energy_kwh,
            "electricity_kwh": breakdown.get("electricity_kwh"),
            "gas_kwh": breakdown.get("gas_kwh"),
            "transport_kwh": breakdown.get("transport_kwh"),
            "note": "Detailed energy split reported where metered data is available.",
        },
        "intensity_ratio": intensity_ratio,
        "methodology": {
            "standard": "GHG Protocol Corporate Standard",
            "emission_factors": "UK DEFRA / BEIS Conversion Factors",
            "gwp_source": "IPCC AR6",
            "boundary": "Operational Control",
        },
        "energy_efficiency_narrative": (
            f"{company_name} is actively pursuing energy efficiency improvements "
            "including LED lighting upgrades, HVAC optimisation, and procurement "
            "of renewable electricity certificates."
        ),
        "data_quality": {
            "confidence_score": confidence,
            "data_sources": sources or [],
        },
    }
