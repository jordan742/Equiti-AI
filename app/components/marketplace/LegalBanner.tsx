export default function LegalBanner() {
  return (
    <div className="rounded-lg p-4" style={{ background: "#2a0909", border: "1px solid rgba(255,71,87,0.4)" }}>
      <div className="flex items-start gap-3">
        <div className="shrink-0 font-mono text-lg" style={{ color: "#ff4757" }}>⚠</div>
        <div>
          <div className="font-mono text-sm font-bold mb-1" style={{ color: "#ff4757" }}>
            IMPORTANT LEGAL NOTICE — READ BEFORE PROCEEDING
          </div>
          <ul className="flex flex-col gap-1">
            {[
              "This marketplace is a SIMULATION for educational purposes only. No real securities are being bought or sold.",
              "Reg CF securities are subject to a 12-month resale restriction under 17 CFR § 227.501. Resale before this period may be unlawful.",
              "Secondary trading of Reg CF securities requires a registered broker-dealer or an SEC-registered funding portal. This platform does not qualify.",
              "Investing in startups involves a high degree of risk. You may lose your entire investment. Illiquidity and lack of dividends are common.",
              "This interface does not constitute a broker-dealer, investment advisor, or funding portal. Always consult a licensed financial professional.",
            ].map((item, i) => (
              <li key={i} className="flex gap-2 text-xs" style={{ color: "#f0c8c8" }}>
                <span style={{ color: "#ff4757", flexShrink: 0 }}>•</span>
                {item}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
