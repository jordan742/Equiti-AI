"""
Equiti-AI: Comprehensive Investment Research & Reading Platform
Streamlit Cloud Entry Point (Visual Directive: FT / Goldman Research Terminal)
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
SEC_IDENTITY   = os.getenv("SEC_IDENTITY", "Equiti-AI Research admin@equiti.com")
APP_VERSION    = "9.0.0-GOLDMAN-TERMINAL"
set_identity(SEC_IDENTITY)

if "view_mode" not in st.session_state: st.session_state.view_mode = "grid"
if "active_deal" not in st.session_state: st.session_state.active_deal = None
if "deals_cache" not in st.session_state: st.session_state.deals_cache = {}

st.set_page_config(
    page_title="Equiti-AI Research Hub",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════════
# ALPHA-RETAIL LEXICON (Tooltips)
# ═══════════════════════════════════════════════════════════════════════════════
LEXICON = {
    "MOIC": "Money Multiple: A 2.0x MOIC means you have doubled your original investment.",
    "IRR": "Annual Growth Rate: The average speed your investment grows each year.",
    "Burn Multiple": "Efficiency Ratio: How much the startup spends to generate $1 of new revenue.",
    "LBO Model": "Debt Analysis: A model that checks if the company can pay off its debts using its own cash flow.",
    "Marketability Score": "Liquidity Check: How easy it is to sell your shares for cash right now.",
    "SOFR/LSTA": "Market Benchmark: The standard interest rates banks use to price business loans."
}

# ═══════════════════════════════════════════════════════════════════════════════
# ELITE AESTHETICS (FT / Goldman Sachs Styling)
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Serif:ital,wght@0,400;0,600;1,400&display=swap');
  
  html, body, [class*="css"] { 
      font-family: 'Inter', -apple-system, sans-serif; 
      color: #000000 !important; 
      background-color: #FFFFFF !important; 
  }
  
  /* Pure White Backgrounds */
  div.stApp { background-color: #FFFFFF !important; }
  section[data-testid="stSidebar"] { background-color: #F9F9F9 !important; border-right: 1px solid #E5E5E5; }
  
  /* Typography - Editorial */
  h1, h2, h3, h4, h5, h6 { font-family: 'Inter', sans-serif !important; color: #000000 !important; font-weight: 700 !important; letter-spacing: -0.5px; }
  p { font-size: 1.05rem; line-height: 1.6; color: #333333; }
  
  /* 16px Rounded Cards - No Shadows */
  div[data-testid="stContainer"] > div {
    background: #FFFFFF !important; 
    border: 1px solid #E5E5E5 !important; 
    border-radius: 16px !important;
    padding: 1.5rem !important;
    box-shadow: none !important;
    color: #000000 !important;
  }
  
  /* Top Intelligence Feed Navigation */
  .intelligence-ribbon {
      border-bottom: 1px solid #E5E5E5; padding: 0.5rem 0; margin-bottom: 2.5rem;
      display: flex; gap: 1.5rem; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;
      align-items: center; letter-spacing: 0.5px; width: 100%;
  }
  .intel-tag { color: #A3A3A3; margin-right: 1rem; }
  .alert-badge { border: 1px solid #E5E5E5; padding: 0.15rem 0.5rem; border-radius: 4px; background: #FFFFFF; }
  
  /* Thesis Bullets */
  .thesis-bullet { font-size: 1.1rem; border-left: 2px solid #000000; padding-left: 1rem; margin-bottom: 1rem; font-weight: 500; }
  
  /* Solid Black primary button */
  .stButton > button {
      background-color: #000000 !important;
      color: #FFFFFF !important;
      font-weight: 600 !important;
      border-radius: 8px !important;
      border: 1px solid #000000 !important;
      padding: 0.5rem 1rem !important;
      text-transform: uppercase; letter-spacing: 0.5px;
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
# MOCK GENERATORS / HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def generate_candlesticks(days: int = 90) -> pd.DataFrame:
    np.random.seed(42)
    base = 100.0
    dates = [date.today() - timedelta(days=x) for x in range(days)]
    dates.reverse()
    df = pd.DataFrame({'Date': dates})
    prices = [base]
    for _ in range(1, days): prices.append(prices[-1] * (1 + np.random.normal(0, 0.025)))
    df['Close'] = prices
    df['Open'] = df['Close'] * (1 + np.random.normal(0, 0.01))
    df['High'] = df[['Open', 'Close']].max(axis=1) * (1 + abs(np.random.normal(0, 0.005)))
    df['Low'] = df[['Open', 'Close']].min(axis=1) * (1 - abs(np.random.normal(0, 0.005)))
    return df

def get_logo_emoji(name: str) -> str:
    emojis = ["🚀", "⚙️", "🧬", "💻", "☁️", "📈", "🛡️", "🌐", "🧠"]
    return emojis[int(hashlib.sha256(name.encode('utf-8')).hexdigest(), 16) % len(emojis)]

def generate_thesis(sector: str) -> list[str]:
    return [
        f"Significant market penetration expected in the {sector} vertical driven by favorable underlying macroeconomic regulation.",
        "Management has repeatedly demonstrated capital efficiency resulting in an artificially low burn-multiple relative to peers.",
        "Proprietary distribution channels lock in LTV metrics that strongly justify the current entry EV valuation."
    ]

def generate_narrative(name: str) -> str:
    return f"""**Executive Summary:** {name} operates at the frontier of its vertical, deploying rapid capital to isolate 
    key intellectual property advantages before institutional money prices them out. The founding team brings ex-FAANG 
    operational rigor, immediately reflecting heavily in their tight margins and explosive top-line growth.

