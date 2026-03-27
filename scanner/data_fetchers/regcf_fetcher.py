"""
SEC EDGAR Reg CF Fetcher
Pulls Form C filings from the SEC EDGAR full-text search API.
No API key required. Identifies per SEC user-agent guidelines.
Data-only: never routes to execution or handles funds.
"""

from __future__ import annotations

import httpx
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional

from config import EDGAR_USER_AGENT


EDGAR_SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
EDGAR_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
EDGAR_FILING_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{accession_clean}/{filename}"


@dataclass
class RegCFDeal:
    company_name: str
    cik: str
    filing_date: str
    accession_number: str
    form_type: str                    # "C", "C-U" (update), "C-AR" (annual report)
    offering_amount: Optional[float] = None   # Target raise in USD
    max_offering_amount: Optional[float] = None
    deadline: Optional[str] = None
    sec_url: str = ""
    error: Optional[str] = None


def fetch_recent_regcf_deals(
    days_back: int = 90,
    max_results: int = 20,
) -> list[RegCFDeal]:
    """
    Returns recent Form C filings from SEC EDGAR (Reg CF offerings).

    Args:
        days_back:   How many calendar days to look back.
        max_results: Maximum number of deals to return.

    Returns:
        List of RegCFDeal objects with filing metadata.
    """
    start_date = (date.today() - timedelta(days=days_back)).isoformat()
    end_date = date.today().isoformat()

    params = {
        "q": '"Form C"',
        "dateRange": "custom",
        "startdt": start_date,
        "enddt": end_date,
        "forms": "C",
        "_source": "file_date,display_names,entity_name,file_num,period_of_report",
        "from": "0",
        "size": str(max_results),
    }

    headers = {"User-Agent": EDGAR_USER_AGENT}
    deals: list[RegCFDeal] = []

    with httpx.Client(headers=headers, timeout=20) as client:
        r = client.get(EDGAR_SEARCH_URL, params=params)
        if r.status_code != 200:
            return [RegCFDeal(
                company_name="ERROR",
                cik="",
                filing_date="",
                accession_number="",
                form_type="C",
                error=f"EDGAR API returned {r.status_code}",
            )]

        data = r.json()
        hits = data.get("hits", {}).get("hits", [])

        for hit in hits:
            src = hit.get("_source", {})
            entity_names = src.get("display_names", [])
            company = entity_names[0].get("name", "Unknown") if entity_names else "Unknown"
            cik_raw = entity_names[0].get("entity_id", "") if entity_names else ""
            accession = hit.get("_id", "").replace("-", "")

            deal = RegCFDeal(
                company_name=company,
                cik=cik_raw,
                filing_date=src.get("file_date", ""),
                accession_number=accession,
                form_type=src.get("form_type", "C"),
                sec_url=f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik_raw}&type=C&dateb=&owner=include&count=10",
            )
            deals.append(deal)

    return deals


def fetch_deal_details(cik: str, accession_number: str) -> dict:
    """
    Fetches the structured XML data from a specific Form C filing.
    Returns raw offering metadata (raise amount, deadline, description).

    Args:
        cik:              SEC CIK number (zero-padded to 10 digits).
        accession_number: Accession number without dashes.

    Returns:
        Dict with offering fields parsed from the filing index.
    """
    cik_padded = cik.zfill(10)
    accession_dashed = f"{accession_number[:10]}-{accession_number[10:12]}-{accession_number[12:]}"
    index_url = (
        f"https://www.sec.gov/Archives/edgar/data/{cik_padded}/"
        f"{accession_number}/{accession_dashed}-index.htm"
    )

    headers = {"User-Agent": EDGAR_USER_AGENT}
    with httpx.Client(headers=headers, timeout=20) as client:
        r = client.get(index_url)
        # Return raw URL for now; full XML parsing is a future enhancement
        return {
            "index_url": index_url,
            "status": r.status_code,
            "cik": cik,
            "accession": accession_number,
        }
