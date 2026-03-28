import { fmtCurrency } from "@/lib/formatting";

const REG_CF_LIMIT = 124000; // max annual for high-income

interface RegCFUtilBarProps {
  invested: number;
  limit: number;
}

export default function RegCFUtilBar({ invested, limit }: RegCFUtilBarProps) {
  const pct = Math.min((invested / limit) * 100, 100);
  const remaining = Math.max(limit - invested, 0);
  const color = pct >= 90 ? "#ff4757" : pct >= 70 ? "#ffb830" : "#00d4aa";

  return (
    <div className="rounded-lg p-4" style={{ background: "#0f1929", border: "1px solid #1e2d4a" }}>
      <div className="flex justify-between items-center mb-2">
        <div>
          <span className="font-mono text-xs font-bold" style={{ color: "#e8edf5" }}>Reg CF Annual Limit Utilization</span>
          <span className="font-mono text-xs ml-2" style={{ color: "#4a5a7a" }}>(2026 Rules)</span>
        </div>
        <span className="font-mono text-xs font-bold" style={{ color }}>
          {pct.toFixed(1)}% used
        </span>
      </div>

      <div className="h-3 rounded-full overflow-hidden mb-2" style={{ background: "#1e2d4a" }}>
        <div className="h-full rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, background: color }} />
      </div>

      <div className="flex justify-between">
        <span className="font-mono text-xs" style={{ color: "#8899bb" }}>
          Invested: <span style={{ color }}>{fmtCurrency(invested)}</span>
        </span>
        <span className="font-mono text-xs" style={{ color: "#8899bb" }}>
          Remaining: <span style={{ color: "#e8edf5" }}>{fmtCurrency(remaining)}</span>
          {" / "}Limit: {fmtCurrency(limit)}
        </span>
      </div>

      {pct >= 90 && (
        <div className="mt-2 p-2 rounded" style={{ background: "#2a090933", border: "1px solid #ff475733" }}>
          <p className="font-mono text-xs" style={{ color: "#ff4757" }}>
            ⚠ You are approaching your annual Reg CF investment limit. Additional investments may not be permitted.
          </p>
        </div>
      )}
    </div>
  );
}
