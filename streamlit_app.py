"""
Equiti-AI v5.0 Pro Ecosystem — Multi-Company Marketplace
Streamlit Cloud entry point: streamlit_app.py
"""

import os, time, hashlib
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
SEC_IDENTITY   = os.getenv("SEC_IDENTITY", "Jordan equiti-ai-research@example.com")
APP_VERSION    = "5.0.0-PRO-ECOSYSTEM"
PORTFOLIO_FILE = "portfolio.csv"
set_identity(SEC_IDENTITY)

if "view_mode" not in st.session_state:
    st.session_state.view_mode = "grid"
if "active_deal" not in st.session_state:
    st.session_state.active_deal = None
if "deals_cache" not in st.session_state:
    st.session_state.deals_cache = {}

if not os.path.exists(PORTFOLIO_FILE):
    pd.DataFrame(columns=["CIK", "Company", "Investment", "Runway"]).to_csv(PORTFOLIO_FILE, index=False)

st.set_page_config(
    page_title="Equiti-AI Pro | Ecosystem Marketplace",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════════
# ARTIFACT CSS: GLASSMORPHISM & ICE BLUE
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Unbounded:wght@300;500;700&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
  
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  h1, h2, h3 { font-family: 'Unbounded', sans-serif; letter-spacing: -0.5px; }

  /* Ice Blue Base Theme */
  div.stApp { background-color: #020617; }
  
  .terminal-hdr {
    background: linear-gradient(135deg, #020617 0%, #082f49 100%);
    border-bottom: 1px solid #0ea5e9;
    padding: 1.5rem 2rem; margin-bottom: 2rem;
  }
  .terminal-hdr h1 { color: #f8fafc; margin:0; font-size:1.8rem; letter-spacing:1px; font-weight: 700; text-transform: uppercase; }
  .terminal-hdr p  { color: #0ea5e9; margin:0.3rem 0 0; font-size:0.85rem; letter-spacing:1px; }

  /* Glassmorphism Marketplace Grid Cards */
  div[data-testid="stContainer"] > div {
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(14, 165, 233, 0.25);
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
    transition: all 0.3s ease-in-out;
  }
  div[data-testid="stContainer"] > div:hover {
    border: 1px solid rgba(14, 165, 233, 0.8);
    box-shadow: 0 8px 32px 0 rgba(14, 165, 233, 0.25);
    transform: translateY(-2px);
  }
  
  /* Metric Styling */
  div[data-testid="stMetric"] label { 
      color: #7dd3fc !important; 
      font-size: 0.8rem; 
      font-weight: 600; 
      text-transform: uppercase; 
  }
  div[data-testid="stMetric"] div { 
      color: #f1f5f9 !important; 
      font-size: 2rem; 
      font-weight: 300; 
  }

  .badge-hot {
      display: inline-block; padding: 0.25rem 0.75rem; border-radius: 9999px;
      background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; color: #f87171;
      font-weight: 700; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px;
      margin-bottom: 0.5rem;
  }
  .badge-sector {
      display: inline-block; padding: 0.2rem 0.6rem; border-radius: 4px;
      background: rgba(14, 165, 233, 0.1); border: 1px solid #0ea5e9; color: #38bdf8;
      font-weight: 500; font-size: 0.7rem; text-transform: uppercase;
      margin-bottom: 0.5rem;
  }
  
  /* Sidebar Radio override for Premium Feel */
  div[role="radiogroup"] label { font-family: 'Unbounded', sans-serif; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="terminal-hdr">
  <h1>EQUITI-AI PRO &nbsp;|&nbsp; INSTITUTIONAL MARKETPLACE</h1>
  <p>v{APP_VERSION} &nbsp;&middot;&nbsp; HIGH-FIDELITY DEEP AUDIT &nbsp;&middot;&nbsp; SEC EDGAR INTEGRATION</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PLOTLY & UI HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
TOOLTIPS = {
    "burn_multiple": "Burn Multiple: How efficiently the startup uses cash to generate revenue. $1 burned for $1 ARR is a 1.0x (Optimal target). Over 2.5x is highly inefficient.",
    "operating_margin": "Operating Margin: The percentage of revenue left after paying variable costs. Negative margins map to heavy growth stages.",
    "cac": "Estimated Customer Acquisition Cost: Roughly what they spend on sales/marketing to acquire one user.",
    "ltv": "Estimated Lifetime Value: How much total revenue they extract from one user over time.",
    "yoy_growth": "Year-over-Year Revenue Growth: Comparing current reported revenue to the trailing prior period.",
    "social_buzz": "Social Velocity: An aggregated momentum metric out of 100 capturing syndicate inflows and online sentiment.",
    "funding_vel": "Funding Velocity: The estimated dollar amount pledged to the round per trailing 24 hours.",
}

def get_logo_emoji(name: str) -> str:
    """Mock logo allocation for the grid."""
    emojis = ["🚀", "⚡", "🧬", "🤖", "☁️", "📈", "🛡️", "🌐", "🧠"]
    idx = int(hashlib.sha256(name.encode('utf-8')).hexdigest(), 16) % len(emojis)
    return emojis[idx]

def generate_health_score(deal) -> int:
    """Generates 0-100 score mimicking result.score."""
    base = 5.0
    if deal.cash is not None and deal.net_income not in (None, 0):
        runway = deal.cash / (abs(deal.net_income) / 12)
        if runway < 6: base -= 3
    if deal.yoy_revenue_growth and deal.yoy_revenue_growth > 20:
        base += 2
    val = max(1.0, min(10.0, base))
    return int(val * 10)

def metric_delta_format(val, benchmark, lower_is_better=False):
    """Calculates formatted values and strict deltas vs Sector Baseline."""
    if val is None or benchmark is None:
        return "N/A", None, "normal"
    
    diff = val - benchmark
    color = "normal"
    if lower_is_better:
        color = "inverse" if diff > 0 else "normal"
    else:
        color = "inverse" if diff < 0 else "normal"
        
    delta_str = f"{abs(diff):.1f} vs Sector"
    if diff > 0: delta_str = "↑ " + delta_str
    elif diff < 0: delta_str = "↓ " + delta_str
    
    return val, delta_str, color

def build_sparkline(data: list) -> go.Figure:
    fig = go.Figure(go.Scatter(
        y=data, mode="lines", 
        fill="tozeroy", fillcolor="rgba(14, 165, 233, 0.15)",
        line=dict(color="#0ea5e9", width=2.5, shape="spline"),
        hoverinfo="skip"
    ))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0), height=60, xaxis=dict(visible=False), yaxis=dict(visible=False)
    )
    return fig

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR ROUTER (AGENT 2)
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🧭 TERMINAL OS")
    current_page = st.radio(
        "Application Layer", 
        ["Discovery Marketplace", "My Portfolio", "Secondary Exchange"], 
        label_visibility="collapsed"
    )
    st.divider()
    
    with st.expander("Terminal Settings & State"):
        st.markdown("Mock controls for live queries.")
        demo_mode = st.toggle("Demo Mode Database", value=True)
        clear_cache = st.button("Purge Deal Cache", use_container_width=True)
        if clear_cache:
            st.session_state.deals_cache.clear()
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1: DISCOVERY MARKETPLACE
# ═══════════════════════════════════════════════════════════════════════════════
if current_page == "Discovery Marketplace":
    
    # GRID MODE
    if st.session_state.view_mode == "grid":
        st.markdown("## Live Deal Syndicates")
            
        urls = harvester.discover_recent_deals()
        
        # Populate cache
        with st.spinner("Executing mass parallel scrape on SEC EDGAR pipelines..."):
            for url in urls:
                if url not in st.session_state.deals_cache:
                    st.session_state.deals_cache[url] = harvester.harvest(url)
        
        # Render Multi-Company Artifact Grid
        for i in range(0, len(urls), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(urls):
                    url = urls[i + j]
                    deal = st.session_state.deals_cache[url]
                    health_100 = generate_health_score(deal)
                    
                    with cols[j]:
                        with st.container(border=True):
                            if deal.social_buzz_velocity > 75:
                                st.markdown("<span class='badge-hot'>🔥 TRENDING</span>", unsafe_allow_html=True)
                            
                            # Logo, Title, and Health
                            h1, h2 = st.columns([3, 1])
                            h1.markdown(f"### {get_logo_emoji(deal.company_name)} {deal.company_name}")
                            h2.markdown(f"<h3 style='color:#00f2fe; text-align:right;'>{health_100}</h3>", unsafe_allow_html=True)
                            
                            st.markdown(f"<span class='badge-sector'>{deal.sector}</span>", unsafe_allow_html=True)
                            
                            m1, m2 = st.columns(2)
                            m1.metric("Revenue", f"${deal.revenues/1000:,.0f}k" if deal.revenues else "Pre-Rev", help="Total topline revenue reported.")
                            bm_val = deal.burn_multiple if deal.burn_multiple else "N/A"
                            m2.metric("Burn Multiple", f"{bm_val}x" if bm_val != "N/A" else "N/A")
                            
                            # 'Funding Velocity' Sparkline
                            slope = [0, deal.funding_velocity * 0.2, deal.funding_velocity * 0.5, deal.funding_velocity * 0.8, deal.funding_velocity]
                            st.plotly_chart(build_sparkline(slope), use_container_width=True, config={'displayModeBar': False})
                            
                            if st.button(f"Deep Audit [{deal.cik}]", key=f"btn_{deal.cik}", use_container_width=True):
                                st.session_state.active_deal = deal
                                st.session_state.view_mode = "audit"
                                st.rerun()

    # DEEP AUDIT DRILL-DOWN MODE
    elif st.session_state.view_mode == "audit":
        deal = st.session_state.active_deal
        bmk = harvester.get_sector_benchmarks(deal.sector)

        if st.button("← Back to Marketplace Grid"):
            st.session_state.view_mode = "grid"
            st.session_state.active_deal = None
            st.rerun()
            
        st.markdown(f"## {get_logo_emoji(deal.company_name)} {deal.company_name}")
        st.markdown(f"<span class='badge-sector'>{deal.sector}</span>", unsafe_allow_html=True)
        st.markdown("---")
        
        # AGENT 3: Retail Translator Summary
        runway_mo = "Unknown"
        if deal.cash is not None and deal.net_income is not None and deal.net_income < 0:
            runway_mo = f"{deal.cash / (abs(deal.net_income) / 12):.1f}"
            
        st.info(f"**Retail Analyst Plain-English Summary:** \n\n"
                f"{deal.company_name} is operating in the {deal.sector} space. "
                f"Currently, they show an estimated burn multiple of {deal.burn_multiple}x (meaning they burn "
                f"${deal.burn_multiple} to acquire $1 in ARR). Their operating margin is "
                f"{deal.operating_margin}%, which indicates how deeply they are bleeding cash against their "
                f"revenue. They rely on an estimated CAC of ${deal.customer_acquisition_cost}. "
                f"Current calculated runway: {runway_mo} months.")
        
        tab_sum, tab_fin, tab_risk = st.tabs(["SUMMARY & LOG", "DEEP FINANCIALS", "RISK FACTORS"])
        
        with tab_sum:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("#### Use of Funds Breakdown")
                labels = list(deal.use_of_funds.keys())
                values = list(deal.use_of_funds.values())
                fig_uof = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6, marker_colors=["#0284c7", "#0ea5e9", "#7dd3fc", "#e0f2fe"])])
                fig_uof.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=30, b=10, l=10, r=10), height=300)
                st.plotly_chart(fig_uof, use_container_width=True)
            
            with col2:
                st.markdown("#### Market Positioning")
                st.metric("Social Momentum", f"{deal.social_buzz_velocity} / 100", help=TOOLTIPS["social_buzz"])
                st.metric("Deal Velocity", f"${deal.funding_velocity:,.0f}/d", help=TOOLTIPS["funding_vel"])
                
                st.markdown("<br>", unsafe_allow_html=True)
                amount = st.number_input("Log Investment Size", value=1000, step=500)
                if st.button("LOG TO PORTFOLIO", use_container_width=True, type="primary"):
                    new_row = {"CIK": deal.cik, "Company": deal.company_name, "Investment": amount, "Runway": runway_mo}
                    pd.DataFrame([new_row]).to_csv(PORTFOLIO_FILE, mode="a", header=False, index=False)
                    st.toast("Investment mapped to Portfolio.")
                
        with tab_fin:
            st.markdown("### Target vs. Benchmark Engine")
            st.caption("All Metric Deltas specifically reflect performance strictly against the broader sector baseline.")
            
            m1, m2, m3 = st.columns(3)
            
            yoy_val, yoy_del, yoy_col = metric_delta_format(deal.yoy_revenue_growth, bmk["yoy_growth"])
            with m1:
                with st.container(border=True):
                    st.metric("YoY Rev. Growth", f"{yoy_val:.1f}%" if yoy_val != "N/A" else "N/A", delta=yoy_del, delta_color=yoy_col, help=TOOLTIPS["yoy_growth"])
            
            bm_val, bm_del, bm_col = metric_delta_format(deal.burn_multiple, bmk["burn_multiple"], lower_is_better=True)
            with m2:    
                with st.container(border=True):
                    st.metric("Burn Multiple", f"{bm_val:.2f}x" if bm_val != "N/A" else "N/A", delta=bm_del, delta_color=bm_col, help=TOOLTIPS["burn_multiple"])
                    
            om_val, om_del, om_col = metric_delta_format(deal.operating_margin, bmk["operating_margin"])
            with m3:
                with st.container(border=True):
                    st.metric("Operating Margin", f"{om_val:.1f}%" if om_val != "N/A" else "N/A", delta=om_del, delta_color=om_col, help=TOOLTIPS["operating_margin"])
            
            st.markdown("#### Validated Form C Data")
            fc1, fc2, fc3, fc4 = st.columns(4)
            with st.container(border=True):
                rcol1, rcol2, rcol3, rcol4 = st.columns(4)
                rcol1.metric("Cash equivalent", f"${deal.cash/1000:,.0f}k" if deal.cash else "N/A")
                rcol2.metric("S.T. Debt", f"${deal.short_term_debt/1000:,.0f}k" if deal.short_term_debt else "N/A")
                rcol3.metric("Est. CAC", f"${deal.customer_acquisition_cost}", help=TOOLTIPS["cac"])
                rcol4.metric("Est. LTV", f"${deal.lifetime_value}", help=TOOLTIPS["ltv"])

        with tab_risk:
            st.markdown("### Evaluated Risk Flags")
            st.error("**Regulatory Risk (General):** Startups are illiquid. Loss of capital is possible.")
            if deal.burn_multiple and deal.burn_multiple > 2.0:
                st.warning("**Efficiency Risk:** Elevated burn multiple means high spend for low proportional growth.")
            if deal.operating_margin and deal.operating_margin < -50.0:
                st.warning("**Profitability Runway:** Extreme negative operating margins require imminent capital raises.")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2: MY PORTFOLIO
