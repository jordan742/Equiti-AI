"use client";
import type { Company } from "@/lib/types";
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { fmtCurrency } from "@/lib/formatting";
import SectionBox from "../ui/SectionBox";
import StatCard from "../ui/StatCard";

export default function RevenuePanel({ company: c }: { company: Company }) {
  const combined = c.quarterLabels.map((q, i) => ({
    q,
    Revenue: c.quarterlyRevenue[i],
    Burn: c.quarterlyBurn[i],
  }));

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <StatCard label="MRR" value={fmtCurrency(c.revenue, true)} color="#00d4aa" sub={`+${c.revenueGrowthPct}% QoQ`} />
        <StatCard label="Gross Margin" value={`${c.grossMarginPct}%`} color="#2e6cf6" />
        <StatCard label="Monthly Burn" value={fmtCurrency(c.monthlyBurn, true)} color="#ff4757" />
        <StatCard label="Coverage" value={`${((c.revenue / c.monthlyBurn) * 100).toFixed(0)}%`}
          color={c.revenue >= c.monthlyBurn ? "#00d4aa" : "#ffb830"} sub="MRR / Burn" />
      </div>

      <SectionBox title="Revenue vs Burn" tag="Quarterly">
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={combined} margin={{ top: 5, right: 10, bottom: 0, left: 10 }}>
            <XAxis dataKey="q" tick={{ fill: "#4a5a7a", fontSize: 10, fontFamily: "JetBrains Mono" }} />
            <YAxis tickFormatter={(v) => fmtCurrency(v, true)} tick={{ fill: "#4a5a7a", fontSize: 10, fontFamily: "JetBrains Mono" }} />
            <Tooltip contentStyle={{ background: "#0c1220", border: "1px solid #1e2d4a", fontFamily: "JetBrains Mono", fontSize: 11 }}
              formatter={(v: number) => [fmtCurrency(v), ""]} />
            <Legend wrapperStyle={{ fontSize: 11, fontFamily: "JetBrains Mono", color: "#8899bb" }} />
            <Bar dataKey="Revenue" fill="#00d4aa" opacity={0.85} radius={[3,3,0,0]} />
            <Bar dataKey="Burn" fill="#ff4757" opacity={0.65} radius={[3,3,0,0]} />
          </BarChart>
        </ResponsiveContainer>
      </SectionBox>

      <SectionBox title="Revenue Trend" tag="MRR Trajectory">
        <ResponsiveContainer width="100%" height={160}>
          <AreaChart data={c.quarterLabels.map((q,i) => ({ q, rev: c.quarterlyRevenue[i] }))}
            margin={{ top: 5, right: 10, bottom: 0, left: 10 }}>
            <defs>
              <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#00d4aa" stopOpacity={0.35} />
                <stop offset="100%" stopColor="#00d4aa" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="q" tick={{ fill: "#4a5a7a", fontSize: 10, fontFamily: "JetBrains Mono" }} />
            <YAxis tickFormatter={(v) => fmtCurrency(v, true)} tick={{ fill: "#4a5a7a", fontSize: 10, fontFamily: "JetBrains Mono" }} />
            <Tooltip contentStyle={{ background: "#0c1220", border: "1px solid #1e2d4a", fontFamily: "JetBrains Mono", fontSize: 11 }}
              formatter={(v: number) => [fmtCurrency(v), "Revenue"]} />
            <Area type="monotone" dataKey="rev" stroke="#00d4aa" fill="url(#revGrad)" strokeWidth={2} dot={{ fill: "#00d4aa", r: 3 }} />
          </AreaChart>
        </ResponsiveContainer>
      </SectionBox>
    </div>
  );
}
