"use client";
import { AreaChart, Area, ResponsiveContainer, Tooltip } from "recharts";
import { fmtCurrency } from "@/lib/formatting";

interface SparkChartProps {
  data: number[];
  color?: string;
  height?: number;
  prefix?: string;
}

export default function SparkChart({ data, color = "#2e6cf6", height = 48, prefix = "$" }: SparkChartProps) {
  const chartData = data.map((v, i) => ({ i, v }));
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={chartData} margin={{ top: 2, right: 0, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id={`sg-${color.replace("#","")}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.3} />
            <stop offset="100%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <Area
          type="monotone" dataKey="v"
          stroke={color} strokeWidth={1.5}
          fill={`url(#sg-${color.replace("#","")})`}
          dot={false} isAnimationActive={false}
        />
        <Tooltip
          contentStyle={{ background: "#0c1220", border: "1px solid #1e2d4a", fontSize: 11, fontFamily: "JetBrains Mono" }}
          formatter={(v: number) => [`${prefix}${v.toLocaleString()}`, ""]}
          labelFormatter={() => ""}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
