"use client";
import { useState } from "react";
import type { Company } from "@/lib/types";
import { fm, months } from "@/lib/format";
import { score as calcScore, scoreColor } from "@/lib/scoring";
import ScoreRing from "./ScoreRing";
import Pill from "./Pill";
import SectionBox from "./SectionBox";
import AIPanel from "./AIPanel";

type Tab = "AI Analysis" | "Financials" | "Risks" | "Invest";
const TABS: Tab[] = ["AI Analysis", "Financials", "Risks", "Invest"];

function RisksTab({ c }: { c: Company }) {
  return (
    <div className="flex flex-col gap-4">
      <SectionBox title="Risk Factors">
        <div className="flex flex-col gap-2">
          {c.risks.map((r, i) => (
            <div key={i} className="flex gap-3 rounded-lg p-3"
              style={{ background: "#131a28", borderLeft: `3px solid ${i === 0 ? "#ff4757" : "#ffb830"}` }}>
              <span className="font-mono text-xs font-bold shrink-0" style={{ color: i === 0 ? "#ff4757" : "#ffb830" }}>
                {i + 1}
              </span>
              <span className="text-sm" style={{ color: "#c4cde0" }}>{r}</span>
            </div>
          ))}
        </div>
      </SectionBox>

      <SectionBox title="Use of Proceeds">
        <div className="flex flex-col gap-2">
          {Object.entries(c.useOfProceeds).map(([k, v]) => (
            <div key={k}>
              <div className="flex justify-between mb-1">
                <span className="font-mono text-xs" style={{ color: "#8594b0" }}>{k}</span>
                <span className="font-mono text-xs font-bold" style={{ color: "#2e6cf6" }}>{v}%</span>
              </div>
              <div className="h-2 rounded-full overflow-hidden" style={{ background: "#1b2540" }}>
                <div className="h-full rounded-full" style={{ width: `${v}%`, background: "#2e6cf6" }} />
              </div>
            </div>
          ))}
        </div>
      </SectionBox>
    </div>
  );
}

