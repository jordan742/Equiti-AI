"""
Equiti-AI x AlphaDesk Pro: Final Visual Sync (Artifact Identity)
Streamlit Cloud entry point: streamlit_app.py
"""

import os, time, hashlib, random
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import date, timedelta
from edgar import set_identity
import harvester

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════
SEC_IDENTITY   = os.getenv("SEC_IDENTITY", "Equiti-AI Admin admin@equiti.com")
APP_VERSION    = "8.0.0-ARTIFACT-SYNC"
PORTFOLIO_FILE = "portfolio.csv"
set_identity(SEC_IDENTITY)

if "view_mode" not in st.session_state: st.session_state.view_mode = "grid"
if "active_deal" not in st.session_state: st.session_state.active_deal = None
if "deals_cache" not in st.session_state: st.session_state.deals_cache = {}

st.set_page_config(
    page_title="Equiti-AI | Discovery Terminal",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════════
# ARTIFACT CSS: PURE WHITE & 1PX BORDERS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #333333; }
  
  /* Pure White Background */
  div.stApp { background-color: #FFFFFF !important; }
  section[data-testid="stSidebar"] { background-color: #F9F9F9 !important; border-right: 1px solid #E5E5E5; }
  
  /* Typography */
  h1, h2, h3, h4, h5, h6 { color: #000000 !important; font-weight: 700 !important; }
  
  /* Top Intelligence Feed Ribbon */
  .intelligence-feed {
      display: flex; gap: 1rem; align-items: center; justify-content: start;
      padding: 0.75rem 0; margin-bottom: 2rem; border-bottom: 1px solid #E5E5E5;
      font-size: 0.85rem; font-weight: 600; text-transform: uppercase; color: #000000;
  }
  .feed-badge { padding: 0.2rem 0.6rem; border-radius: 4px; border: 1px solid #E5E5E5; background: #FFFFFF; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
  .alert-red { color: #ef4444; border-color: #ef4444; background: rgba(239, 68, 68, 0.05); }
  .alert-yellow { color: #f59e0b; border-color: #f59e0b; background: rgba(245, 158, 11, 0.05); }
  .alert-blue { color: #3b82f6; border-color: #3b82f6; background: rgba(59, 130, 246, 0.05); }

  /* Minimalist 16px Grid Cards */
  div[data-testid="stContainer"] > div {
    background: #FFFFFF !important; 
    border: 1px solid #E5E5E5 !important; 
    border-radius: 16px !important;
    padding: 1.5rem !important;
    box-shadow: none !important;
    transition: all 0.2s ease-in-out;
  }
  div[data-testid="stContainer"] > div:hover {
    border: 1px solid #CCCCCC !important; 
  }
  
  /* Primary Button Override (Black Sharp) */
  .stButton > button {
      background-color: #000000 !important;
      color: #FFFFFF !important;
      font-weight: 600 !important;
      border-radius: 8px !important;
      border: none !important;
      padding: 0.5rem 1rem !important;
  }
  .stButton > button:hover {
      background-color: #333333 !important;
      color: #FFFFFF !important;
      border: none !important;
  }
  
  div[data-testid="stMetric"] label { color: #666666 !important; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; }
  div[data-testid="stMetric"] div { color: #000000 !important; font-size: 2.2rem; font-weight: 700; font-variant-numeric: tabular-nums; }
  
  /* Sidebar Font Size */
  div[role="radiogroup"] label { font-size: 1.05rem; font-weight: 600; color: #000000; }
  
  /* Minimal Footer */
  .footer {
      position: fixed; left: 0; bottom: 0; width: 100%;
      background-color: #FFFFFF; border-top: 1px solid #E5E5E5;
      color: #A3A3A3; text-align: center; padding: 0.5rem;
      font-size: 10px; font-weight: 500; z-index: 1000;
  }
  
  /* Secondary Market Orderbook Table */
  .orderbook { width: 100%; font-family: 'Inter', monospace; font-size: 0.85rem; text-align: left; }
  .orderbook th { border-bottom: 2px solid #E5E5E5; padding-bottom: 0.5rem; color: #000000; }
  .orderbook td { padding: 0.3rem 0; border-bottom: 1px solid #F5F5F5; }
  .ask { color: #ef4444; font-weight: 600; }
  .bid { color: #22c55e; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MOCK GENERATORS & ALGORITHMS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_candlesticks(days: int = 30) -> pd.DataFrame:
    np.random.seed(42)
    base = 100.0
    dates = [date.today() - timedelta(days=x) for x in range(days)]
    dates.reverse()
    df = pd.DataFrame({'Date': dates})
    prices = [base]
    for _ in range(1, days): prices.append(prices[-1] * (1 + np.random.normal(0, 0.02)))
    df['Close'] = prices
    df['Open'] = df['Close'] * (1 + np.random.normal(0, 0.01))
    df['High'] = df[['Open', 'Close']].max(axis=1) * (1 + abs(np.random.normal(0, 0.005)))
    df['Low'] = df[['Open', 'Close']].min(axis=1) * (1 - abs(np.random.normal(0, 0.005)))
    return df

def get_logo_emoji(name: str) -> str:
    emojis = ["🚀", "⚡", "🧬", "🤖", "☁️", "📈", "🛡️", "🌐", "🧠"]
    return emojis[int(hashlib.sha256(name.encode('utf-8')).hexdigest(), 16) % len(emojis)]

@st.dialog("Safety Check: Pre-Trade Verification")
def execute_trade_modal(asset, shares, price, action):
    st.markdown(f"### You are routing a {action} for {shares:,} shares of {asset}")
    st.info("Because private equity is highly illiquid, Federal regulations require active checklist confirmation before submitting directly to the Ledger.")
    c1 = st.checkbox("1. Is this money you can completely afford to lose?")
    c2 = st.checkbox("2. Do you conceptually understand the 12-month lockup transfer constraints?")
    c3 = st.checkbox("3. Have you reviewed the SEC Risk Factors explicitly warning against private speculation?")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("EXECUTE TRADE", use_container_width=True, type="primary", disabled=not (c1 and c2 and c3)):
        st.success("Trade authorized. Routing instantly to Dark Pool execution matrix.")
        time.sleep(2)
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# ARTIFACT SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
modules = ["Intelligence & Discovery", "Secondary Market"]

with st.sidebar:
    st.markdown("### EQUITI-AI OS")
    current_page = st.radio("Navigation Engine", modules, label_visibility="collapsed")
    
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.caption("Active Development Build")
    with st.expander("Admin Debug / Tools"):
        if st.button("Purge Deal Cache", use_container_width=True):
            st.session_state.deals_cache.clear()

# ═══════════════════════════════════════════════════════════════════════════════
# CURRENT PAGE LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

if current_page == "Intelligence & Discovery":
    
    # ── PILLAR 1: THE INTELLIGENCE FEED ─────────────────────────────────────
    st.markdown("""
    <div class="intelligence-feed">
        <span style="color:#A3A3A3; font-weight:400; font-size:0.75rem;">LIVE INTELLIGENCE FEED |</span>
        <span class="feed-badge alert-red">🚨 Covenant Breach: Massive Dynamic</span>
        <span class="feed-badge alert-yellow">📅 SEC Filing Due: Globex Aerospace</span>
        <span class="feed-badge alert-blue">📈 Market Volatility: LSTA Index Jump</span>
    </div>
    """, unsafe_allow_html=True)
    
    # ── PILLAR 2: ARTIFACT DISCOVERY GRID ───────────────────────────────────
    if st.session_state.view_mode == "grid":
        urls = harvester.discover_recent_deals()
        
        with st.spinner("Synchronizing SEC data vectors..."):
            for url in urls:
                if url not in st.session_state.deals_cache:
                    st.session_state.deals_cache[url] = harvester.harvest(url)
                    
        for i in range(0, len(urls), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(urls):
                    url = urls[i+j]
                    deal = st.session_state.deals_cache[url]
                    with cols[j]:
                        with st.container():
                            hs = int((deal.governance_score + deal.social_buzz_velocity) / 2)
                            h1, h2 = st.columns([3, 1])
                            h1.markdown(f"### {get_logo_emoji(deal.company_name)} {deal.company_name}")
                            
                            color = "#22c55e" if hs > 60 else "#f59e0b"
                            h2.markdown(f"<div style='text-align:right; font-weight:700; color:{color};'>{hs}/100</div>", unsafe_allow_html=True)
                            
                            st.markdown(f"<p style='font-size:0.9rem; margin-top:0.5rem; height:4rem; color:#666666;'>{deal.elevator_pitch}</p>", unsafe_allow_html=True)
                            
                            if st.button("Analyze Opportunity", key=f"btn_{deal.cik}", use_container_width=True):
                                st.session_state.active_deal = deal
                                st.session_state.view_mode = "audit"
                                st.rerun()

    # ── PILLAR 3: COMPANY DEEP-DIVE (ALPHADESK DATA LAYER) ──────────────────
    elif st.session_state.view_mode == "audit":
        deal = st.session_state.active_deal

        if st.button("← Back to Discovery Feed"):
            st.session_state.view_mode = "grid"
            st.session_state.active_deal = None
            st.rerun()
            
        st.markdown(f"## {get_logo_emoji(deal.company_name)} {deal.company_name}")
        st.caption(f"**Sector:** {deal.sector} | **CIK:** {deal.cik} | **Integrity Score:** {deal.founder_integrity_score}/100")
        
        # Retail Section
        st.markdown("### Retail Overview")
        rc1, rc2 = st.columns(2)
        with rc1:
            with st.container():
                max_vel = 300_000
                val = min(deal.funding_velocity, max_vel)
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number", value = val,
                    title = {'text': "Funding Velocity", 'font': {'color': '#000000', 'size': 14}},
                    gauge = {
                        'axis': {'range': [None, max_vel], 'tickcolor': "#E5E5E5"},
                        'bar': {'color': "#000000"},
                        'steps': [
                            {'range': [0, 50000], 'color': "#F9F9F9"},
                            {'range': [50000, 150000], 'color': "#E5E5E5"},
                            {'range': [150000, max_vel], 'color': "#ef4444"}],
                    }
                ))
                fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=30, b=10, l=10, r=10), height=220)
                st.plotly_chart(fig_gauge, use_container_width=True)
        with rc2:
            with st.container():
                st.markdown("<div style='text-align:center; color:#000000; font-weight:700; margin-bottom:1rem;'>Calculated Burn Matrix</div>", unsafe_allow_html=True)
                m1, m2 = st.columns(2)
                bm = f"{deal.burn_multiple}x" if deal.burn_multiple else "N/A"
                m1.metric("Burn Multiple", bm)
                m2.metric("Op. Margin", f"{deal.operating_margin}%" if deal.operating_margin else "N/A")
                st.caption("Lower Burn Multiple signifies highly efficient localized cash deployment. Negative margins are standard for hyper-growth artifacts.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Institutional Section (AlphaDesk Engine Sync)
        with st.expander("💼 Professional Underwriting & Modeler", expanded=False):
            st.markdown("#### 5-Year Synthesized LBO Return Profile")
            i1, i2, i3, i4 = st.columns(4)
            rev = i1.number_input("Est. Revenue ($M)", value=max(10.0, deal.revenues/1000000 if deal.revenues else 10.0))
            ebitda_mar = i2.number_input("EBITDA Margin (%)", value=20.0)
            entry_mult = i3.number_input("Entry EV/EBITDA", value=deal.sector_multiplier * 2)
            lev_ratio = i4.slider("Leverage Ratio", 1.0, 7.0, 4.0, 0.5)
            
            ebitda = rev * (ebitda_mar/100)
            entry_ev = ebitda * entry_mult
            equity = entry_ev - (ebitda * lev_ratio)
            
            years = [1, 2, 3, 4, 5]
            proj_ebitda = [(rev * (1.10 ** y)) * (ebitda_mar/100) for y in years]
            exit_ev = proj_ebitda[-1] * entry_mult
            debt_left = (ebitda * lev_ratio) * 0.7 
            exit_equity = exit_ev - debt_left
            moic = exit_equity / equity if equity > 0 else 0
            irr = ((moic ** (1/5)) - 1) * 100 if moic > 0 else 0
            
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("EV Entry", f"${entry_ev:.1f}M")
            r2.metric("Sponsor Eq.", f"${equity:.1f}M")
            r3.metric("Projected MOIC", f"{moic:.2f}x")
            r4.metric("Blended IRR", f"{irr:.1f}%")
            
            st.markdown("---")
            st.markdown("#### Database Overwrite")
            st.caption("AlphaDesk Master Layer Sync: Import proprietary localized spread validations over SEC Form C scraped values.")
            st.file_uploader("Import Primary Institutional Ledger (.csv, .xlsx)", type=["csv", "xlsx"])

# ═══════════════════════════════════════════════════════════════════════════════
# PILLAR 4: ACCESSIBLE SECONDARY MARKET
# ═══════════════════════════════════════════════════════════════════════════════
elif current_page == "Secondary Market":
    st.markdown("## 🔄 OTC Execution Interface")
    
    # Top: Candlestick Chart
    df_candle = generate_candlesticks(90)
    fig_candle = go.Figure(data=[go.Candlestick(
        x=df_candle['Date'], open=df_candle['Open'],
        high=df_candle['High'], low=df_candle['Low'], close=df_candle['Close'],
        increasing_line_color='#22c55e', decreasing_line_color='#ef4444'
    )])
    fig_candle.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis_rangeslider_visible=False, height=350,
        yaxis=dict(gridcolor="#E5E5E5"), xaxis=dict(gridcolor="rgba(0,0,0,0)")
    )
    
    with st.container():
        st.markdown("### Price Discovery [ACME.P]")
        st.plotly_chart(fig_candle, use_container_width=True)
    
    # Middle & Bottom: Order Book & Retail Box
    c_book, c_trade = st.columns([1, 1], gap="large")
    with c_book:
        st.markdown("#### Scaled Order Book L2")
        st.markdown("""
        <table class="orderbook">
            <tr><th>Type</th><th>Price</th><th>Volume</th></tr>
            <tr><td class='ask'>Ask</td><td>106.50</td><td>25,000</td></tr>
            <tr><td class='ask'>Ask</td><td>106.25</td><td>10,000</td></tr>
            <tr><td class='ask'>Ask</td><td>106.10</td><td>4,500</td></tr>
            <tr><td style='color:#E5E5E5;'>---</td><td style='color:#E5E5E5;'>---</td><td style='color:#E5E5E5;'>---</td></tr>
            <tr><td class='bid'>Bid</td><td>105.90</td><td>50,000</td></tr>
            <tr><td class='bid'>Bid</td><td>105.75</td><td>100,000</td></tr>
            <tr><td class='bid'>Bid</td><td>105.60</td><td>15,000</td></tr>
        </table>
        """, unsafe_allow_html=True)
        
    with c_trade:
        with st.container():
            st.markdown("#### Sandbox Execution")
            tr_type = st.selectbox("Market Bias", ["Bid (Buy Level)", "Ask (Sell Level)"], label_visibility="collapsed")
            col_sh, col_pr = st.columns(2)
            shares = col_sh.number_input("Shares", value=5000)
            price = col_pr.number_input("Limit Price", value=106.15, step=0.10)
            
            st.markdown(f"### Score: <span style='color:#22c55e;'>92/100</span> (Highly Liquid)", unsafe_allow_html=True)
            
            if st.button("EXECUTE TRADE", type="primary", use_container_width=True):
                execute_trade_modal("ACME", shares, price, tr_type)


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL COMPLIANCE FOOTER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer">
    Equiti-AI Institutional Tier. Data provided for analytical purposes. Not a registered broker-dealer.
</div>
""", unsafe_allow_html=True)
