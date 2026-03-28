"""
Equiti-AI v2.0 — Institutional Reg CF Intelligence Terminal
Streamlit Cloud entry point: streamlit_app.py
"""

import os, re, time, math
import requests
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import Optional
from datetime import date, timedelta, datetime
from edgar import Company, set_identity

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION — change SEC_IDENTITY to your name + email before deploying
# ═══════════════════════════════════════════════════════════════════════════════
SEC_IDENTITY   = os.getenv("SEC_IDENTITY", "Jordan equiti-ai-research@example.com")
REG_CF_CAP     = 5_000_000
EDGAR_PING_URL = "https://data.sec.gov/submissions/CIK0000320193.json"
APP_VERSION    = "2.0.0"

set_identity(SEC_IDENTITY)

if "view_mode" not in st.session_state: st.session_state.view_mode = "grid"
if "active_deal" not in st.session_state: st.session_state.active_deal = None
if "deals_cache" not in st.session_state: st.session_state.deals_cache = {}

st.set_page_config(
    page_title="Equiti-AI v2 | Institutional Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/jordan742/Equiti-AI",
        "Report a bug": "https://github.com/jordan742/Equiti-AI/issues",
        "About": f"Equiti-AI v{APP_VERSION} — Reg CF Intelligence. Data only.",
    },
)

