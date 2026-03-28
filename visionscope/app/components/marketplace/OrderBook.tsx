import type { Company } from "@/lib/types";
import { fmtCurrency } from "@/lib/formatting";

interface OrderBookProps {
  company: Company;
}

// Generate simulated order book levels
function genLevels(basePrice: number, side: "bid" | "ask", count = 6) {
  return Array.from({ length: count }, (_, i) => {
    const spread = side === "bid" ? -(i + 1) * 0.02 : (i + 1) * 0.02;
    const price = parseFloat((basePrice + basePrice * spread).toFixed(2));
    const size = Math.floor(Math.random() * 800 + 100);
    return { price, size };
  });
}

export default function OrderBook({ company: c }: OrderBookProps) {
  const bids = genLevels(c.market.bidPrice, "bid");
  const asks = genLevels(c.market.askPrice, "ask");
  const spread = (c.market.askPrice - c.market.bidPrice).toFixed(2);
  const spreadPct = (((c.market.askPrice - c.market.bidPrice) / c.market.bidPrice) * 100).toFixed(2);

  return (
    <div className="rounded-lg overflow-hidden" style={{ background: "#0f1929", border: "1px solid #1e2d4a" }}>
      <div className="px-4 py-3 flex justify-between items-center" style={{ borderBottom: "1px solid #1e2d4a" }}>
        <span className="font-mono text-xs font-bold uppercase tracking-wider" style={{ color: "#8899bb" }}>Order Book</span>
        <span className="font-mono text-xs" style={{ color: "#4a5a7a" }}>
          Spread: <span style={{ color: "#ffb830" }}>${spread} ({spreadPct}%)</span>
        </span>
      </div>

      <div className="grid grid-cols-2 divide-x" style={{ borderColor: "#1e2d4a" }}>
        {/* Bids */}
        <div>
          <div className="grid grid-cols-2 px-3 py-1.5 font-mono text-xs" style={{ background: "#060a13", borderBottom: "1px solid #1e2d4a", color: "#4a5a7a" }}>
            <div>Bid Price</div><div className="text-right">Size</div>
          </div>
          {bids.map((b, i) => (
            <div key={i} className="grid grid-cols-2 px-3 py-1.5 relative overflow-hidden"
              style={{ borderBottom: "1px solid #0c1220" }}>
              <div className="absolute inset-0 right-auto"
                style={{ width: `${Math.min((b.size / 900) * 100, 100)}%`, background: "#00d4aa08" }} />
              <div className="font-mono text-xs font-bold relative" style={{ color: "#00d4aa" }}>{fmtCurrency(b.price)}</div>
              <div className="font-mono text-xs text-right relative" style={{ color: "#8899bb" }}>{b.size}</div>
            </div>
          ))}
        </div>

        {/* Asks */}
        <div>
          <div className="grid grid-cols-2 px-3 py-1.5 font-mono text-xs" style={{ background: "#060a13", borderBottom: "1px solid #1e2d4a", color: "#4a5a7a" }}>
            <div>Ask Price</div><div className="text-right">Size</div>
          </div>
          {asks.map((a, i) => (
            <div key={i} className="grid grid-cols-2 px-3 py-1.5 relative overflow-hidden"
              style={{ borderBottom: "1px solid #0c1220" }}>
              <div className="absolute inset-0 right-auto"
                style={{ width: `${Math.min((a.size / 900) * 100, 100)}%`, background: "#ff475708" }} />
              <div className="font-mono text-xs font-bold relative" style={{ color: "#ff4757" }}>{fmtCurrency(a.price)}</div>
              <div className="font-mono text-xs text-right relative" style={{ color: "#8899bb" }}>{a.size}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="px-4 py-2 flex gap-4" style={{ background: "#060a13", borderTop: "1px solid #1e2d4a" }}>
        <span className="font-mono text-xs" style={{ color: "#4a5a7a" }}>
          24h Vol: <span style={{ color: "#e8edf5" }}>{fmtCurrency(c.market.volume24h, true)}</span>
        </span>
        <span className="font-mono text-xs" style={{ color: "#4a5a7a" }}>
          Trades: <span style={{ color: "#e8edf5" }}>{c.market.trades24h}</span>
        </span>
      </div>
    </div>
  );
}
