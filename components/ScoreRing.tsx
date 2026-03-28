import { score as calcScore, label, scoreColor } from "@/lib/scoring";
import type { Company } from "@/lib/types";

interface Props { company: Company; size?: number; }

export default function ScoreRing({ company, size = 72 }: Props) {
  const s = calcScore(company);
  const lbl = label(s);
  const color = scoreColor(s);
  const r = (size / 2) - 6;
  const circ = 2 * Math.PI * r;
  const fill = (s / 100) * circ;

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#1b2540" strokeWidth={5} />
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth={5}
          strokeDasharray={`${fill} ${circ}`} strokeLinecap="round"
          style={{ filter: `drop-shadow(0 0 6px ${color}88)` }} />
        <text x="50%" y="50%" dominantBaseline="middle" textAnchor="middle"
          style={{ transform: "rotate(90deg)", transformOrigin: "center", fill: color, fontSize: size * 0.26, fontFamily: "JetBrains Mono", fontWeight: 700 }}>
          {s}
        </text>
      </svg>
      <span className="font-mono text-xs font-bold" style={{ color, fontSize: 10 }}>{lbl}</span>
    </div>
  );
}
