import type { Company } from "@/lib/types";
import SectionBox from "../ui/SectionBox";

const CONVICTION_COLOR = { HIGH: "#00d4aa", MODERATE: "#ffb830", LOW: "#ff4757" };
const VERDICT_BG = { "Strong": "#052e1c", "Favorable": "#082040", "Cautious Optimism": "#2a1e06", "High Risk": "#2a0909" } as Record<string, string>;
const VERDICT_COLOR = { "Strong": "#00d4aa", "Favorable": "#2e6cf6", "Cautious Optimism": "#ffb830", "High Risk": "#ff4757" } as Record<string, string>;

export default function AIAnalysisPanel({ company: c }: { company: Company }) {
  const ai = c.aiAnalysis;
  const vbg = VERDICT_BG[ai.verdict] || "#141c30";
  const vc  = VERDICT_COLOR[ai.verdict] || "#e8edf5";

  return (
    <div className="flex flex-col gap-4">
      {/* Verdict banner */}
      <div className="rounded-lg p-4 flex flex-col sm:flex-row sm:items-center gap-4"
        style={{ background: vbg, border: `1px solid ${vc}44` }}>
        <div className="flex-1">
          <div className="font-mono text-xs uppercase tracking-widest mb-1" style={{ color: "#8899bb" }}>AI Verdict</div>
          <div className="font-mono font-bold text-2xl" style={{ color: vc }}>{ai.verdict}</div>
        </div>
        <div className="flex gap-6">
          <div>
            <div className="font-mono text-xs uppercase tracking-widest mb-1" style={{ color: "#8899bb" }}>Conviction</div>
            <div className="font-mono font-bold text-lg" style={{ color: CONVICTION_COLOR[ai.conviction] }}>{ai.conviction}</div>
          </div>
          <div>
            <div className="font-mono text-xs uppercase tracking-widest mb-1" style={{ color: "#8899bb" }}>Risk Level</div>
            <div className="flex gap-1 mt-1">
              {[1,2,3,4,5].map((i) => (
                <div key={i} className="w-3 h-3 rounded-sm"
                  style={{ background: i <= ai.riskLevel ? "#ff4757" : "#1e2d4a" }} />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Plain English */}
      <SectionBox title="Plain English" tag="Everyday Analogy">
        <p className="font-mono text-sm leading-relaxed" style={{ color: "#00e5ff" }}>
          &quot;{ai.plainEnglish}&quot;
        </p>
      </SectionBox>

      {/* Summary */}
      <SectionBox title="Analyst Summary">
        <p className="text-sm leading-relaxed" style={{ color: "#c8d8f0" }}>{ai.summary}</p>
      </SectionBox>

      {/* Bull / Bear */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="rounded-lg p-4" style={{ background: "#052e1c", border: "1px solid rgba(0,212,170,0.25)" }}>
          <div className="flex items-center gap-2 mb-2">
            <span className="font-mono text-xs font-bold uppercase" style={{ color: "#00d4aa" }}>▲ Bull Case</span>
          </div>
          <p className="text-sm leading-relaxed" style={{ color: "#c8f0e0" }}>{ai.bullCase}</p>
        </div>
        <div className="rounded-lg p-4" style={{ background: "#2a0909", border: "1px solid rgba(255,71,87,0.25)" }}>
          <div className="flex items-center gap-2 mb-2">
            <span className="font-mono text-xs font-bold uppercase" style={{ color: "#ff4757" }}>▼ Bear Case</span>
          </div>
          <p className="text-sm leading-relaxed" style={{ color: "#f0c8c8" }}>{ai.bearCase}</p>
        </div>
      </div>
    </div>
  );
}
