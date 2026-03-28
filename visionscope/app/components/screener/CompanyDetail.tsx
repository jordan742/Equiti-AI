"use client";
import { useState } from "react";
import type { Company } from "@/lib/types";
import { calculateScore, getScoreLabel, getScoreColor } from "@/lib/scoring";
import { fmtCurrency, fmtMonths } from "@/lib/formatting";
import ScoreRing from "../ui/ScoreRing";
import Pill from "../ui/Pill";
import AIAnalysisPanel from "../analysis/AIAnalysisPanel";
import RunwayPanel from "../analysis/RunwayPanel";
import RevenuePanel from "../analysis/RevenuePanel";
import RiskPanel from "../analysis/RiskPanel";
import XBRLPanel from "../financials/XBRLPanel";
import BalanceSheet from "../financials/BalanceSheet";
import KeyRatios from "../financials/KeyRatios";

type SubTab = "ai" | "financials" | "risks";

export default function CompanyDetail({ company: c, onBack }: { company: Company; onBack: () => void }) {
  const [subTab, setSubTab] = useState<SubTab>("ai");
  const score = calculateScore(c);
  const runway = c.cashOnHand / c.monthlyBurn;

  return (
    <div className="flex flex-col gap-4">
      {/* Back + header */}
      <div className="flex items-center gap-3">
        <button onClick={onBack}
          className="font-mono text-xs px-3 py-1.5 rounded transition-all"
          style={{ background: "#0f1929", border: "1px solid #1e2d4a", color: "#8899bb" }}>
          ← Back
        </button>
        <span className="font-mono text-xs" style={{ color: "#4a5a7a" }}>Screener / Detail</span>
      </div>

      {/* Company header card */}
      <div className="rounded-lg p-5" style={{ background: "#0f1929", border: "1px solid #1e2d4a" }}>
        <div className="flex items-start gap-5">
          <ScoreRing score={score} size={80} showLabel={true} />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <span className="font-mono font-bold text-base" style={{ color: "#2e6cf6" }}>{c.id}</span>
              <span className="font-semibold text-lg" style={{ color: "#e8edf5" }}>{c.name}</span>
              <Pill label={c.status} variant={c.status === "Live" ? "live" : "closed"} />
              <Pill label={c.stage} variant="blue" />
              <Pill label={c.platform} variant="moderate" />
            </div>
            <p className="text-sm mb-3" style={{ color: "#8899bb" }}>{c.sector} · {c.description}</p>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {[
                { label: "Raised", value: fmtCurrency(c.raised, true) },
                { label: "Goal", value: fmtCurrency(c.target, true) },
                { label: "Valuation Cap", value: fmtCurrency(c.valuationCap, true) },
                { label: "Price/Share", value: `$${c.pricePerShare.toFixed(2)}` },
                { label: "Runway", value: fmtMonths(runway), color: runway < 6 ? "#ff4757" : runway < 12 ? "#ffb830" : "#00d4aa" },
                { label: "MRR", value: fmtCurrency(c.revenue, true) },
                { label: "Monthly Burn", value: fmtCurrency(c.monthlyBurn, true) },
                { label: "Investors", value: c.investors.toLocaleString() },
              ].map((m) => (
                <div key={m.label} className="rounded px-2 py-1.5" style={{ background: "#060a13", border: "1px solid #1e2d4a" }}>
                  <div className="font-mono text-xs" style={{ color: "#8899bb" }}>{m.label}</div>
                  <div className="font-mono font-bold text-sm" style={{ color: m.color || "#e8edf5" }}>{m.value}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-4">
          <div className="flex justify-between mb-1">
            <span className="font-mono text-xs" style={{ color: "#8899bb" }}>Funding Progress</span>
            <span className="font-mono text-xs font-bold" style={{ color: "#2e6cf6" }}>
              {((c.raised / c.target) * 100).toFixed(0)}%
            </span>
          </div>
          <div className="h-2 rounded-full overflow-hidden" style={{ background: "#1e2d4a" }}>
            <div className="h-full rounded-full transition-all"
              style={{ width: `${Math.min((c.raised / c.target) * 100, 100)}%`, background: "#2e6cf6" }} />
          </div>
          <div className="flex justify-between mt-1">
            <span className="font-mono text-xs" style={{ color: "#4a5a7a" }}>{fmtCurrency(c.raised)} raised</span>
            <span className="font-mono text-xs" style={{ color: "#4a5a7a" }}>Goal: {fmtCurrency(c.target)}</span>
          </div>
        </div>
      </div>

      {/* Sub-tabs */}
      <div className="flex gap-1 rounded-lg p-1" style={{ background: "#0f1929", border: "1px solid #1e2d4a" }}>
        {([
          { key: "ai", label: "AI Analysis" },
          { key: "financials", label: "Financials" },
          { key: "risks", label: "Risks & Use of Proceeds" },
        ] as { key: SubTab; label: string }[]).map(({ key, label }) => (
          <button key={key} onClick={() => setSubTab(key)}
            className="flex-1 py-2 font-mono text-xs rounded transition-all"
            style={{
              background: subTab === key ? "#1e2d4a" : "transparent",
              color: subTab === key ? "#2e6cf6" : "#4a5a7a",
            }}>
            {label}
          </button>
        ))}
      </div>

      {/* Sub-tab content */}
      {subTab === "ai" && (
        <div className="flex flex-col gap-4">
          <AIAnalysisPanel company={c} />
          <RunwayPanel company={c} />
          <RevenuePanel company={c} />
        </div>
      )}
      {subTab === "financials" && (
        <div className="flex flex-col gap-4">
          <KeyRatios company={c} />
          <BalanceSheet company={c} />
          <XBRLPanel company={c} />
        </div>
      )}
      {subTab === "risks" && <RiskPanel company={c} />}
    </div>
  );
}
