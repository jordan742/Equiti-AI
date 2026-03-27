"""
Central configuration for Equiti-AI.
All environment variables and constants are loaded here.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Safety ───────────────────────────────────────────────────────────────────
# SAFE_MODE = True means the platform NEVER handles, routes, or custodies
# user funds. It operates as a data-and-analysis layer only.
SAFE_MODE: bool = os.getenv("SAFE_MODE", "True").lower() == "true"

# ── API Keys ─────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
CRUNCHBASE_API_KEY: str = os.getenv("CRUNCHBASE_API_KEY", "")
PROXYCURL_API_KEY: str = os.getenv("PROXYCURL_API_KEY", "")

# ── SEC EDGAR ─────────────────────────────────────────────────────────────────
# Public API — no key required. Identifies as Equiti-AI per SEC guidelines.
EDGAR_USER_AGENT: str = "Equiti-AI research@equiti-ai.com"
EDGAR_BASE_URL: str = "https://efts.sec.gov/LATEST/search-index"
EDGAR_SEARCH_URL: str = "https://efts.sec.gov/LATEST/search-index?q=%22Form+C%22&dateRange=custom&startdt={start}&enddt={end}&forms=C"

# ── GitHub API ────────────────────────────────────────────────────────────────
GITHUB_API_BASE: str = "https://api.github.com"

# ── Scoring Weights ───────────────────────────────────────────────────────────
# Composite score = weighted sum of normalized sub-scores (0–100 each)
SCORE_WEIGHTS: dict = {
    "github_momentum": 0.25,   # Star growth, commit velocity, contributors
    "hiring_velocity": 0.20,   # Employee growth rate, seniority of new hires
    "deal_quality":    0.20,   # Crunchbase investor quality, round size
    "dcf_upside":      0.35,   # DCF-implied upside vs. current valuation
}

# ── Reg CF 2026 Limits ────────────────────────────────────────────────────────
# SEC Regulation Crowdfunding investment caps (inflation-adjusted, 2026)
REG_CF_MAX_RAISE: int = 5_000_000          # Max per issuer per 12 months
REG_CF_NON_ACCREDITED_ANNUAL_CAP: float = 0.10  # 10% of annual income or net worth
REG_CF_MIN_NON_ACCREDITED: int = 2_200     # Floor: $2,200 regardless of income

# ── Claude Model ─────────────────────────────────────────────────────────────
CLAUDE_MODEL: str = "claude-opus-4-6"
CLAUDE_MAX_TOKENS: int = 2048
