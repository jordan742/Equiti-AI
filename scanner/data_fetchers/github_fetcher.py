"""
GitHub Alternative Data Fetcher
Pulls star growth, commit velocity, and contributor signals for a repo.
Uses the public GitHub REST API (no key required; token raises rate limit).
"""

from __future__ import annotations

import httpx
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from typing import Optional

from config import GITHUB_API_BASE, GITHUB_TOKEN


@dataclass
class GitHubSignals:
    repo: str
    stars: int = 0
    stars_30d_delta: int = 0        # Star growth over last 30 days (approx)
    forks: int = 0
    open_issues: int = 0
    commits_30d: int = 0            # Commits in last 30 days
    contributors: int = 0
    last_push_days_ago: int = 0     # Days since last commit (staleness check)
    language: str = ""
    score: float = 0.0              # Normalized 0–100 momentum score
    error: Optional[str] = None


def _headers() -> dict:
    h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h


def fetch_github_signals(owner: str, repo: str) -> GitHubSignals:
    """
    Fetch GitHub momentum signals for a given repo.

    Args:
        owner: GitHub username or org (e.g. 'openai')
        repo:  Repository name (e.g. 'whisper')

    Returns:
        GitHubSignals dataclass with raw metrics and a composite momentum score.
    """
    slug = f"{owner}/{repo}"
    result = GitHubSignals(repo=slug)

    with httpx.Client(headers=_headers(), timeout=15) as client:
        # ── Repo metadata ──────────────────────────────────────────────────
        r = client.get(f"{GITHUB_API_BASE}/repos/{slug}")
        if r.status_code != 200:
            result.error = f"Repo not found or API error: {r.status_code}"
            return result

        meta = r.json()
        result.stars = meta.get("stargazers_count", 0)
        result.forks = meta.get("forks_count", 0)
        result.open_issues = meta.get("open_issues_count", 0)
        result.language = meta.get("language") or ""

        pushed_at = meta.get("pushed_at", "")
        if pushed_at:
            pushed_dt = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            result.last_push_days_ago = (datetime.now(timezone.utc) - pushed_dt).days

        # ── Commit activity (last 52 weeks, GitHub aggregates by week) ──────
        r2 = client.get(f"{GITHUB_API_BASE}/repos/{slug}/stats/commit_activity")
        if r2.status_code == 200:
            weekly = r2.json()  # list of 52 weekly objects
            if isinstance(weekly, list) and len(weekly) >= 4:
                # Last ~30 days = last 4 weeks
                result.commits_30d = sum(w.get("total", 0) for w in weekly[-4:])

        # ── Contributors ───────────────────────────────────────────────────
        r3 = client.get(
            f"{GITHUB_API_BASE}/repos/{slug}/contributors",
            params={"per_page": 100, "anon": "false"},
        )
        if r3.status_code == 200:
            result.contributors = len(r3.json())

        # ── Star history delta (approx via stargazers with timestamps) ──────
        # We sample the last page of stargazers to estimate 30-day delta.
        # This avoids paginating all stars; it's an approximation.
        star_headers = {**_headers(), "Accept": "application/vnd.github.star+json"}
        r4 = client.get(
            f"{GITHUB_API_BASE}/repos/{slug}/stargazers",
            headers=star_headers,
            params={"per_page": 100},
        )
        if r4.status_code == 200:
            stars_data = r4.json()
            cutoff = datetime.now(timezone.utc) - timedelta(days=30)
            result.stars_30d_delta = sum(
                1 for s in stars_data
                if isinstance(s, dict)
                and datetime.fromisoformat(
                    s.get("starred_at", "1970-01-01T00:00:00Z").replace("Z", "+00:00")
                ) >= cutoff
            )

    result.score = _compute_momentum_score(result)
    return result


def _compute_momentum_score(s: GitHubSignals) -> float:
    """
    Produces a 0–100 momentum score from raw GitHub signals.
    Weights: star growth (40%), commits (30%), contributors (20%), freshness (10%).
    """
    # Star growth: log-scale, 100+ new stars in 30d ≈ 100 points
    import math
    star_score = min(math.log1p(s.stars_30d_delta) / math.log1p(100) * 100, 100)

    # Commit velocity: 50+ commits/30d ≈ 100 points
    commit_score = min(s.commits_30d / 50 * 100, 100)

    # Contributors: 20+ contributors ≈ 100 points
    contrib_score = min(s.contributors / 20 * 100, 100)

    # Freshness: pushed within 7 days = 100, >90 days = 0
    freshness = max(0, 1 - s.last_push_days_ago / 90) * 100

    return round(
        star_score * 0.40
        + commit_score * 0.30
        + contrib_score * 0.20
        + freshness * 0.10,
        2,
    )