function FinancialsTab({ c }: { c: Company }) {
  const runway = c.cash / c.burn;
  const burnMultiple = c.burn / (c.revenue || 1);
  const grossMargin = c.margin;
  const debtRatio = c.xbrl.assets > 0 ? (c.debt / c.xbrl.assets) * 100 : 0;
  const coverage = (c.revenue / c.burn) * 100;
  const cr = c.xbrl.liabilities > 0 ? c.xbrl.assets / c.xbrl.liabilities : 10;

  const ratios = [
    { label: "Cash Runway",       value: `${runway.toFixed(1)} mo`,  color: runway > 12 ? "#00d4aa" : runway > 6 ? "#ffb830" : "#ff4757", tip: "Months of cash remaining at current burn rate." },
    { label: "Current Ratio",     value: cr.toFixed(2) + "x",        color: cr >= 2 ? "#00d4aa" : cr >= 1 ? "#ffb830" : "#ff4757", tip: "Assets ÷ Liabilities. >2 is healthy." },
    { label: "Burn Multiple",     value: burnMultiple.toFixed(1) + "x", color: burnMultiple <= 1.5 ? "#00d4aa" : burnMultiple <= 3 ? "#ffb830" : "#ff4757", tip: "Monthly Burn ÷ MRR. <1.5x is excellent." },
    { label: "Revenue Coverage",  value: coverage.toFixed(0) + "%",  color: coverage >= 100 ? "#00d4aa" : coverage >= 50 ? "#ffb830" : "#ff4757", tip: "MRR ÷ Burn. 100% = break-even." },
    { label: "Gross Margin",      value: grossMargin + "%",           color: grossMargin >= 60 ? "#00d4aa" : grossMargin >= 40 ? "#ffb830" : "#ff4757", tip: "Gross profit as % of revenue." },
    { label: "Debt / Assets",     value: debtRatio.toFixed(1) + "%", color: debtRatio <= 30 ? "#00d4aa" : debtRatio <= 60 ? "#ffb830" : "#ff4757", tip: "Lower is better for early-stage." },
  ];

  return (
    <div className="flex flex-col gap-4">
      <SectionBox title="Key Ratios">
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {ratios.map((r) => (
            <div key={r.label} className="rounded-lg p-3" style={{ background: "#131a28", border: `1px solid ${r.color}33` }}>
              <div className="font-mono text-xs mb-1" style={{ color: "#4e5f7d" }}>{r.label}</div>
              <div className="font-mono font-bold text-xl" style={{ color: r.color }}>{r.value}</div>
              <div className="text-xs mt-1 leading-relaxed" style={{ color: "#4e5f7d" }}>{r.tip}</div>
            </div>
          ))}
        </div>
      </SectionBox>

      <SectionBox title="XBRL Balance Sheet" tag={`XBRL • Form C`}>
        <div className="flex flex-col gap-1">
          {[
            { label: "Total Assets",       value: c.xbrl.assets,       bold: true,  color: "#2e6cf6" },
            { label: "Current Assets",     value: c.cash,               indent: true },
            { label: "Total Liabilities",  value: c.xbrl.liabilities,  bold: true,  color: "#ff4757" },
            { label: "Stockholders' Equity", value: c.xbrl.equity,     bold: true,  color: c.xbrl.equity >= 0 ? "#00d4aa" : "#ff4757" },
            { label: "Revenue (TTM)",      value: c.xbrl.revenueTTM,   indent: true, color: "#00d4aa" },
            { label: "Net Income (TTM)",   value: c.xbrl.netIncome,    indent: true, color: c.xbrl.netIncome >= 0 ? "#00d4aa" : "#ff4757" },
          ].map((row) => (
            <div key={row.label} className="flex justify-between items-center py-1.5"
              style={{ borderBottom: "1px solid #1b2540", paddingLeft: row.indent ? 16 : 0 }}>
              <span className="font-mono text-xs" style={{ color: row.bold ? "#c4cde0" : "#8594b0" }}>{row.label}</span>
              <span className="font-mono text-xs font-bold" style={{ color: row.color || "#f0f4ff" }}>
                {row.value < 0 ? `-${fm(Math.abs(row.value))}` : fm(row.value)}
              </span>
            </div>
          ))}
        </div>
      </SectionBox>
    </div>
  );
}

function InvestTab({ c }: { c: Company }) {
  return (
    <SectionBox title="Investment Details">
      <div className="flex flex-col gap-4">
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-lg p-3" style={{ background: "#131a28", border: "1px solid #1b2540" }}>
            <div className="font-mono text-xs mb-1" style={{ color: "#8594b0" }}>Price Per Share</div>
            <div className="font-mono font-bold text-2xl" style={{ color: "#2e6cf6" }}>${c.pricePerShare.toFixed(2)}</div>
          </div>
          <div className="rounded-lg p-3" style={{ background: "#131a28", border: "1px solid #1b2540" }}>
            <div className="font-mono text-xs mb-1" style={{ color: "#8594b0" }}>Security Type</div>
            <div className="font-mono font-bold text-sm" style={{ color: c.security === "SAFE" ? "#2e6cf6" : "#8b5cf6" }}>{c.security}</div>
          </div>
        </div>

        <button className="w-full py-3 rounded-xl font-mono font-bold text-sm transition-all"
          style={{ background: c.status === "Live" ? "#082040" : "#131a28", color: c.status === "Live" ? "#2e6cf6" : "#4e5f7d", border: `1px solid ${c.status === "Live" ? "#2e6cf644" : "#1b2540"}` }}>
          {c.status === "Live" ? "Simulate Investment (Concept)" : "Raise Closed — Secondary Market Only"}
        </button>

        <div className="rounded-xl p-4" style={{ background: "#2a090933", border: "1px solid #ff475744" }}>
          <div className="font-mono text-xs font-bold mb-2" style={{ color: "#ff4757" }}>IMPORTANT DISCLAIMER</div>
          <p className="text-xs leading-relaxed" style={{ color: "#c4cde0" }}>
            This is an educational simulation only. VisionScope is NOT a broker-dealer, investment adviser, or SEC-registered funding portal.
            No real investment transactions occur here. Reg CF investments are illiquid for 12 months. You may lose your entire investment.
            Always invest through a licensed SEC-registered funding portal.
          </p>
        </div>
      </div>
    </SectionBox>
  );
}

