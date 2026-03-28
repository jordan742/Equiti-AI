const ITEMS = [
  "ACTIVE DEALS: 220",
  "WEEKLY VOL: $4.9M",
  "AVG DEAL SIZE: $847K",
  "MED RUNWAY: 8.2 mo",
  "AI SECTOR SHARE: 34%",
  "REG CF CAP: $5.0M",
  "NEW FILINGS (7D): 14",
  "AVG HEALTH SCORE: 52",
  "TOP SECTOR: FINTECH",
  "TOTAL INVESTORS: 18.4K",
];

export default function MarketTicker() {
  const repeated = [...ITEMS, ...ITEMS];
  return (
    <div className="overflow-hidden py-1.5 shrink-0"
      style={{ background: "#060e1f", borderBottom: "1px solid #1e2d4a" }}>
      <div className="ticker-inner flex items-center gap-0 whitespace-nowrap" style={{ width: "max-content" }}>
        {repeated.map((item, i) => (
          <span key={i} className="font-mono text-xs" style={{ color: "#4a9eff" }}>
            <span style={{ color: "#2e4a7a", margin: "0 12px" }}>◆</span>
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}
