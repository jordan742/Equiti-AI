"""
Alpha Scanner — Stage 1 Intelligence Layer Orchestrator

Coordinates all data fetchers, the financial model, composite scorer,
and memo generator into a single pipeline per deal.

Usage:
    from scanner.alpha_scanner import scan_deal, scan_regcf_feed

Safe Mode: This module NEVER routes to execution, handles funds,
or provides investment advice. Output is analytical data only.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Optional

from config import SAFE_MODE
from scanner.data_fetchers.github_fetcher import GitHubSignals, fetch_github_signals
from scanner.data_fetchers.crunchbase_fetcher import CrunchbaseSignals, fetch_crunchbase_signals
from scanner.data_fetchers.hiring_fetcher import HiringSignals, fetch_hiring_signals
from scanner.data_fetchers.regcf_fetcher import RegCFDeal, fetch_recent_regcf_deals
from scanner.models.dcf_model import DCFInputs, DCFResult, run_dcf
from scanner.models.scoring_model import AlphaScore, compute_alpha_score
from scanner.models.memo_generator import generate_investment_memo


@dataclass
class DealAnalysis:
    """Complete analysis package for a single deal."""
    company_name: str
    regcf_deal: Optional[RegCFDeal]
    github: Optional[GitHubSignals]
    hiring: Optional[HiringSignals]
    crunchbase: Optional[CrunchbaseSignals]
    dcf: Optional[DCFResult]
    alpha_score: AlphaScore
    investment_memo: str
    safe_mode_active: bool = True

    def summary(self) -> str:
        return (
            f"{self.company_name} | "
            f"Alpha: {self.alpha_score.composite_score}/100 ({self.alpha_score.signal_tier})"
        )


def scan_deal(
    company_name: str,
    github_owner: Optional[str] = None,
    github_repo: Optional[str] = None,
    linkedin_url: Optional[str] = None,
    cb_permalink: Optional[str] = None,
    dcf_inputs: Optional[DCFInputs] = None,
    regcf_deal: Optional[RegCFDeal] = None,
    extra_context: str = "",
) -> DealAnalysis:
    """
    Run a full Alpha Scan on a single company.

    This function:
    1. Fetches GitHub, hiring, and Crunchbase signals in parallel.
    2. Runs the DCF model (if inputs provided).
    3. Computes the composite Alpha Score.
    4. Generates an Investment Memo via Claude.

    Args:
        company_name:   Target company name.
        github_owner:   GitHub org/user (e.g. 'openai').
        github_repo:    GitHub repo name (e.g. 'gpt-3').
        linkedin_url:   LinkedIn company URL for hiring data.
        cb_permalink:   Crunchbase permalink slug.
        dcf_inputs:     Financial model inputs (optional).
        regcf_deal:     Pre-fetched RegCFDeal object (optional).
        extra_context:  Qualitative notes to include in the memo.

    Returns:
        DealAnalysis with all signals, scores, and the Investment Memo.
    """
    assert SAFE_MODE, "SAFE_MODE must be True. This platform does not handle funds."

    # ── Fetch data in parallel (I/O-bound) ────────────────────────────────
    github: Optional[GitHubSignals] = None
    hiring: Optional[HiringSignals] = None
    crunchbase: Optional[CrunchbaseSignals] = None

    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {}

        if github_owner and github_repo:
            futures["github"] = pool.submit(fetch_github_signals, github_owner, github_repo)

        if linkedin_url:
            futures["hiring"] = pool.submit(fetch_hiring_signals, company_name, linkedin_url)
        else:
            futures["hiring"] = pool.submit(fetch_hiring_signals, company_name, "")

        futures["crunchbase"] = pool.submit(
            fetch_crunchbase_signals, company_name, cb_permalink or ""
        )

        if "github" in futures:
            github = futures["github"].result()
        hiring = futures["hiring"].result()
        crunchbase = futures["crunchbase"].result()

    # ── Run DCF model ─────────────────────────────────────────────────────
    dcf: Optional[DCFResult] = None
    if dcf_inputs:
        dcf = run_dcf(dcf_inputs)

    # ── Compute Alpha Score ───────────────────────────────────────────────
    alpha_score = compute_alpha_score(
        company_name=company_name,
        github=github,
        hiring=hiring,
        crunchbase=crunchbase,
        dcf=dcf,
    )

    # ── Generate Investment Memo ──────────────────────────────────────────
    memo = generate_investment_memo(
        company_name=company_name,
        alpha_score=alpha_score,
        github=github,
        hiring=hiring,
        crunchbase=crunchbase,
        dcf=dcf,
        extra_context=extra_context,
    )

    return DealAnalysis(
        company_name=company_name,
        regcf_deal=regcf_deal,
        github=github,
        hiring=hiring,
        crunchbase=crunchbase,
        dcf=dcf,
        alpha_score=alpha_score,
        investment_memo=memo,
        safe_mode_active=SAFE_MODE,
    )


def scan_regcf_feed(
    days_back: int = 90,
    max_deals: int = 10,
    github_map: Optional[dict[str, tuple[str, str]]] = None,
) -> list[DealAnalysis]:
    """
    Scan the live SEC EDGAR Reg CF filing feed and score each deal.

    This is the "fire hose" entry point — pulls recent Form C filings
    and runs a lightweight scan on each one. GitHub/hiring/Crunchbase
    data is only fetched for companies in `github_map`.

    Args:
        days_back:   How many days back to search EDGAR.
        max_deals:   Maximum number of deals to process.
        github_map:  Optional dict mapping company_name → (owner, repo)
                     to enable GitHub signal fetching per deal.

    Returns:
        List of DealAnalysis objects, sorted by Alpha Score descending.
    """
    assert SAFE_MODE, "SAFE_MODE must be True."

    deals = fetch_recent_regcf_deals(days_back=days_back, max_results=max_deals)
    results: list[DealAnalysis] = []

    for deal in deals:
        if deal.error:
            continue

        gh_owner, gh_repo = None, None
        if github_map and deal.company_name in github_map:
            gh_owner, gh_repo = github_map[deal.company_name]

        analysis = scan_deal(
            company_name=deal.company_name,
            github_owner=gh_owner,
            github_repo=gh_repo,
            regcf_deal=deal,
        )
        results.append(analysis)

    results.sort(key=lambda a: a.alpha_score.composite_score, reverse=True)
    return results
