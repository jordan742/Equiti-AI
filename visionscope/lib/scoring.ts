import type { Company, ScoreLabel } from "./types";

export function calculateScore(c: Company): number {
  let score = 0;

  // 1. Cash Runway (25 pts)
  const runway = c.cashOnHand / c.monthlyBurn;
  if (runway > 18) score += 25;
  else if (runway > 12) score += 20;
  else if (runway > 6)  score += 14;
  else if (runway > 3)  score += 7;
  else score += 2;

  // 2. Revenue Growth QoQ (25 pts)
  const g = c.revenueGrowthPct;
  if (g > 80)      score += 25;
  else if (g > 50) score += 20;
  else if (g > 25) score += 14;
  else if (g > 0)  score += 7;
  else score += 1;

  // 3. Debt Health (15 pts): totalDebt / totalAssets
  const dr = c.xbrl.totalAssets > 0 ? c.totalDebt / c.xbrl.totalAssets : 1;
  if (dr < 0.15)      score += 15;
  else if (dr < 0.30) score += 11;
  else if (dr < 0.50) score += 6;
  else score += 2;

  // 4. Revenue Coverage (20 pts): MRR / monthly burn
  const cov = c.monthlyBurn > 0 ? c.revenue / c.monthlyBurn : 0;
  if (cov > 1.0)      score += 20;
  else if (cov > 0.5) score += 15;
  else if (cov > 0.2) score += 9;
  else if (cov > 0.05) score += 4;
  else score += 1;

  // 5. Current Ratio (15 pts)
  const cr = c.xbrl.currentLiabilities > 0
    ? c.xbrl.currentAssets / c.xbrl.currentLiabilities
    : 99;
  if (cr > 3)      score += 15;
  else if (cr > 2) score += 12;
  else if (cr > 1) score += 8;
  else score += 2;

  return Math.min(100, Math.max(0, score));
}

export function getScoreLabel(score: number): ScoreLabel {
  if (score >= 75) return "STRONG";
  if (score >= 55) return "MODERATE";
  if (score >= 35) return "CAUTION";
  return "HIGH RISK";
}

export function getScoreColor(score: number): string {
  if (score >= 75) return "#00d4aa";
  if (score >= 55) return "#2e6cf6";
  if (score >= 35) return "#ffb830";
  return "#ff4757";
}

export function getRunwayMonths(c: Company): number {
  return c.cashOnHand / c.monthlyBurn;
}