# ═══════════════════════════════════════════════════════════════════════════════
# INSTITUTIONAL CSS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'JetBrains Mono', monospace; }

  .terminal-hdr {
    background: linear-gradient(135deg, #060a14 0%, #0c1a3a 100%);
    border: 1px solid #0066cc; border-radius: 10px;
    padding: 1.5rem 2rem; margin-bottom: 1.2rem;
  }
  .terminal-hdr h1 { color: #0099ff; margin:0; font-size:1.5rem; letter-spacing:3px; }
  .terminal-hdr p  { color: #4a90d9; margin:0.3rem 0 0; font-size:0.72rem; letter-spacing:1px; }

  .diag-ok   { color:#00cc66; font-weight:600; }
  .diag-fail { color:#ff4444; font-weight:600; }

  div[data-testid="metric-container"] {
    background: #111827; border:1px solid #1e3a5f;
    border-radius:8px; padding:0.9rem;
  }
  div[data-testid="metric-container"] label { color:#4a9eff !important; letter-spacing:1px; }

  .signal-badge {
    display:inline-block; padding:0.45rem 1.2rem; border-radius:6px;
    font-weight:700; font-size:0.95rem; letter-spacing:2px; text-align:center;
  }
  .badge-bull { background:#052e16; border:1px solid #22c55e; color:#4ade80; }
  .badge-neut { background:#422006; border:1px solid #f59e0b; color:#fbbf24; }
  .badge-bear { background:#450a0a; border:1px solid #ef4444; color:#f87171; }

  .investor-card {
    background:#0f172a; border:1px solid #1e40af; border-radius:8px;
    padding:1rem 1.2rem; margin-top:0.5rem;
  }
  .investor-card h4 { color:#60a5fa; margin:0 0 0.4rem; font-size:0.85rem; }
  .investor-card .limit { color:#34d399; font-size:1.4rem; font-weight:700; }

  .disclaimer-box {
    background:#0d1117; border:1px solid #333; border-left:4px solid #0066cc;
    border-radius:4px; padding:1rem 1.2rem; font-size:0.7rem;
    color:#6b7280; line-height:1.65; margin-top:2rem;
  }
  .stButton > button:hover { background-color: #333333 !important; }
  
  /* Global Metrics */
  div[data-testid="stMetric"] label { color: #666666 !important; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; }
  div[data-testid="stMetric"] div { color: #000000 !important; font-size: 2.2rem; font-weight: 700; letter-spacing: -1px; }
  
  /* Sidebar Footer */
  .sidebar-footer { position: fixed; left: 0; bottom: 0; width: inherit; padding: 1rem; border-top: 1px solid #E5E5E5; font-size: 10px; color: #666666; background: #F9F9F9; z-index: 1000; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="terminal-hdr">
  <h1>EQUITI-AI &nbsp;|&nbsp; INSTITUTIONAL REG CF TERMINAL</h1>
  <p>v{APP_VERSION} &nbsp;&middot;&nbsp; SAFE MODE &nbsp;&middot;&nbsp; DATA ONLY &nbsp;&middot;&nbsp; NOT INVESTMENT ADVICE</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MOCK GENERATORS / HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("CONNECTION DIAGNOSTIC", expanded=True):
    d1, d2, d3 = st.columns(3)
    with d1:
        try:
            t0 = time.time()
            r = requests.get(EDGAR_PING_URL, headers={"User-Agent": SEC_IDENTITY}, timeout=8)
            ms = int((time.time() - t0) * 1000)
            if r.status_code == 200:
                st.markdown(f'<span class="diag-ok">SEC EDGAR &nbsp; ONLINE &nbsp; {ms}ms</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="diag-fail">SEC EDGAR &nbsp; HTTP {r.status_code}</span>', unsafe_allow_html=True)
        except Exception:
            st.markdown('<span class="diag-fail">SEC EDGAR &nbsp; UNREACHABLE</span>', unsafe_allow_html=True)
    with d2:
        try:
            t0 = time.time()
            requests.get("https://wefunder.com", timeout=8, allow_redirects=True)
            ms2 = int((time.time() - t0) * 1000)
            st.markdown(f'<span class="diag-ok">WEFUNDER &nbsp; ONLINE &nbsp; {ms2}ms</span>', unsafe_allow_html=True)
        except Exception:
            st.markdown('<span class="diag-fail">WEFUNDER &nbsp; UNREACHABLE</span>', unsafe_allow_html=True)
    with d3:
        st.markdown(f'<span class="diag-ok">IDENTITY: {SEC_IDENTITY.split()[0]}</span>', unsafe_allow_html=True)

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
    min_investment: Optional[float] = None

class ComplianceResult(BaseModel):
    compliant: bool
    status: str
    total_raised_12m: float
    current_offer_amount: float
    combined_total: float
    filing_count: int

# ═══════════════════════════════════════════════════════════════════════════════
# DEMO DATA
# ═══════════════════════════════════════════════════════════════════════════════
DEMO = StartupFinancials(
    cik="0001234567",
    company_name="Acme AI, Inc. (Demo)",
    cash=850_000.0,
    net_income=-1_200_000.0,
    revenues=2_400_000.0,
    short_term_debt=300_000.0,
    min_investment=100.0,
)

# ═══════════════════════════════════════════════════════════════════════════════
# SEC REG CF INVESTOR LIMIT CALCULATOR (2026 Rules — 17 CFR §227.100)
# ═══════════════════════════════════════════════════════════════════════════════
def calc_reg_cf_limit(annual_income: float, net_worth: float) -> float:
    if annual_income < 124_000 and net_worth < 124_000:
        return max(2_500, 0.05 * min(annual_income, net_worth))
    else:
        return min(0.10 * min(annual_income, net_worth), 124_000)

# ═══════════════════════════════════════════════════════════════════════════════
# SIGNAL BADGE
# ═══════════════════════════════════════════════════════════════════════════════
def render_signal_badge(health_score: float) -> str:
    if health_score > 7:
        return '<span class="signal-badge badge-bull">STRONGLY BULLISH</span>'
    elif health_score >= 4:
        return '<span class="signal-badge badge-neut">NEUTRAL</span>'
    else:
        return '<span class="signal-badge badge-bear">BEARISH / HIGH RISK</span>'

# ═══════════════════════════════════════════════════════════════════════════════
# CASH BURN PLOTLY CHART
# ═══════════════════════════════════════════════════════════════════════════════
def build_cash_burn_chart(cash: float, monthly_burn: float, months: int = 18) -> go.Figure:
    labels = []
    balances = []
    today = date.today()
    bal = cash
    for i in range(months + 1):
        d = today + timedelta(days=30 * i)
        labels.append(d.strftime("%b %Y"))
        balances.append(max(bal, 0))
        bal -= monthly_burn

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels, y=balances,
        fill="tozeroy",
        fillcolor="rgba(0,102,204,0.15)",
        line=dict(color="#0066cc", width=2),
        mode="lines",
        name="Projected Cash",
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
    ))

    # Zero line
    fig.add_hline(y=0, line_dash="dot", line_color="#ef4444", opacity=0.6,
                  annotation_text="ZERO CASH", annotation_position="bottom left",
                  annotation_font_color="#ef4444")

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        title=dict(text="PROJECTED CASH BURN", font=dict(size=14, color="#4a9eff", family="JetBrains Mono")),
        yaxis=dict(title="Cash Balance ($)", tickprefix="$", tickformat=",", gridcolor="#1e293b"),
        xaxis=dict(gridcolor="#1e293b"),
        height=340,
        margin=dict(l=60, r=20, t=50, b=40),
        showlegend=False,
    )
    return fig

# ═══════════════════════════════════════════════════════════════════════════════
# HARVESTER
# ═══════════════════════════════════════════════════════════════════════════════
def _find_cik_and_min(campaign_url: str) -> tuple[str, Optional[float]]:
    headers = {"User-Agent": SEC_IDENTITY}
    resp = requests.get(campaign_url, headers=headers, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract min investment
    min_inv = None
    patterns = [
        r'minimum\s+investment[^\$]*\$\s*([\d,]+)',
        r'min\.?\s+investment[^\$]*\$\s*([\d,]+)',
        r'\$\s*([\d,]+)\s+minimum',
        r'invest\s+as\s+little\s+as\s+\$\s*([\d,]+)',
        r'starting\s+at\s+\$\s*([\d,]+)',
    ]
    page_text = soup.get_text(" ", strip=True)
    for pat in patterns:
        m = re.search(pat, page_text, re.IGNORECASE)
        if m:
            try:
                min_inv = float(m.group(1).replace(",", ""))
                break
            except ValueError:
                continue

    # Find CIK
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        text = tag.get_text(strip=True).lower()
        if "form c" in text or "form-c" in text or "sec.gov" in href:
            m = re.search(r'CIK=?(\d+)', href, re.IGNORECASE) or re.search(r'/(\d{7,10})/', href)
            if m:
                return m.group(1), min_inv

    raise ValueError("No CIK found on this page. Confirm it links to an SEC Form C filing.")


def _xbrl_fact(filing, concept: str) -> Optional[float]:
    for fn in [
        lambda: float(getattr(filing.obj(), concept)),
        lambda: float(filing.xbrl().facts.get(f"us-gaap:{concept}")),
        lambda: float(filing.xbrl().facts.to_dataframe().query(f"concept.str.endswith('{concept}')").iloc[-1]["value"]),
    ]:
        try:
            v = fn()
            if v is not None:
                return v
        except Exception:
            continue
    return None


def harvest(campaign_url: str) -> StartupFinancials:
    cik, min_inv = _find_cik_and_min(campaign_url)
    company = Company(cik)
    filings = company.get_filings(form="C")
    if not filings:
        raise ValueError(f"No Form C filings for CIK {cik}.")
    latest = filings.latest()
    return StartupFinancials(
        cik=cik,
        company_name=company.name,
        cash=_xbrl_fact(latest, "Cash"),
        net_income=_xbrl_fact(latest, "NetIncomeLoss"),
        revenues=_xbrl_fact(latest, "Revenues"),
        short_term_debt=_xbrl_fact(latest, "ShortTermBorrowings"),
        min_investment=min_inv,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# SCORER
# ═══════════════════════════════════════════════════════════════════════════════
def score(fin: StartupFinancials, prior_revenues: Optional[float] = None) -> ScoreResult:
    base = 5.0
    runway = None
    if fin.cash is not None and fin.net_income not in (None, 0):
        runway = fin.cash / (abs(fin.net_income) / 12)
        if runway < 6:
            base -= 3
    debt_ratio = None
    if fin.short_term_debt is not None and fin.revenues not in (None, 0):
        debt_ratio = fin.short_term_debt / fin.revenues
    growth_pct = None
    if prior_revenues and fin.revenues is not None and prior_revenues > 0:
        growth_pct = (fin.revenues - prior_revenues) / prior_revenues * 100
        if growth_pct > 20:
            base += 2
    val = max(1.0, min(10.0, base))
    r_str = f"{runway:.1f} months" if runway else "unknown"
    d_str = f"{debt_ratio:.2f}" if debt_ratio else "unknown"
    g_str = f"{growth_pct:.1f}%" if growth_pct is not None else "unavailable"
    risk = "Immediate runway risk warrants caution" if runway and runway < 6 else "Runway is adequate for near-term operations"
    thesis = (
        f"{fin.company_name or 'This company'} scores {val:.1f}/10 based on "
        f"a cash runway of {r_str} and a debt-to-revenue ratio of {d_str}. "
        f"Revenue growth versus prior period is {g_str}, "
        f"{'exceeding' if growth_pct and growth_pct > 20 else 'not exceeding'} the 20% threshold. "
        f"{risk}, and the profile {'supports' if val >= 6 else 'does not yet support'} further diligence."
    )
    return ScoreResult(
        score=val,
        runway_months=round(runway, 2) if runway else None,
        debt_ratio=round(debt_ratio, 4) if debt_ratio else None,
        revenue_growth_pct=round(growth_pct, 2) if growth_pct is not None else None,
        investment_thesis=thesis,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# COMPLIANCE
# ═══════════════════════════════════════════════════════════════════════════════
def check_compliance(cik: str, current_offer: float) -> ComplianceResult:
    cutoff = date.today() - timedelta(days=365)
    company = Company(cik)
    filings = company.get_filings(form=["C", "C-U"])
    total = 0.0
    count = 0
    for f in (filings or []):
        fd = getattr(f, "filing_date", None) or getattr(f, "date", None)
        if fd is None:
            continue
        if isinstance(fd, str):
            fd = datetime.strptime(fd[:10], "%Y-%m-%d").date()
        if fd < cutoff:
            continue
        for field in ["offeringAmount", "amountSold", "totalAmountSold", "totalOfferingAmount"]:
            try:
                v = getattr(f.obj(), field, None)
                if v is not None:
                    total += float(v)
                    break
            except Exception:
                continue
        count += 1
    combined = total + current_offer
    ok = combined <= REG_CF_CAP
    return ComplianceResult(
        compliant=ok,
        status="COMPLIANT" if ok else "NON_COMPLIANT",
        total_raised_12m=total,
        current_offer_amount=current_offer,
        combined_total=combined,
        filing_count=count,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### TERMINAL SETTINGS")
    demo_mode = st.toggle("Demo Mode", value=True, help="Sample data — no URL or API key needed.")
    st.divider()
    offer_amount   = st.number_input("Current Offer ($)", 0, REG_CF_CAP, 500_000, 25_000)
    prior_revenues = st.number_input("Prior Year Revenue ($)", 0, value=0, step=10_000)
    st.divider()

    # ── Investor Profile — SEC Reg CF Limit Calculator ─────────────────────
    st.markdown("### INVESTOR PROFILE")
    st.caption("2026 Reg CF Limits (17 CFR §227.100)")
    annual_income = st.number_input("Annual Income ($)", 0, value=75_000, step=5_000)
    net_worth     = st.number_input("Net Worth ($)", 0, value=60_000, step=5_000)
    inv_limit     = calc_reg_cf_limit(annual_income, net_worth)

    st.markdown(f"""
    <div class="investor-card">
      <h4>YOUR 2026 REG CF LIMIT</h4>
      <span class="limit">${inv_limit:,.0f}</span>
    </div>
    """, unsafe_allow_html=True)

    if annual_income < 124_000 and net_worth < 124_000:
        st.caption(f"Rule: max($2,500, 5% x min(${annual_income:,}, ${net_worth:,}))")
    else:
        st.caption(f"Rule: 10% x min(${annual_income:,}, ${net_worth:,}), capped at $124,000")

    st.divider()
    st.caption(f"Equiti-AI v{APP_VERSION} | Cap: ${REG_CF_CAP:,}")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN INPUT
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
col_url, col_btn = st.columns([5, 1])
wefunder_url = col_url.text_input("url", placeholder="https://wefunder.com/company-name",
                                  disabled=demo_mode, label_visibility="collapsed")
run = col_btn.button("SCAN", type="primary", use_container_width=True)

if not run:
    st.markdown("""
    <div style="text-align:center;color:#475569;padding:3rem 0;font-size:0.85rem;">
        Toggle <b>Demo Mode</b> in the sidebar and click <b>SCAN</b> to explore the terminal,<br>
        or paste a Wefunder URL to scan a live Reg CF deal.
    </div>
    """, unsafe_allow_html=True)

else:
    # ── DATA PIPELINE ──────────────────────────────────────────────────────
    if demo_mode:
        financials = DEMO
    else:
        if not wefunder_url.strip():
            st.warning("Enter a Wefunder URL or enable Demo Mode.")
            st.stop()
        with st.spinner("Scraping Wefunder & pulling SEC Form C…"):
            try:
                financials = harvest(wefunder_url.strip())
            except Exception as e:
                st.error(f"**Harvest Error:** {e}")
                st.stop()

    with st.spinner("Compliance check…"):
        try:
            compliance = check_compliance(financials.cik, float(offer_amount))
        except Exception as e:
            st.error(f"**Compliance Error:** {e}")
            st.stop()

    with st.spinner("Scoring…"):
        result = score(financials, prior_revenues=prior_revenues or None)

    # ── COMPANY HEADER + SIGNAL BADGE ──────────────────────────────────────
    hdr1, hdr2 = st.columns([3, 2])
    with hdr1:
        st.markdown(f"## {financials.company_name or f'CIK {financials.cik}'}")
        if demo_mode:
            st.caption("Demo data — disable Demo Mode to scan live deals.")
    with hdr2:
        st.markdown(render_signal_badge(result.score), unsafe_allow_html=True)

    # ── COMPLIANCE BANNER ──────────────────────────────────────────────────
    used_pct = compliance.combined_total / REG_CF_CAP * 100
    if compliance.compliant:
        st.success(f"REG CF: COMPLIANT — ${compliance.combined_total:,.0f} of ${REG_CF_CAP:,} cap ({used_pct:.1f}%)")
    else:
        st.warning(f"REG CF: NON-COMPLIANT — ${compliance.combined_total:,.0f} exceeds ${REG_CF_CAP:,} cap")
    st.progress(min(used_pct / 100, 1.0))
    st.markdown("---")

    # ── METRIC CARDS ───────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Health Score", f"{result.score:.1f} / 10")
    m2.metric(
        "Cash Runway",
        f"{result.runway_months:.1f} mo" if result.runway_months else "N/A",
        delta="LOW" if result.runway_months and result.runway_months < 6 else None,
        delta_color="inverse",
    )
    m3.metric(
        "Min Investment",
        f"${financials.min_investment:,.0f}" if financials.min_investment else "N/A",
    )
    m4.metric(
        "Your Reg CF Limit",
        f"${inv_limit:,.0f}",
    )

    st.markdown("---")

    # ── TWO-COLUMN LAYOUT ──────────────────────────────────────────────────
    left, right = st.columns([3, 2], gap="large")

    with left:
        # Cash burn chart
        if financials.cash is not None and financials.net_income is not None and financials.net_income < 0:
            monthly_burn = abs(financials.net_income) / 12
            fig = build_cash_burn_chart(financials.cash, monthly_burn)
            st.plotly_chart(fig, use_container_width=True)
        elif financials.cash is not None:
            st.info("Company is cash-flow positive — no burn projection needed.")

        # Investment thesis
        st.markdown("#### INVESTMENT THESIS")
        st.info(result.investment_thesis)

        # Deal memo
        st.markdown("#### DEAL MEMO")
        compliance_label = "PASS" if compliance.compliant else "FAIL"
        key_risk = result.investment_thesis.split(". ")[-1].strip().rstrip(".")
        st.markdown(f"""
| Field | Value |
|:---|:---|
| **Company** | {financials.company_name or financials.cik} |
| **Health Score** | {result.score:.1f} / 10 |
| **Signal** | {'STRONGLY BULLISH' if result.score > 7 else 'NEUTRAL' if result.score >= 4 else 'BEARISH / HIGH RISK'} |
| **Compliance** | {compliance_label} |
| **Key Risk** | {key_risk}. |
""")

    with right:
        # Balance sheet — st.dataframe
        st.markdown("#### BALANCE SHEET (FORM C)")

        def fmt(v):
            return f"${v:,.0f}" if v is not None else "—"

        bs_df = pd.DataFrame({
            "Line Item": [
                "Cash & Equivalents",
                "Total Revenues",
                "Net Income / (Loss)",
                "Short-Term Debt",
                "Debt / Revenue Ratio",
                "Monthly Burn Rate",
            ],
            "Amount": [
                fmt(financials.cash),
                fmt(financials.revenues),
                fmt(financials.net_income),
                fmt(financials.short_term_debt),
                f"{result.debt_ratio:.4f}" if result.debt_ratio else "—",
                fmt(abs(financials.net_income) / 12) if financials.net_income and financials.net_income < 0 else "—",
            ],
        })
        st.dataframe(bs_df, use_container_width=True, hide_index=True)

        # Revenue Growth metric
        if result.revenue_growth_pct is not None:
            st.metric("YoY Revenue Growth", f"{result.revenue_growth_pct:.1f}%",
                      delta="Above 20% threshold" if result.revenue_growth_pct > 20 else None)

        # Compliance detail
        with st.expander("COMPLIANCE DETAIL"):
            st.json({
                "cik": financials.cik,
                "status": compliance.status,
                "filings_12m": compliance.filing_count,
                "raised_12m": f"${compliance.total_raised_12m:,.0f}",
                "current_offer": f"${compliance.current_offer_amount:,.0f}",
                "combined": f"${compliance.combined_total:,.0f}",
                "cap": f"${REG_CF_CAP:,}",
                "remaining": f"${max(REG_CF_CAP - compliance.combined_total, 0):,.0f}",
            })

    st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# LEGAL DISCLAIMER — 2026 SEC/FINRA AI DISCLOSURE
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="disclaimer-box">
<b>LEGAL DISCLAIMER & AI DISCLOSURE — EQUITI-AI v{APP_VERSION} — 2026</b><br><br>

<b>Not Investment Advice.</b> Equiti-AI is a data aggregation and analytical research tool.
Nothing on this platform constitutes investment advice, a solicitation to buy or sell securities,
or a recommendation. All outputs are algorithmic and for informational purposes only.<br><br>

<b>AI-Generated Content Disclosure (SEC AI Guidance 2024-2026 / FINRA Rule 2010).</b>
Portions of this analysis are generated by artificial intelligence. AI output may contain errors,
omissions, or hallucinations. Users must independently verify all data against primary sources
including SEC EDGAR filings before making any financial decision.<br><br>

<b>Regulation Crowdfunding (Reg CF) — 17 CFR §227.</b> Non-accredited investors: if both annual
income and net worth are below $124,000, limit is the greater of $2,500 or 5% of the lesser of
income/net worth. If either exceeds $124,000, limit is 10% of the lesser, capped at $124,000 per
12-month period. Maximum issuer raise: $5,000,000 per 12 months. Subject to SEC inflation
adjustments.<br><br>

<b>No Broker-Dealer Registration.</b> Equiti-AI is not a registered broker-dealer, investment
adviser, or funding portal. This platform operates in "Safe Mode" — it never holds, transfers,
custodies, or routes investor funds. All execution must occur through a FINRA-registered portal.<br><br>

<b>Investing in startups carries a high degree of risk including total loss of investment.
There is no guaranteed secondary market for Reg CF securities. Past performance does not
indicate future results.</b>
</div>
""", unsafe_allow_html=True)
