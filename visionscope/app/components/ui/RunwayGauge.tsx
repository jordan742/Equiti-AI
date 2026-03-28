import { fmtMonths } from "@/lib/formatting";

interface RunwayGaugeProps {
  months: number;
  size?: number;
}

export default function RunwayGauge({ months, size = 120 }: RunwayGaugeProps) {
  const maxMonths = 24;
  const pct = Math.min(months / maxMonths, 1);
  const color = months > 12 ? "#00d4aa" : months > 6 ? "#ffb830" : "#ff4757";

  const cx = size / 2, cy = size * 0.62;
  const r = size * 0.38;
  const startAngle = Math.PI;
  const endAngle = 2 * Math.PI;
  const sweepAngle = endAngle - startAngle;

  const arcStart = { x: cx + r * Math.cos(startAngle), y: cy + r * Math.sin(startAngle) };
  const arcEnd   = { x: cx + r * Math.cos(endAngle),   y: cy + r * Math.sin(endAngle) };
  const fillEnd  = {
    x: cx + r * Math.cos(startAngle + sweepAngle * pct),
    y: cy + r * Math.sin(startAngle + sweepAngle * pct),
  };

  const bgPath = `M ${arcStart.x} ${arcStart.y} A ${r} ${r} 0 0 1 ${arcEnd.x} ${arcEnd.y}`;
  const fillPath = pct > 0
    ? `M ${arcStart.x} ${arcStart.y} A ${r} ${r} 0 ${pct > 0.5 ? 1 : 0} 1 ${fillEnd.x} ${fillEnd.y}`
    : "";

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size * 0.65}>
        <path d={bgPath} fill="none" stroke="#1e2d4a" strokeWidth={8} strokeLinecap="round" />
        {fillPath && (
          <path d={fillPath} fill="none" stroke={color} strokeWidth={8} strokeLinecap="round"
            style={{ filter: `drop-shadow(0 0 6px ${color}88)` }} />
        )}
        <text x={cx} y={cy - r * 0.1} textAnchor="middle" dominantBaseline="middle"
          fill={color} fontSize={size * 0.16} fontFamily="JetBrains Mono,monospace" fontWeight="700">
          {fmtMonths(months)}
        </text>
        <text x={cx} y={cy + r * 0.25} textAnchor="middle" dominantBaseline="middle"
          fill="#8899bb" fontSize={size * 0.08} fontFamily="JetBrains Mono,monospace">
          RUNWAY
        </text>
      </svg>
    </div>
  );
}
