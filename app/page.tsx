"use client";
import { useState } from "react";
import { COMPANIES } from "@/lib/data";
import { score as calcScore } from "@/lib/scoring";
import CompanyCard from "@/components/CompanyCard";
import CompanyDetail from "@/components/CompanyDetail";
import Marketplace from "@/components/Marketplace";
import DisclaimerFooter from "@/components/DisclaimerFooter";
import type { Company } from "@/lib/types";

type Tab = "Screener" | "Marketplace";

const TICKER_ITEMS = [
  "ACTIVE DEALS: 220", "WEEKLY VOL: $4.9M", "NMSH $1.35 ▲8.0%",
  "CBOT $3.15 ▲12.5%", "HLNS $0.55 ▼8.3%", "SYNK $5.10 ▲21.4%",
  "TOTAL RAISED YTD: $8.4M", "INVESTORS: 11,923",
];

export default function Home() {
  const [tab, setTab] = useState<Tab>("Screener");
  const [detail, setDetail] = useState<Company | null>(null);
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<"Score" | "Runway" | "Raised" | "Growth">("Score");

  const filtered = COMPANIES
    .filter(c => !query || c.name.toLowerCase().includes(query.toLowerCase()) || c.id.toLowerCase().includes(query.toLowerCase()))
    .sort((a, b) => {
      if (sort === "Score")   return calcScore(b) - calcScore(a);
      if (sort === "Runway")  return (b.cash / b.burn) - (a.cash / a.burn);
      if (sort === "Raised")  return b.raised - a.raised;
      if (sort === "Growth")  return b.growth - a.growth;
      return 0;
    });

  return (
    <div className="min-h-screen flex flex-col" style={{ background: "#0a0e17" }}>
      {/* Header */}
      <header className="px-4 py-3 flex items-center justify-between" style={{ background: "#0f1520", borderBottom: "1px solid #1b2540" }}>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-lg flex items-center justify-center" style={{ background: "#2e6cf6" }}>
              <span className="font-mono text-xs font-bold text-white">V</span>
            </div>
            <span className="font-mono font-bold text-sm" style={{ color: "#f0f4ff" }}>VisionScope</span>
          </div>
          <span className="font-mono text-xs px-2 py-0.5 rounded" style={{ background: "#00d4aa22", color: "#00d4aa", border: "1px solid #00d4aa44" }}>
            ● LIVE
          </span>
        </div>
        <div className="font-mono text-xs px-2 py-1 rounded" style={{ background: "#ff475722", color: "#ff4757", border: "1px solid #ff475744" }}>
          NOT FINANCIAL ADVICE
        </div>
      </header>

      {/* Market ticker */}
      <div className="overflow-hidden py-1.5" style={{ background: "#060d18", borderBottom: "1px solid #1b2540" }}>
        <div className="ticker-track flex gap-8 whitespace-nowrap" style={{ width: "max-content" }}>
          {[...TICKER_ITEMS, ...TICKER_ITEMS].map((item, i) => (
            <span key={i} className="font-mono text-xs" style={{ color: "#4e5f7d" }}>
              {item}
            </span>
          ))}
        </div>
      </div>

      {/* Tab nav */}
      <nav className="px-4 flex gap-1 py-2" style={{ background: "#0f1520", borderBottom: "1px solid #1b2540" }}>
        {(["Screener", "Marketplace"] as Tab[]).map(t => (
          <button key={t} onClick={() => { setTab(t); setDetail(null); }}
            className="px-4 py-1.5 rounded-lg font-mono text-xs font-bold transition-all"
            style={{
              background: tab === t ? "#1b2540" : "transparent",
              color: tab === t ? "#f0f4ff" : "#4e5f7d",
              border: `1px solid ${tab === t ? "#2e6cf644" : "transparent"}`,
            }}>
            {t}
          </button>
        ))}
      </nav>

      {/* Main content */}
      <main className="flex-1 px-4 py-4 max-w-5xl mx-auto w-full">
        {tab === "Screener" && (
          detail ? (
            <CompanyDetail company={detail} onBack={() => setDetail(null)} />
          ) : (
            <div className="flex flex-col gap-4">
              {/* Search + sort */}
              <div className="flex gap-3 flex-wrap">
                <input
                  type="text"
                  placeholder="Search by name or ticker..."
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  className="flex-1 rounded-xl px-4 py-2.5 font-mono text-sm outline-none min-w-48"
                  style={{ background: "#0f1520", border: "1px solid #1b2540", color: "#f0f4ff" }}
                />
                <div className="flex gap-1 rounded-xl p-1" style={{ background: "#0f1520", border: "1px solid #1b2540" }}>
                  {(["Score", "Runway", "Raised", "Growth"] as const).map(s => (
                    <button key={s} onClick={() => setSort(s)}
                      className="px-3 py-1.5 rounded-lg font-mono text-xs transition-all"
                      style={{ background: sort === s ? "#1b2540" : "transparent", color: sort === s ? "#2e6cf6" : "#4e5f7d" }}>
                      {s}
                    </button>
                  ))}
                </div>
              </div>

              {/* Company cards */}
              <div className="flex flex-col gap-3">
                {filtered.map(c => (
                  <CompanyCard key={c.id} company={c} onClick={() => setDetail(c)} />
                ))}
                {filtered.length === 0 && (
                  <div className="rounded-xl p-8 text-center" style={{ background: "#0f1520", border: "1px solid #1b2540" }}>
                    <span className="font-mono text-sm" style={{ color: "#4e5f7d" }}>No deals match your search.</span>
                  </div>
                )}
              </div>
            </div>
          )
        )}

        {tab === "Marketplace" && <Marketplace />}
      </main>

      <DisclaimerFooter />
    </div>
  );
}
