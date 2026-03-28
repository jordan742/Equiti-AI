"use client";
import { useState } from "react";
import { COMPANIES } from "@/lib/data";
import { score as calcScore, scoreColor } from "@/lib/scoring";
import { fm } from "@/lib/format";
import ScoreRing from "./ScoreRing";
import Pill from "./Pill";

export default function Marketplace() {
  const [selected, setSelected] = useState<string | null>(null);
  const [side, setSide] = useState<"buy" | "sell">("buy");
  const [sharesInput, setSharesInput] = useState("");

  const selectedCompany = COMPANIES.find(c => c.id === selected);
  const shares = parseFloat(sharesInput) || 0;
  const price = selectedCompany ? (side === "buy" ? selectedCompany.market.ask : selectedCompany.market.bid) : 0;
  const total = shares * price;

  return (
    <div className="flex flex-col gap-4">
      <div className="rounded-xl p-4" style={{ background: "#2a090966", border: "2px solid #ff475766" }}>
        <div className="font-mono text-xs font-bold mb-2" style={{ color: "#ff4757" }}>⚠ CONCEPT DEMO ONLY — NOT A REAL MARKET</div>
        <p className="text-xs leading-relaxed" style={{ color: "#f0c8c8" }}>
          Real secondary market for Reg CF securities requires SEC ATS registration and FINRA broker-dealer membership.
          The 12-month Reg CF lock-up restriction applies. No real trades execute here.
        </p>
      </div>

      <div className="rounded-xl overflow-hidden" style={{ background: "#0f1520", border: "1px solid #1b2540" }}>
        <div className="px-4 py-3" style={{ background: "#0a0e17", borderBottom: "1px solid #1b2540" }}>
          <span className="font-mono text-xs font-bold uppercase tracking-wider" style={{ color: "#c4cde0" }}>Secondary Order Book</span>
        </div>
        <div className="grid px-4 py-2 font-mono text-xs" style={{ gridTemplateColumns: "2fr 1fr 1fr 1fr 1fr 1fr 1fr", background: "#131a28", borderBottom: "1px solid #1b2540", color: "#4e5f7d" }}>
          <div>Company</div>
          <div className="text-center">Score</div>
          <div className="text-right" style={{ color: "#00d4aa" }}>Bid</div>
          <div className="text-right" style={{ color: "#ff4757" }}>Ask</div>
          <div className="text-right">Spread</div>
          <div className="text-right">24h Vol</div>
          <div className="text-right">Status</div>
        </div>
        {COMPANIES.map((c, i) => {
          const s = calcScore(c);
          const spread = ((c.market.ask - c.market.bid) / c.market.bid * 100).toFixed(1);
          const isSelected = selected === c.id;
          return (
            <div key={c.id}>
              <button onClick={() => setSelected(isSelected ? null : c.id)}
                className="w-full grid px-4 py-3 items-center text-left transition-all"
                style={{ gridTemplateColumns: "2fr 1fr 1fr 1fr 1fr 1fr 1fr", background: isSelected ? "#1b254033" : i % 2 === 0 ? "#0c1220" : "#0f1520", borderBottom: "1px solid #0a0e17", borderLeft: isSelected ? "3px solid #2e6cf6" : "3px solid transparent" }}>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold" style={{ color: "#2e6cf6" }}>{c.id}</span>
                    <span className="font-mono text-xs" style={{ color: "#8594b0" }}>{c.name.split(" ")[0]}</span>
                  </div>
                  <div className="font-mono text-xs" style={{ color: "#4e5f7d", fontSize: 9 }}>{c.market.trades} trades today</div>
                </div>
                <div className="flex justify-center"><ScoreRing company={c} size={36} /></div>
                <div className="font-mono text-xs font-bold text-right" style={{ color: "#00d4aa" }}>${c.market.bid.toFixed(2)}</div>
                <div className="font-mono text-xs font-bold text-right" style={{ color: "#ff4757" }}>${c.market.ask.toFixed(2)}</div>
                <div className="font-mono text-xs text-right" style={{ color: "#8594b0" }}>{spread}%</div>
                <div className="font-mono text-xs text-right" style={{ color: "#f0f4ff" }}>{fm(c.market.vol, true)}</div>
                <div className="text-right"><Pill label={c.status === "Live" ? "Locked" : "Open"} variant={c.status === "Live" ? "amber" : "green"} small /></div>
              </button>
              {isSelected && (
                <div className="px-4 pb-4 pt-2" style={{ background: "#0a0e17", borderBottom: "1px solid #1b2540" }}>
                  <div className="rounded-xl p-4 max-w-md" style={{ background: "#0f1520", border: "1px solid #1b2540" }}>
                    <div className="font-mono text-xs font-bold mb-3" style={{ color: "#c4cde0" }}>Order Form — {c.id}</div>
                    <div className="flex gap-1 rounded-lg p-1 mb-3" style={{ background: "#131a28" }}>
                      <button onClick={() => setSide("buy")} className="flex-1 py-2 rounded font-mono text-xs font-bold transition-all"
                        style={{ background: side === "buy" ? "#052e1c" : "transparent", color: side === "buy" ? "#00d4aa" : "#4e5f7d" }}>BUY</button>
                      <button onClick={() => setSide("sell")} className="flex-1 py-2 rounded font-mono text-xs font-bold transition-all"
                        style={{ background: side === "sell" ? "#2a0909" : "transparent", color: side === "sell" ? "#ff4757" : "#4e5f7d" }}>SELL</button>
                    </div>
                    <div className="flex gap-3 mb-3">
                      <div className="flex-1">
                        <label className="font-mono text-xs block mb-1" style={{ color: "#4e5f7d" }}>Shares</label>
                        <input type="number" min="1" value={sharesInput} onChange={e => setSharesInput(e.target.value)}
                          placeholder="0" className="w-full rounded-lg px-3 py-2 font-mono text-sm outline-none"
                          style={{ background: "#131a28", border: "1px solid #1b2540", color: "#f0f4ff" }} />
                      </div>
                      <div className="flex-1">
                        <label className="font-mono text-xs block mb-1" style={{ color: "#4e5f7d" }}>Price</label>
                        <div className="rounded-lg px-3 py-2 font-mono text-sm"
                          style={{ background: "#131a28", border: "1px solid #1b2540", color: side === "buy" ? "#ff4757" : "#00d4aa" }}>
                          ${price.toFixed(2)}
                        </div>
                      </div>
                    </div>
                    {shares > 0 && (
                      <div className="rounded-lg px-3 py-2 mb-3 flex justify-between" style={{ background: "#131a28", border: "1px solid #1b2540" }}>
                        <span className="font-mono text-xs" style={{ color: "#4e5f7d" }}>Estimated Total</span>
                        <span className="font-mono text-xs font-bold" style={{ color: "#f0f4ff" }}>{fm(total)}</span>
                      </div>
                    )}
                    <button className="w-full py-2.5 rounded-xl font-mono text-xs font-bold"
                      style={{ background: c.status === "Live" ? "#2a160066" : side === "buy" ? "#052e1c" : "#2a0909", color: c.status === "Live" ? "#ffb830" : side === "buy" ? "#00d4aa" : "#ff4757", border: `1px solid ${c.status === "Live" ? "#ffb83044" : side === "buy" ? "#00d4aa44" : "#ff475744"}` }}>
                      {c.status === "Live" ? "Locked — 12mo hold required" : `Preview ${side.toUpperCase()} (concept only)`}
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
