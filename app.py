import streamlit as st
import pandas as pd
from harvester import StartupFinancials
from scorer import score, ScoreResult
from compliance import check_compliance, ComplianceResult

st.set_page_config(
    page_title="Equiti-AI — Reg CF Scanner",
    page_icon="📈",
    layout="wide",
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    .metric-label { font-size: 0.85rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📈 Equiti-AI — Reg CF Deal Scanner")
st.caption("Safe Mode Active · Data only · Not investment advice")
st.divider()

# ── Demo fixture ──────────────────────────────────────────────────────────────
DEMO_FINANCIALS = StartupFinancials(
    cik="0001234567",
    company_name="Acme AI (Demo)",
    cash=850_000.0,
    net_income=-1_200_000.0,
    revenues=2_400_000.0,
    short_term_debt=300_000.0,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    demo_mode = st.toggle("Demo Mode (no URL needed)", value=True)
    st.caption("Uses sample data so you can explore the UI instantly.")
    st.divider()
    offer_amount = st.number_input("Current Offer Amount ($)", min_value=0, max_value=5_000_000, value=500_000, step=25_000)
    prior_revenues = st.number_input("Prior Year Revenue ($) — optional", min_value=0, value=0, step=10_000)
    st.divider()
    st.caption("Equiti-AI v0.1")

# ── URL input + button ────────────────────────────────────────────────────────
col_input, col_btn = st.columns([4, 1])
wefunder_url = col_input.text_input(
    "url",
    placeholder="https://wefunder.com/company-name",
    disabled=demo_mode,
    label_visibility="collapsed",
)
generate = col_btn.button("Generate Memo", type="primary", use_container_width=True)

# ── Gate: only run pipeline when button clicked ───────────────────────────────
if not generate:
    st.info("👆 Click **Generate Memo** — Demo Mode is ON so no URL is needed to start.")
else:
    # ── Fetch data ────────────────────────────────────────────────────────
    if demo_mode:
        financials = DEMO_FINANCIALS
    else:
        if not wefunder_url.strip():
            st.warning("Please enter a Wefunder campaign URL.")
            st.stop()
        with st.spinner("Fetching SEC Form C filing…"):
            try:
                from harvester import harvest
                financials = harvest(wefunder_url.strip())
            except Exception as e:
                st.error(f"**Harvest failed:** {e}")
                st.stop()

    with st.spinner("Running compliance check…"):
        try:
            compliance: ComplianceResult = check_compliance(financials.cik, float(offer_amount))
        except Exception as e:
            st.error(f"**Compliance check failed:** {e}")
            st.stop()

    with st.spinner("Scoring…"):
        result: ScoreResult = score(financials, prior_revenues=prior_revenues or None)

    # ── Layout ────────────────────────────────────────────────────────────
    left, right = st.columns([3, 2], gap="large")

    with left:
        st.subheader(financials.company_name or f"CIK {financials.cik}")
        if demo_mode:
            st.caption("⚡ Demo data — toggle off Demo Mode to scan a real deal.")

        # Compliance
        used_pct = compliance.combined_total / 5_000_000 * 100
        if compliance.compliant:
            st.success(f"✅ **Reg CF Compliance: PASS** — ${compliance.combined_total:,.0f} of $5,000,000 cap used ({used_pct:.1f}%)")
        else:
            st.warning(f"⚠️ **Reg CF Compliance: FAIL** — ${compliance.combined_total:,.0f} exceeds the $5,000,000 annual cap.")
        st.progress(min(used_pct / 100, 1.0))

        st.divider()

        # Score metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Health Score", f"{result.score:.1f} / 10")
        m2.metric(
            "Cash Runway",
            f"{result.runway_months:.1f} mo" if result.runway_months else "N/A",
            delta="⚠ Low" if result.runway_months and result.runway_months < 6 else None,
            delta_color="inverse",
        )
        m3.metric(
            "YoY Revenue Growth",
            f"{result.revenue_growth_pct:.1f}%" if result.revenue_growth_pct is not None else "N/A",
        )

        st.divider()
        st.subheader("Investment Thesis")
        st.info(result.investment_thesis)

    with right:
        # Balance sheet
        st.subheader("Balance Sheet (Form C)")

        def fmt(val):
            return f"${val:,.0f}" if val is not None else "N/A"

        balance_df = pd.DataFrame({
            "Metric": ["Cash", "Revenues", "Net Income", "Short-Term Debt", "Debt Ratio"],
            "Value": [
                fmt(financials.cash),
                fmt(financials.revenues),
                fmt(financials.net_income),
                fmt(financials.short_term_debt),
                f"{result.debt_ratio:.4f}" if result.debt_ratio is not None else "N/A",
            ],
        }).set_index("Metric")
        st.table(balance_df)

        # Deal memo card
        st.subheader("Deal Memo")
        compliance_label = "PASS ✅" if compliance.compliant else "FAIL ⚠️"
        key_risk = result.investment_thesis.split(". ")[-1].strip().rstrip(".")
        st.markdown(f"""
| Field | Detail |
|:---|:---|
| **Deal Name** | {financials.company_name or financials.cik} |
| **Health Score** | {result.score:.1f} / 10 |
| **Compliance** | {compliance_label} |
| **Key Risk** | {key_risk}. |
""")

        with st.expander("Compliance Detail"):
            st.json({
                "cik": compliance.cik,
                "status": compliance.status,
                "filings_found_12m": compliance.filing_count,
                "total_raised_12m": f"${compliance.total_raised_12m:,.0f}",
                "current_offer": f"${compliance.current_offer_amount:,.0f}",
                "combined_total": f"${compliance.combined_total:,.0f}",
                "reg_cf_cap": "$5,000,000",
            })

    st.divider()
    st.caption("Equiti-AI · Safe Mode · Data only · Not investment advice")
