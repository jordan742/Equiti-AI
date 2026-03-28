import type { Company } from "@/lib/types";
import { fm, months } from "@/lib/format";
import ScoreRing from "./ScoreRing";
import Pill from "./Pill";

export default function CompanyCard({ company: c, onClick }: { company: Company; onClick: () => void }) {
  const runway = c.cash / c.burn;
  const runwayColor = runway > 12 ? "#00d4aa" : runway > 6 ? "#ffb830" : "#ff4757";

  return (
    <button onClick={onClick} className="w-full text-left rounded-xl p-4 transition-all"
      style={{ background: "#0f1520", border: "1px solid #1b2540" }}>
      <div className="flex gap-4">
        <div className="shrink-0"><ScoreRing company={c} size={72} /></div>
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <span className="font-mono font-bold text-sm" style={{ color: "#2e6cf6" }}>{c.id}</span>
            <span className="font-semibold" style={{ color: "#f0f4ff", fontFamily: "'Instrument Serif', serif" }}>{c.name}</span>
            <Pill label={c.status} variant={c.status === "Live" ? "live" : "closed"} small />
            <Pill label={c.security} variant={c.security === "SAFE" ? "blue" : "purple"} small />
            <Pill label={c.stage} variant="gray" small />
          </div>
          <div className="font-mono text-xs mb-2" style={{ color: "#4e5f7d" }}>{c.sector} · {c.platform} · {c.location}</div>
          <div className="rounded-lg px-3 py-2 mb-3" style={{ background: "#06b6d40d", border: "1px solid #06b6d422" }}>
            <span className="font-mono text-xs" style={{ color: "#06b6d4" }}>{c.ai.conviction} conviction — {c.ai.verdict.toLowerCase()}</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
            {[
              { label: "Raised",  value: fm(c.raised, true) },
              { label: "Runway",  value: months(c.cash, c.burn), color: runwayColor },
              { label: "MRR",     value: fm(c.revenue, true) },
              { label: "Burn",    value: fm(c.burn, true) },
              { label: "Val Cap", value: fm(c.valuationCap, true) },
            ].map((m) => (
              <div key={m.label} className="rounded px-2 py-1.5" style={{ background: "#131a28", border: "1px solid #1b2540" }}>
                <div className="font-mono" style={{ color: "#4e5f7d", fontSize: 9 }}>{m.label}</div>
                <div className="font-mono font-bold text-xs" style={{ color: m.color || "#f0f4ff" }}>{m.value}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </button>
  );
}
