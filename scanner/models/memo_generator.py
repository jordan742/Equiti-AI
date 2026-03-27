"""
Investment Memo Generator

Uses Claude (claude-opus-4-6) to synthesize all data signals into a
structured Investment Memo — the core output of the Equiti-AI platform.

Output format mirrors institutional VC one-pagers:
  1. Company Snapshot
  2. Alternative Data Signals
  3. Financial Analysis (DCF)
  4. Risk Factors
  5. Alpha Score & Signal Tier
  6. Regulatory Context (Reg CF)
  7. Safe Mode Disclaimer

NOT investment advice. Data-only analytical output.
"""

from __future__ import annotations

import anthropic
from typing import Optional

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, CLAUDE_MAX_TOKENS
from scanner.data_fetchers.github_fetcher import GitHubSignals
from scanner.data_fetchers.crunchbase_fetcher import CrunchbaseSignals
from scanner.data_fetchers.hiring_fetcher import HiringSignals
from scanner.models.dcf_model import DCFResult
from scanner.models.scoring_model import AlphaScore


def generate_investment_memo(
    company_name: str,
    alpha_score: AlphaScore,
    github: Optional[GitHubSignals] = None,
    hiring: Optional[HiringSignals] = None,
    crunchbase: Optional[CrunchbaseSignals] = None,
    dcf: Optional[DCFResult] = None,
    extra_context: str = "",
) -> str:
    """
    Generate a structured investment memo using Claude.

    Args:
        company_name:  Target company.
        alpha_score:   Composite Alpha Score object.
        github:        GitHub signals (optional).
        hiring:        Hiring signals (optional).
        crunchbase:    Crunchbase signals (optional).
        dcf:           DCF result (optional).
        extra_context: Any additional qualitative context to include.

    Returns:
        Formatted markdown investment memo string.
    """
    if not ANTHROPIC_API_KEY:
        return _fallback_memo(company_name, alpha_score, github, hiring, crunchbase, dcf)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = _build_prompt(company_name, alpha_score, github, hiring, crunchbase, dcf, extra_context)

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=CLAUDE_MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


