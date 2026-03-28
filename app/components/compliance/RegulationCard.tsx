import type { Regulation } from "@/lib/types";

const STATUS_COLOR: Record<string, string> = {
  green: "#00d4aa",
  amber: "#ffb830",
  red: "#ff4757",
  blue: "#2e6cf6",
};

const STATUS_BG: Record<string, string> = {
  green: "#052e1c",
  amber: "#2a1e06",
  red: "#2a0909",
  blue: "#082040",
};

export default function RegulationCard({ reg }: { reg: Regulation }) {
  const color = STATUS_COLOR[reg.statusColor];
  const bg = STATUS_BG[reg.statusColor];

  return (
    <div className="rounded-lg p-4" style={{ background: "#0f1929", border: "1px solid #1e2d4a" }}>
      <div className="flex flex-col sm:flex-row sm:items-start gap-3 mb-2">
        <div className="flex-1">
          <h3 className="font-semibold text-sm mb-1" style={{ color: "#e8edf5" }}>{reg.title}</h3>
          <code className="font-mono text-xs" style={{ color: "#4a5a7a" }}>{reg.citation}</code>
        </div>
        <div className="shrink-0">
          <span className="font-mono text-xs px-2 py-1 rounded"
            style={{ background: bg, color, border: `1px solid ${color}44` }}>
            {reg.status}
          </span>
        </div>
      </div>
      <p className="text-xs leading-relaxed" style={{ color: "#8899bb" }}>{reg.description}</p>
      {reg.effectiveDate && (
        <div className="mt-2 font-mono text-xs" style={{ color: "#4a5a7a" }}>
          Effective: <span style={{ color }}>{reg.effectiveDate}</span>
        </div>
      )}
    </div>
  );
}