export default function CompanyDetail({ company: c, onBack }: { company: Company; onBack: () => void }) {
  const [tab, setTab] = useState<Tab>("AI Analysis");
  const runway = c.cash / c.burn;
  const runwayColor = runway > 12 ? "#00d4aa" : runway > 6 ? "#ffb830" : "#ff4757";
  const fundedPct = Math.min((c.raised / c.target) * 100, 100);

  return (
    <div className="flex flex-col gap-4">
      {/* Back */}
      <button onClick={onBack} className="self-start font-mono text-xs px-3 py-1.5 rounded-lg transition-all"
        style={{ background: "#0f1520", border: "1px solid #1b2540", color: "#8594b0" }}>
        ← Back to Screener
      </button>

      {/* Header card */}
      <div className="rounded-xl p-5" style={{ background: "#0f1520", border: "1px solid #1b2540" }}>
        <div className="flex gap-5">
          <div className="shrink-0"><ScoreRing company={c} size={80} /></div>
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2 mb-1">
              <Pill label={c.id} variant="blue" />
              <Pill label={c.status} variant={c.status === "Live" ? "live" : "closed"} small />
              <Pill label={c.security} variant={c.security === "SAFE" ? "blue" : "purple"} small />
              <h2 className="font-semibold text-lg" style={{ color: "#f0f4ff", fontFamily: "'Instrument Serif', serif" }}>{c.name}</h2>
            </div>
            <div className="font-mono text-xs mb-3" style={{ color: "#4e5f7d" }}>
              {c.sector} · {c.platform} · {c.location}
            </div>

            {/* Funding bar */}
            <div className="mb-3">
              <div className="flex justify-between mb-1">
                <span className="font-mono text-xs" style={{ color: "#8594b0" }}>{fm(c.raised, true)} raised of {fm(c.target, true)}</span>
                <span className="font-mono text-xs font-bold" style={{ color: "#2e6cf6" }}>{fundedPct.toFixed(0)}% funded</span>
              </div>
              <div className="h-2 rounded-full overflow-hidden" style={{ background: "#1b2540" }}>
                <div className="h-full rounded-full" style={{ width: `${fundedPct}%`, background: "#2e6cf6" }} />
              </div>
              <div className="font-mono text-xs mt-1" style={{ color: "#4e5f7d" }}>{c.investors.toLocaleString()} investors</div>
            </div>

            {/* Quick stats */}
            <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
              {[
                { l: "Runway",   v: months(c.cash, c.burn), c: runwayColor },
                { l: "MRR",      v: fm(c.revenue, true) },
                { l: "Burn/mo",  v: fm(c.burn, true) },
                { l: "Margin",   v: c.margin + "%" },
                { l: "Debt",     v: fm(c.debt, true) },
                { l: "$/Share",  v: `$${c.pricePerShare.toFixed(2)}` },
              ].map((m) => (
                <div key={m.l} className="rounded px-2 py-1.5" style={{ background: "#131a28", border: "1px solid #1b2540" }}>
                  <div className="font-mono" style={{ color: "#4e5f7d", fontSize: 9 }}>{m.l}</div>
                  <div className="font-mono font-bold text-xs" style={{ color: m.c || "#f0f4ff" }}>{m.v}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Sub-tabs */}
      <div className="flex gap-1 rounded-xl p-1" style={{ background: "#0f1520", border: "1px solid #1b2540" }}>
        {TABS.map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className="flex-1 py-2 rounded-lg font-mono text-xs transition-all"
            style={{ background: tab === t ? "#1b2540" : "transparent", color: tab === t ? "#f0f4ff" : "#4e5f7d" }}>
            {t}
          </button>
        ))}
      </div>

      {tab === "AI Analysis" && <AIPanel company={c} />}
      {tab === "Financials"  && <FinancialsTab c={c} />}
      {tab === "Risks"       && <RisksTab c={c} />}
      {tab === "Invest"      && <InvestTab c={c} />}
    </div>
  );
}
