import type { Company } from "@/lib/types";
import { fmtCurrency } from "@/lib/formatting";
import SectionBox from "../ui/SectionBox";
import StatCard from "../ui/StatCard";

export default function KeyRatios({ company: c }: { company: Company }) {
  const currentRatio = c.xbrl.currentAssets / (c.xbrl.currentLiabilities || 1);
  const debtRatio = (c.totalDebt / (c.xbrl.totalAssets || 1)) * 100;
  const grossMargin = ((c.xbrl.revenue - c.xbrl.cogs) / (c.xbrl.revenue || 1)) * 100;
  const burnMultiple = c.monthlyBurn / (c.revenue || 1);
  const coverage = (c.revenue / (c.monthlyBurn || 1)) * 100;
  const runway = c.cashOnHand / (c.monthlyBurn || 1);

  const ratios = [
    {
      name: "Current Ratio",
      value: currentRatio.toFixed(2),
      raw: currentRatio,
      color: currentRatio >= 2 ? "#00d4aa" : currentRatio >= 1 ? "#ffb830" : "#ff4757",
      description: "Current Assets / Current Liabilities. >2 is healthy.",
      benchmark: ">2.0x",
    },
    {
      name: "Burn Multiple",
      value: `${burnMultiple.toFixed(1)}x`,
      raw: burnMultiple,
      color: burnMultiple <= 1.5 ? "#00d4aa" : burnMultiple <= 3 ? "#ffb830" : "#ff4757",
      description: "Monthly Burn / MRR. Measures capital efficiency. <1.5x is excellent.",
      benchmark: "<1.5x",
    },
    {
      name: "Gross Margin",
      value: `${grossMargin.toFixed(1)}%`,
      raw: grossMargin,
      color: grossMargin >= 60 ? "#00d4aa" : grossMargin >= 40 ? "#ffb830" : "#ff4757",
      description: "Gross Profit / Revenue. Software businesses typically target >60%.",
      benchmark: ">60%",
    },
    {
      name: "Debt Ratio",
      value: `${debtRatio.toFixed(1)}%`,
      raw: debtRatio,
      color: debtRatio <= 30 ? "#00d4aa" : debtRatio <= 60 ? "#ffb830" : "#ff4757",
      description: "Total Debt / Total Assets. Lower is better for early-stage.",
      benchmark: "<30%",
    },
    {
      name: "Revenue Coverage",
      value: `${coverage.toFixed(0)}%`,
      raw: coverage,
      color: coverage >= 100 ? "#00d4aa" : coverage >= 50 ? "#ffb830" : "#ff4757",
      description: "MRR / Monthly Burn. 100%+ means revenue covers burn.",
      benchmark: ">100%",
    },
    {
      name: "Runway",
      value: `${runway.toFixed(1)} mo`,
      raw: runway,
      color: runway >= 12 ? "#00d4aa" : runway >= 6 ? "#ffb830" : "#ff4757",
      description: "Cash On Hand / Monthly Burn. >12 months is preferred.",
      benchmark: ">12 mo",
    },
  ];

  return (
    <SectionBox title="Key Financial Ratios" tag="Health Indicators">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {ratios.map((r) => (
          <div key={r.name} className="rounded-lg p-3" style={{ background: "#060a13", border: `1px solid ${r.color}33` }}>
            <div className="flex justify-between items-start mb-2">
              <div>
                <div className="font-mono text-xs" style={{ color: "#8899bb" }}>{r.name}</div>
                <div className="font-mono font-bold text-xl mt-0.5" style={{ color: r.color }}>{r.value}</div>
              </div>
              <div className="font-mono text-xs px-2 py-1 rounded" style={{ background: `${r.color}22`, color: r.color }}>
                Benchmark: {r.benchmark}
              </div>
            </div>
            <p className="text-xs leading-relaxed" style={{ color: "#4a5a7a" }}>{r.description}</p>
          </div>
        ))}
      </div>
    </SectionBox>
  );
}
