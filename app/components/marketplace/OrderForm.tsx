"use client";
import { useState } from "react";
import type { Company } from "@/lib/types";
import { fmtCurrency } from "@/lib/formatting";

export default function OrderForm({ company: c }: { company: Company }) {
  const [side, setSide] = useState<"buy" | "sell">("buy");
  const [shares, setShares] = useState("");
  const [price, setPrice] = useState(side === "buy" ? c.market.askPrice.toFixed(2) : c.market.bidPrice.toFixed(2));
  const [submitted, setSubmitted] = useState(false);

  const sharesNum = parseFloat(shares) || 0;
  const priceNum = parseFloat(price) || 0;
  const total = sharesNum * priceNum;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 3000);
  }

  return (
    <div className="rounded-lg p-4" style={{ background: "#0f1929", border: "1px solid #1e2d4a" }}>
      <div className="font-mono text-xs font-bold uppercase tracking-wider mb-3" style={{ color: "#8899bb" }}>
        Place Order — {c.id}
      </div>

      {/* Buy / Sell toggle */}
      <div className="flex gap-1 rounded mb-4 p-1" style={{ background: "#060a13" }}>
        <button onClick={() => { setSide("buy"); setPrice(c.market.askPrice.toFixed(2)); }}
          className="flex-1 py-2 rounded font-mono text-xs font-bold transition-all"
          style={{ background: side === "buy" ? "#052e1c" : "transparent", color: side === "buy" ? "#00d4aa" : "#4a5a7a", border: side === "buy" ? "1px solid #00d4aa44" : "1px solid transparent" }}>
          BUY
        </button>
        <button onClick={() => { setSide("sell"); setPrice(c.market.bidPrice.toFixed(2)); }}
          className="flex-1 py-2 rounded font-mono text-xs font-bold transition-all"
          style={{ background: side === "sell" ? "#2a0909" : "transparent", color: side === "sell" ? "#ff4757" : "#4a5a7a", border: side === "sell" ? "1px solid #ff475744" : "1px solid transparent" }}>
          SELL
        </button>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <div>
          <label className="font-mono text-xs mb-1 block" style={{ color: "#8899bb" }}>Shares</label>
          <input type="number" min="1" step="1" value={shares} onChange={(e) => setShares(e.target.value)}
            placeholder="0"
            className="w-full rounded px-3 py-2 font-mono text-sm outline-none"
            style={{ background: "#060a13", border: "1px solid #1e2d4a", color: "#e8edf5" }} />
        </div>
        <div>
          <label className="font-mono text-xs mb-1 block" style={{ color: "#8899bb" }}>Limit Price (USD)</label>
          <input type="number" min="0.01" step="0.01" value={price} onChange={(e) => setPrice(e.target.value)}
            className="w-full rounded px-3 py-2 font-mono text-sm outline-none"
            style={{ background: "#060a13", border: "1px solid #1e2d4a", color: "#e8edf5" }} />
        </div>

        {/* Order summary */}
        {sharesNum > 0 && priceNum > 0 && (
          <div className="rounded p-3" style={{ background: "#060a13", border: "1px solid #1e2d4a" }}>
            <div className="flex justify-between mb-1">
              <span className="font-mono text-xs" style={{ color: "#4a5a7a" }}>Estimated Total</span>
              <span className="font-mono text-xs font-bold" style={{ color: side === "buy" ? "#00d4aa" : "#ff4757" }}>
                {fmtCurrency(total)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="font-mono text-xs" style={{ color: "#4a5a7a" }}>Simulated Fee (0%)</span>
              <span className="font-mono text-xs" style={{ color: "#4a5a7a" }}>$0.00</span>
            </div>
          </div>
        )}

        <button type="submit" disabled={sharesNum <= 0 || priceNum <= 0}
          className="w-full py-2.5 rounded font-mono text-sm font-bold transition-all disabled:opacity-40"
          style={{ background: side === "buy" ? "#052e1c" : "#2a0909", color: side === "buy" ? "#00d4aa" : "#ff4757", border: `1px solid ${side === "buy" ? "#00d4aa44" : "#ff475744"}` }}>
          {submitted ? "✓ Order Simulated" : `${side === "buy" ? "BUY" : "SELL"} ${sharesNum > 0 ? sharesNum : ""} ${c.id}`}
        </button>
      </form>

      <p className="font-mono text-xs mt-3 text-center" style={{ color: "#4a5a7a" }}>
        DEMO ONLY — No real orders are placed. Reg CF resale restrictions apply.
      </p>
    </div>
  );
}
