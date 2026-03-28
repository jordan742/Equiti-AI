"use client";
import { LayoutGrid, Briefcase, ArrowLeftRight, ShieldCheck, Lock } from "lucide-react";

const ICONS: Record<string, React.ReactNode> = {
  SCREENER:    <LayoutGrid size={14} />,
  PORTFOLIO:   <Briefcase size={14} />,
  MARKETPLACE: <ArrowLeftRight size={14} />,
  COMPLIANCE:  <ShieldCheck size={14} />,
  GUARDRAIL:   <Lock size={14} />,
};

interface TabNavProps {
  tabs: string[];
  active: string;
  onChange: (t: string) => void;
}

export default function TabNav({ tabs, active, onChange }: TabNavProps) {
  return (
    <nav className="flex items-center gap-1 px-4" style={{ background: "#0c1220", borderBottom: "1px solid #1e2d4a" }}>
      {tabs.map((tab) => (
        <button
          key={tab}
          onClick={() => onChange(tab)}
          className={`flex items-center gap-1.5 px-4 py-3 font-mono text-xs font-semibold uppercase tracking-widest transition-all ${
            active === tab ? "tab-active" : "hover:text-text-primary"
          }`}
          style={{ color: active === tab ? "#e8edf5" : "#8899bb", borderBottom: active === tab ? "2px solid #2e6cf6" : "2px solid transparent" }}
        >
          {ICONS[tab]}
          {tab}
        </button>
      ))}
    </nav>
  );
}
