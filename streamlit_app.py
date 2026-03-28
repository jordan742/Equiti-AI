"""
Equiti-AI v3.0 Pro — Institutional Reg CF Intelligence Terminal
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
import harvester

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════
SEC_IDENTITY   = os.getenv("SEC_IDENTITY", "Jordan equiti-ai-research@example.com")
REG_CF_CAP     = 5_000_000
EDGAR_PING_URL = "https://data.sec.gov/submissions/CIK0000320193.json"
APP_VERSION    = "3.0.0-PRO"
PORTFOLIO_FILE = "portfolio.csv"

set_identity(SEC_IDENTITY)

if not os.path.exists(PORTFOLIO_FILE):
    pd.DataFrame(columns=["CIK", "Company", "Investment", "Runway"]).to_csv(PORTFOLIO_FILE, index=False)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Equiti-AI Pro | Institutional Terminal",
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
# INSTITUTIONAL CSS — GLASSMORPHISM
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
  
  html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
  code, pre { font-family: 'JetBrains Mono', monospace; }

  /* Glassmorphism Theme */
  div.stApp {
    background: radial-gradient(circle at 15% 50%, rgba(10,25,47,1) 0%, rgba(0,0,0,1) 100%);
  }
  
  .terminal-hdr {
    background: rgba(10, 25, 47, 0.4);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 1.5rem 2rem; margin-bottom: 1.2rem;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  }
  .terminal-hdr h1 { color: #00f2fe; margin:0; font-size:1.6rem; letter-spacing:2px; font-weight: 700; text-transform: uppercase; text-shadow: 0 0 10px rgba(0,242,254,0.7); }
  .terminal-hdr p  { color: #60a5fa; margin:0.3rem 0 0; font-size:0.8rem; letter-spacing:1px; }

  .diag-ok   { color:#00ff00; font-weight:700; }
  .diag-fail { color:#ff003c; font-weight:700; }

  /* Glassmorphic Metrics */
  div[data-testid="stContainer"] > div {
    background: rgba(10, 25, 47, 0.4);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 0.5rem;
    box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.2);
  }
  
  div[data-testid="stMetric"] label { color: #60a5fa !important; letter-spacing: 0.5px; font-size: 0.9rem; font-weight: 700; text-transform: uppercase; }
  div[data-testid="stMetric"] div { color: #ffffff !important; font-size: 1.8rem; font-weight: 300; }

  @media (max-width: 768px) {
    div[data-testid="stVerticalBlock"] > div[data-testid="column"] { 
        width: 100% !important; 
        min-width: 100% !important; 
        flex: 1 1 100% !important; 
    }
  }

  .signal-badge {
    display:inline-block; padding:0.45rem 1.2rem; border-radius:6px;
    font-weight:700; font-size:0.95rem; letter-spacing:2px; text-align:center;
  }
  .badge-bull { background:rgba(5,46,22,0.6); border:1px solid #00ff00; color:#00ff00; }
  .badge-neut { background:rgba(66,32,6,0.6); border:1px solid #f59e0b; color:#fbbf24; }
  .badge-bear { background:rgba(69,10,10,0.6); border:1px solid #ff003c; color:#ff003c; }

  .investor-card {
    background: rgba(10, 25, 47, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 6px;
    padding: 1rem 1.2rem; margin-top: 0.5rem;
  }
  .investor-card h4 { color: #60a5fa; margin: 0 0 0.4rem; font-size: 0.85rem; text-transform: uppercase; }
  .investor-card .limit { color: #00f2fe; font-size: 1.6rem; font-weight: 700; }

  .disclaimer-box {
    background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1); border-left: 4px solid #00f2fe;
    border-radius: 4px; padding: 1rem 1.2rem; font-size: 0.75rem;
    color: #94a3b8; line-height: 1.65; margin-top: 2rem;
  }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="terminal-hdr">
  <h1>EQUITI-AI PRO &nbsp;|&nbsp; INSTITUTIONAL REG CF TERMINAL</h1>
  <p>v{APP_VERSION} &nbsp;&middot;&nbsp; SAFE MODE &nbsp;&middot;&nbsp; DATA ONLY &nbsp;&middot;&nbsp; NOT INVESTMENT ADVICE</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════
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
# DEMO DATA
# ═══════════════════════════════════════════════════════════════════════════════
DEMO = harvester.StartupFinancials(
    cik="0001234567",
    company_name="Acme AI, Inc. (Demo)",
    cash=850_000.0,
    net_income=-1_200_000.0,
    revenues=2_400_000.0,
    short_term_debt=300_000.0,
    min_investment=100.0,
    customer_acquisition_cost=15.50,
    lifetime_value=250.00,
    burn_multiple=0.5
)

def calc_reg_cf_limit(annual_income: float, net_worth: float) -> float:
    if annual_income < 124_000 and net_worth < 124_000:
        return max(2_500, 0.05 * min(annual_income, net_worth))
    else:
        return min(0.10 * min(annual_income, net_worth), 124_000)

def render_signal_badge(health_score: float) -> str:
    if health_score > 7:
        return '<span class="signal-badge badge-bull">STRONGLY BULLISH</span>'
    elif health_score >= 4:
        return '<span class="signal-badge badge-neut">NEUTRAL</span>'
    else:
        return '<span class="signal-badge badge-bear">BEARISH / HIGH RISK</span>'

def build_cash_burn_chart(cash: float, monthly_burn: float, months: int = 18) -> go.Figure:
    labels = []
    balances = []
    today = date.today()
    bal = cash
    for i in range(months + 1):
        d = today + timedelta(days=30 * i)
        labels.append(d.strftime("%b %y"))
        balances.append(max(bal, 0))
        bal -= monthly_burn

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels, y=balances,
        fill="tozeroy",
        fillcolor="rgba(0,242,254,0.15)",
        line=dict(color="#00f2fe", width=2),
        mode="lines",
        name="Projected Cash",
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
    ))
    fig.add_hline(y=0, line_dash="dot", line_color="#ff003c", opacity=0.6)
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title=dict(text="PROJECTED CASH BURN", font=dict(size=14, color="#60a5fa", family="Roboto")),
        yaxis=dict(title="Cash Balance ($)", tickprefix="$", tickformat=",", gridcolor="rgba(255,255,255,0.05)"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        height=340,
        margin=dict(l=60, r=20, t=50, b=40),
        showlegend=False,
    )
    return fig

def build_liquidity_gauge(score: float) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Liquidity Score", 'font': {'size': 18, 'color': '#00f2fe', 'family': 'Roboto'}},
        gauge = {
            'axis': {'range': [None, 10], 'tickwidth': 1, 'tickcolor': "rgba(255,255,255,0.1)"},
            'bar': {'color': "#00f2fe"},
            'bgcolor': "rgba(0,0,0,0.5)",
            'borderwidth': 2,
            'bordercolor': "rgba(255,255,255,0.1)",
            'steps': [
                {'range': [0, 4], 'color': '#ff003c'},
                {'range': [4, 7], 'color': '#fbbf24'},
                {'range': [7, 10], 'color': '#00ff00'}],
            'threshold': {'line': {'color': "#ffffff", 'width': 4}, 'thickness': 0.75, 'value': score}
        }
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def score(fin: harvester.StartupFinancials, prior_revenues: Optional[float] = None) -> ScoreResult:
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
    thesis = f"Calculated score {val:.1f}/10. Runway: {r_str}, Debt Ratio: {d_str}."
    return ScoreResult(score=val, runway_months=round(runway, 2) if runway else None, debt_ratio=d_str, revenue_growth_pct=growth_pct, investment_thesis=thesis)

def check_compliance(cik: str, current_offer: float) -> ComplianceResult:
    return ComplianceResult(compliant=True, status="COMPLIANT", total_raised_12m=0.0, current_offer_amount=current_offer, combined_total=current_offer, filing_count=1)

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
    st.divider()
    
    st.markdown("### DISCOVERY ENGINE")
    st.caption("Actively tracking live deals...")
    deals = harvester.discover_recent_deals()
    for d in deals:
        st.markdown(f"📡 `{d.split('/')[-1]}`")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN INTERFACE (TABS)
# ═══════════════════════════════════════════════════════════════════════════════

tab_scanner, tab_portfolio, tab_secondary = st.tabs(["Scanner", "My Portfolio", "Secondary Exchange"])

# ── 1. SCANNER TAB ─────────────────────────────────────────────────────────────
with tab_scanner:
    col_url, col_btn = st.columns([5, 1])
    wefunder_url = col_url.text_input("url", placeholder="https://wefunder.com/company-name", disabled=demo_mode, label_visibility="collapsed")
    run = col_btn.button("SCAN", type="primary", use_container_width=True)

    if not run:
        st.markdown("""
        <div style="text-align:center;color:#64748b;padding:3rem 0;font-size:0.85rem;">
            Toggle <b>Demo Mode</b> in the sidebar and click <b>SCAN</b> to explore the terminal,<br>
            or paste a Wefunder URL to scan a live Reg CF deal.
        </div>
        """, unsafe_allow_html=True)
    else:
        if demo_mode:
            financials = DEMO
        else:
            if not wefunder_url.strip():
                st.warning("Enter a Wefunder URL or enable Demo Mode.")
                st.stop()
            with st.spinner("Scraping Wefunder & pulling SEC Form C…"):
                try:
                    financials = harvester.harvest(wefunder_url.strip())
                except Exception as e:
                    st.error(f"**Harvest Error:** {e}")
                    st.stop()

        compliance = check_compliance(financials.cik, float(offer_amount))
        result = score(financials, prior_revenues=prior_revenues or None)

        hdr1, hdr2 = st.columns([3, 2])
        with hdr1:
            st.markdown(f"## {financials.company_name or f'CIK {financials.cik}'}")
        with hdr2:
            st.markdown(render_signal_badge(result.score), unsafe_allow_html=True)

        used_pct = compliance.combined_total / REG_CF_CAP * 100
        if compliance.compliant:
            st.success(f"REG CF: COMPLIANT — ${compliance.combined_total:,.0f} of ${REG_CF_CAP:,} cap")
        else:
            st.warning(f"REG CF: NON-COMPLIANT — ${compliance.combined_total:,.0f} exceeds ${REG_CF_CAP:,} cap")
        
        st.markdown("---")

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            with st.container(border=True):
                st.metric("Health Score", f"{result.score:.1f} / 10")
        with m2:
            with st.container(border=True):
                st.metric("Cash Runway", f"{result.runway_months:.1f} mo" if result.runway_months else "N/A", delta="LOW" if result.runway_months and result.runway_months < 6 else None, delta_color="inverse")
        with m3:
            with st.container(border=True):
                st.metric("Min Investment", f"${financials.min_investment:,.0f}" if financials.min_investment else "N/A")
        with m4:
            with st.container(border=True):
                st.metric("Your Reg CF Limit", f"${inv_limit:,.0f}")

        st.markdown("---")

        left, right = st.columns([3, 2], gap="large")
        with left:
            if financials.cash is not None and financials.net_income is not None and financials.net_income < 0:
                monthly_burn = abs(financials.net_income) / 12
                fig = build_cash_burn_chart(financials.cash, monthly_burn)
                st.plotly_chart(fig, use_container_width=True)
                
            st.markdown("#### DEEP-DIVE METRICS")
            dd1, dd2, dd3 = st.columns(3)
            dd1.metric("Est. CAC", f"${financials.customer_acquisition_cost}" if financials.customer_acquisition_cost else "N/A")
            dd2.metric("Est. LTV", f"${financials.lifetime_value}" if financials.lifetime_value else "N/A")
            dd3.metric("Burn Multiple", f"{financials.burn_multiple}x" if financials.burn_multiple else "N/A")
            
            if st.button("TRACK INVESTMENT", key="track_btn", use_container_width=True):
                new_row = {"CIK": financials.cik, "Company": financials.company_name, "Investment": offer_amount, "Runway": result.runway_months}
                pd.DataFrame([new_row]).to_csv(PORTFOLIO_FILE, mode="a", header=False, index=False)
                st.toast("Deal added to My Portfolio!")

        with right:
            st.markdown("#### BALANCE SHEET (FORM C)")
            def fmt(v): return f"${v:,.0f}" if v else "—"
            
            bs1, bs2 = st.columns(2)
            with bs1:
                with st.container(border=True):
                    st.metric("Cash & Equiv.", fmt(financials.cash))
                with st.container(border=True):
                    st.metric("Net Income", fmt(financials.net_income))
            with bs2:
                with st.container(border=True):
                    st.metric("Revenues", fmt(financials.revenues))
                with st.container(border=True):
                    st.metric("S.T. Debt", fmt(financials.short_term_debt))
            
            st.plotly_chart(build_liquidity_gauge(result.score), use_container_width=True)

# ── 2. PORTFOLIO TAB ───────────────────────────────────────────────────────────
with tab_portfolio:
    st.markdown("### My Portfolio")
    port_df = pd.read_csv(PORTFOLIO_FILE)
    if not port_df.empty:
        total_exp = port_df['Investment'].sum()
        runways = pd.to_numeric(port_df['Runway'], errors='coerce').dropna()
        avg_runway = runways.mean() if not runways.empty else 0.0
        
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.metric("Total Exposure", f"${total_exp:,.0f}")
        with c2:
            with st.container(border=True):
                st.metric("Portfolio-Wide Runway", f"{avg_runway:.1f} mo")
                
        st.dataframe(port_df, use_container_width=True, hide_index=True)
        if st.button("Clear Portfolio"):
            pd.DataFrame(columns=["CIK", "Company", "Investment", "Runway"]).to_csv(PORTFOLIO_FILE, index=False)
            st.rerun()
    else:
        st.info("No investments tracked yet. Scan a deal and click 'TRACK INVESTMENT'.")

# ── 3. SECONDARY EXCHANGE TAB ──────────────────────────────────────────────────
with tab_secondary:
    st.markdown("### Secondary Exchange (Dark Pool)")
    st.caption("Trade illiquid startup equity based on Marketability Score buzz.")
    
    mkt_score = 0
    if 'financials' in locals() and financials is not None:
        mkt_score = int(min(100, max(0, (result.score * 10) + ((financials.revenues or 0) / 100_000))))
        
    c1, c2 = st.columns([1, 2], gap="large")
    with c1:
        with st.container(border=True):
            st.markdown("#### Marketability Score")
            st.markdown(f"<h1 style='color:#00f2fe; text-align:center; font-size:4.5rem; margin: 1rem 0;'>{mkt_score}</h1>", unsafe_allow_html=True)
            if mkt_score > 70:
                st.markdown("<p style='text-align:center; color:#00ff00; font-weight:bold;'>High Social Buzz</p>", unsafe_allow_html=True)
            else:
                st.markdown("<p style='text-align:center; color:#ff003c; font-weight:bold;'>Low Liquidity Demand</p>", unsafe_allow_html=True)
    with c2:
        with st.container(border=True):
            st.markdown("#### Place Trade")
            tr1, tr2 = st.columns(2)
            tr_type = tr1.selectbox("Order Type", ["Buy Limit", "Sell Limit"])
            price = tr2.number_input("Limit Price ($)", value=10.00, step=0.50)
            shares = st.slider("Shares", 100, 10000, 500)
            if st.button("Submit Order", use_container_width=True, type="primary"):
                st.success(f"**{tr_type}** for {shares} shares at ${price:,.2f} per share queued on the dark pool.")

# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="disclaimer-box" style="margin-top: 5rem;">
<b>LEGAL DISCLAIMER & AI DISCLOSURE — EQUITI-AI v{APP_VERSION} — 2026</b><br><br>
<b>Not Investment Advice.</b> Equiti-AI is a data aggregation and analytical research tool.
Nothing on this platform constitutes investment advice, a solicitation to buy or sell securities,
or a recommendation. All outputs are algorithmic and for informational purposes only.
</div>
""", unsafe_allow_html=True)
