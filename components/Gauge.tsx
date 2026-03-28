interface Props { value: number; max?: number; label?: string; color?: string; }

export default function Gauge({ value, max = 24, label = "mo runway", color }: Props) {
  const pct = Math.min(value / max, 1);
  const c = color || (value > 12 ? "#00d4aa" : value > 6 ? "#ffb830" : "#ff4757");

  // Semi-circle: from 180° to 0° (left to right)
  const W = 120, H = 65, cx = W / 2, cy = H - 8, r = 50;
  const angle = Math.PI * (1 - pct); // 180° = empty, 0° = full
  const x = cx + r * Math.cos(Math.PI - angle);
  const y = cy - r * Math.sin(Math.PI - angle);

  const arc = (start: number, end: number) => {
    const s = { x: cx + r * Math.cos(start), y: cy - r * Math.sin(start) };
    const e = { x: cx + r * Math.cos(end),   y: cy - r * Math.sin(end) };
    const large = end - start > Math.PI ? 1 : 0;
    return `M ${s.x} ${s.y} A ${r} ${r} 0 ${large} 0 ${e.x} ${e.y}`;
  };

  return (
    <div className="flex flex-col items-center">
      <svg width={W} height={H}>
        <path d={arc(0, Math.PI)} fill="none" stroke="#1b2540" strokeWidth={7} strokeLinecap="round" />
        {pct > 0 && (
          <path d={arc(Math.PI - Math.PI * pct, Math.PI)} fill="none" stroke={c} strokeWidth={7} strokeLinecap="round"
            style={{ filter: `drop-shadow(0 0 4px ${c}88)` }} />
        )}
        <circle cx={x} cy={y} r={4} fill={c} />
      </svg>
      <div className="font-mono text-xs font-bold -mt-1" style={{ color: c }}>
        {value.toFixed(1)} {label}
      </div>
    </div>
  );
}
