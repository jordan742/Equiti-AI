import type { PortfolioPosition } from "@/lib/types";
import { companies } from "@/lib/companies";
import { getRunwayMonths } from "@/lib/scoring";

interface Alert {
  ticker: string;
  type: "danger" | "warning" | "info";
  message: string;
}

export default function AlertsPanel({ positions }: { positions: PortfolioPosition[] }) {
  const alerts: Alert[] = [];

  for (const pos of positions) {
    const company = companies.find((c) => c.id === pos.ticker);
    if (!company) continue;

    const runway = getRunwayMonths(company);
    if (runway < 6) alerts.push({ ticker: pos.ticker, type: "danger", message: `${company.name} has <6 months runway (${runway.toFixed(1)} mo). May require emergency bridge.` });
    else if (runway < 12) alerts.push({ ticker: pos.ticker, type: "warning", message: `${company.name} runway is ${runway.toFixed(1)} months. Monitor closely.` });

    if (pos.isLocked) alerts.push({ ticker: pos.ticker, type: "info", message: `${company.name} shares are locked under the 12-month Reg CF resale restriction.` });

    const pnlPct = ((pos.currentPrice - pos.avgCost) / pos.avgCost) * 100;
    if (pnlPct < -30) alerts.push({ ticker: pos.ticker, type: "danger", message: `${company.name} position is down ${Math.abs(pnlPct).toFixed(0)}% from cost basis.` });
    else if (pnlPct > 50) alerts.push({ ticker: pos.ticker, type: "info", message: `${company.name} position is up ${pnlPct.toFixed(0)}% — consider reviewing allocation.` });
  }

  const COLOR = { danger: "#ff4757", warning: "#ffb830", info: "#2e6cf6" };
  const BG = { danger: "#2a0909", warning: "#2a1e06", info: "#082040" };
  const ICON = { danger: "⚠", warning: "!", info: "i" };

  return (
    <div className="rounded-lg p-4" style={{ background: "#0f1929", border: "1px solid #1e2d4a" }}>
      <div className="font-mono text-xs font-bold uppercase tracking-wider mb-3" style={{ color: "#8899bb" }}>
        Portfolio Alerts
      </div>

      {alerts.length === 0 ? (
        <div className="rounded p-3 text-center" style={{ background: "#060a13", border: "1px solid #1e2d4a" }}>
          <span className="font-mono text-xs" style={{ color: "#00d4aa" }}>✓ No active alerts. Portfolio is within normal parameters.</span>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {alerts.map((a, i) => (
            <div key={i} className="flex gap-3 rounded-lg p-3 items-start"
              style={{ background: BG[a.type], border: `1px solid ${COLOR[a.type]}33` }}>
              <div className="shrink-0 w-5 h-5 rounded-full flex items-center justify-center font-mono text-xs font-bold"
                style={{ background: `${COLOR[a.type]}22`, color: COLOR[a.type] }}>
                {ICON[a.type]}
              </div>
              <div className="flex-1 min-w-0">
                <span className="font-mono text-xs font-bold mr-2" style={{ color: COLOR[a.type] }}>{a.ticker}</span>
                <span className="text-xs" style={{ color: "#c8d8f0" }}>{a.message}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
