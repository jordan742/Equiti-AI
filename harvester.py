import os
import re
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from edgar import Company

load_dotenv()

SEC_IDENTITY = os.getenv("SEC_IDENTITY", "Equiti-AI equiti@example.com")


class StartupFinancials(BaseModel):
    cik: str
    company_name: Optional[str] = None
    cash: Optional[float] = None
    net_income: Optional[float] = None
    revenues: Optional[float] = None
    short_term_debt: Optional[float] = None
    min_investment: Optional[float] = None


def _extract_cik_from_url(url: str) -> Optional[str]:
    """Extract a numeric CIK from an SEC-related URL."""
    match = re.search(r'CIK=?(\d+)', url, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r'/(\d{7,10})/', url)
    if match:
        return match.group(1)
    return None


def _extract_min_investment(soup: "BeautifulSoup") -> Optional[float]:
    """
    Scrape the Wefunder campaign page for a minimum investment amount.
    Looks for patterns like 'Minimum Investment', 'Min. Investment', '$X minimum'.
    """
    patterns = [
        r'minimum\s+investment[^\$]*\$\s*([\d,]+)',
        r'min\.?\s+investment[^\$]*\$\s*([\d,]+)',
        r'\$\s*([\d,]+)\s+minimum',
        r'invest\s+as\s+little\s+as\s+\$\s*([\d,]+)',
        r'starting\s+at\s+\$\s*([\d,]+)',
    ]
    text = soup.get_text(" ", strip=True)
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            try:
                return float(m.group(1).replace(",", ""))
            except ValueError:
                continue

    # Fallback: scan data attributes and aria-labels for dollar amounts near "min"
    for tag in soup.find_all(True, string=re.compile(r'minimum', re.IGNORECASE)):
        nearby = tag.find_next(string=re.compile(r'\$[\d,]+'))
        if nearby:
            m2 = re.search(r'\$([\d,]+)', nearby)
            if m2:
                try:
                    return float(m2.group(1).replace(",", ""))
                except ValueError:
                    continue
    return None


def _find_form_c_link(campaign_url: str) -> tuple[Optional[str], Optional[float]]:
    """
    Scrape a Wefunder campaign page.
    Returns (form_c_link, min_investment).
    """
    headers = {"User-Agent": SEC_IDENTITY}
    response = requests.get(campaign_url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    min_investment = _extract_min_investment(soup)

    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        text = tag.get_text(strip=True).lower()
        if "form c" in text or "form-c" in text or ("sec.gov" in href and "/Archives/" in href):
            return href, min_investment
        if re.search(r'edgar.*CIK', href, re.IGNORECASE):
            return href, min_investment

    # Fallback: scan all links for SEC EDGAR patterns
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        if "sec.gov" in href and re.search(r'\d{7,10}', href):
            return href, min_investment

    return None, min_investment


def _extract_xbrl_fact(filing, concept: str) -> Optional[float]:
    """
    Attempt to extract a numeric XBRL fact from an edgartools filing object.
    Tries common US-GAAP namespace variants.
    """
    namespaces = ["us-gaap", "dei"]
    for ns in namespaces:
        try:
            facts = filing.xbrl().facts
            key = f"{ns}:{concept}"
            if hasattr(facts, "get"):
                val = facts.get(key)
                if val is not None:
                    return float(val)
            # edgartools may expose facts as attributes or via a query method
            if hasattr(facts, concept):
                val = getattr(facts, concept)
                if val is not None:
                    return float(val)
        except Exception:
            continue

    # Try the facts dataframe if available
    try:
        df = filing.xbrl().facts.to_dataframe()
        matches = df[df["concept"].str.endswith(concept)]
        if not matches.empty:
            return float(matches.iloc[-1]["value"])
    except Exception:
        pass

    return None


def harvest(campaign_url: str) -> StartupFinancials:
    """
    Harvest SEC financials for a startup from its Wefunder campaign URL.

    Steps:
    1. Scrape the Wefunder page for a Form C link.
    2. Extract the CIK from that link.
    3. Use edgartools to fetch the latest Form C filing.
    4. Extract XBRL facts: Cash, NetIncome, Revenues, ShortTermDebt.
    5. Return a StartupFinancials Pydantic model.

    Args:
        campaign_url: Full Wefunder campaign URL
                      (e.g. 'https://wefunder.com/acme').

    Returns:
        StartupFinancials with available financial data.

    Raises:
        ValueError: If no Form C link or CIK can be found.
        requests.HTTPError: If the campaign page cannot be fetched.
    """
    form_c_link, min_investment = _find_form_c_link(campaign_url)
    if not form_c_link:
        raise ValueError(f"No Form C link found on page: {campaign_url}")

    cik = _extract_cik_from_url(form_c_link)
    if not cik:
        raise ValueError(f"Could not extract CIK from link: {form_c_link}")

    company = Company(cik)
    filings = company.get_filings(form="C")
    if not filings:
        raise ValueError(f"No Form C filings found for CIK {cik}")

    latest = filings.latest()

    return StartupFinancials(
        cik=cik,
        company_name=company.name,
        cash=_extract_xbrl_fact(latest, "Cash"),
        net_income=_extract_xbrl_fact(latest, "NetIncomeLoss"),
        revenues=_extract_xbrl_fact(latest, "Revenues"),
        short_term_debt=_extract_xbrl_fact(latest, "ShortTermBorrowings"),
        min_investment=min_investment,
    )
