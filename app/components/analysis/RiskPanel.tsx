"use client";
import type { Company } from "@/lib/types";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import SectionBox from "../ui/SectionBox";

const RISK_COLORS = ["#ff4757", "#ffb830", "#2e6cf6"];

export default function RiskPanel({ company: c }: { company: Company }) {
  const proceeds = Object.entries(c.useOfProceeds).map(([k, v]) => ({ name: k, pct: v }));

  return (
    <div className="flex flex-col gap-4">
      <SectionBox title="Risk Factors" tag={`${c.riskFactors.length} identified`}>
        <div className="flex flex-col gap-3">
          {c.riskFactors.map((rf, i) => (
            <div key={i} className="flex gap-3 p-3 rounded-lg" style={{ background: "#0c1220", border: `1px solid ${RISK_COLORS[i] || "#1e2d4a"}44` }}>
              <div className="shrink-0 w-6 h-6 rounded flex items-center justify-center font-mono text-xs font-bold"
                style={{ background: `${RISK_COLORS[i] || "#1e2d4a"}22`, color: RISK_COLORS[i] || "#8899bb" }}>
                {i + 1}
              </div>
              <p className="text-sm leading-relaxed" style={{ color: "#c8d8f0" }}>{rf}</p>
            </div>
          ))}
        </div>
      </SectionBox>

      <SectionBox title="Use of Proceeds">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            {proceeds.map(({ name, pct }, i) => (
              <div key={name} className="mb-3">
                <div className="flex justify-between mb-1">
                  <span className="font-mono text-xs" style={{ color: "#8899bb" }}>{name}</span>
                  <span className="font-mono text-xs font-bold" style={{ color: "#e8edf5" }}>{pct}%</span>
                </div>
                <div className="h-1.5 rounded-full overflow-hidden" style={{ background: "#1e2d4a" }}>
                  <div className="h-full rounded-full transition-all" style={{
                    width: `${pct}%`,
                    background: ["#2e6cf6","#00d4aa","#ffb830","#a855f7"][i % 4],
                  }} />
                </div>
              </div>
            ))}
          </div>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={proceeds} layout="vertical" margin={{ top: 0, right: 10, bottom: 0, left: 60 }}>
              <XAxis type="number" tickFormatter={(v) => `${v}%`} tick={{ fill: "#4a5a7a", fontSize: 10, fontFamily: "JetBrains Mono" }} />
              <YAxis type="category" dataKey="name" tick={{ fill: "#8899bb", fontSize: 10, fontFamily: "JetBrains Mono" }} />
              <Tooltip contentStyle={{ background: "#0c1220", border: "1px solid #1e2d4a", fontFamily: "JetBrains Mono", fontSize: 11 }}
                formatter={(v: number) => [`${v}%`, "Allocation"]} />
              <Bar dataKey="pct" radius={[0,3,3,0]}>
                {proceeds.map((_, i) => (
                  <Cell key={i} fill={["#2e6cf6","#00d4aa","#ffb830","#a855f7"][i % 4]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </SectionBox>
    </div>
  );
}
