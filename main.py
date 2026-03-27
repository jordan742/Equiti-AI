"""
Equiti-AI — Stage 1 Intelligence Layer
Alpha Scanner Entry Point

Usage:
    # Scan a specific deal (with GitHub data)
    python main.py --company "Acme AI" --github-owner acme-ai --github-repo core

    # Scan the live Reg CF EDGAR feed (last 90 days, top 10 deals)
    python main.py --feed

    # Demo mode (no API keys required)
    python main.py --demo

Safe Mode: This tool is data-only. It never handles, routes, or
custodies user funds. All execution must go through a licensed
Broker-Dealer portal.
"""

import argparse
import sys

from config import SAFE_MODE
from scanner.alpha_scanner import scan_deal, scan_regcf_feed
from scanner.models.dcf_model import DCFInputs
from scanner.output.memo_formatter import print_deal_analysis, print_feed_summary


def run_demo() -> None:
    """
    Demo scan using a public GitHub repo as a proxy for a Reg CF startup.
    No API keys required — shows the full pipeline with GitHub data only.
    """
    print("\n[Demo Mode] Running Alpha Scan on 'Hugging Face' using public GitHub data...\n")

    dcf = DCFInputs(
        company_name="Hugging Face (Demo)",
        current_arr=50_000_000,
        revenue_growth_rate_y1=1.20,
        revenue_growth_rate_y2=0.90,
        revenue_growth_rate_y3=0.60,
        revenue_growth_rate_y4=0.40,
        revenue_growth_rate_y5=0.25,
        current_offering_valuation=4_500_000_000,
        wacc=0.30,
    )

    analysis = scan_deal(
        company_name="Hugging Face (Demo)",
        github_owner="huggingface",
        github_repo="transformers",
        dcf_inputs=dcf,
        extra_context=(
            "Open-source ML model hub. ~500k public models. "
            "Series D at $4.5B valuation. Demo purposes only — "
            "not a current Reg CF offering."
        ),
    )

    print_deal_analysis(analysis)


def run_feed(days_back: int = 90, max_deals: int = 10) -> None:
    """Pull and score the live Reg CF filing feed from SEC EDGAR."""
    print(f"\nFetching Reg CF deals from last {days_back} days (max {max_deals})...\n")
    analyses = scan_regcf_feed(days_back=days_back, max_deals=max_deals)
    if not analyses:
        print("No deals found or EDGAR API unavailable.")
        return
    print_feed_summary(analyses)


def run_single(
    company: str,
    github_owner: str,
    github_repo: str,
    offering_valuation: float,
    current_arr: float,
) -> None:
    """Scan a single company with provided parameters."""
    dcf = None
    if current_arr > 0 and offering_valuation > 0:
        dcf = DCFInputs(
            company_name=company,
            current_arr=current_arr,
            revenue_growth_rate_y1=1.50,
            revenue_growth_rate_y2=1.00,
            revenue_growth_rate_y3=0.70,
            revenue_growth_rate_y4=0.45,
            revenue_growth_rate_y5=0.25,
            current_offering_valuation=offering_valuation,
        )

    analysis = scan_deal(
        company_name=company,
        github_owner=github_owner or None,
        github_repo=github_repo or None,
        dcf_inputs=dcf,
    )
    print_deal_analysis(analysis)


def main() -> None:
    assert SAFE_MODE, "CRITICAL: SAFE_MODE is disabled. Aborting."

    parser = argparse.ArgumentParser(
        description="Equiti-AI Alpha Scanner — Reg CF Deal Intelligence"
    )
    parser.add_argument("--demo", action="store_true", help="Run demo scan (no API keys needed)")
    parser.add_argument("--feed", action="store_true", help="Scan live Reg CF EDGAR feed")
    parser.add_argument("--company", type=str, default="", help="Company name to scan")
    parser.add_argument("--github-owner", type=str, default="", help="GitHub org/user")
    parser.add_argument("--github-repo", type=str, default="", help="GitHub repo name")
    parser.add_argument("--valuation", type=float, default=0, help="Current offering pre-money valuation (USD)")
    parser.add_argument("--arr", type=float, default=0, help="Current ARR / TTM revenue (USD)")
    parser.add_argument("--days-back", type=int, default=90, help="Days back for EDGAR feed")
    parser.add_argument("--max-deals", type=int, default=10, help="Max deals from EDGAR feed")

    args = parser.parse_args()

    if args.demo:
        run_demo()
    elif args.feed:
        run_feed(days_back=args.days_back, max_deals=args.max_deals)
    elif args.company:
        run_single(
            company=args.company,
            github_owner=args.github_owner,
            github_repo=args.github_repo,
            offering_valuation=args.valuation,
            current_arr=args.arr,
        )
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
