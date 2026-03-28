"use client";
import type { PortfolioPosition } from "@/lib/types";
import { fmtCurrency, fmtPct } from "@/lib/formatting";
import PortfolioSummary from "./PortfolioSummary";
import RegCFUtilBar from "./RegCFUtilBar";
import AlertsPanel from "./AlertsPanel";

const DEMO_POSITIONS: PortfolioPosition[] = [
  { ticker: "NMSH", companyName: "NeuralMesh AI",     shares: 500,  avgCost: 1.00, currentPrice: 1.20, totalInvested: 500,   isLocked: true },
  { ticker: "CBOT", companyName: "CompliBot",         shares: 250,  avgCost: 2.40, currentPrice: 2.80, totalInvested: 600,   isLocked: true },
  { ticker: "HLNS", companyName: "HeliosNet",         shares: 1000, avgCost: 0.85, currentPrice: 0.62, totalInvested: 850,   isLocked: false },
  { ticker: "SYNK", companyName: "Synkraft Systems",  shares: 400,  avgCost: 3.10, currentPrice: 4.20, totalInvested: 1240,  isLocked: false },
];

const DEMO_LIMIT = 12400; // example limit for demo user
const TOTAL_INVESTED = DEMO_POSITIONS.reduce((s, p) => s + p.totalInvested, 0);

export default function PortfolioView() {
  return (
    <div className="flex flex-col gap-4">
      <PortfolioSummary positions={DEMO_POSITIONS} />
      <RegCFUtilBar invested={TOTAL_INVESTED} limit={DEMO_LIMIT} />
      <AlertsPanel positions={DEMO_POSITIONS} />

      {/* Position table */}
      <div className="rounded-lg overflow-hidden" style={{ background: "#0f1929", border: "1px solid #1e2d4a" }}>
        <div className="px-4 py-3" style={{ borderBottom: "1px solid #1e2d4a" }}>
          <span className="font-mono text-xs font-bold uppercase tracking-wider" style={{ color: "#8899bb" }}>
            Holdings
          </span>
        </div>

        {/* Table header */}
        <div className="grid grid-cols-8 px-4 py-2 font-mono text-xs" style={{ background: "#060a13", borderBottom: "1px solid #1e2d4a", color: "#4a5a7a" }}>
          <div className="col-span-2">Company</div>
          <div className="text-right">Shares</div>
          <div className="text-right">Avg Cost</div>
          <div className="text-right">Mkt Price</div>
          <div className="text-right">Invested</div>
          <div className="text-right">Cur Value</div>
          <div className="text-right">P&L</div>
        </div>

        {DEMO_POSITIONS.map((p, i) => {
          const curValue = p.shares * p.currentPrice;
          const pnl = curValue - p.totalInvested;
          const pnlPct = (pnl / p.totalInvested) * 100;
          const color = pnl >= 0 ? "#00d4aa" : "#ff4757";

          return (
            <div key={p.ticker}
              className="grid grid-cols-8 px-4 py-3 items-center"
              style={{ background: i % 2 === 0 ? "#0c1220" : "#0f1929", borderBottom: "1px solid #0c1220" }}>
              <div className="col-span-2">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold" style={{ color: "#2e6cf6" }}>{p.ticker}</span>
                  {p.isLocked && (
                    <span className="font-mono text-xs px-1.5 py-0.5 rounded" style={{ background: "#ffb83022", color: "#ffb830" }}>
                      LOCKED
                    </span>
                  )}
                </div>
                <div className="font-mono text-xs" style={{ color: "#4a5a7a" }}>{p.companyName}</div>
              </div>
              <div className="font-mono text-xs text-right" style={{ color: "#e8edf5" }}>{p.shares.toLocaleString()}</div>
              <div className="font-mono text-xs text-right" style={{ color: "#8899bb" }}>{fmtCurrency(p.avgCost)}</div>
              <div className="font-mono text-xs text-right" style={{ color: "#e8edf5" }}>{fmtCurrency(p.currentPrice)}</div>
              <div className="font-mono text-xs text-right" style={{ color: "#8899bb" }}>{fmtCurrency(p.totalInvested)}</div>
              <div className="font-mono text-xs text-right" style={{ color: "#e8edf5" }}>{fmtCurrency(curValue)}</div>
              <div className="font-mono text-xs text-right font-bold" style={{ color }}>
                {pnl >= 0 ? "+" : ""}{fmtCurrency(pnl, true)}
                <div className="font-normal" style={{ color }}>{fmtPct(pnlPct)}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Disclaimer */}
      <div className="rounded p-3" style={{ background: "#0c1220", border: "1px solid #1e2d4a" }}>
        <p className="font-mono text-xs text-center" style={{ color: "#4a5a7a" }}>
          DEMO PORTFOLIO — Simulated data only. Reg CF investments are illiquid and subject to a 12-month resale restriction.
          Not financial advice. Portfolio values do not reflect real transactions.
        </p>
      </div>
    </div>
  );
}
