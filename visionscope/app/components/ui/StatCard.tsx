interface StatCardProps {
  label: string;
  value: string;
  sub?: string;
  color?: string;
  icon?: React.ReactNode;
}

export default function StatCard({ label, value, sub, color = "#e8edf5", icon }: StatCardProps) {
  return (
    <div className="rounded-lg p-4 flex flex-col gap-1" style={{ background: "#0f1929", border: "1px solid #1e2d4a" }}>
      <div className="flex items-center gap-2 text-xs text-text-secondary font-mono uppercase tracking-widest" style={{ color: "#8899bb" }}>
        {icon && <span>{icon}</span>}
        {label}
      </div>
      <div className="font-mono font-bold text-xl" style={{ color }}>
        {value}
      </div>
      {sub && <div className="text-xs font-mono" style={{ color: "#8899bb" }}>{sub}</div>}
    </div>
  );
}
