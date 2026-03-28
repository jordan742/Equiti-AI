export default function TopBar() {
  const now = new Date().toLocaleDateString("en-US", { weekday:"short", month:"short", day:"numeric", year:"numeric" });
  return (
    <header className="flex items-center justify-between px-5 py-3 shrink-0"
      style={{ background: "#0c1220", borderBottom: "1px solid #1e2d4a" }}>
      <div className="flex items-center gap-3">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <rect x="2" y="14" width="4" height="8" rx="1" fill="#2e6cf6"/>
          <rect x="8" y="9"  width="4" height="13" rx="1" fill="#2e6cf6" opacity="0.8"/>
          <rect x="14" y="5" width="4" height="17" rx="1" fill="#00d4aa"/>
          <rect x="20" y="2" width="4" height="20" rx="1" fill="#00d4aa" opacity="0.7"/>
        </svg>
        <span className="font-bold text-lg tracking-tight" style={{ color: "#e8edf5", fontFamily: "Inter, sans-serif" }}>
          Vision<span style={{ color: "#2e6cf6" }}>Scope</span>
        </span>
        <span className="font-mono text-xs px-2 py-0.5 rounded ml-1"
          style={{ background: "rgba(46,108,246,0.12)", color: "#2e6cf6", border: "1px solid rgba(46,108,246,0.25)" }}>
          v1.0
        </span>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <span className="pulse w-2 h-2 rounded-full inline-block" style={{ background: "#00d4aa" }} />
          <span className="font-mono text-xs font-semibold" style={{ color: "#00d4aa" }}>LIVE</span>
        </div>
        <span className="font-mono text-xs" style={{ color: "#8899bb" }}>{now}</span>
        <span className="font-mono text-xs px-2 py-1 rounded"
          style={{ background: "rgba(255,71,87,0.1)", color: "#ff4757", border: "1px solid rgba(255,71,87,0.25)" }}>
          NOT A FINANCIAL ADVISOR
        </span>
      </div>
    </header>
  );
}
