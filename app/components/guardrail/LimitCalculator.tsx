"use client";
import { useState } from "react";
import { fmtCurrency } from "@/lib/formatting";

function calcLimit(income: number, netWorth: number): number {
  if (income < 124_000 && netWorth < 124_000) {
    return Math.max(2_500, 0.05 * Math.min(income, netWorth));
  }
  return Math.min(0.10 * Math.min(income, netWorth), 124_000);
}

export default function LimitCalculator() {
  const [income, setIncome] = useState("");
  const [netWorth, setNetWorth] = useState("");
  const [invested, setInvested] = useState("");

  const incomeNum = parseFloat(income.replace(/,/g, "")) || 0;
  const nwNum = parseFloat(netWorth.replace(/,/g, "")) || 0;
  const investedNum = parseFloat(invested.replace(/,/g, "")) || 0;

  const canCalc = incomeNum > 0 && nwNum > 0;
  const limit = canCalc ? calcLimit(incomeNum, nwNum) : 0;
  const remaining = Math.max(limit - investedNum, 0);
  const usedPct = canCalc ? Math.min((investedNum / limit) * 100, 100) : 0;
  const rule = incomeNum < 124_000 && nwNum < 124_000 ? "A" : "B";
  const color = usedPct >= 90 ? "#ff4757" : usedPct >= 70 ? "#ffb830" : "#00d4aa";

  return (
    <div className="rounded-lg p-4" style={{ background: "#0f1929", border: "1px solid #1e2d4a" }}>
      <div className="font-mono text-xs font-bold uppercase tracking-wider mb-4" style={{ color: "#8899bb" }}>
        Reg CF Investor Limit Calculator — 2026 Rules
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
        {[
          { label: "Annual Income ($)", value: income, set: setIncome, placeholder: "e.g. 85000" },
          { label: "Net Worth ($) — excl. primary residence", value: netWorth, set: setNetWorth, placeholder: "e.g. 120000" },
          { label: "Already Invested This Year ($)", value: invested, set: setInvested, placeholder: "e.g. 2500" },
        ].map((f) => (
          <div key={f.label}>
            <label className="font-mono text-xs mb-1 block" style={{ color: "#4a5a7a" }}>{f.label}</label>
            <input type="text" value={f.value} onChange={(e) => f.set(e.target.value)}
              placeholder={f.placeholder}
              className="w-full rounded px-3 py-2 font-mono text-sm outline-none"
              style={{ background: "#060a13", border: "1px solid #1e2d4a", color: "#e8edf5" }} />
          </div>
        ))}
      </div>

      {canCalc ? (
        <div className="flex flex-col gap-3">
          {/* Result banner */}
          <div className="rounded-lg p-4" style={{ background: "#060a13", border: `1px solid ${color}44` }}>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <div className="font-mono text-xs" style={{ color: "#4a5a7a" }}>Annual Limit (Rule {rule})</div>
                <div className="font-mono text-2xl font-bold mt-1" style={{ color }}>{fmtCurrency(limit)}</div>
              </div>
              <div>
                <div className="font-mono text-xs" style={{ color: "#4a5a7a" }}>Already Invested</div>
                <div className="font-mono text-2xl font-bold mt-1" style={{ color: "#ffb830" }}>{fmtCurrency(investedNum)}</div>
              </div>
              <div>
                <div className="font-mono text-xs" style={{ color: "#4a5a7a" }}>Remaining Capacity</div>
                <div className="font-mono text-2xl font-bold mt-1" style={{ color: remaining > 0 ? "#00d4aa" : "#ff4757" }}>
                  {fmtCurrency(remaining)}
                </div>
              </div>
            </div>
          </div>

          {/* Utilization bar */}
          <div>
            <div className="flex justify-between mb-1">
              <span className="font-mono text-xs" style={{ color: "#4a5a7a" }}>Utilization</span>
              <span className="font-mono text-xs font-bold" style={{ color }}>{usedPct.toFixed(1)}%</span>
            </div>
            <div className="h-3 rounded-full overflow-hidden" style={{ background: "#1e2d4a" }}>
              <div className="h-full rounded-full transition-all" style={{ width: `${usedPct}%`, background: color }} />
            </div>
          </div>

          {/* Formula used */}
          <div className="rounded p-3" style={{ background: "#060a13", border: "1px solid #1e2d4a" }}>
            <div className="font-mono text-xs mb-1" style={{ color: "#4a5a7a" }}>Formula Applied (Rule {rule}):</div>
            {rule === "A" ? (
              <div className="font-mono text-xs" style={{ color: "#e8edf5" }}>
                max($2,500, 5% × min({fmtCurrency(incomeNum)}, {fmtCurrency(nwNum)})) = {fmtCurrency(limit)}
              </div>
            ) : (
              <div className="font-mono text-xs" style={{ color: "#e8edf5" }}>
                min(10% × min({fmtCurrency(incomeNum)}, {fmtCurrency(nwNum)}), $124,000) = {fmtCurrency(limit)}
              </div>
            )}
          </div>

          {remaining <= 0 && (
            <div className="rounded p-3" style={{ background: "#2a0909", border: "1px solid #ff475744" }}>
              <p className="font-mono text-xs" style={{ color: "#ff4757" }}>
                ⚠ You have reached your annual Reg CF investment limit. Additional Reg CF investments this year may violate SEC rules.
              </p>
            </div>
          )}
        </div>
      ) : (
        <div className="rounded p-4 text-center" style={{ background: "#060a13", border: "1px solid #1e2d4a" }}>
          <span className="font-mono text-xs" style={{ color: "#4a5a7a" }}>
            Enter your income and net worth above to calculate your limit.
          </span>
        </div>
      )}
    </div>
  );
}
