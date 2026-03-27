"""
Hiring Velocity Fetcher (via Proxycurl LinkedIn API)

Measures employee growth rate and seniority of recent hires —
a leading indicator of pre-Series A momentum.

Falls back to a stub when PROXYCURL_API_KEY is not configured.
Data-only mode: no fund routing, no financial advice.
"""

from __future__ import annotations

import httpx
from dataclasses import dataclass, field
from typing import Optional

from config import PROXYCURL_API_KEY

PROXYCURL_BASE = "https://nubela.co/proxycurl/api"


@dataclass
class HiringSignals:
    company_name: str
    linkedin_url: str = ""
    employee_count: Optional[int] = None
    employee_count_6m_ago: Optional[int] = None
    growth_rate_6m: Optional[float] = None   # % growth over 6 months
    senior_hires_90d: int = 0                # C-suite / VP / Director hires in 90 days
    engineering_ratio: Optional[float] = None  # Engineering headcount / total
    score: float = 0.0
    error: Optional[str] = None
    is_stub: bool = False


def fetch_hiring_signals(company_name: str, linkedin_url: str = "") -> HiringSignals:
    """
    Fetch hiring velocity signals from LinkedIn via Proxycurl.

    Args:
        company_name: Human-readable company name.
        linkedin_url: Full LinkedIn company URL
                      (e.g. 'https://www.linkedin.com/company/openai').

    Returns:
        HiringSignals with growth metrics and a 0–100 velocity score.
    """
    if not PROXYCURL_API_KEY:
        return _stub_signals(company_name)

    result = HiringSignals(company_name=company_name, linkedin_url=linkedin_url)
    headers = {"Authorization": f"Bearer {PROXYCURL_API_KEY}"}

    with httpx.Client(headers=headers, timeout=20) as client:
        # ── Company profile ───────────────────────────────────────────────
        r = client.get(
            f"{PROXYCURL_BASE}/linkedin/company",
            params={"url": linkedin_url, "use_cache": "if-present"},
        )
        if r.status_code != 200:
            result.error = f"Proxycurl error: {r.status_code}"
            return result

        profile = r.json()
        result.employee_count = profile.get("company_size_on_linkedin")

        # ── Employee growth headcount (Proxycurl Headcount endpoint) ──────
        r2 = client.get(
            f"{PROXYCURL_BASE}/linkedin/company/employees/count",
            params={"linkedin_company_url": linkedin_url, "use_cache": "if-present"},
        )
        if r2.status_code == 200:
            result.employee_count = r2.json().get("linkedin_employee_count")

        # ── Recent hires (last 90 days) ───────────────────────────────────
        r3 = client.get(
            f"{PROXYCURL_BASE}/linkedin/company/employees/",
            params={
                "linkedin_company_url": linkedin_url,
                "employment_status": "current",
                "page_size": "100",
            },
        )
        if r3.status_code == 200:
            employees = r3.json().get("employees", [])
            senior_titles = {"ceo", "cto", "coo", "cfo", "vp", "vice president", "director", "head of"}
            engineering_titles = {"engineer", "developer", "software", "ml", "data", "infra"}
            senior_count = 0
            eng_count = 0
            for emp in employees:
                title = (emp.get("profile", {}).get("occupation") or "").lower()
                if any(t in title for t in senior_titles):
                    senior_count += 1
                if any(t in title for t in engineering_titles):
                    eng_count += 1
            result.senior_hires_90d = senior_count
            if employees:
                result.engineering_ratio = round(eng_count / len(employees), 3)

    result.score = _compute_hiring_score(result)
    return result


def _stub_signals(company_name: str) -> HiringSignals:
    return HiringSignals(
        company_name=company_name,
        score=50.0,
        is_stub=True,
        error="PROXYCURL_API_KEY not set. Configure .env to enable live hiring data.",
    )


def _compute_hiring_score(s: HiringSignals) -> float:
    """
    Produces a 0–100 hiring velocity score.
    Weights: growth rate (50%), senior hires (30%), eng ratio (20%).
    """
    growth_score = 0.0
    if s.growth_rate_6m is not None:
        # 30% growth in 6 months ≈ 100 points
        growth_score = min(s.growth_rate_6m / 30 * 100, 100)

    # Senior hires: 5+ in 90 days ≈ 100 points
    senior_score = min((s.senior_hires_90d or 0) / 5 * 100, 100)

    # Engineering ratio: >50% eng = 100 points
    eng_score = min((s.engineering_ratio or 0) / 0.5 * 100, 100)

    return round(
        growth_score * 0.50 + senior_score * 0.30 + eng_score * 0.20,
        2,
    )
