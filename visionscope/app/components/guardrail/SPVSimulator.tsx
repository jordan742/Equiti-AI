"use client";
import { useState } from "react";
import { fmtCurrency, fmtPct } from "@/lib/formatting";

interface Scenario {
  label: string;
  exitMultiple: number;
  probability: number;
}

const DEFAULT_SCENARIOS: Scenario[] = [
  { label: "Failure",      exitMultiple: 0,   probability: 60 },
  { label: "Modest Exit",  exitMultiple: 1.5, probability: 25 },
  { label: "Good Exit",    exitMultiple: 5,   probability: 10 },
  { label: "Home Run",     exitMultiple: 20,  probability: 5  },
];

export default function SPVSimulator() {
  const [investment, setInvestment] = useState("1000");
  const [scenarios, setScenarios] = useState<Scenario[]>(DEFAULT_SCENARIOS);

  const investNum = parseFloat(investment) || 0;
  const totalProb = scenarios.reduce((s, sc) => s + sc.probability, 0);
  const expectedValue = scenarios.reduce((s, sc) => s + (sc.exitMultiple * investNum * sc.probability) / 100, 0);
  const ev_return = ((expectedValue - investNum) / investNum) * 100;

  function updateScenario(i: number, field: keyof Scenario, val: string) {
    setScenarios((prev) => prev.map((s, idx) => idx !== i ? s : { ...s, [field]: parseFloat(val) || 0 }));
  }

  const COLORS = ["#ff4757", "#ffb830", "#2e6cf6", "#00d4aa"];

  return (
    <div className="rounded-lg p-4" style={{ background: "#0f1929", border: "1px solid #1e2d4a" }}>
      <div className="font-mono text-xs font-bold uppercase tracking-wider mb-4" style={{ color: "#8899bb" }}>
        Investment Scenario Simulator
      </div>

      <div className="mb-4">
        <label className="font-mono text-xs mb-1 block" style={{ color: "#4a5a7a" }}>Investment Amount ($)</label>
        <input type="number" min="100" step="100" value={investment} onChange={(e) => setInvestment(e.target.value)}
          className="w-full sm:w-48 rounded px-3 py-2 font-mono text-sm outline-none"
          style={{ background: "#060a13", border: "1px solid #1e2d4a", color: "#e8edf5" }} />
      </div>

      {/* Scenario table */}
      <div className="rounded overflow-hidden mb-4" style={{ border: "1px solid #1e2d4a" }}>
        <div className="grid grid-cols-4 px-3 py-2 font-mono text-xs" style={{ background: "#060a13", borderBottom: "1px solid #1e2d4a", color: "#4a5a7a" }}>
          <div>Scenario</div>
          <div className="text-right">Exit Multiple</div>
          <div className="text-right">Probability %</div>
          <div className="text-right">Expected Return</div>
        </div>
        {scenarios.map((sc, i) => {
          const returns = sc.exitMultiple * investNum;
          const pnl = returns - investNum;
          return (
            <div key={i} className="grid grid-cols-4 px-3 py-2 items-center"
              style={{ background: i % 2 === 0 ? "#0c1220" : "#0f1929", borderBottom: "1px solid #0c1220" }}>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full" style={{ background: COLORS[i] }} />
                <input value={sc.label} onChange={(e) => updateScenario(i, "label", e.target.value)}
                  className="font-mono text-xs bg-transparent outline-none w-24" style={{ color: COLORS[i] }} />
              </div>
              <div className="text-right">
                <input type="number" min="0" step="0.5" value={sc.exitMultiple}
                  onChange={(e) => updateScenario(i, "exitMultiple", e.target.value)}
                  className="font-mono text-xs text-right bg-transparent outline-none w-16" style={{ color: "#e8edf5" }} />
                <span className="font-mono text-xs" style={{ color: "#4a5a7a" }}>x</span>
              </div>
              <div className="text-right">
                <input type="number" min="0" max="100" step="1" value={sc.probability}
                  onChange={(e) => updateScenario(i, "probability", e.target.value)}
                  className="font-mono text-xs text-right bg-transparent outline-none w-12" style={{ color: "#e8edf5" }} />
                <span className="font-mono text-xs" style={{ color: "#4a5a7a" }}>%</span>
              </div>
              <div className="text-right">
                <div className="font-mono text-xs font-bold" style={{ color: pnl >= 0 ? "#00d4aa" : "#ff4757" }}>
                  {fmtCurrency(returns, true)}
                </div>
                <div className="font-mono text-xs" style={{ color: pnl >= 0 ? "#00d4aa" : "#ff4757" }}>
                  ({pnl >= 0 ? "+" : ""}{fmtCurrency(pnl, true)})
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* EV summary */}
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded p-3" style={{ background: "#060a13", border: "1px solid #1e2d4a" }}>
          <div className="font-mono text-xs" style={{ color: "#4a5a7a" }}>Total Probability</div>
          <div className="font-mono font-bold text-sm mt-1" style={{ color: totalProb === 100 ? "#00d4aa" : "#ffb830" }}>
            {totalProb}%
            {totalProb !== 100 && <span className="text-xs ml-1" style={{ color: "#ffb830" }}>(should = 100%)</span>}
          </div>
        </div>
        <div className="rounded p-3" style={{ background: "#060a13", border: "1px solid #1e2d4a" }}>
          <div className="font-mono text-xs" style={{ color: "#4a5a7a" }}>Expected Value</div>
          <div className="font-mono font-bold text-sm mt-1" style={{ color: expectedValue >= investNum ? "#00d4aa" : "#ff4757" }}>
            {fmtCurrency(expectedValue, true)}
          </div>
        </div>
        <div className="rounded p-3" style={{ background: "#060a13", border: "1px solid #1e2d4a" }}>
          <div className="font-mono text-xs" style={{ color: "#4a5a7a" }}>Expected Return</div>
          <div className="font-mono font-bold text-sm mt-1" style={{ color: ev_return >= 0 ? "#00d4aa" : "#ff4757" }}>
            {ev_return >= 0 ? "+" : ""}{ev_return.toFixed(1)}%
          </div>
        </div>
      </div>

      <p className="font-mono text-xs mt-3" style={{ color: "#4a5a7a" }}>
        * Expected value = weighted average of outcomes. Probabilities are user-defined estimates. This is a simplified model — actual outcomes depend on dilution, pro-rata rights, liquidation preferences, and other factors.
      </p>
    </div>
  );
}
