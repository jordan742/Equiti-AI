"use client";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import type { Company } from "@/lib/types";
import { fm } from "@/lib/format";

export default function RevenueChart({ company: c }: { company: Company }) {
  const data = c.quarterLabels.map((q, i) => ({
    q,
    Revenue: c.quarterlyRevenue[i],
    Burn: c.quarterlyBurn[i],
  }));

  return (
    <div>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={data} margin={{ top: 10, right: 10, bottom: 0, left: 10 }}>
          <defs>
            <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#00d4aa" stopOpacity={0.12} />
              <stop offset="100%" stopColor="#00d4aa" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="burnGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#ff4757" stopOpacity={0.12} />
              <stop offset="100%" stopColor="#ff4757" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid vertical={false} stroke="#1b2540" strokeDasharray="3 3" />
          <XAxis dataKey="q" tick={{ fill: "#4e5f7d", fontSize: 10, fontFamily: "JetBrains Mono" }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: "#4e5f7d", fontSize: 10, fontFamily: "JetBrains Mono" }} axisLine={false} tickLine={false}
            tickFormatter={(v) => fm(v, true)} width={52} />
          <Tooltip
            contentStyle={{ background: "#131a28", border: "1px solid #1b2540", borderRadius: 8, fontFamily: "JetBrains Mono", fontSize: 11 }}
            labelStyle={{ color: "#c4cde0" }}
            formatter={(v: number, name: string) => [fm(v), name]}
          />
          <Area type="monotone" dataKey="Revenue" stroke="#00d4aa" strokeWidth={2} fill="url(#revGrad)" dot={false} />
          <Area type="monotone" dataKey="Burn"    stroke="#ff4757" strokeWidth={2} fill="url(#burnGrad)" dot={false} />
        </AreaChart>
      </ResponsiveContainer>
      <div className="flex gap-4 mt-2 justify-center">
        {[{ color: "#00d4aa", label: "Revenue" }, { color: "#ff4757", label: "Burn" }].map(({ color, label }) => (
          <div key={label} className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full" style={{ background: color }} />
            <span className="font-mono text-xs" style={{ color: "#8594b0" }}>{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
