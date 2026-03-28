"use client";
import { useState, useMemo } from "react";
import type { Company } from "@/lib/types";
import { calculateScore, getScoreLabel, getScoreColor } from "@/lib/scoring";
import { companies } from "@/lib/companies";
import CompanyCard from "./CompanyCard";
import CompanyDetail from "./CompanyDetail";

type SortKey = "score" | "runway" | "revenue" | "raised";

const SORT_OPTIONS: { key: SortKey; label: string }[] = [
  { key: "score", label: "Score" },
  { key: "runway", label: "Runway" },
  { key: "revenue", label: "MRR" },
  { key: "raised", label: "Raised" },
];

const STAGES = ["All", "Pre-Seed", "Seed", "Series A", "Series B"];
const PLATFORMS = ["All", "Wefunder", "Republic", "StartEngine", "Mainvest"];
const STATUSES = ["All", "Live", "Closed"];

export default function ScreenerView() {
  const [selected, setSelected] = useState<Company | null>(null);
  const [query, setQuery] = useState("");
  const [sortKey, setSortKey] = useState<SortKey>("score");
  const [sortDir, setSortDir] = useState<"desc" | "asc">("desc");
  const [filterStage, setFilterStage] = useState("All");
  const [filterPlatform, setFilterPlatform] = useState("All");
  const [filterStatus, setFilterStatus] = useState("All");

  const filtered = useMemo(() => {
    return companies
      .filter((c) => {
        const q = query.toLowerCase();
        const matchQ = !q || c.name.toLowerCase().includes(q) || c.id.toLowerCase().includes(q) || c.sector.toLowerCase().includes(q);
        const matchStage = filterStage === "All" || c.stage === filterStage;
        const matchPlatform = filterPlatform === "All" || c.platform === filterPlatform;
        const matchStatus = filterStatus === "All" || c.status === filterStatus;
        return matchQ && matchStage && matchPlatform && matchStatus;
      })
      .sort((a, b) => {
        let av = 0, bv = 0;
        if (sortKey === "score") { av = calculateScore(a); bv = calculateScore(b); }
        else if (sortKey === "runway") { av = a.cashOnHand / a.monthlyBurn; bv = b.cashOnHand / b.monthlyBurn; }
        else if (sortKey === "revenue") { av = a.revenue; bv = b.revenue; }
        else if (sortKey === "raised") { av = a.raised; bv = b.raised; }
        return sortDir === "desc" ? bv - av : av - bv;
      });
  }, [query, sortKey, sortDir, filterStage, filterPlatform, filterStatus]);

  if (selected) {
    return <CompanyDetail company={selected} onBack={() => setSelected(null)} />;
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Search + controls */}
      <div className="rounded-lg p-4 flex flex-col sm:flex-row gap-3" style={{ background: "#0f1929", border: "1px solid #1e2d4a" }}>
        <input
          type="text"
          placeholder="Search by name, ticker, or sector..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1 rounded px-3 py-2 font-mono text-sm outline-none"
          style={{ background: "#060a13", border: "1px solid #1e2d4a", color: "#e8edf5" }}
        />
        <div className="flex gap-2 flex-wrap">
          {/* Sort */}
          <div className="flex gap-1 rounded" style={{ background: "#060a13", border: "1px solid #1e2d4a" }}>
            {SORT_OPTIONS.map((o) => (
              <button key={o.key}
                onClick={() => { if (sortKey === o.key) setSortDir(d => d === "desc" ? "asc" : "desc"); else { setSortKey(o.key); setSortDir("desc"); } }}
                className="px-3 py-1.5 font-mono text-xs rounded transition-all"
                style={{ background: sortKey === o.key ? "#1e2d4a" : "transparent", color: sortKey === o.key ? "#2e6cf6" : "#8899bb" }}>
                {o.label}{sortKey === o.key ? (sortDir === "desc" ? " ↓" : " ↑") : ""}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Filter pills */}
      <div className="flex gap-3 flex-wrap">
        <FilterGroup label="Stage" options={STAGES} value={filterStage} onChange={setFilterStage} />
        <FilterGroup label="Platform" options={PLATFORMS} value={filterPlatform} onChange={setFilterPlatform} />
        <FilterGroup label="Status" options={STATUSES} value={filterStatus} onChange={setFilterStatus} />
      </div>

      {/* Results header */}
      <div className="flex items-center justify-between">
        <span className="font-mono text-xs" style={{ color: "#4a5a7a" }}>
          {filtered.length} deal{filtered.length !== 1 ? "s" : ""} found
        </span>
        <span className="font-mono text-xs" style={{ color: "#4a5a7a" }}>
          Sorted by {sortKey} {sortDir === "desc" ? "↓" : "↑"}
        </span>
      </div>

      {/* Cards */}
      <div className="flex flex-col gap-3">
        {filtered.length === 0 ? (
          <div className="rounded-lg p-8 text-center" style={{ background: "#0f1929", border: "1px solid #1e2d4a" }}>
            <span className="font-mono text-sm" style={{ color: "#4a5a7a" }}>No deals match your filters.</span>
          </div>
        ) : (
          filtered.map((c) => (
            <CompanyCard key={c.id} company={c} onClick={() => setSelected(c)} />
          ))
        )}
      </div>

      {/* Disclaimer */}
      <div className="rounded p-3 text-center" style={{ background: "#0c1220", border: "1px solid #1e2d4a" }}>
        <p className="font-mono text-xs" style={{ color: "#4a5a7a" }}>
          All data is simulated for educational purposes only. Not financial advice. Past performance does not guarantee future results.
        </p>
      </div>
    </div>
  );
}

function FilterGroup({ label, options, value, onChange }: {
  label: string; options: string[]; value: string; onChange: (v: string) => void;
}) {
  return (
    <div className="flex items-center gap-1">
      <span className="font-mono text-xs mr-1" style={{ color: "#4a5a7a" }}>{label}:</span>
      {options.map((o) => (
        <button key={o} onClick={() => onChange(o)}
          className="px-2 py-1 rounded font-mono text-xs transition-all"
          style={{ background: value === o ? "#1e2d4a" : "transparent", color: value === o ? "#2e6cf6" : "#4a5a7a", border: `1px solid ${value === o ? "#2e6cf6" : "#1e2d4a"}` }}>
          {o}
        </button>
      ))}
    </div>
  );
}
