import type { Company } from "@/lib/types";
import Gauge from "./Gauge";
import RevenueChart from "./RevenueChart";
import SectionBox from "./SectionBox";

const CONV_COLOR = { HIGH: "#00d4aa", MODERATE: "#ffb830", LOW: "#ff4757" };

export default function AIPanel({ company: c }: { company: Company }) {
  const convColor = CONV_COLOR[c.ai.conviction];
  const runway = c.cash / c.burn;

  return (
    <div className="flex flex-col gap-4">
      {/* Verdict banner */}
      <div className="rounded-xl p-4" style={{ background: "#0f1520", border: "1px solid #1b2540" }}>
        <div className="flex items-center justify-between flex-wrap gap-2 mb-3">
          <div>
            <span className="font-mono text-xs" style={{ color: "#8594b0" }}>AI VERDICT — </span>
            <span className="font-semibold text-base" style={{ color: "#f0f4ff", fontFamily: "'Instrument Serif', serif" }}>
              {c.ai.verdict}
            </span>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5">
              <span className="font-mono text-xs" style={{ color: "#8594b0" }}>CONVICTION</span>
              <span className="font-mono text-xs font-bold px-2 py-0.5 rounded"
                style={{ background: `${convColor}22`, color: convColor, border: `1px solid ${convColor}44` }}>
                {c.ai.conviction}
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="font-mono text-xs" style={{ color: "#8594b0" }}>RISK</span>
              <div className="flex gap-0.5">
                {[1,2,3,4,5].map(i => (
                  <div key={i} className="w-2.5 h-2.5 rounded-sm"
                    style={{ background: i <= c.ai.risk ? "#ff4757" : "#1b2540" }} />
                ))}
              </div>
            </div>
          </div>
        </div>
        <p className="text-sm leading-relaxed" style={{ color: "#c4cde0" }}>{c.ai.summary}</p>
      </div>

      {/* Plain English */}
      <div className="rounded-xl p-4" style={{ background: "#06b6d411", border: "1px solid #06b6d422" }}>
        <div className="font-mono text-xs font-bold mb-2 flex items-center gap-2" style={{ color: "#06b6d4" }}>
          <span>ℹ</span> IN PLAIN ENGLISH
        </div>
        <p className="text-sm leading-relaxed" style={{ color: "#c4cde0" }}>{c.ai.plainEnglish}</p>
      </div>

      {/* Bull / Bear */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="rounded-xl p-4" style={{ background: "#00d4aa0d", border: "1px solid #00d4aa22" }}>
          <div className="font-mono text-xs font-bold mb-2" style={{ color: "#00d4aa" }}>▲ BULL CASE</div>
          <p className="text-sm leading-relaxed" style={{ color: "#c4cde0" }}>{c.ai.bull}</p>
        </div>
        <div className="rounded-xl p-4" style={{ background: "#ff47570d", border: "1px solid #ff475722" }}>
          <div className="font-mono text-xs font-bold mb-2" style={{ color: "#ff4757" }}>▼ BEAR CASE</div>
          <p className="text-sm leading-relaxed" style={{ color: "#c4cde0" }}>{c.ai.bear}</p>
        </div>
      </div>

      {/* Revenue vs Burn chart */}
      <SectionBox title="Revenue vs Burn" tag="Quarterly">
        <RevenueChart company={c} />
      </SectionBox>

      {/* Cash runway gauge */}
      <div className="rounded-xl p-4 flex items-center gap-6" style={{ background: "#0f1520", border: "1px solid #1b2540" }}>
        <Gauge value={runway} max={24} label="mo runway" />
        <div>
          <div className="font-mono text-xs mb-1" style={{ color: "#8594b0" }}>CASH RUNWAY</div>
          <div className="font-mono text-lg font-bold" style={{ color: runway > 12 ? "#00d4aa" : runway > 6 ? "#ffb830" : "#ff4757" }}>
            {runway.toFixed(1)} months
          </div>
          <div className="font-mono text-xs mt-1" style={{ color: "#4e5f7d" }}>
            ${(c.cash / 1000).toFixed(0)}K cash · ${(c.burn / 1000).toFixed(0)}K/mo burn
          </div>
        </div>
      </div>
    </div>
  );
}
