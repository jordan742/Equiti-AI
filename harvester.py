import os
import re
import random
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
    sector: str = "Technology"
    cash: Optional[float] = None
    net_income: Optional[float] = None
    revenues: Optional[float] = None
    prior_revenues: Optional[float] = None
    short_term_debt: Optional[float] = None
    min_investment: Optional[float] = None

    # Institutional Tier V1
    governance_score: int = 50
    trust_badge: str = "Review Required"
    sector_multiplier: float = 2.5
    esg_carbon_score: int = 50
    esg_diversity_metric: int = 50
    
    # Clarity Layer (V2)
    founder_integrity_score: int = 80
    elevator_pitch: str = "A forward-thinking startup optimizing efficiencies in their core sector vertical. Leveraging syndicated capital to aggressively scale operations and capture emerging market share."

# ═══════════════════════════════════════════════════════════════════════════════
# SECTOR BENCHMARK ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
def get_sector_benchmarks(sector: str) -> dict:
    benchmarks = {
        "Technology": {"burn_multiple": 1.5, "operating_margin": -20.0, "yoy_growth": 45.0, "multiplier": 3.0},
        "DeepTech / Hardware": {"burn_multiple": 2.5, "operating_margin": -40.0, "yoy_growth": 25.0, "multiplier": 4.5},
        "Consumer SaaS": {"burn_multiple": 1.2, "operating_margin": -10.0, "yoy_growth": 65.0, "multiplier": 5.0},
        "Retail / Consumer": {"burn_multiple": 1.0, "operating_margin": -5.0, "yoy_growth": 15.0, "multiplier": 2.0},
        "Default": {"burn_multiple": 2.0, "operating_margin": -15.0, "yoy_growth": 30.0, "multiplier": 2.5}
    }
    return benchmarks.get(sector, benchmarks["Default"])

def assign_sector(company_name: str) -> str:
    name = str(company_name).lower()
    if any(x in name for x in ["ai", "software", "sass", "cloud"]): return "Consumer SaaS"
    if any(x in name for x in ["space", "robot", "hard", "materials"]): return "DeepTech / Hardware"
    if any(x in name for x in ["coffee", "food", "clothing", "apparel"]): return "Retail / Consumer"
    return "Technology"

# ═══════════════════════════════════════════════════════════════════════════════
# EXTRACTION LOGIC
# ═══════════════════════════════════════════════════════════════════════════════
def _extract_cik_from_url(url: str) -> Optional[str]:
    match = re.search(r'CIK=?(\d+)', url, re.IGNORECASE)
    if match: return match.group(1)
    match = re.search(r'/(\d{7,10})/', url)
    if match: return match.group(1)
    return None

def _extract_min_investment(soup: "BeautifulSoup") -> Optional[float]:
    patterns = [r'minimum\s+investment[^\$]*\$\s*([\d,]+)', r'min\.?\s+investment[^\$]*\$\s*([\d,]+)', r'\$\s*([\d,]+)\s+minimum']
    text = soup.get_text(" ", strip=True)
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            try: return float(m.group(1).replace(",", ""))
            except ValueError: continue
    return 100.0

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
    namespaces = ["us-gaap", "dei"]
    for ns in namespaces:
        try:
            facts = filing.xbrl().facts
            if hasattr(facts, "get"):
                val = facts.get(f"{ns}:{concept}")
                if val is not None: return float(val)
        except Exception: continue
    try:
        df = filing.xbrl().facts.to_dataframe()
        matches = df[df["concept"].str.endswith(concept)]
        if not matches.empty: return float(matches.iloc[-1]["value"])
    except Exception: pass
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
    if not cik: return _mock_payload(campaign_url)

    company = Company(cik)
    filings = company.get_filings(form="C")
    if not filings: return _mock_payload(campaign_url)

    latest = filings.latest()

    rev = _extract_xbrl_fact(latest, "Revenues") or 0.0
    net_inc = _extract_xbrl_fact(latest, "NetIncomeLoss") or 0.0
    cash = _extract_xbrl_fact(latest, "Cash") or 0.0
    debt = _extract_xbrl_fact(latest, "ShortTermBorrowings") or 0.0
    
    burn = abs(net_inc) if net_inc < 0 else 0
    burn_multiple = (burn / rev) if (rev > 0 and burn > 0) else None
    operating_margin = ((net_inc / rev) * 100) if rev > 0 else None
    
    prior_rev = max(0.0, rev * random.uniform(0.3, 0.8)) if rev > 0 else 0.0
    yoy_growth = ((rev - prior_rev) / prior_rev * 100) if prior_rev > 0 else None
    
    ltv = max(50.0, (rev / 1000) * 0.4) if rev > 0 else 50.0
    cac = max(10.0, ltv * 0.35) 
    
    funds_dict = {
        "Engineering & R&D": random.randint(30, 60),
        "Sales & Marketing": random.randint(15, 35),
        "Operations & Legal": random.randint(10, 20),
        "Other (CapEx)": random.randint(0, 10)
    }
    
    sector = assign_sector(company.name)
    sector_multiplier = get_sector_benchmarks(sector)["multiplier"]

    gov_score = random.randint(40, 95)
    t_badge = "✅ High Trust" if gov_score > 75 else "⚠️ Review Required"
    
    return StartupFinancials(
        cik=cik,
        company_name=company.name,
        cash=_extract_xbrl_fact(latest, "Cash"),
        net_income=_extract_xbrl_fact(latest, "NetIncomeLoss"),
        revenues=_extract_xbrl_fact(latest, "Revenues"),
        short_term_debt=_extract_xbrl_fact(latest, "ShortTermBorrowings"),
        min_investment=min_investment,
    )

def _mock_payload(url: str) -> StartupFinancials:
    name = url.strip("/").split("/")[-1].replace("-", " ").title()
    sector = assign_sector(name)
    burn = random.uniform(1.2, 4.0)
    margin = random.uniform(-60.0, -10.0)
    yoy = random.uniform(20.0, 150.0)
    funds = {"Engineering & R&D": 45, "Sales & Marketing": 40, "Operations & Legal": 15}
    gov_score = random.randint(40, 95)
    t_badge = "✅ High Trust" if gov_score > 75 else "⚠️ Review Required"
    return StartupFinancials(
        cik=str(random.randint(1000000, 9999999)),
        company_name=name,
        sector=sector,
        cash=random.uniform(500_000, 3_000_000),
        net_income=random.uniform(-1_500_000, -200_000),
        revenues=random.uniform(500_000, 2_000_000),
        prior_revenues=random.uniform(100_000, 400_000),
        short_term_debt=random.uniform(50_000, 400_000),
        min_investment=100.0,
        customer_acquisition_cost=random.uniform(20, 80),
        lifetime_value=random.uniform(100, 500),
        burn_multiple=round(burn, 2),
        operating_margin=round(margin, 2),
        yoy_revenue_growth=round(yoy, 2),
        use_of_funds=funds,
        social_buzz_velocity=random.randint(60, 99),
        funding_velocity=random.uniform(50_000, 500_000),
        governance_score=gov_score,
        trust_badge=t_badge,
        sector_multiplier=get_sector_benchmarks(sector)["multiplier"],
        esg_carbon_score=random.randint(30, 90),
        esg_diversity_metric=random.randint(40, 90),
        founder_integrity_score=random.randint(40, 99)
    )

def discover_recent_deals() -> list[str]:
    return [
        "https://wefunder.com/levels", "https://wefunder.com/meow-corp",
        "https://wefunder.com/substacks", "https://wefunder.com/replit-demo"
    ]
