from pydantic import BaseModel
from typing import Optional
from harvester import StartupFinancials


class ScoreResult(BaseModel):
    company_name: Optional[str]
    score: float
    runway_months: Optional[float]
    debt_ratio: Optional[float]
    revenue_growth_pct: Optional[float]
    investment_thesis: str


def score(financials: StartupFinancials, prior_revenues: Optional[float] = None) -> ScoreResult:
    base = 5.0

    # Runway: Cash / (|NetIncome| / 12)
    runway = None
    if financials.cash is not None and financials.net_income not in (None, 0):
        runway = financials.cash / (abs(financials.net_income) / 12)
        if runway < 6:
            base -= 3

    # Debt ratio: ShortTermDebt / Revenues
    debt_ratio = None
    if financials.short_term_debt is not None and financials.revenues not in (None, 0):
        debt_ratio = financials.short_term_debt / financials.revenues

    # Revenue growth bonus
    growth_pct = None
    if prior_revenues and financials.revenues is not None and prior_revenues > 0:
        growth_pct = (financials.revenues - prior_revenues) / prior_revenues * 100
        if growth_pct > 20:
            base += 2

    score_val = max(1.0, min(10.0, base))

    # Investment thesis
    runway_str = f"{runway:.1f} months" if runway is not None else "unknown"
    dr_str = f"{debt_ratio:.2f}" if debt_ratio is not None else "unknown"
    growth_str = f"{growth_pct:.1f}%" if growth_pct is not None else "unavailable"

    thesis = (
        f"{financials.company_name or 'This company'} scores {score_val:.1f}/10 based on "
        f"a cash runway of {runway_str} and a debt-to-revenue ratio of {dr_str}. "
        f"Revenue growth versus the prior period is {growth_str}, "
        f"{'exceeding' if growth_pct and growth_pct > 20 else 'not exceeding'} the 20% growth threshold. "
        f"{'Immediate runway risk warrants caution' if runway is not None and runway < 6 else 'Runway is adequate for near-term operations'}, "
        f"and the overall financial profile {'supports' if score_val >= 6 else 'does not yet support'} further due diligence."
    )

    return ScoreResult(
        company_name=financials.company_name,
        score=score_val,
        runway_months=round(runway, 2) if runway is not None else None,
        debt_ratio=round(debt_ratio, 4) if debt_ratio is not None else None,
        revenue_growth_pct=round(growth_pct, 2) if growth_pct is not None else None,
        investment_thesis=thesis,
    )