**Market Tailwinds:** Federal regulatory frameworks currently advantage localized operators over global incumbents. This creates 
a 36-month window for {name} to scale operations nationally before compliance burdens flatten the landscape. 

**Underwriting Perspective:** We view this asset as a high-velocity play perfectly suited for early-liquidity milestones.
"""

@st.dialog("Execution Gateway")
def execution_modal(asset: str):
    st.markdown(f"### Trade Authorization: {asset}")
    st.markdown("You are submitting binding electronic instruction to purchase illiquid equity.")
    c1 = st.checkbox("Accept 12-Month Reg CF Lockup")
    c2 = st.checkbox("Sign Binding Transfer Agreement")
    if st.button("AUTHORIZE FUNDS", disabled=not (c1 and c2), type="primary", use_container_width=True):
        st.success(f"Trade successful. Funds deducted and {asset} equity routed to ledger.")
        time.sleep(2)
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### EQUITI RESEARCH")
    st.markdown("<br>", unsafe_allow_html=True)
    current_page = st.radio("Core Index", ["Discovery", "My Portfolio", "Secondary Market", "Document AI"], label_visibility="collapsed")
    
    # 10px Market Footer
    st.markdown(f"""
    <div class="sidebar-footer">
        <b>MARKET BENCHMARKS</b><br>
        SOFR: 5.33%<br>
        LSTA INDEX: 8.25%<br>
        <span title="{LEXICON['SOFR/LSTA']}">Hover for definitions.</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    with st.expander("Admin / Debug"):
        if st.button("Purge Deal Cache", use_container_width=True):
            st.session_state.deals_cache.clear()

# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INTELLIGENCE HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="intelligence-ribbon">
    <span class="intel-tag">EQUITI INTELLIGENCE</span>
    <span class="alert-badge">🚨 Covenant Breach: Massive Dynamic</span>
    <span class="alert-badge">📅 SEC Form C Due: Globex Aerospace</span>
    <span class="alert-badge">📈 New Bid: Acme Cloud Storage</span>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ROUTING LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

