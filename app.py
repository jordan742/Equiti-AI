import streamlit as st
import pandas as pd
from main import get_deal_memo
from harvester import harvest
from scorer import score
from compliance import check_compliance

st.set_page_config(page_title="Equiti-AI", page_icon="📈", layout="centered")

st.title("📈 Equiti-AI — Reg CF Deal Memo Generator")
st.caption("Safe Mode Active · Data only · Not investment advice")
st.divider()

wefunder_url = st.text_input(
    "Wefunder Campaign URL",
    placeholder="https://wefunder.com/company-name",
)
offer_amount = st.number_input(
    "Current Offer Amount ($)", min_value=0, value=500_000, step=10_000
)

if st.button("Generate Memo", use_container_width=True, type="primary"):
    if not wefunder_url.strip():
        st.warning("Please enter a Wefunder URL.")
        st.stop()

    with st.spinner("Fetching SEC filings…"):
        try:
            financials = harvest(wefunder_url)
        except Exception as e:
            st.error(f"Harvest error: {e}")
            st.stop()

    with st.spinner("Running compliance check…"):
        compliance = check_compliance(financials.cik, float(offer_amount))

    with st.spinner("Scoring…"):
        result = score(financials)

    compliance_label = "PASS" if compliance.compliant else "FAIL"
    key_risk = result.investment_thesis.split(". ")[-1].strip().rstrip(".")

    # ── Deal header ───────────────────────────────────────────────────────
    st.divider()
    st.subheader(financials.company_name or f"CIK {financials.cik}")

    # ── Compliance banner ─────────────────────────────────────────────────
    if compliance.compliant:
        st.success(f"✅ Compliance: PASS — ${compliance.combined_total:,.0f} of $5,000,000 Reg CF cap used")
    else:
        st.warning(
            f"⚠️ Compliance: FAIL — Combined raise ${compliance.combined_total:,.0f} "
            f"exceeds the $5,000,000 Reg CF annual cap."
        )

    st.divider()

    # ── Score metrics ─────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    col1.metric("Health Score", f"{result.score:.1f} / 10")
    col2.metric(
        "Runway",
        f"{result.runway_months:.1f} mo" if result.runway_months else "N/A",
        delta="⚠ Low" if result.runway_months and result.runway_months < 6 else None,
        delta_color="inverse",
    )
    col3.metric(
        "Revenue Growth",
        f"{result.revenue_growth_pct:.1f}%" if result.revenue_growth_pct is not None else "N/A",
    )

    # ── Balance sheet table ───────────────────────────────────────────────
    st.divider()
    st.subheader("Balance Sheet (Form C)")

    balance_sheet = pd.DataFrame(
        {
            "Item": ["Cash", "Revenues", "Net Income", "Short-Term Debt", "Debt Ratio"],
            "Value": [
                f"${financials.cash:,.0f}" if financials.cash is not None else "N/A",
                f"${financials.revenues:,.0f}" if financials.revenues is not None else "N/A",
                f"${financials.net_income:,.0f}" if financials.net_income is not None else "N/A",
                f"${financials.short_term_debt:,.0f}" if financials.short_term_debt is not None else "N/A",
                f"{result.debt_ratio:.4f}" if result.debt_ratio is not None else "N/A",
            ],
        }
    )
    st.table(balance_sheet)

    # ── Deal memo ─────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Deal Memo")
    st.markdown(
        f"""
| Field | Detail |
|---|---|
| **Deal Name** | {financials.company_name or financials.cik} |
| **Health Score** | {result.score:.1f} / 10 |
| **Compliance Status** | {compliance_label} |
| **Key Risk** | {key_risk}. |
"""
    )

    st.info(f"**Investment Thesis:** {result.investment_thesis}")

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

    st.divider()
    st.caption("Equiti-AI · Safe Mode · Data only · Not investment advice")
