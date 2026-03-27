import os
from datetime import date, timedelta
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from edgar import Company, set_identity

load_dotenv()

set_identity(os.getenv("SEC_IDENTITY", "Equiti-AI equiti@example.com"))

REG_CF_CAP = 5_000_000


class ComplianceResult(BaseModel):
    cik: str
    compliant: bool
    status: str                      # 'COMPLIANT' or 'NON_COMPLIANT'
    total_raised_12m: float
    current_offer_amount: float
    combined_total: float
    filing_count: int


def _extract_amount_raised(filing) -> float:
    """Pull 'offeringAmount' or 'amountSold' from a C / C-U filing."""
    candidates = [
        "offeringAmount",
        "amountSold",
        "totalAmountSold",
        "totalOfferingAmount",
    ]
    for field in candidates:
        try:
            obj = filing.obj()
            val = getattr(obj, field, None)
            if val is not None:
                return float(val)
        except Exception:
            pass

    # Fallback: XBRL facts dataframe
    try:
        df = filing.xbrl().facts.to_dataframe()
        for field in candidates:
            matches = df[df["concept"].str.endswith(field)]
            if not matches.empty:
                return float(matches.iloc[-1]["value"])
    except Exception:
        pass

    return 0.0


def check_compliance(cik: str, current_offer_amount: float) -> ComplianceResult:
    """
    Check whether a Reg CF issuer is within the $5M annual cap.

    Sums 'Amount Raised' across all Form C and C-U filings in the
    last 12 months, then adds the proposed current offer amount.

    Args:
        cik:                   SEC CIK for the issuer.
        current_offer_amount:  Proposed raise amount for the current offering.

    Returns:
        ComplianceResult with compliant flag, status string, and totals.
    """
    cutoff = date.today() - timedelta(days=365)

    company = Company(cik)
    filings = company.get_filings(form=["C", "C-U"])

    total_raised = 0.0
    filing_count = 0

    for filing in filings:
        filed_date = getattr(filing, "filing_date", None) or getattr(filing, "date", None)
        if filed_date is None:
            continue
        if isinstance(filed_date, str):
            from datetime import datetime
            filed_date = datetime.strptime(filed_date[:10], "%Y-%m-%d").date()
        if filed_date < cutoff:
            continue
        total_raised += _extract_amount_raised(filing)
        filing_count += 1

    combined = total_raised + current_offer_amount
    compliant = combined <= REG_CF_CAP

    return ComplianceResult(
        cik=cik,
        compliant=compliant,
        status="COMPLIANT" if compliant else "NON_COMPLIANT",
        total_raised_12m=total_raised,
        current_offer_amount=current_offer_amount,
        combined_total=combined,
        filing_count=filing_count,
    )
