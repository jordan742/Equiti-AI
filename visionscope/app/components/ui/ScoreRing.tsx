import { getScoreColor, getScoreLabel } from "@/lib/scoring";

interface ScoreRingProps {
  score: number;
  size?: number;
  showLabel?: boolean;
}

export default function ScoreRing({ score, size = 64, showLabel = true }: ScoreRingProps) {
  const r = (size / 2) - 6;
  const circ = 2 * Math.PI * r;
  const filled = (score / 100) * circ;
  const color = getScoreColor(score);
  const label = getScoreLabel(score);
  const glowClass =
    score >= 75 ? "score-ring-strong"
    : score >= 55 ? "score-ring-moderate"
    : score >= 35 ? "score-ring-caution"
    : "score-ring-risk";

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size} className={glowClass}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#1e2d4a" strokeWidth={5} />
        <circle
          cx={size/2} cy={size/2} r={r}
          fill="none"
          stroke={color}
          strokeWidth={5}
          strokeDasharray={`${filled} ${circ - filled}`}
          strokeDashoffset={circ / 4}
          strokeLinecap="round"
          style={{ transition: "stroke-dasharray 0.6s ease" }}
        />
        <text
          x={size/2} y={size/2 + 1}
          textAnchor="middle" dominantBaseline="middle"
          fill={color} fontSize={size > 56 ? 14 : 11}
          fontFamily="JetBrains Mono, monospace" fontWeight="700"
        >
          {score}
        </text>
      </svg>
      {showLabel && (
        <span className="font-mono text-xs font-semibold uppercase" style={{ color }}>
          {label}
        </span>
      )}
    </div>
  );
}
