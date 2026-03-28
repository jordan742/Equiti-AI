import { companies } from "@/lib/companies";
import { calculateScore } from "@/lib/scoring";
import { fmtCurrency } from "@/lib/formatting";

interface ComplianceAlert {
  type: "danger" | "warning" | "info";
  title: string;
  body: string;
}

const REG_CF_CAP = 5_000_000;

export default function ComplianceAlerts() {
  const alerts: ComplianceAlert[] = [];

  for (const c of companies) {
    if (c.raised >= REG_CF_CAP * 0.95) {
      alerts.push({
        type: "danger",
        title: `${c.id} Near Reg CF Cap`,
        body: `${c.name} has raised ${fmtCurrency(c.raised, true)} — approaching the $5M annual Reg CF limit. Further raises may require Reg A+ or a registered offering.`,
      });
    } else if (c.raised >= REG_CF_CAP * 0.80) {
      alerts.push({
        type: "warning",
        title: `${c.id} Elevated Raise Level`,
        body: `${c.name} has raised ${fmtCurrency(c.raised, true)} (${((c.raised / REG_CF_CAP) * 100).toFixed(0)}% of cap). Monitor remaining raise capacity.`,
      });
    }

    const runway = c.cashOnHand / c.monthlyBurn;
    if (runway < 6) {
      alerts.push({
        type: "danger",
        title: `${c.id} Critical Runway`,
        body: `${c.name} has ${runway.toFixed(1)} months of runway. Companies with <6 months runway face heightened risk of going concern issues before their next Form C-AR filing.`,
      });
    }

    const score = calculateScore(c);
    if (score < 25) {
      alerts.push({
        type: "warning",
        title: `${c.id} High Risk Classification`,
        body: `${c.name} scores ${score}/100 — classified as HIGH RISK. Investors should review all Form C disclosures and risk factors before investing.`,
      });
    }
  }

  // Platform-level compliance notices
  alerts.push({
    type: "info",
    title: "Annual Form C-AR Reminder",
    body: "Reg CF issuers must file annual reports (Form C-AR) within 120 days of fiscal year end (17 CFR 227.202). Verify filing status for each company on SEC EDGAR.",
  });

  alerts.push({
    type: "info",
    title: "12-Month Resale Lock Period Active",
    body: "Securities acquired in Reg CF offerings are restricted for 12 months from purchase date per 17 CFR 227.501. Plan liquidity accordingly.",
  });

  const COLOR = { danger: "#ff4757", warning: "#ffb830", info: "#2e6cf6" };
  const BG = { danger: "#2a0909", warning: "#2a1e06", info: "#082040" };

  return (
    <div className="rounded-lg p-4" style={{ background: "#0f1929", border: "1px solid #1e2d4a" }}>
      <div className="font-mono text-xs font-bold uppercase tracking-wider mb-3" style={{ color: "#8899bb" }}>
        Compliance Alerts ({alerts.length})
      </div>
      <div className="flex flex-col gap-2">
        {alerts.map((a, i) => (
          <div key={i} className="rounded-lg p-3" style={{ background: BG[a.type], border: `1px solid ${COLOR[a.type]}33` }}>
            <div className="font-mono text-xs font-bold mb-1" style={{ color: COLOR[a.type] }}>{a.title}</div>
            <p className="text-xs leading-relaxed" style={{ color: "#c8d8f0" }}>{a.body}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
