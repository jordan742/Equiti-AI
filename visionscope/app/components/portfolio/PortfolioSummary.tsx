"use client";
import type { PortfolioPosition } from "@/lib/types";
import { fmtCurrency, fmtPct } from "@/lib/formatting";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const PORTFOLIO_HISTORY = [
  { m: "Oct", value: 5800 },
  { m: "Nov", value: 6200 },
  { m: "Dec", value: 5950 },
  { m: "Jan", value: 6800 },
  { m: "Feb", value: 7200 },
  { m: "Mar", value: 7940 },
];

export default function PortfolioSummary({ positions }: { positions: PortfolioPosition[] }) {
  const totalInvested = positions.reduce((s, p) => s + p.totalInvested, 0);
  const currentValue = positions.reduce((s, p) => s + p.shares * p.currentPrice, 0);
  const totalPnl = currentValue - totalInvested;
  const pnlPct = (totalPnl / totalInvested) * 100;

  const stats = [
    { label: "Portfolio Value", value: fmtCurrency(currentValue, true), color: "#2e6cf6" },
    { label: "Total Invested", value: fmtCurrency(totalInvested, true), color: "#e8edf5" },
    { label: "Unrealized P&L", value: fmtCurrency(totalPnl, true), color: totalPnl >= 0 ? "#00d4aa" : "#ff4757" },
    { label: "Return", value: fmtPct(pnlPct), color: pnlPct >= 0 ? "#00d4aa" : "#ff4757" },
    { label: "# Positions", value: positions.length.toString(), color: "#e8edf5" },
    { label: "Active Locks", value: positions.filter(p => p.isLocked).length.toString(), color: "#ffb830" },
  ];

  return (
    <div className="rounded-lg p-4" style={{ background: "#0f1929", border: "1px solid #1e2d4a" }}>
      <div className="grid grid-cols-3 sm:grid-cols-6 gap-3 mb-4">
        {stats.map((s) => (
          <div key={s.label}>
            <div className="font-mono text-xs" style={{ color: "#4a5a7a" }}>{s.label}</div>
            <div className="font-mono font-bold text-sm mt-0.5" style={{ color: s.color }}>{s.value}</div>
          </div>
        ))}
      </div>

      <div>
        <div className="font-mono text-xs mb-2" style={{ color: "#4a5a7a" }}>Portfolio Value — 6 Month</div>
        <ResponsiveContainer width="100%" height={100}>
          <AreaChart data={PORTFOLIO_HISTORY} margin={{ top: 5, right: 10, bottom: 0, left: 10 }}>
            <defs>
              <linearGradient id="portGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#2e6cf6" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#2e6cf6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="m" tick={{ fill: "#4a5a7a", fontSize: 10, fontFamily: "JetBrains Mono" }} />
            <YAxis tick={{ fill: "#4a5a7a", fontSize: 10, fontFamily: "JetBrains Mono" }} tickFormatter={(v) => fmtCurrency(v, true)} />
            <Tooltip contentStyle={{ background: "#0c1220", border: "1px solid #1e2d4a", fontFamily: "JetBrains Mono", fontSize: 11 }}
              formatter={(v: number) => [fmtCurrency(v), "Value"]} />
            <Area type="monotone" dataKey="value" stroke="#2e6cf6" fill="url(#portGrad)" strokeWidth={2} dot={false} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
