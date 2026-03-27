import streamlit as st
from harvester import harvest, StartupFinancials
from scorer import score
from compliance import check_compliance

st.set_page_config(page_title="Equiti-AI", page_icon="📈", layout="centered")

st.title("📈 Equiti-AI — Reg CF Deal Scanner")
st.caption("Data-only · Safe Mode Active · Not investment advice")

st.divider()

with st.form("scan_form"):
    campaign_url = st.text_input(
        "Wefunder Campaign URL",
        placeholder="https://wefunder.com/company-name",
    )
    col1, col2 = st.columns(2)
    current_offer = col1.number_input(
        "Current Offer Amount ($)", min_value=0, value=500_000, step=10_000
    )
    prior_revenues = col2.number_input(
        "Prior Year Revenue ($) — optional", min_value=0, value=0, step=10_000
    )
    submitted = st.form_submit_button("Run Scan", use_container_width=True)

if submitted and campaign_url:
    with st.spinner("Fetching SEC filings…"):
        try:
            financials: StartupFinancials = harvest(campaign_url)
        except Exception as e:
            st.error(f"Harvest failed: {e}")
            st.stop()

    with st.spinner("Scoring…"):
        result = score(financials, prior_revenues=prior_revenues or None)

    with st.spinner("Checking Reg CF compliance…"):
        compliance = check_compliance(financials.cik, current_offer_amount=float(current_offer))

    # ── Company header ────────────────────────────────────────────────────
    st.subheader(financials.company_name or f"CIK {financials.cik}")

    # ── Compliance banner ─────────────────────────────────────────────────
    if compliance.compliant:
        st.success(f"✅ COMPLIANT — Combined 12-month raise: **${compliance.combined_total:,.0f}** / $5,000,000 cap")
    else:
        st.error(f"🚫 NON-COMPLIANT — Combined raise **${compliance.combined_total:,.0f}** exceeds $5M Reg CF cap")

    st.divider()

    # ── Score ─────────────────────────────────────────────────────────────
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Alpha Score", f"{result.score:.1f} / 10")
    col_b.metric("Runway", f"{result.runway_months:.1f} mo" if result.runway_months else "N/A")
    col_c.metric("Debt Ratio", f"{result.debt_ratio:.2f}" if result.debt_ratio else "N/A")

    if result.revenue_growth_pct is not None:
        st.metric("Revenue Growth (YoY)", f"{result.revenue_growth_pct:.1f}%")

    st.divider()

    # ── Financials ────────────────────────────────────────────────────────
    st.subheader("SEC Financials (Form C)")
    fcol1, fcol2, fcol3, fcol4 = st.columns(4)
    fcol1.metric("Cash", f"${financials.cash:,.0f}" if financials.cash else "N/A")
    fcol2.metric("Revenue", f"${financials.revenues:,.0f}" if financials.revenues else "N/A")
    fcol3.metric("Net Income", f"${financials.net_income:,.0f}" if financials.net_income else "N/A")
    fcol4.metric("ST Debt", f"${financials.short_term_debt:,.0f}" if financials.short_term_debt else "N/A")

    st.divider()

    # ── Investment thesis ─────────────────────────────────────────────────
    st.subheader("Investment Thesis")
    st.info(result.investment_thesis)

    # ── Compliance detail ─────────────────────────────────────────────────
    with st.expander("Compliance Detail"):
        st.json({
            "cik": compliance.cik,
            "status": compliance.status,
            "filings_found_12m": compliance.filing_count,
            "total_raised_12m": compliance.total_raised_12m,
            "current_offer": compliance.current_offer_amount,
            "combined_total": compliance.combined_total,
            "reg_cf_cap": 5_000_000,
        })

elif submitted:
    st.warning("Please enter a Wefunder campaign URL.")
