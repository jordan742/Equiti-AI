import type { Company } from "@/lib/types";
import { calculateScore } from "@/lib/scoring";
import { fmtCurrency, fmtMonths } from "@/lib/formatting";
import ScoreRing from "../ui/ScoreRing";
import Pill from "../ui/Pill";

interface CompanyCardProps {
  company: Company;
  onClick: () => void;
}

export default function CompanyCard({ company: c, onClick }: CompanyCardProps) {
  const score = calculateScore(c);
  const runway = c.cashOnHand / c.monthlyBurn;

  return (
    <div className="company-card rounded-lg p-4 cursor-pointer"
      style={{ background: "#0f1929", border: "1px solid #1e2d4a" }}
      onClick={onClick}>
      <div className="flex items-start gap-4">
        <ScoreRing score={score} size={64} showLabel={true} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className="font-mono font-bold text-sm" style={{ color: "#2e6cf6" }}>{c.id}</span>
            <span className="font-semibold text-sm" style={{ color: "#e8edf5" }}>{c.name}</span>
            <Pill label={c.status} variant={c.status === "Live" ? "live" : "closed"} />
            <Pill label={c.stage} variant="blue" />
            <Pill label={c.platform} variant="moderate" />
          </div>
          <p className="text-xs mb-2 line-clamp-2" style={{ color: "#8899bb" }}>
            <span className="italic font-mono" style={{ color: "#00d4aa" }}>
              &quot;{c.aiAnalysis.verdict}&quot;
            </span>
            {" — "}{c.aiAnalysis.summary.slice(0, 100)}...
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {[
              { label: "Raised", value: fmtCurrency(c.raised, true) },
              { label: "Runway", value: fmtMonths(runway), color: runway < 6 ? "#ff4757" : runway < 12 ? "#ffb830" : "#00d4aa" },
              { label: "MRR", value: fmtCurrency(c.revenue, true) },
              { label: "Val Cap", value: fmtCurrency(c.valuationCap, true) },
            ].map((m) => (
              <div key={m.label} className="rounded px-2 py-1.5" style={{ background: "#060a13", border: "1px solid #1e2d4a" }}>
                <div className="font-mono text-xs" style={{ color: "#8899bb" }}>{m.label}</div>
                <div className="font-mono font-bold text-sm" style={{ color: m.color || "#e8edf5" }}>{m.value}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
