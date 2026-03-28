"use client";
import type { Company } from "@/lib/types";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";
import { fmtCurrency, fmtMonths } from "@/lib/formatting";
import { getRunwayMonths } from "@/lib/scoring";
import RunwayGauge from "../ui/RunwayGauge";
import SectionBox from "../ui/SectionBox";
import StatCard from "../ui/StatCard";

export default function RunwayPanel({ company: c }: { company: Company }) {
  const runway = getRunwayMonths(c);

  // Build 18-month projection
  const months = Array.from({ length: 19 }, (_, i) => ({
    month: i === 0 ? "Now" : `+${i}mo`,
    cash: Math.max(0, c.cashOnHand - c.monthlyBurn * i),
  }));

  const color = runway > 12 ? "#00d4aa" : runway > 6 ? "#ffb830" : "#ff4757";

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <StatCard label="Cash on Hand" value={fmtCurrency(c.cashOnHand, true)} color={color} />
        <StatCard label="Monthly Burn" value={fmtCurrency(c.monthlyBurn, true)} color="#ff4757" />
        <StatCard label="MRR" value={fmtCurrency(c.revenue, true)} color="#00d4aa" />
        <StatCard label="Net Burn" value={fmtCurrency(c.monthlyBurn - c.revenue, true)} color="#ffb830" />
      </div>

      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex justify-center items-center py-4">
          <RunwayGauge months={runway} size={140} />
        </div>
        <SectionBox title="18-Month Cash Projection" className="flex-1">
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={months} margin={{ top: 5, right: 10, bottom: 0, left: 10 }}>
              <defs>
                <linearGradient id="cashGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={color} stopOpacity={0.3} />
                  <stop offset="100%" stopColor={color} stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="month" tick={{ fill: "#4a5a7a", fontSize: 10, fontFamily: "JetBrains Mono" }} />
              <YAxis tickFormatter={(v) => fmtCurrency(v, true)} tick={{ fill: "#4a5a7a", fontSize: 10, fontFamily: "JetBrains Mono" }} />
              <Tooltip
                contentStyle={{ background: "#0c1220", border: "1px solid #1e2d4a", fontFamily: "JetBrains Mono", fontSize: 11 }}
                formatter={(v: number) => [fmtCurrency(v), "Cash"]}
              />
              <ReferenceLine y={0} stroke="#ff4757" strokeDasharray="4 2" />
              <Area type="monotone" dataKey="cash" stroke={color} fill="url(#cashGrad)" strokeWidth={2} dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </SectionBox>
      </div>

      {/* Quarterly cash history */}
      <SectionBox title="Quarterly Cash History">
        <ResponsiveContainer width="100%" height={160}>
          <AreaChart data={c.quarterLabels.map((q, i) => ({ q, cash: c.quarterlyCash[i] }))}
            margin={{ top: 5, right: 10, bottom: 0, left: 10 }}>
            <defs>
              <linearGradient id="histGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#2e6cf6" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#2e6cf6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="q" tick={{ fill: "#4a5a7a", fontSize: 10, fontFamily: "JetBrains Mono" }} />
            <YAxis tickFormatter={(v) => fmtCurrency(v, true)} tick={{ fill: "#4a5a7a", fontSize: 10, fontFamily: "JetBrains Mono" }} />
            <Tooltip contentStyle={{ background: "#0c1220", border: "1px solid #1e2d4a", fontFamily: "JetBrains Mono", fontSize: 11 }}
              formatter={(v: number) => [fmtCurrency(v), "Cash"]} />
            <Area type="monotone" dataKey="cash" stroke="#2e6cf6" fill="url(#histGrad)" strokeWidth={2} dot={false} />
          </AreaChart>
        </ResponsiveContainer>
      </SectionBox>
    </div>
  );
}
