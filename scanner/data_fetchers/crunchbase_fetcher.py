"""
Crunchbase / Deal-Flow Data Fetcher

Uses the Crunchbase Basic API (free tier) when a key is present.
Falls back to a stub dataset for development/demo when no key is configured.
Data-only: no transaction routing, no fund handling.
"""

from __future__ import annotations

import httpx
from dataclasses import dataclass, field
from typing import Optional

from config import CRUNCHBASE_API_KEY

CRUNCHBASE_BASE = "https://api.crunchbase.com/api/v4"


@dataclass
class CrunchbaseSignals:
    company_name: str
    cb_permalink: str = ""
    total_funding_usd: Optional[float] = None
    last_round_type: str = ""          # e.g. "Seed", "Series A"
    last_round_date: str = ""
    last_round_amount_usd: Optional[float] = None
    investor_count: int = 0
    notable_investors: list[str] = field(default_factory=list)
    employee_count_range: str = ""     # e.g. "1-10", "11-50"
    founded_year: Optional[int] = None
    categories: list[str] = field(default_factory=list)
    score: float = 0.0                 # Normalized 0–100 deal quality score
    error: Optional[str] = None
    is_stub: bool = False              # True if no API key — using stub data


def fetch_crunchbase_signals(company_name: str, cb_permalink: str = "") -> CrunchbaseSignals:
    """
    Fetch deal-flow signals from Crunchbase.

    When CRUNCHBASE_API_KEY is not set, returns a clearly-marked stub.
    This allows the scorer and memo generator to function in dev mode.

    Args:
        company_name:  Human-readable company name.
        cb_permalink:  Crunchbase permalink slug (e.g. 'openai').

    Returns:
        CrunchbaseSignals with deal quality metrics and a 0–100 score.
    """
    if not CRUNCHBASE_API_KEY:
        return _stub_signals(company_name)

    slug = cb_permalink or company_name.lower().replace(" ", "-")
    result = CrunchbaseSignals(company_name=company_name, cb_permalink=slug)

    with httpx.Client(timeout=15) as client:
        # Organization entity
        r = client.get(
            f"{CRUNCHBASE_BASE}/entities/organizations/{slug}",
            params={
                "user_key": CRUNCHBASE_API_KEY,
                "field_ids": (
                    "short_description,funding_total,last_funding_type,"
                    "last_funding_at,num_employees_enum,founded_on,"
                    "categories,num_investors"
                ),
            },
        )

        if r.status_code != 200:
            result.error = f"Crunchbase API error: {r.status_code}"
            return result

        props = r.json().get("properties", {})
        result.total_funding_usd = _parse_money(props.get("funding_total"))
        result.last_round_type = props.get("last_funding_type", "")
        result.last_round_date = props.get("last_funding_at", "")
        result.investor_count = props.get("num_investors", 0) or 0
        result.employee_count_range = props.get("num_employees_enum", "")
        result.categories = [
            c.get("value", "") for c in (props.get("categories") or [])
        ]
        raw_year = props.get("founded_on", {})
        result.founded_year = raw_year.get("value", "")[:4] if isinstance(raw_year, dict) else None

        # Funding rounds — get last round amount
        r2 = client.get(
            f"{CRUNCHBASE_BASE}/entities/organizations/{slug}/funding_rounds",
            params={"user_key": CRUNCHBASE_API_KEY, "field_ids": "money_raised,announced_on,investment_type"},
        )
        if r2.status_code == 200:
            rounds = r2.json().get("entities", [])
            if rounds:
                latest = rounds[0].get("properties", {})
                result.last_round_amount_usd = _parse_money(latest.get("money_raised"))

    result.score = _compute_deal_score(result)
    return result


def _stub_signals(company_name: str) -> CrunchbaseSignals:
    """
    Returns placeholder signals when no API key is available.
    The memo generator will note that Crunchbase data is unavailable.
    """
    return CrunchbaseSignals(
        company_name=company_name,
        total_funding_usd=None,
        last_round_type="N/A (no API key)",
        investor_count=0,
        employee_count_range="Unknown",
        score=50.0,   # Neutral score — neither penalise nor reward
        is_stub=True,
        error="CRUNCHBASE_API_KEY not set. Configure .env to enable live data.",
    )


def _parse_money(value: object) -> Optional[float]:
    """Extracts USD value from Crunchbase money objects."""
    if isinstance(value, dict):
        return value.get("value_usd")
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _compute_deal_score(s: CrunchbaseSignals) -> float:
    """
    Produces a 0–100 deal quality score.
    Weights: round type prestige (40%), investor count (30%), funding size (30%).
    """
    # Round type prestige
    prestige_map = {
        "pre_seed": 40, "seed": 55, "series_a": 70,
        "series_b": 85, "series_c": 90, "angel": 50,
        "convertible_note": 45, "equity_crowdfunding": 60,
    }
    round_score = prestige_map.get((s.last_round_type or "").lower(), 50)

    # Investor count: 10+ investors ≈ 100 points
    investor_score = min((s.investor_count or 0) / 10 * 100, 100)

    # Funding size: log-scale, $5M ≈ 100 points
    import math
    if s.total_funding_usd and s.total_funding_usd > 0:
        fund_score = min(math.log10(s.total_funding_usd) / math.log10(5_000_000) * 100, 100)
    else:
        fund_score = 0.0

    return round(
        round_score * 0.40 + investor_score * 0.30 + fund_score * 0.30,
        2,
    )
