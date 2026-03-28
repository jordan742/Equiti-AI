export default function LimitExplainer() {
  return (
    <div className="rounded-lg p-4" style={{ background: "#0f1929", border: "1px solid #1e2d4a" }}>
      <div className="font-mono text-xs font-bold uppercase tracking-wider mb-3" style={{ color: "#8899bb" }}>
        How the 2026 Reg CF Limit Works
      </div>
      <div className="flex flex-col gap-3 text-xs leading-relaxed" style={{ color: "#8899bb" }}>
        <div className="rounded p-3" style={{ background: "#060a13", border: "1px solid #1e2d4a" }}>
          <div className="font-mono text-xs font-bold mb-1" style={{ color: "#ffb830" }}>Rule A — Lower-Income / Lower-Wealth</div>
          <p>If BOTH annual income AND net worth are below $124,000:</p>
          <div className="font-mono text-sm mt-1" style={{ color: "#e8edf5" }}>
            Limit = max($2,500, 5% × min(income, net worth))
          </div>
        </div>
        <div className="rounded p-3" style={{ background: "#060a13", border: "1px solid #1e2d4a" }}>
          <div className="font-mono text-xs font-bold mb-1" style={{ color: "#2e6cf6" }}>Rule B — Higher-Income / Higher-Wealth</div>
          <p>If EITHER annual income OR net worth is $124,000 or more:</p>
          <div className="font-mono text-sm mt-1" style={{ color: "#e8edf5" }}>
            Limit = min(10% × min(income, net worth), $124,000)
          </div>
        </div>
        <div className="rounded p-3" style={{ background: "#060a13", border: "1px solid #1e2d4a" }}>
          <div className="font-mono text-xs font-bold mb-1" style={{ color: "#00d4aa" }}>Key Notes</div>
          <ul className="flex flex-col gap-1">
            <li>• The limit applies across ALL Reg CF platforms (Wefunder, Republic, etc.) combined.</li>
            <li>• Annual limit resets each 12-month period from your first Reg CF investment.</li>
            <li>• Accredited investors have no Reg CF investment limit.</li>
            <li>• Net worth excludes primary residence value (SEC Rule).</li>
            <li>• Source: 17 CFR 227.100(a)(2) as amended by JOBS Act 3.0 rules effective 2021.</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
