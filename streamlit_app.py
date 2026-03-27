"""
Equiti-AI — Reg CF Deal Intelligence Terminal
Streamlit Cloud entry point: streamlit_app.py

SAFE MODE: This application is a data-only research tool.
It does not provide investment advice, handle funds, or execute transactions.
All execution must occur through a licensed FINRA-registered Broker-Dealer.
"""

import os
import re
import time
import requests
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import Optional
from edgar import Company, set_identity

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION — edit these variables to customise identity and limits
# ═══════════════════════════════════════════════════════════════════════════════
SEC_IDENTITY   = os.getenv("SEC_IDENTITY", "Jordan equiti-ai-research@example.com")
REG_CF_CAP     = 5_000_000      # 2026 Reg CF annual raise cap
EDGAR_PING_URL = "https://data.sec.gov/submissions/CIK0000320193.json"  # AAPL as canary
APP_VERSION    = "1.0.0"

set_identity(SEC_IDENTITY)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Equiti-AI | Reg CF Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/jordan742/Equiti-AI",
        "Report a bug": "https://github.com/jordan742/Equiti-AI/issues",
        "About": f"Equiti-AI v{APP_VERSION} — Reg CF Deal Intelligence. Data only. Not investment advice.",
    },
)

# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS — finance terminal aesthetic
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap');

  html, body, [class*="css"] { font-family: 'JetBrains Mono', monospace; }

  .terminal-header {
    background: linear-gradient(135deg, #0a0f1e 0%, #0d1b3e 100%);
    border: 1px solid #0066cc;
    border-radius: 8px;
    padding: 1.2rem 1.8rem;
    margin-bottom: 1rem;
  }
  .terminal-header h1 { color: #0099ff; margin: 0; font-size: 1.6rem; letter-spacing: 2px; }
  .terminal-header p  { color: #4a9eff; margin: 0.2rem 0 0; font-size: 0.75rem; }

  .diag-ok   { color: #00cc66; font-weight: 600; }
  .diag-fail { color: #ff4444; font-weight: 600; }
  .diag-warn { color: #ffaa00; font-weight: 600; }

  div[data-testid="metric-container"] {
    background: #1a1f2e;
    border: 1px solid #0066cc33;
    border-radius: 6px;
    padding: 0.8rem;
  }

  .stTable thead tr th {
    background: #0d1b3e !important;
    color: #4a9eff !important;
    font-size: 0.8rem;
    letter-spacing: 1px;
  }

  .disclaimer-box {
    background: #0d1117;
    border: 1px solid #333;
    border-left: 4px solid #0066cc;
    border-radius: 4px;
    padding: 1rem 1.2rem;
    font-size: 0.72rem;
    color: #6b7280;
    line-height: 1.6;
    margin-top: 2rem;
  }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TERMINAL HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="terminal-header">
  <h1>📈 EQUITI-AI &nbsp;|&nbsp; REG CF INTELLIGENCE TERMINAL</h1>
  <p>v{APP_VERSION} &nbsp;·&nbsp; SAFE MODE ACTIVE &nbsp;·&nbsp; DATA ONLY &nbsp;·&nbsp; NOT INVESTMENT ADVICE</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# CONNECTION DIAGNOSTIC
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("🔌 Connection Diagnostic", expanded=True):
    diag_col1, diag_col2, diag_col3 = st.columns(3)

    # SEC EDGAR
    with diag_col1:
        try:
            t0 = time.time()
            r = requests.get(EDGAR_PING_URL, headers={"User-Agent": SEC_IDENTITY}, timeout=8)
            latency = int((time.time() - t0) * 1000)
            if r.status_code == 200:
                st.markdown(f'<span class="diag-ok">✔ SEC EDGAR</span> &nbsp; {latency} ms', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="diag-warn">⚠ SEC EDGAR</span> &nbsp; HTTP {r.status_code}', unsafe_allow_html=True)
        except Exception as e:
            st.markdown('<span class="diag-fail">✘ SEC EDGAR &nbsp; UNREACHABLE</span>', unsafe_allow_html=True)

    # Wefunder
    with diag_col2:
        try:
            t0 = time.time()
            r2 = requests.get("https://wefunder.com", timeout=8, allow_redirects=True)
            latency2 = int((time.time() - t0) * 1000)
            st.markdown(f'<span class="diag-ok">✔ Wefunder</span> &nbsp; {latency2} ms', unsafe_allow_html=True)
        except Exception:
            st.markdown('<span class="diag-fail">✘ Wefunder &nbsp; UNREACHABLE</span>', unsafe_allow_html=True)

    # Identity
    with diag_col3:
        st.markdown(f'<span class="diag-ok">✔ SEC Identity</span><br><small style="color:#4a9eff">{SEC_IDENTITY}</small>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════
class StartupFinancials(BaseModel):
    cik: str
    company_name: Optional[str] = None
    cash: Optional[float] = None
    net_income: Optional[float] = None
    revenues: Optional[float] = None
    short_term_debt: Optional[float] = None

class ScoreResult(BaseModel):
    score: float
    runway_months: Optional[float] = None
    debt_ratio: Optional[float] = None
    revenue_growth_pct: Optional[float] = None
    investment_thesis: str

class ComplianceResult(BaseModel):
    compliant: bool
    status: str
    total_raised_12m: float
    current_offer_amount: float
    combined_total: float
    filing_count: int

# ═══════════════════════════════════════════════════════════════════════════════
# DEMO FIXTURE
# ═══════════════════════════════════════════════════════════════════════════════
DEMO = StartupFinancials(
    cik="0001234567",
    company_name="Acme AI, Inc. (Demo)",
    cash=850_000.0,
    net_income=-1_200_000.0,
    revenues=2_400_000.0,
    short_term_debt=300_000.0,
)

# ═══════════════════════════════════════════════════════════════════════════════
# HARVESTER — Wefunder scraper + EDGAR extractor
# ═══════════════════════════════════════════════════════════════════════════════
def _find_cik(campaign_url: str) -> str:
    headers = {"User-Agent": SEC_IDENTITY}
    resp = requests.get(campaign_url, headers=headers, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        text = tag.get_text(strip=True).lower()
        if "form c" in text or "form-c" in text:
            m = re.search(r'CIK=?(\d+)', href, re.IGNORECASE) or re.search(r'/(\d{7,10})/', href)
            if m:
                return m.group(1)
        if "sec.gov" in href:
            m = re.search(r'CIK=?(\d+)', href, re.IGNORECASE) or re.search(r'/(\d{7,10})/', href)
            if m:
                return m.group(1)

    raise ValueError("No CIK found. Confirm the URL links to an SEC Form C filing.")


def _xbrl_fact(filing, concept: str) -> Optional[float]:
    for attempt in [
        lambda: float(getattr(filing.obj(), concept)),
        lambda: float(filing.xbrl().facts.get(f"us-gaap:{concept}")),
        lambda: float(
            filing.xbrl().facts.to_dataframe()
            .query(f"concept.str.endswith('{concept}')")
            .iloc[-1]["value"]
        ),
    ]:
        try:
            val = attempt()
            if val is not None:
                return val
        except Exception:
            continue
    return None


def harvest(campaign_url: str) -> StartupFinancials:
    cik = _find_cik(campaign_url)
    company = Company(cik)
    filings = company.get_filings(form="C")
    if not filings:
        raise ValueError(f"No Form C filings found for CIK {cik}.")
    latest = filings.latest()
    return StartupFinancials(
        cik=cik,
        company_name=company.name,
        cash=_xbrl_fact(latest, "Cash"),
        net_income=_xbrl_fact(latest, "NetIncomeLoss"),
        revenues=_xbrl_fact(latest, "Revenues"),
        short_term_debt=_xbrl_fact(latest, "ShortTermBorrowings"),
    )

# ═══════════════════════════════════════════════════════════════════════════════
# SCORER
# ═══════════════════════════════════════════════════════════════════════════════
def score(financials: StartupFinancials, prior_revenues: Optional[float] = None) -> ScoreResult:
    base = 5.0

    runway = None
    if financials.cash is not None and financials.net_income not in (None, 0):
        runway = financials.cash / (abs(financials.net_income) / 12)
        if runway < 6:
            base -= 3

    debt_ratio = None
    if financials.short_term_debt is not None and financials.revenues not in (None, 0):
        debt_ratio = financials.short_term_debt / financials.revenues

    growth_pct = None
    if prior_revenues and financials.revenues is not None and prior_revenues > 0:
        growth_pct = (financials.revenues - prior_revenues) / prior_revenues * 100
        if growth_pct > 20:
            base += 2

    score_val = max(1.0, min(10.0, base))

    runway_str  = f"{runway:.1f} months" if runway is not None else "unknown"
    dr_str      = f"{debt_ratio:.2f}" if debt_ratio is not None else "unknown"
    growth_str  = f"{growth_pct:.1f}%" if growth_pct is not None else "unavailable"
    risk_flag   = "Immediate runway risk warrants caution" if runway is not None and runway < 6 else "Runway is adequate for near-term operations"
    profile_str = "supports" if score_val >= 6 else "does not yet support"

    thesis = (
        f"{financials.company_name or 'This company'} scores {score_val:.1f}/10 based on "
        f"a cash runway of {runway_str} and a debt-to-revenue ratio of {dr_str}. "
        f"Revenue growth versus the prior period is {growth_str}, "
        f"{'exceeding' if growth_pct and growth_pct > 20 else 'not exceeding'} the 20% growth threshold. "
        f"{risk_flag}, and the overall financial profile {profile_str} further due diligence."
    )

    return ScoreResult(
        score=score_val,
        runway_months=round(runway, 2) if runway is not None else None,
        debt_ratio=round(debt_ratio, 4) if debt_ratio is not None else None,
        revenue_growth_pct=round(growth_pct, 2) if growth_pct is not None else None,
        investment_thesis=thesis,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# COMPLIANCE
# ═══════════════════════════════════════════════════════════════════════════════
def check_compliance(cik: str, current_offer_amount: float) -> ComplianceResult:
    from datetime import date, timedelta, datetime
    cutoff = date.today() - timedelta(days=365)
    company = Company(cik)
    filings = company.get_filings(form=["C", "C-U"])

    total_raised = 0.0
    filing_count = 0

    candidates = ["offeringAmount", "amountSold", "totalAmountSold", "totalOfferingAmount"]

    for filing in (filings or []):
        filed_date = getattr(filing, "filing_date", None) or getattr(filing, "date", None)
        if filed_date is None:
            continue
        if isinstance(filed_date, str):
            filed_date = datetime.strptime(filed_date[:10], "%Y-%m-%d").date()
        if filed_date < cutoff:
            continue

        amount = 0.0
        for field in candidates:
            try:
                val = getattr(filing.obj(), field, None)
                if val is not None:
                    amount = float(val)
                    break
            except Exception:
                continue
        total_raised += amount
        filing_count += 1

    combined   = total_raised + current_offer_amount
    compliant  = combined <= REG_CF_CAP

    return ComplianceResult(
        compliant=compliant,
        status="COMPLIANT" if compliant else "NON_COMPLIANT",
        total_raised_12m=total_raised,
        current_offer_amount=current_offer_amount,
        combined_total=combined,
        filing_count=filing_count,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚙️ Terminal Settings")
    demo_mode = st.toggle("Demo Mode", value=True, help="Uses sample data — no URL or API key needed.")
    st.divider()
    offer_amount   = st.number_input("Current Offer Amount ($)", 0, REG_CF_CAP, 500_000, 25_000)
    prior_revenues = st.number_input("Prior Year Revenue ($)", 0, value=0, step=10_000,
                                     help="Used for YoY revenue growth calculation.")
    st.divider()
    st.caption(f"Equiti-AI v{APP_VERSION}")
    st.caption(f"Reg CF Cap: ${REG_CF_CAP:,}")
    st.caption("SEC Identity: " + SEC_IDENTITY.split()[0])

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN INPUT
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
col_url, col_btn = st.columns([5, 1])
wefunder_url = col_url.text_input(
    "wefunder_url",
    placeholder="https://wefunder.com/company-name",
    disabled=demo_mode,
    label_visibility="collapsed",
)
run = col_btn.button("▶  SCAN", type="primary", use_container_width=True)

if not run:
    st.markdown("""
    <div style="text-align:center; color:#4a5568; padding: 3rem 0; font-size:0.9rem;">
        Enable <b>Demo Mode</b> in the sidebar and click <b>▶ SCAN</b> to load a sample deal.<br>
        Or paste a Wefunder URL and scan a live Reg CF filing.
    </div>
    """, unsafe_allow_html=True)

else:
    # ── Fetch ──────────────────────────────────────────────────────────────
    if demo_mode:
        financials = DEMO
    else:
        if not wefunder_url.strip():
            st.warning("Enter a Wefunder URL or enable Demo Mode.")
            st.stop()
        with st.spinner("Scraping Wefunder & fetching SEC Form C…"):
            try:
                financials = harvest(wefunder_url.strip())
            except Exception as e:
                st.error(f"**Harvest Error:** {e}")
                st.stop()

    with st.spinner("Checking Reg CF compliance…"):
        try:
            compliance = check_compliance(financials.cik, float(offer_amount))
        except Exception as e:
            st.error(f"**Compliance Error:** {e}")
            st.stop()

    with st.spinner("Scoring financials…"):
        result = score(financials, prior_revenues=prior_revenues or None)

    # ── Header row ─────────────────────────────────────────────────────────
    st.markdown(f"## {financials.company_name or f'CIK {financials.cik}'}")
    if demo_mode:
        st.caption("⚡ Demo data — disable Demo Mode to scan a live deal.")

    # ── Compliance banner ──────────────────────────────────────────────────
    used_pct = compliance.combined_total / REG_CF_CAP * 100
    if compliance.compliant:
        st.success(
            f"✅  **REG CF: COMPLIANT** — "
            f"${compliance.combined_total:,.0f} of ${REG_CF_CAP:,} cap used ({used_pct:.1f}%)"
        )
    else:
        st.warning(
            f"⚠️  **REG CF: NON-COMPLIANT** — "
            f"${compliance.combined_total:,.0f} exceeds the ${REG_CF_CAP:,} annual cap."
        )
    st.progress(min(used_pct / 100, 1.0))

    st.markdown("---")

    # ── Two-column layout ──────────────────────────────────────────────────
    left, right = st.columns([3, 2], gap="large")

    with left:
        # Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Health Score", f"{result.score:.1f} / 10")
        m2.metric(
            "Cash Runway",
            f"{result.runway_months:.1f} mo" if result.runway_months else "N/A",
            delta="⚠ < 6 mo" if result.runway_months and result.runway_months < 6 else None,
            delta_color="inverse",
        )
        m3.metric(
            "Revenue Growth",
            f"{result.revenue_growth_pct:.1f}%" if result.revenue_growth_pct is not None else "N/A",
        )

        st.markdown("#### Investment Thesis")
        st.info(result.investment_thesis)

        # Deal memo
        st.markdown("#### Deal Memo")
        compliance_label = "PASS ✅" if compliance.compliant else "FAIL ⚠️"
        key_risk = result.investment_thesis.split(". ")[-1].strip().rstrip(".")
        st.markdown(f"""
| Field | Value |
|:---|:---|
| **Company** | {financials.company_name or financials.cik} |
| **Health Score** | {result.score:.1f} / 10 |
| **Compliance** | {compliance_label} |
| **Debt Ratio** | {f"{result.debt_ratio:.4f}" if result.debt_ratio else "N/A"} |
| **Key Risk** | {key_risk}. |
""")

    with right:
        # Balance sheet
        st.markdown("#### Balance Sheet (Form C, XBRL)")

        def fmt(v: Optional[float]) -> str:
            return f"${v:,.0f}" if v is not None else "—"

        bs = pd.DataFrame({
            "Line Item": ["Cash & Equivalents", "Total Revenues", "Net Income / (Loss)",
                          "Short-Term Debt", "Debt / Revenue Ratio"],
            "Value": [
                fmt(financials.cash),
                fmt(financials.revenues),
                fmt(financials.net_income),
                fmt(financials.short_term_debt),
                f"{result.debt_ratio:.4f}" if result.debt_ratio is not None else "—",
            ],
        }).set_index("Line Item")
        st.table(bs)

        # Compliance detail
        with st.expander("📋 Compliance Detail"):
            st.json({
                "cik": financials.cik,
                "status": compliance.status,
                "form_c_filings_12m": compliance.filing_count,
                "total_raised_12m_usd": f"${compliance.total_raised_12m:,.0f}",
                "current_offer_usd": f"${compliance.current_offer_amount:,.0f}",
                "combined_total_usd": f"${compliance.combined_total:,.0f}",
                "reg_cf_annual_cap": f"${REG_CF_CAP:,}",
                "cap_remaining_usd": f"${max(REG_CF_CAP - compliance.combined_total, 0):,.0f}",
            })

    st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# LEGAL DISCLAIMER — 2026 SEC/FINRA AI Disclosure
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="disclaimer-box">
<b>LEGAL DISCLAIMER & AI DISCLOSURE — EQUITI-AI v{ver} — EFFECTIVE 2026</b><br><br>

<b>Not Investment Advice.</b> Equiti-AI is a financial data aggregation and analytical research tool.
Nothing on this platform constitutes investment advice, a solicitation to buy or sell any security,
or a recommendation of any kind. All outputs are generated algorithmically and are for informational
purposes only.<br><br>

<b>AI-Generated Content Disclosure (SEC AI Guidance 2024–2026 / FINRA Rule 2010).</b>
Portions of this analysis are generated by artificial intelligence models, including large language
models (LLMs). AI-generated content may contain errors, omissions, or hallucinations. Users must
independently verify all data against primary sources including SEC EDGAR filings before making
any financial decision. Equiti-AI does not guarantee the accuracy, completeness, or timeliness
of any AI-generated output.<br><br>

<b>Regulation Crowdfunding (Reg CF) Disclosure.</b> Investment limits under SEC Regulation
Crowdfunding (17 CFR §227) cap non-accredited investor participation at the greater of $2,500 or
5% of annual income/net worth (income or net worth below $124,000), or 10% of annual income/net
worth up to $124,000 (income or net worth above $124,000), with an absolute cap of $124,000 per
12-month period. Maximum issuer raise is $5,000,000 per 12-month period. These figures are subject
to SEC inflation adjustments.<br><br>

<b>No Broker-Dealer or Investment Adviser Registration.</b> Equiti-AI is not a registered
broker-dealer, investment adviser, funding portal, or placement agent. This platform operates
exclusively in "Safe Mode" — it does not hold, transfer, custody, or route investor funds at any
time. All investment execution must occur through a FINRA-registered funding portal or licensed
broker-dealer.<br><br>

<b>Past performance is not indicative of future results. Investing in startups involves a high
degree of risk, including the potential loss of the entire investment. Illiquidity risk is
significant — there is no guaranteed secondary market for Reg CF securities.</b>
</div>
""".format(ver=APP_VERSION), unsafe_allow_html=True)