if current_page == "Discovery":
    
    if st.session_state.view_mode == "grid":
        st.markdown("## Primary Research Grid")
        st.caption("Editorial curation of active Private Market opportunities.")
        urls = harvester.discover_recent_deals()
        
        with st.spinner("Compiling Editorial Data..."):
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
                            h1.markdown(f"#### {get_logo_emoji(deal.company_name)} {deal.company_name}")
                            color = "#000000" if hs > 60 else "#666666"
                            h2.markdown(f"<div style='text-align:right; font-weight:700; color:{color}; font-size:1.2rem;'>{hs}</div>", unsafe_allow_html=True)
                            
                            st.markdown(f"<p style='font-size:0.9rem; margin-top:0.5rem; height:4rem; color:#666666;'>{deal.elevator_pitch}</p>", unsafe_allow_html=True)
                            
                            if st.button("Read Memorandum", key=f"btn_{deal.cik}", use_container_width=True):
                                st.session_state.active_deal = deal
                                st.session_state.view_mode = "memo"
                                st.rerun()

    elif st.session_state.view_mode == "memo":
        deal = st.session_state.active_deal
        
        if st.button("← Return To Sector Research", type="secondary"):
            st.session_state.view_mode = "grid"
            st.session_state.active_deal = None
            st.rerun()
            
        st.markdown(f"## {get_logo_emoji(deal.company_name)} Investment Memorandum: {deal.company_name}")
        st.markdown("---")
        
        # ── SECTION A: THE THESIS ──────────────────────────────────────────
        st.markdown("### Section A: Investment Thesis")
        thesis_points = generate_thesis(deal.sector)
        for point in thesis_points:
            st.markdown(f"<div class='thesis-bullet'>{point}</div>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ── SECTION B: UNDERWRITING ──────────────────────────────────────────
        st.markdown("### Section B: Underwriting & Narrative")
        left, right = st.columns([3, 2], gap="large")
        with left:
            st.markdown(generate_narrative(deal.company_name))
        
        with right:
            with st.container():
                st.markdown("#### Institutional Metrics")
                m1, m2 = st.columns(2)
                # Mathematical Mock for Moic
                equity = deal.revenues * 5 if deal.revenues else 1000000
                exit_v = equity * 2.5
                est_moic = exit_v / equity if equity > 0 else 0
                est_irr = ((est_moic ** (1/5)) - 1) * 100 if est_moic > 0 else 0
                bm = f"{deal.burn_multiple}x" if deal.burn_multiple else "2.1x"
                
                m1.metric("Gross MOIC", f"{est_moic:.1f}x", help=LEXICON["MOIC"])
                m2.metric("Blended IRR", f"{est_irr:.1f}%", help=LEXICON["IRR"])
                
                m3, m4 = st.columns(2)
                m3.metric("Burn Multiple", bm, help=LEXICON["Burn Multiple"])
                m4.metric("Debt Ratio", "1.5x", help=LEXICON["LBO Model"])
                
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("---")
        
        # ── SECTION C: THE TRADE DESK ──────────────────────────────────────────
        st.markdown("### Section C: The Trade Desk")
        cl, cr = st.columns([2, 1], gap="large")
        
        with cl:
            df_candle = generate_candlesticks(90)
            fig = go.Figure(data=[go.Candlestick(
                x=df_candle['Date'], open=df_candle['Open'],
                high=df_candle['High'], low=df_candle['Low'], close=df_candle['Close'],
                increasing_line_color='#000000', decreasing_line_color='#CCCCCC'
            )])
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=300, margin=dict(t=0, b=0, l=0, r=0),
                xaxis_rangeslider_visible=False,
                yaxis=dict(gridcolor="#E5E5E5", showline=False, zeroline=False), 
                xaxis=dict(gridcolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with cr:
            with st.container():
                st.markdown(f"#### Order Routing")
                st.metric("Marketability Score", "89 / 100", help=LEXICON["Marketability Score"])
                st.caption("Pricing indicates strong historical liquidity windows over 90-day averages.")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Execute Investment", type="primary", use_container_width=True):
                    execution_modal(deal.company_name)


elif current_page == "Secondary Market":
    st.markdown("## Institutional Trade Desk")
    st.info("The Secondary Market execution logic has directly merged into the Reading Platform. Please navigate to **Discovery**, select an asset, and scroll to **Section C: The Trade Desk** to route block trades.")

else:
    st.markdown(f"## {current_page} Module")
    st.info("Module locked to Administrative credentials or awaiting SEC data sync.")
