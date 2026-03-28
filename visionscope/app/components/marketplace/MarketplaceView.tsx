"use client";
import { useState } from "react";
import type { Company } from "@/lib/types";
import { companies } from "@/lib/companies";
import { fmtCurrency } from "@/lib/formatting";
import { calculateScore, getScoreColor } from "@/lib/scoring";
import LegalBanner from "./LegalBanner";
import OrderBook from "./OrderBook";
import OrderForm from "./OrderForm";

export default function MarketplaceView() {
  const [selected, setSelected] = useState<Company>(companies[0]);

  return (
    <div className="flex flex-col gap-4">
      <LegalBanner />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left: ticker list */}
        <div className="flex flex-col gap-2">
          <div className="font-mono text-xs font-bold uppercase tracking-wider px-1" style={{ color: "#4a5a7a" }}>
            Listed Securities
          </div>
          {companies.map((c) => {
            const score = calculateScore(c);
            const change = ((c.market.askPrice - c.pricePerShare) / c.pricePerShare) * 100;
            const isUp = change >= 0;
            return (
              <button key={c.id} onClick={() => setSelected(c)}
                className="rounded-lg p-3 text-left transition-all"
                style={{
                  background: selected.id === c.id ? "#1e2d4a" : "#0f1929",
                  border: `1px solid ${selected.id === c.id ? "#2e6cf6" : "#1e2d4a"}`,
                }}>
                <div className="flex justify-between items-center">
                  <div>
                    <span className="font-mono text-xs font-bold" style={{ color: "#2e6cf6" }}>{c.id}</span>
                    <span className="font-mono text-xs ml-2" style={{ color: "#8899bb" }}>{c.name.split(" ")[0]}</span>
                  </div>
                  <div className="text-right">
                    <div className="font-mono text-xs font-bold" style={{ color: "#e8edf5" }}>
                      {fmtCurrency(c.market.askPrice)}
                    </div>
                    <div className="font-mono text-xs" style={{ color: isUp ? "#00d4aa" : "#ff4757" }}>
                      {isUp ? "+" : ""}{change.toFixed(1)}%
                    </div>
                  </div>
                </div>
                <div className="flex gap-1 mt-1.5">
                  <div className="h-1 rounded-full flex-1" style={{ background: getScoreColor(score), opacity: 0.6 }} />
                  <span className="font-mono text-xs" style={{ color: "#4a5a7a" }}>Score: {score}</span>
                </div>
              </button>
            );
          })}
        </div>

        {/* Right: order book + form */}
        <div className="lg:col-span-2 flex flex-col gap-4">
          {/* Ticker header */}
          <div className="rounded-lg p-4 flex items-center gap-4" style={{ background: "#0f1929", border: "1px solid #1e2d4a" }}>
            <div>
              <div className="font-mono font-bold text-lg" style={{ color: "#2e6cf6" }}>{selected.id}</div>
              <div className="font-mono text-xs" style={{ color: "#8899bb" }}>{selected.name}</div>
            </div>
            <div className="flex gap-6 ml-4">
              <div>
                <div className="font-mono text-xs" style={{ color: "#4a5a7a" }}>Ask</div>
                <div className="font-mono font-bold" style={{ color: "#ff4757" }}>{fmtCurrency(selected.market.askPrice)}</div>
              </div>
              <div>
                <div className="font-mono text-xs" style={{ color: "#4a5a7a" }}>Bid</div>
                <div className="font-mono font-bold" style={{ color: "#00d4aa" }}>{fmtCurrency(selected.market.bidPrice)}</div>
              </div>
              <div>
                <div className="font-mono text-xs" style={{ color: "#4a5a7a" }}>24h Vol</div>
                <div className="font-mono font-bold" style={{ color: "#e8edf5" }}>{fmtCurrency(selected.market.volume24h, true)}</div>
              </div>
              <div>
                <div className="font-mono text-xs" style={{ color: "#4a5a7a" }}>Status</div>
                <div className="font-mono font-bold text-xs" style={{ color: selected.status === "Live" ? "#00d4aa" : "#4a5a7a" }}>
                  {selected.status}
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <OrderBook company={selected} />
            <OrderForm company={selected} />
          </div>
        </div>
      </div>
    </div>
  );
}
