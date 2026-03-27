"""
Tests for the DCF/NPV financial model.
No API keys or network access required.
"""

import pytest
from scanner.models.dcf_model import DCFInputs, run_dcf, npv


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def base_inputs():
    return DCFInputs(
        company_name="TestCo",
        current_arr=1_000_000,
        revenue_growth_rate_y1=1.50,
        revenue_growth_rate_y2=1.00,
        revenue_growth_rate_y3=0.70,
        revenue_growth_rate_y4=0.40,
        revenue_growth_rate_y5=0.25,
        current_offering_valuation=10_000_000,
        wacc=0.35,
    )


# ── Revenue Projection Tests ──────────────────────────────────────────────────

def test_revenue_projections_length(base_inputs):
    result = run_dcf(base_inputs)
    assert len(result.projected_revenues) == 5


def test_revenue_projections_are_increasing(base_inputs):
    result = run_dcf(base_inputs)
    for i in range(1, 5):
        assert result.projected_revenues[i] > result.projected_revenues[i - 1], (
            f"Revenue in year {i+1} should exceed year {i}"
        )


def test_revenue_y1_correct(base_inputs):
    result = run_dcf(base_inputs)
    expected_y1 = 1_000_000 * (1 + 1.50)
    assert abs(result.projected_revenues[0] - expected_y1) < 1.0


def test_revenue_y5_correct(base_inputs):
    result = run_dcf(base_inputs)
    rev = 1_000_000
    for g in [1.50, 1.00, 0.70, 0.40, 0.25]:
        rev *= (1 + g)
    assert abs(result.projected_revenues[4] - rev) < 1.0


# ── Terminal Value Tests ──────────────────────────────────────────────────────

def test_terminal_value_positive(base_inputs):
    result = run_dcf(base_inputs)
    assert result.terminal_value > 0


def test_terminal_value_dominates_ev(base_inputs):
    """Terminal value should be the dominant component of EV for high-growth startups."""
    result = run_dcf(base_inputs)
    # TV discounted back 5 years
    pv_tv = result.terminal_value / (1 + base_inputs.wacc) ** 5
    assert pv_tv > 0


# ── Enterprise Value Tests ────────────────────────────────────────────────────

def test_enterprise_value_positive(base_inputs):
    result = run_dcf(base_inputs)
    assert result.enterprise_value > 0


def test_enterprise_value_exceeds_current_arr(base_inputs):
    result = run_dcf(base_inputs)
    assert result.enterprise_value > base_inputs.current_arr


# ── Implied Upside Tests ──────────────────────────────────────────────────────

def test_implied_upside_calculated_when_valuation_provided(base_inputs):
    result = run_dcf(base_inputs)
    assert result.implied_upside_x is not None


def test_implied_upside_is_positive(base_inputs):
    result = run_dcf(base_inputs)
    assert result.implied_upside_x > 0


def test_implied_upside_none_when_no_valuation():
    inputs = DCFInputs(
        company_name="NoValCo",
        current_arr=500_000,
        revenue_growth_rate_y1=1.00,
        revenue_growth_rate_y2=0.80,
        revenue_growth_rate_y3=0.60,
        revenue_growth_rate_y4=0.40,
        revenue_growth_rate_y5=0.20,
        current_offering_valuation=None,
    )
    result = run_dcf(inputs)
    assert result.implied_upside_x is None


# ── DCF Score Tests ───────────────────────────────────────────────────────────

def test_dcf_score_between_0_and_100(base_inputs):
    result = run_dcf(base_inputs)
    assert 0 <= result.dcf_score <= 100


def test_dcf_score_neutral_without_valuation():
    inputs = DCFInputs(
        company_name="NeutralCo",
        current_arr=500_000,
        revenue_growth_rate_y1=1.00,
        revenue_growth_rate_y2=0.80,
        revenue_growth_rate_y3=0.60,
        revenue_growth_rate_y4=0.40,
        revenue_growth_rate_y5=0.20,
        current_offering_valuation=None,
    )
    result = run_dcf(inputs)
    assert result.dcf_score == 50.0


def test_higher_growth_yields_higher_dcf_score():
    # Use a low offering valuation ($500K) so both scenarios produce
    # implied_upside_x > 1, allowing the log-scale scorer to differentiate them.
    low = DCFInputs(
        company_name="LowGrowth",
        current_arr=1_000_000,
        revenue_growth_rate_y1=0.20,
        revenue_growth_rate_y2=0.20,
        revenue_growth_rate_y3=0.15,
        revenue_growth_rate_y4=0.10,
        revenue_growth_rate_y5=0.08,
        current_offering_valuation=500_000,
    )
    high = DCFInputs(
        company_name="HighGrowth",
        current_arr=1_000_000,
        revenue_growth_rate_y1=2.00,
        revenue_growth_rate_y2=1.50,
        revenue_growth_rate_y3=1.00,
        revenue_growth_rate_y4=0.70,
        revenue_growth_rate_y5=0.40,
        current_offering_valuation=500_000,
    )
    assert run_dcf(high).dcf_score > run_dcf(low).dcf_score


# ── NPV Utility Tests ─────────────────────────────────────────────────────────

def test_npv_single_cash_flow():
    result = npv([110.0], 0.10)
    assert abs(result - 100.0) < 0.01


def test_npv_zero_flows():
    assert npv([0.0, 0.0, 0.0], 0.20) == 0.0


def test_npv_multiple_flows():
    # PV of $100 each year for 3 years at 10%
    result = npv([100, 100, 100], 0.10)
    expected = 100 / 1.1 + 100 / 1.21 + 100 / 1.331
    assert abs(result - expected) < 0.01


def test_npv_high_discount_reduces_value():
    low_discount = npv([1000, 1000, 1000], 0.05)
    high_discount = npv([1000, 1000, 1000], 0.50)
    assert low_discount > high_discount


# ── Disclaimer Tests ──────────────────────────────────────────────────────────

def test_result_includes_disclaimer(base_inputs):
    result = run_dcf(base_inputs)
    assert "Safe Mode" in result.assumptions_note
    assert "NOT investment advice" in result.assumptions_note