# ═══════════════════════════════════════════════════════════════════════════════
elif current_page == "My Portfolio":
    st.markdown("## 📁 Portfolio Global Exposure")
    
    port_df = pd.read_csv(PORTFOLIO_FILE)
    if not port_df.empty:
        total_exp = port_df['Investment'].sum()
        runways = pd.to_numeric(port_df['Runway'], errors='coerce').dropna()
        avg_runway = runways.mean() if not runways.empty else 0.0
        
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.metric("Total Institutional Exposure", f"${total_exp:,.0f}")
        with c2:
            with st.container(border=True):
                st.metric("Weighted Portfolio Runway", f"{avg_runway:.1f} mo")
                
        st.dataframe(port_df, use_container_width=True, hide_index=True)
        if st.button("Wipe Institutional Record", type="primary"):
            pd.DataFrame(columns=["CIK", "Company", "Investment", "Runway"]).to_csv(PORTFOLIO_FILE, index=False)
            st.rerun()
    else:
        st.info("No investments tracked yet. Return to the Discovery Marketplace and log a deal via Deep Audit.")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3: SECONDARY EXCHANGE
# ═══════════════════════════════════════════════════════════════════════════════
elif current_page == "Secondary Exchange":
    st.markdown("## 🔄 Secondary Dark Pool (OTC Sandbox)")
    st.caption("Trade illiquid startup equity previously logged in your portfolio.")
    
    mkt_score = 42 # Abstracted mock value for standalone page
    
    c1, c2 = st.columns([1, 2], gap="large")
    with c1:
        with st.container(border=True):
            st.markdown("#### Global Marketability")
            st.markdown(f"<h1 style='color:#0ea5e9; text-align:center; font-size:4.5rem; margin: 1rem 0;'>{mkt_score}</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center; color:#ef4444; font-weight:bold;'>Low Liquidity Demand</p>", unsafe_allow_html=True)
    with c2:
        with st.container(border=True):
            st.markdown("#### Submit Private Execution")
            
            port_df = pd.read_csv(PORTFOLIO_FILE)
            assets = port_df['Company'].tolist() if not port_df.empty else ["No Assets Held"]
            
            tr1, tr2 = st.columns(2)
            asset = tr1.selectbox("Portfolio Asset", assets)
            tr_type = tr2.selectbox("Order Strategy", ["Ask / Sell Limit", "Bid / Buy Limit"])
            
            price = st.number_input("Limit Price per Share ($)", value=10.00, step=0.50)
            shares = st.slider("Share Volume", 100, 10000, 500)
            
            if st.button("Submit Cryptographic Block Trade", use_container_width=True, type="primary"):
                if asset == "No Assets Held":
                    st.error("You must hold assets to submit an OTC request.")
                else:
                    st.success(f"**{tr_type}** for {shares} shares of {asset} at ${price:,.2f} per share executed on the shadow ledger.")
