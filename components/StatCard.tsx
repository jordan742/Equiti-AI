export default function StatCard({ label, value, sub, color }: {
  label: string; value: string; sub?: string; color?: string;
}) {
  return (
    <div className="rounded-lg px-3 py-2" style={{ background: "#131a28", border: "1px solid #1b2540" }}>
      <div className="font-mono text-xs mb-0.5" style={{ color: "#8594b0" }}>{label}</div>
      <div className="font-mono font-bold text-sm" style={{ color: color || "#f0f4ff" }}>{value}</div>
      {sub && <div className="font-mono text-xs mt-0.5" style={{ color: "#4e5f7d" }}>{sub}</div>}
    </div>
  );
}
