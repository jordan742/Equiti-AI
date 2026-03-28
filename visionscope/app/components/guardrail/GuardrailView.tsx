import LimitCalculator from "./LimitCalculator";
import LimitExplainer from "./LimitExplainer";
import SPVSimulator from "./SPVSimulator";

export default function GuardrailView() {
  return (
    <div className="flex flex-col gap-4">
      {/* Header */}
      <div className="rounded-lg p-4" style={{ background: "#082040", border: "1px solid #2e6cf644" }}>
        <div className="font-mono text-sm font-bold mb-1" style={{ color: "#2e6cf6" }}>
          Investor Guardrail Tools
        </div>
        <p className="text-xs leading-relaxed" style={{ color: "#8899bb" }}>
          These tools help retail investors understand and comply with Regulation Crowdfunding investment limits.
          All calculators use 2026 SEC rules (17 CFR Part 227). Results are estimates only — consult a financial
          professional for personalized advice.
        </p>
      </div>

      <LimitCalculator />
      <LimitExplainer />
      <SPVSimulator />

      {/* Footer disclaimer */}
      <div className="rounded p-3 text-center" style={{ background: "#0c1220", border: "1px solid #1e2d4a" }}>
        <p className="font-mono text-xs" style={{ color: "#4a5a7a" }}>
          Guardrail tools are for educational purposes only. Not financial, legal, or tax advice.
          Reg CF investment limits are applied by funding portals at the time of investment. Always verify your
          remaining capacity directly with each platform before investing.
        </p>
      </div>
    </div>
  );
}
