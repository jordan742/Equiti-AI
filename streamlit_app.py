"""
Equiti-AI x AlphaDesk Pro: Unified Institutional OS
Streamlit Cloud entry point: streamlit_app.py
"""

import os, time, hashlib, random
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import date, timedelta
from edgar import set_identity
import harvester

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════
SEC_IDENTITY   = os.getenv("SEC_IDENTITY", "AlphaDesk Admin admin@alphadesk.com")
APP_VERSION    = "7.0.0-ALPHADESK-OS"
PORTFOLIO_FILE = "portfolio.csv"
set_identity(SEC_IDENTITY)

if "view_mode" not in st.session_state: st.session_state.view_mode = "grid"
if "active_deal" not in st.session_state: st.session_state.active_deal = None
if "deals_cache" not in st.session_state: st.session_state.deals_cache = {}

st.set_page_config(
    page_title="AlphaDesk Pro | Unified UI",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════════
# ALPHADESK CSS: NAVY-CHARCOAL & STATUS HIGHLIGHTS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  /* Navy-Charcoal Base */
  div.stApp { background-color: #0f172a; } /* Slate 900 */
  
  .terminal-hdr {
    background: #1e293b; /* Slate 800 */
    border-bottom: 2px solid #3b82f6; /* Blue 500 */
    padding: 1.2rem 2rem; margin-bottom: 2rem;
  }
  .terminal-hdr h1 { color: #f8fafc; margin:0; font-size:1.6rem; letter-spacing:0.5px; font-weight: 700; text-transform: uppercase; }
  .terminal-hdr p  { color: #94a3b8; margin:0.2rem 0 0; font-size:0.85rem; letter-spacing:1px; }

  /* Institutional Panel Container */
  div[data-testid="stContainer"] > div {
    background: #1e293b; 
    border: 1px solid #334155; 
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
    color: #cbd5e1;
  }
  
  /* KPI Typography */
  div[data-testid="stMetric"] label { color: #94a3b8 !important; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; }
  div[data-testid="stMetric"] div { color: #f8fafc !important; font-size: 2.2rem; font-weight: 700; }

  /* AlphaDesk Status Badges */
  .badge-active { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 4px; background: rgba(34, 197, 94, 0.15); border: 1px solid #22c55e; color: #4ade80; font-weight: 600; font-size: 0.75rem; text-transform: uppercase; }
  .badge-watch { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 4px; background: rgba(245, 158, 11, 0.15); border: 1px solid #f59e0b; color: #fbbf24; font-weight: 600; font-size: 0.75rem; text-transform: uppercase; }
  .badge-restructure { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 4px; background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; color: #f87171; font-weight: 600; font-size: 0.75rem; text-transform: uppercase; }
  .badge-sector { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 4px; background: rgba(59, 130, 246, 0.15); border: 1px solid #3b82f6; color: #60a5fa; font-weight: 600; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 0.5rem; }

  /* Sidebar Routing Links */
  div[role="radiogroup"] label { font-size: 1.1rem; font-weight: 500; }
  
  /* Footer Pin */
  .footer {
      position: fixed; left: 0; bottom: 0; width: 100%;
      background-color: #0f172a; border-top: 1px solid #334155;
      color: #64748b; text-align: center; padding: 0.75rem;
      font-size: 0.7rem; font-weight: 500; z-index: 1000;
  }
  
  .stDataFrame { background: #1e293b; border-radius: 8px; }
  table { color: #cbd5e1 !important; }
  th { background-color: #0f172a !important; color: #94a3b8 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="terminal-hdr">
  <h1>ALPHADESK PRO &nbsp;|&nbsp; PRIVATE MARKETS UI</h1>
  <p>POWERED BY EQUITI-AI v{APP_VERSION} &nbsp;&middot;&nbsp; SEC EDGAR CONNECTED</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MOCK GENERATORS & ALGORITHMS (PORTFOLIO & OTC)
# ═══════════════════════════════════════════════════════════════════════════════
def generate_portfolio_df() -> pd.DataFrame:
    data = []
    names = ["Acme Cloud Storage", "Globex Aerospace", "Soylent Foods", "Initech Software", "Massive Dynamic Biotech"]
    sectors = ["SaaS", "DeepTech", "Retail", "Enterprise Software", "Healthcare"]
    types = ["Equity", "Sub-Debt", "Equity", "Equity", "Senior Term Loan"]
    statuses = ["Active", "Watch", "Active", "Active", "Restructuring"]
    for i in range(5):
        cost = random.uniform(5.0, 50.0)
        moic = random.uniform(0.5, 4.5)
        fmv = cost * moic
        irr = ((moic ** (1/random.uniform(1.0, 5.0))) - 1) * 100
        data.append({
            "Company": names[i], "Sector": sectors[i], "Type": types[i],
            "Cost ($M)": round(cost, 1), "FMV ($M)": round(fmv, 1),
            "MOIC": round(moic, 2), "IRR (%)": round(irr, 1),
            "Lev.": f"{random.uniform(1.5, 6.0):.1f}x",
            "Rating": random.choice(["L1", "L2", "L3"]), "Status": statuses[i]
        })
    return pd.DataFrame(data)

def generate_candlesticks(days: int = 30) -> pd.DataFrame:
    np.random.seed(42)
    base = 100.0
    dates = [date.today() - timedelta(days=x) for x in range(days)]
    dates.reverse()
    df = pd.DataFrame({'Date': dates})
    prices = [base]
    for _ in range(1, days):
        prices.append(prices[-1] * (1 + np.random.normal(0, 0.02)))
    df['Close'] = prices
    df['Open'] = df['Close'] * (1 + np.random.normal(0, 0.01))
    df['High'] = df[['Open', 'Close']].max(axis=1) * (1 + abs(np.random.normal(0, 0.005)))
    df['Low'] = df[['Open', 'Close']].min(axis=1) * (1 - abs(np.random.normal(0, 0.005)))
    return df

def get_logo_emoji(name: str) -> str:
    emojis = ["🚀", "⚡", "🧬", "🤖", "☁️", "📈", "🛡️", "🌐", "🧠"]
    return emojis[int(hashlib.sha256(name.encode('utf-8')).hexdigest(), 16) % len(emojis)]

# ═══════════════════════════════════════════════════════════════════════════════
# ALPHADESK SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
modules = [
    "Dashboard", "Deal Pipeline", "Portfolio", "Private Credit", 
    "LBO Model", "Secondary Exchange", "Document AI", 
    "IR & Waterfall", "Compliance", "Market Intel"
]

with st.sidebar:
    st.markdown("### ALPHA OS")
    current_page = st.radio("Core Modules", modules, label_visibility="collapsed")
    
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### LIVE RATES & TICKERS")
    c1, c2 = st.columns(2)
    c1.metric("SOFR", "5.33%")
    c2.metric("LSTA", "8.25%")
    
    with st.expander("Admin Debug"):
        if st.button("Purge Deal Cache", use_container_width=True):
            st.session_state.deals_cache.clear()

# ═══════════════════════════════════════════════════════════════════════════════
# CURRENT PAGE LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

if current_page == "Dashboard":
    # ── KPI HEADER ──────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        with st.container(): st.metric("Total AUM", "$1.45B", delta="3.2% vs Prev Qtr")
    with m2:    
        with st.container(): st.metric("Portfolio FMV", "$980M", delta="$15M Mark-Up")
    with m3:
        with st.container(): st.metric("Gross MOIC", "2.4x", delta="0.1x")
    with m4:
        with st.container(): st.metric("Blended Gross IRR", "22.8%", delta="-1.2%")
        
    st.markdown("---")
    
    # ── ALERTS SYSTEM ───────────────────────────────────────────────────────
    left, right = st.columns([2, 1])
    with left:
        st.markdown("### Portfolio Performance Overview")
        bar_x = ["Vintage 2022", "Vintage 2023", "Vintage 2024", "Vintage 2025"]
        bar_y = [2.8, 1.9, 1.2, 1.05]
        fig_bar = go.Figure([go.Bar(x=bar_x, y=bar_y, marker_color='#3b82f6')])
        fig_bar.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", title="MOIC by Vintage", height=350)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with right:
        st.markdown("### Alerts & Required Actions")
        with st.container():
            st.error("🚨 **COVENANT BREACH:** Massive Dynamic Biotech FCCR dropped below 1.15x threshold. Action required by Workout Group.")
            st.warning("⚠️ **SEC DEADLINE:** Globex Aerospace Form C-AR due in 4 days. Missing XBRL tags detected in Document AI pipeline.")
            st.info("ℹ️ **CAPITAL CALL:** Fund III quarterly capital call notices due to LP portal next Tuesday.")

elif current_page == "Portfolio":
    st.markdown("## 📊 Active Strategy Positions")
    st.caption("AlphaDesk Strict Schema Mode: Use the drag-and-drop ingestion engine to instantly append new holdings to the database.")
    
    # ── EXCEL INGESTION MODULE ──────────────────────────────────────────────
    up_col, stats_col = st.columns([3, 1])
    with up_col:
        st.file_uploader("📥 Drag & Drop Deal Ledger (CSV / Excel format compliant with standard mapping)", type=["csv", "xlsx"])
    with stats_col:
        st.markdown("<br>", unsafe_allow_html=True)
        st.success("✅ **SYSTEM CHECK:** Master Database Sync Active.")
        
    st.markdown("---")
    
    df = generate_portfolio_df()
    
    # Apply AlphaDesk badging via pandas st.dataframe / markdown table equivalent
    def style_status(val):
        if val == "Active": return "color: #4ade80; font-weight: bold;"
        elif val == "Watch": return "color: #fbbf24; font-weight: bold;"
        return "color: #f87171; font-weight: bold;"
        
    st.dataframe(df.style.map(style_status, subset=['Status']), use_container_width=True, hide_index=True)

elif current_page == "LBO Model":
    st.markdown("## ⚙️ 5-Year LBO Engine")
    st.caption("Standardized Private Equity entry/exit telemetry for standalone mid-market sweeps.")
    
    i1, i2, i3, i4 = st.columns(4)
    rev        = i1.number_input("Current Revenue ($M)", value=100.0)
    ebitda_mar = i2.number_input("EBITDA Margin (%)", value=20.0)
    entry_mult = i3.number_input("Entry EV/EBITDA", value=10.0)
    lev_ratio  = i4.slider("Leverage (Debt/EBITDA)", 1.0, 7.0, 4.0, 0.5)
    
    # Simple Math
    ebitda = rev * (ebitda_mar/100)
    entry_ev = ebitda * entry_mult
    debt = ebitda * lev_ratio
    equity = entry_ev - debt
    
    st.markdown("---")
    st.markdown("### Model Outputs")
    o1, o2, o3, o4 = st.columns(4)
    o1.metric("Initial EBITDA", f"${ebitda:.1f}M")
    o2.metric("Entry Enterprise Value", f"${entry_ev:.1f}M")
    o3.metric("Senior Term Loan (Debt)", f"${debt:.1f}M")
    o4.metric("Sponsor Equity Check", f"${equity:.1f}M")
    
    # 5 Year Projection
    years = [1, 2, 3, 4, 5]
    proj_rev = [rev * (1.10 ** y) for y in years] # 10% growth
    proj_ebitda = [r * (ebitda_mar/100) for r in proj_rev]
    exit_ev = proj_ebitda[-1] * entry_mult
    paydown = debt * 0.3 # assumed 30% debt paydown over 5 years
    exit_debt = debt - paydown
    exit_equity = exit_ev - exit_debt
    moic = exit_equity / equity if equity > 0 else 0
    irr = ((moic ** (1/5)) - 1) * 100 if moic > 0 else 0
    
    st.markdown("<br>", unsafe_allow_html=True)
    r1, r2 = st.columns(2)
    with r1:
        with st.container():
            st.markdown("#### Exit Assumptions (Year 5)")
            st.metric("Exit Enterprise Value", f"${exit_ev:.1f}M")
            st.metric("Exit Equity Value", f"${exit_equity:.1f}M")
    with r2:
        with st.container():
            st.markdown("#### Returns Matrix")
            st.markdown(f"<h1 style='color:#3b82f6;'>{moic:.2f}x MOIC</h1>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='color:#22c55e;'>{irr:.1f}% Gross IRR</h2>", unsafe_allow_html=True)

elif current_page == "Secondary Exchange":
    st.markdown("## 🔄 Private Markets Order Book")
    st.caption("OTC Dark Pool limit execution mapped onto standardized SaaS valuation indexes.")
    
    left, right = st.columns([3, 1])
    with left:
        st.markdown("### Asset: Acme Cloud Storage [ACME.P]")
        df_candle = generate_candlesticks(90)
        fig_candle = go.Figure(data=[go.Candlestick(
            x=df_candle['Date'], open=df_candle['Open'],
            high=df_candle['High'], low=df_candle['Low'], close=df_candle['Close']
        )])
        fig_candle.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_rangeslider_visible=False, height=450)
        st.plotly_chart(fig_candle, use_container_width=True)
        
    with right:
        with st.container():
            st.markdown("#### Limit Order Engine")
            tr_type = st.selectbox("Action", ["Bid (Buy)", "Ask (Sell)"])
            shares = st.number_input("Shares / Units", value=50000, step=5000)
            price = st.number_input("Limit Price ($)", value=106.50, step=0.50)
            st.markdown(f"**Notional:** ${(shares * price):,.2f}")
            if st.button("ROUTE TO DARK POOL", type="primary", use_container_width=True):
                st.success("Limit order injected into ledger.")
                
        with st.container():
            st.markdown("#### L2 Depth")
            st.markdown("🔴 Ask: 106.50 x 25k")
            st.markdown("🔴 Ask: 106.25 x 10k")
            st.markdown("---")
            st.markdown("🟢 Bid: 105.90 x 50k")
            st.markdown("🟢 Bid: 105.75 x 100k")

elif current_page == "Deal Pipeline":
    st.markdown("## 📡 Pipeline & M&A Discovery")
    urls = harvester.discover_recent_deals()
    for i in range(0, len(urls), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(urls):
                with cols[j]:
                    with st.container():
                        name = urls[i+j].split("/")[-1].replace("-", " ").title()
                        st.markdown(f"### {get_logo_emoji(name)} {name}")
                        st.markdown("<span class='badge-pipeline'>Phase: Diligence</span>", unsafe_allow_html=True)
                        st.write("Retained from original Equiti-AI Harvester core.")

else:
    st.markdown(f"## {current_page}")
    st.info(f"The `{current_page}` module is currently locked in Institutional Demo Mode.")

# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL COMPLIANCE FOOTER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer">
    Equiti-AI Institutional Tier (AlphaDesk Architecture). Data provided for analytical purposes. Not a registered broker-dealer.
</div>
""", unsafe_allow_html=True)