def _build_prompt(
    company_name: str,
    alpha: AlphaScore,
    github: Optional[GitHubSignals],
    hiring: Optional[HiringSignals],
    crunchbase: Optional[CrunchbaseSignals],
    dcf: Optional[DCFResult],
    extra_context: str,
) -> str:
    """Constructs the structured prompt for Claude."""

    # ── GitHub Section ────────────────────────────────────────────────────
    gh_section = "GitHub: No data available."
    if github and not github.error:
        gh_section = (
            f"GitHub ({github.repo}):\n"
            f"  - Stars: {github.stars:,} (30-day delta: +{github.stars_30d_delta})\n"
            f"  - Commits (last 30d): {github.commits_30d}\n"
            f"  - Contributors: {github.contributors}\n"
            f"  - Primary language: {github.language}\n"
            f"  - Last push: {github.last_push_days_ago} days ago\n"
            f"  - Momentum Score: {github.score}/100"
        )

    # ── Hiring Section ────────────────────────────────────────────────────
    hire_section = "Hiring Velocity: No data available (Proxycurl key not configured)."
    if hiring and not hiring.is_stub:
        hire_section = (
            f"Hiring Velocity (LinkedIn):\n"
            f"  - Current headcount: {hiring.employee_count or 'Unknown'}\n"
            f"  - 6-month growth rate: {hiring.growth_rate_6m or 'N/A'}%\n"
            f"  - Senior hires (90d): {hiring.senior_hires_90d}\n"
            f"  - Engineering ratio: {hiring.engineering_ratio or 'N/A'}\n"
            f"  - Hiring Score: {hiring.score}/100"
        )

    # ── Crunchbase Section ────────────────────────────────────────────────
    cb_section = "Deal Flow (Crunchbase): No data available (API key not configured)."
    if crunchbase and not crunchbase.is_stub:
        cb_section = (
            f"Deal Flow (Crunchbase):\n"
            f"  - Last round: {crunchbase.last_round_type} ({crunchbase.last_round_date})\n"
            f"  - Total funding: ${crunchbase.total_funding_usd:,.0f}\n"
            f"  - Investors: {crunchbase.investor_count}\n"
            f"  - Employees: {crunchbase.employee_count_range}\n"
            f"  - Categories: {', '.join(crunchbase.categories[:3])}\n"
            f"  - Deal Quality Score: {crunchbase.score}/100"
        )

    # ── DCF Section ───────────────────────────────────────────────────────
    dcf_section = "Financial Model: No DCF inputs provided."
    if dcf:
        rev_str = " → ".join(f"${r:,.0f}" for r in dcf.projected_revenues)
        dcf_section = (
            f"DCF Analysis:\n"
            f"  - 5-Year Revenue Projections: {rev_str}\n"
            f"  - Terminal Value: ${dcf.terminal_value:,.0f}\n"
            f"  - Enterprise Value (DCF): ${dcf.enterprise_value:,.0f}\n"
            f"  - Implied Upside: {dcf.implied_upside_x}x vs. current offering valuation\n"
            f"  - DCF Score: {dcf.dcf_score}/100"
        )

    # ── Missing Data ──────────────────────────────────────────────────────
    missing_str = (
        "\n".join(f"  - {m}" for m in alpha.missing_data_flags)
        if alpha.missing_data_flags
        else "  - None (all data sources active)"
    )

    extra = f"\nAdditional Context:\n{extra_context}" if extra_context else ""

    return f"""You are an institutional-grade venture capital analyst writing a concise Investment Memo for the Equiti-AI platform.
Equiti-AI is a data-analysis platform that helps retail investors understand Reg CF (Regulation Crowdfunding) deals.
This is NOT investment advice. This is analytical output only. The platform operates in Safe Mode — it NEVER handles, routes, or custodies user funds.

Write a structured Investment Memo for the following company using ONLY the data provided. Do not invent metrics.
Where data is missing, explicitly state "Data unavailable" rather than estimating.

---
COMPANY: {company_name}

ALPHA SCORE: {alpha.composite_score}/100 ({alpha.signal_tier} signal)
  - GitHub Momentum: {alpha.github_score}/100
  - Hiring Velocity: {alpha.hiring_score}/100
  - Deal Quality:    {alpha.deal_score}/100
  - DCF Upside:      {alpha.dcf_score}/100

DATA SOURCES:
{gh_section}

{hire_section}

{cb_section}

{dcf_section}

DATA GAPS:
{missing_str}
{extra}
---

Format the memo in clean Markdown with these sections:
1. **Company Snapshot** (2-3 sentences — what do they do, what stage, what market)
2. **Alternative Data Signals** (summarize GitHub, hiring, and deal-flow data; call out anomalies)
3. **Financial Analysis** (DCF summary; if no DCF data, note limitations)
4. **Key Risk Factors** (3-4 bullet points based on data gaps and stage-appropriate risks)
5. **Alpha Score Summary** (explain what the {alpha.composite_score}/100 means in plain English)
6. **Reg CF Context** (briefly note the $5M raise cap, investor limits, and where to execute via licensed portal)
7. **Disclaimer** (one sentence Safe Mode notice — data only, not advice, no funds handled)

Keep the tone analytical, precise, and institutional. Avoid hype language.
"""


def _fallback_memo(
    company_name: str,
    alpha: AlphaScore,
    github: Optional[GitHubSignals],
    hiring: Optional[HiringSignals],
    crunchbase: Optional[CrunchbaseSignals],
    dcf: Optional[DCFResult],
) -> str:
    """
    Returns a structured text memo without Claude when no API key is set.
    Useful for testing and demo environments.
    """
    lines = [
        f"# Investment Memo: {company_name}",
        f"> *Generated by Equiti-AI Alpha Scanner — Safe Mode Active*",
        "",
        f"## Alpha Score: {alpha.composite_score}/100 ({alpha.signal_tier})",
        "",
        "| Signal | Score |",
        "|--------|-------|",
        f"| GitHub Momentum | {alpha.github_score}/100 |",
        f"| Hiring Velocity | {alpha.hiring_score}/100 |",
        f"| Deal Quality    | {alpha.deal_score}/100 |",
        f"| DCF Upside      | {alpha.dcf_score}/100 |",
        "",
    ]

    if github and not github.error:
        lines += [
            "## GitHub Signals",
            f"- Repo: `{github.repo}`",
            f"- Stars: {github.stars:,} (+{github.stars_30d_delta} in 30d)",
            f"- Commits (30d): {github.commits_30d}",
            f"- Contributors: {github.contributors}",
            "",
        ]

    if dcf:
        lines += [
            "## Financial Model (DCF)",
            f"- Enterprise Value: ${dcf.enterprise_value:,.0f}",
            f"- Implied Upside: {dcf.implied_upside_x}x",
            "",
        ]

    if alpha.missing_data_flags:
        lines += ["## Data Gaps", ""]
        for flag in alpha.missing_data_flags:
            lines.append(f"- {flag}")
        lines.append("")

    lines += [
        "---",
        "*Disclaimer: This memo is analytical output only. Equiti-AI does not provide "
        "investment advice and does not handle, route, or custody user funds. "
        "All investment execution occurs via licensed Broker-Dealer portals.*",
    ]

    return "\n".join(lines)
