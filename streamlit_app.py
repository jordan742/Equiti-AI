"""
Equiti-AI v4.0 Artifact Pro — Ice Blue Discovery Terminal
Streamlit Cloud entry point: streamlit_app.py
"""

import os, time
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
APP_VERSION    = "4.0.0-ARTIFACT"
set_identity(SEC_IDENTITY)

if "view_mode" not in st.session_state:
    st.session_state.view_mode = "grid"
if "active_deal" not in st.session_state:
    st.session_state.active_deal = None
if "deals_cache" not in st.session_state:
    st.session_state.deals_cache = {}

st.set_page_config(
    page_title="Equiti-AI Artifact | Discovery Grid",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════════════════════
# ARTIFACT CSS: ICE & ELECTRIC BLUE
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

  /* Artifact Grid Cards */
  div[data-testid="stContainer"] > div {
    background: rgba(15, 23, 42, 0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(14, 165, 233, 0.2);
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.4);
    transition: all 0.2s ease-in-out;
  }
  div[data-testid="stContainer"] > div:hover {
    border: 1px solid rgba(14, 165, 233, 0.6);
    box-shadow: 0 4px 24px 0 rgba(14, 165, 233, 0.15);
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
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="terminal-hdr">
  <h1>EQUITI-AI DISCOVERY &nbsp;|&nbsp; ARTIFACT MODE</h1>
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

def metric_delta_format(val, benchmark, lower_is_better=False):
    """Calculates formatted values and strict deltas vs Sector Baseline."""
    if val is None or benchmark is None:
        return "N/A", None
    
    diff = val - benchmark
    color = "normal"
    if lower_is_better:
        if diff > 0: color = "inverse"
    else:
        if diff < 0: color = "inverse"
        
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
        margin=dict(l=0, r=0, t=0, b=0), height=50, xaxis=dict(visible=False), yaxis=dict(visible=False)
    )
    return fig

# ═══════════════════════════════════════════════════════════════════════════════
# DISCOVERY GRID (HOME)
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.view_mode == "grid":
    
    col1, col2 = st.columns([5, 1])
    col1.markdown("## Live Deal Syndicates")
    if col2.button("Run Global Deep-Audit →", use_container_width=True, type="primary"):
        st.session_state.deals_cache.clear()
        
    urls = harvester.discover_recent_deals()
    
    # Populate cache
    with st.spinner("Executing mass parallel scrape on SEC EDGAR pipelines..."):
        for url in urls:
            if url not in st.session_state.deals_cache:
                st.session_state.deals_cache[url] = harvester.harvest(url)
    
    # Render Grid Cards
    for i in range(0, len(urls), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(urls):
                url = urls[i + j]
                deal = st.session_state.deals_cache[url]
                
                with cols[j]:
                    with st.container(border=True):
                        if deal.social_buzz_velocity > 75:
                            st.markdown("<span class='badge-hot'>🔥 TRENDING DEAL</span>", unsafe_allow_html=True)
                        st.markdown(f"<span class='badge-sector'>{deal.sector}</span>", unsafe_allow_html=True)
                        
                        st.markdown(f"### {deal.company_name}")
                        
                        m1, m2 = st.columns(2)
                        m1.metric("Revenue", f"${deal.revenues/1000:,.0f}k" if deal.revenues else "Pre-Rev", help="Total topline revenue reported in the last trailing period.")
                        bm_val = deal.burn_multiple if deal.burn_multiple else "N/A"
                        m2.metric("Burn Multiple", f"{bm_val}x" if bm_val != "N/A" else "N/A", help=TOOLTIPS["burn_multiple"])
                        
                        # Mini Sparkline of simulated funding slope
                        slope = [0, deal.funding_velocity * 0.2, deal.funding_velocity * 0.5, deal.funding_velocity * 0.8, deal.funding_velocity]
                        st.plotly_chart(build_sparkline(slope), use_container_width=True, config={'displayModeBar': False})
                        
                        st.write(f"**Velocity:** ${deal.funding_velocity:,.0f} / day", help=TOOLTIPS["funding_vel"])
                        
                        if st.button(f"Deep Audit [{deal.cik}]", key=f"btn_{deal.cik}", use_container_width=True):
                            st.session_state.active_deal = deal
                            st.session_state.view_mode = "audit"
                            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# DEEP AUDIT VIEW (DRILL-DOWN)
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.view_mode == "audit":
    deal = st.session_state.active_deal
    bmk = harvester.get_sector_benchmarks(deal.sector)

    if st.button("← Back to Discovery Grid"):
        st.session_state.view_mode = "grid"
        st.session_state.active_deal = None
        st.rerun()
        
    st.markdown(f"## {deal.company_name}")
    st.markdown(f"<span class='badge-sector'>{deal.sector}</span>", unsafe_allow_html=True)
    st.markdown("---")
    
    tab_sum, tab_fin, tab_risk, tab_sec = st.tabs(["SUMMARY", "FINANCIALS & METRICS", "RISK FACTORS", "SECONDARY MARKET"])
    
    with tab_sum:
        st.markdown("### Executive Summary")
        st.write(f"A deeper look into the Form C filings for CIK *{deal.cik}*. "
                 f"The company operates in the {deal.sector} vertical with a trailing annual "
                 f"revenue of **${deal.revenues:,.0f}** and an estimated CAC of **${deal.customer_acquisition_cost}**.")
                 
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("#### Use of Funds Breakdown")
            # Create a donut chart for use of funds
            labels = list(deal.use_of_funds.keys())
            values = list(deal.use_of_funds.values())
            fig_uof = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6, marker_colors=["#0284c7", "#0ea5e9", "#7dd3fc", "#e0f2fe"])])
            fig_uof.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=30, b=10, l=10, r=10), height=300)
            st.plotly_chart(fig_uof, use_container_width=True)
        
        with col2:
            st.markdown("#### Market Positioning")
            st.metric("Social Momentum", f"{deal.social_buzz_velocity} / 100", help=TOOLTIPS["social_buzz"])
            st.metric("Deal Velocity", f"${deal.funding_velocity:,.0f}/d", help=TOOLTIPS["funding_vel"])
            
    with tab_fin:
        st.markdown("### Target vs. Benchmark Engine")
        st.caption("All arrows reflect performance strictly against the broader sector baseline.")
        
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
        
        # Base Form C Numbers
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
        
    with tab_sec:
        st.markdown("### OTC Secondary Sandbox")
        st.caption("Simulated dark pool desk. Equiti-AI does not process live monetary execution.")
        
        with st.container(border=True):
            st.markdown("### Submit Execution Query")
            s1, s2, s3 = st.columns([2, 1, 1])
            s1.selectbox("Order Routing Preference", ["Dark Pool ATS", "Public Ledger", "Direct OTC match"])
            shares = s2.number_input("Shares", value=100)
            price = s3.number_input("Limit Price", value=4.50, step=0.10)
            
            if st.button("Commit Block Trade", type="primary", use_container_width=True):
                st.toast(f"Limit order submitted: {shares} shares @ ${price}")
                st.balloons()
