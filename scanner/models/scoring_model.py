"""
Composite Deal Scoring Model

Combines GitHub momentum, hiring velocity, Crunchbase deal quality,
and DCF upside into a single "Alpha Score" (0–100).

Higher scores surface deals that warrant deeper analysis.
NOT a buy recommendation — analytical signal only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from config import SCORE_WEIGHTS
from scanner.data_fetchers.github_fetcher import GitHubSignals
from scanner.data_fetchers.crunchbase_fetcher import CrunchbaseSignals
from scanner.data_fetchers.hiring_fetcher import HiringSignals
from scanner.models.dcf_model import DCFResult


@dataclass
class AlphaScore:
    company_name: str
    github_score: float           # 0–100
    hiring_score: float           # 0–100
    deal_score: float             # 0–100
    dcf_score: float              # 0–100
    composite_score: float        # 0–100 weighted aggregate
    signal_tier: str              # "Strong", "Moderate", "Weak", "Insufficient Data"
    missing_data_flags: list[str]
    reg_cf_compliant: bool = True
    disclaimer: str = (
        "Alpha Score is a quantitative signal for research purposes only. "
        "It is NOT investment advice. Equiti-AI operates in Safe Mode — "
        "no funds are handled, routed, or custodied by this platform."
    )


def compute_alpha_score(
    company_name: str,
    github: Optional[GitHubSignals] = None,
    hiring: Optional[HiringSignals] = None,
    crunchbase: Optional[CrunchbaseSignals] = None,
    dcf: Optional[DCFResult] = None,
) -> AlphaScore:
    """
    Compute the composite Alpha Score for a deal.

    Missing data sources receive a neutral score of 50 and are flagged.
    This prevents missing APIs from artificially deflating a good deal.

    Args:
        company_name: Target company name.
        github:       GitHubSignals (or None).
        hiring:       HiringSignals (or None).
        crunchbase:   CrunchbaseSignals (or None).
        dcf:          DCFResult (or None).

    Returns:
        AlphaScore with composite score, tier, and data quality flags.
    """
    missing: list[str] = []
    weights = SCORE_WEIGHTS

    # ── GitHub ────────────────────────────────────────────────────────────
    if github and not github.error:
        gh_score = github.score
    else:
        gh_score = 50.0
        missing.append("GitHub (no repo or API error)")

    # ── Hiring ────────────────────────────────────────────────────────────
    if hiring and not hiring.is_stub and not hiring.error:
        hire_score = hiring.score
    else:
        hire_score = 50.0
        missing.append("Hiring velocity (Proxycurl key not configured)")

    # ── Crunchbase ────────────────────────────────────────────────────────
    if crunchbase and not crunchbase.is_stub and not crunchbase.error:
        cb_score = crunchbase.score
    else:
        cb_score = 50.0
        missing.append("Deal quality (Crunchbase key not configured)")

    # ── DCF ───────────────────────────────────────────────────────────────
    if dcf:
        d_score = dcf.dcf_score
    else:
        d_score = 50.0
        missing.append("DCF upside (no financial inputs provided)")

    # ── Weighted Composite ────────────────────────────────────────────────
    composite = (
        gh_score   * weights["github_momentum"]
        + hire_score * weights["hiring_velocity"]
        + cb_score   * weights["deal_quality"]
        + d_score    * weights["dcf_upside"]
    )
    composite = round(composite, 2)

    # ── Signal Tier ───────────────────────────────────────────────────────
    if len(missing) >= 3:
        tier = "Insufficient Data"
    elif composite >= 75:
        tier = "Strong"
    elif composite >= 55:
        tier = "Moderate"
    else:
        tier = "Weak"

    return AlphaScore(
        company_name=company_name,
        github_score=round(gh_score, 2),
        hiring_score=round(hire_score, 2),
        deal_score=round(cb_score, 2),
        dcf_score=round(d_score, 2),
        composite_score=composite,
        signal_tier=tier,
        missing_data_flags=missing,
    )
