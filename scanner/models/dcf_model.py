"""
DCF / NPV Financial Model for Reg CF Startups

Produces a pre-money valuation estimate and implied upside multiplier
relative to the current offering valuation.

Inputs are estimates/assumptions — this is analytical output only.
NOT investment advice. NOT a recommendation to buy or sell.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import math


@dataclass
class DCFInputs:
    """
    All inputs required to run the DCF model.
    Designed for early-stage startups where revenue is known or estimated.
    """
    company_name: str

    # Revenue / Growth assumptions
    current_arr: float                  # Current ARR or TTM revenue in USD
    revenue_growth_rate_y1: float       # e.g. 1.50 = 150% YoY growth
    revenue_growth_rate_y2: float
    revenue_growth_rate_y3: float
    revenue_growth_rate_y4: float
    revenue_growth_rate_y5: float
    terminal_growth_rate: float = 0.03  # Long-term growth (3% default)

    # Margin assumptions
    gross_margin: float = 0.70          # SaaS default
    ebitda_margin_terminal: float = 0.25  # Mature SaaS EBITDA margin

    # Discount rate
    wacc: float = 0.35                  # 35% for early-stage (high risk)

    # Valuation context
    current_offering_valuation: Optional[float] = None   # Pre-money valuation in USD


@dataclass
class DCFResult:
    company_name: str
    projected_revenues: list[float]     # 5-year revenue projections
    terminal_value: float
    enterprise_value: float             # Sum of DCF'd cash flows + terminal value
    implied_upside_x: Optional[float]   # EV / current offering valuation
    dcf_score: float                    # Normalized 0–100 (upside score)
    assumptions_note: str = (
        "Model uses management projections discounted at 35% WACC. "
        "NOT investment advice. Data-only output per Equiti-AI Safe Mode."
    )


def run_dcf(inputs: DCFInputs) -> DCFResult:
    """
    Runs a simplified 5-year DCF for an early-stage startup.

    Method:
    - Projects revenue for 5 years using provided growth rates.
    - Approximates free cash flow as revenue × gross_margin × ebitda_margin (year 5).
    - Applies Gordon Growth Model for terminal value.
    - Discounts all cash flows back at WACC.

    Returns:
        DCFResult with enterprise value and implied upside vs. current valuation.
    """
    growth_rates = [
        inputs.revenue_growth_rate_y1,
        inputs.revenue_growth_rate_y2,
        inputs.revenue_growth_rate_y3,
        inputs.revenue_growth_rate_y4,
        inputs.revenue_growth_rate_y5,
    ]

    # ── 5-Year Revenue Projection ──────────────────────────────────────────
    revenues: list[float] = []
    rev = inputs.current_arr
    for g in growth_rates:
        rev = rev * (1 + g)
        revenues.append(round(rev, 2))

    # ── Approximate Free Cash Flow (Year 5 as proxy for normalised FCF) ───
    # FCF = Revenue × Gross Margin × EBITDA Margin (simplified)
    fcf_y5 = revenues[-1] * inputs.gross_margin * inputs.ebitda_margin_terminal

    # ── Terminal Value (Gordon Growth Model) ──────────────────────────────
    terminal_value = fcf_y5 * (1 + inputs.terminal_growth_rate) / (
        inputs.wacc - inputs.terminal_growth_rate
    )

    # ── Discount Cash Flows ────────────────────────────────────────────────
    # We use a simplified approach: discount each year's "proto-FCF" as a
    # fraction of that year's revenue (ramping from 0% in Y1 to full margin in Y5).
    margin_ramp = [0.0, 0.05, 0.10, 0.18, inputs.gross_margin * inputs.ebitda_margin_terminal]
    pv_fcfs = sum(
        revenues[i] * margin_ramp[i] / (1 + inputs.wacc) ** (i + 1)
        for i in range(5)
    )

    # Discount terminal value back 5 years
    pv_terminal = terminal_value / (1 + inputs.wacc) ** 5

    enterprise_value = round(pv_fcfs + pv_terminal, 2)

    # ── Implied Upside ────────────────────────────────────────────────────
    implied_upside_x: Optional[float] = None
    if inputs.current_offering_valuation and inputs.current_offering_valuation > 0:
        implied_upside_x = round(enterprise_value / inputs.current_offering_valuation, 2)

    # ── DCF Score (0–100) ─────────────────────────────────────────────────
    # 3x upside ≈ 50 points; 10x ≈ 100 points; <1x ≈ 0 points
    if implied_upside_x is not None:
        dcf_score = min(math.log1p(max(implied_upside_x - 1, 0)) / math.log1p(9) * 100, 100)
    else:
        dcf_score = 50.0  # Neutral if no offering valuation provided

    return DCFResult(
        company_name=inputs.company_name,
        projected_revenues=revenues,
        terminal_value=round(terminal_value, 2),
        enterprise_value=enterprise_value,
        implied_upside_x=implied_upside_x,
        dcf_score=round(dcf_score, 2),
    )


def npv(cash_flows: list[float], discount_rate: float) -> float:
    """
    Utility: Net Present Value of a cash flow stream.

    Args:
        cash_flows:    List of cash flows [CF_year1, CF_year2, ...].
        discount_rate: Annual discount rate (e.g. 0.35 for 35%).

    Returns:
        NPV in same currency units as cash_flows.
    """
    return sum(cf / (1 + discount_rate) ** (i + 1) for i, cf in enumerate(cash_flows))
