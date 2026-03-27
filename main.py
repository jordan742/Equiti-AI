import sys
import argparse
from harvester import harvest
from scorer import score
from compliance import check_compliance


def get_deal_memo(wefunder_url: str, current_offer_amount: float = 500_000) -> None:
    print(f"\nRunning Equiti-AI scan for: {wefunder_url}\n")

    financials = harvest(wefunder_url)
    compliance = check_compliance(financials.cik, current_offer_amount)
    result = score(financials)

    compliance_label = "PASS" if compliance.compliant else "FAIL"
    key_risk = result.investment_thesis.split(". ")[-1].strip().rstrip(".")

    print("=" * 50)
    print(f"  DEAL MEMO")
    print("=" * 50)
    print(f"  Deal Name         : {financials.company_name or financials.cik}")
    print(f"  Health Score      : {result.score:.1f} / 10")
    print(f"  Compliance Status : {compliance_label}")
    print(f"  Key Risk          : {key_risk}.")
    print("=" * 50)
    print("  [Safe Mode] Data only. Not investment advice.")
    print("=" * 50)


def main() -> None:
    parser = argparse.ArgumentParser(description="Equiti-AI — Reg CF Deal Memo Generator")
    parser.add_argument("url", help="Wefunder campaign URL")
    parser.add_argument(
        "--offer",
        type=float,
        default=500_000,
        help="Current offer amount in USD (default: 500000)",
    )
    args = parser.parse_args()
    get_deal_memo(args.url, args.offer)


if __name__ == "__main__":
    main()
