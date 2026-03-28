export default function DisclaimerFooter() {
  return (
    <footer className="mt-8 py-6 px-4" style={{ borderTop: "1px solid #0f1929" }}>
      <div className="max-w-5xl mx-auto">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
          <div>
            <div className="font-mono text-xs font-bold mb-2" style={{ color: "#4a5a7a" }}>VISIONSCOPE</div>
            <p className="text-xs leading-relaxed" style={{ color: "#2a3a5a" }}>
              Bloomberg Terminal-style analytics for Reg CF startup investments. Educational platform only.
            </p>
          </div>
          <div>
            <div className="font-mono text-xs font-bold mb-2" style={{ color: "#4a5a7a" }}>LEGAL</div>
            <ul className="flex flex-col gap-1">
              {["Not a broker-dealer", "Not an investment adviser", "Not a funding portal", "Simulated data only"].map((item) => (
                <li key={item} className="font-mono text-xs" style={{ color: "#2a3a5a" }}>• {item}</li>
              ))}
            </ul>
          </div>
          <div>
            <div className="font-mono text-xs font-bold mb-2" style={{ color: "#4a5a7a" }}>REGULATORY</div>
            <ul className="flex flex-col gap-1">
              {["SEC Reg CF (17 CFR Part 227)", "Securities Act 4(a)(6)", "JOBS Act · JOBS Act 3.0", "Reg A+ (Alternative)"].map((item) => (
                <li key={item} className="font-mono text-xs" style={{ color: "#2a3a5a" }}>• {item}</li>
              ))}
            </ul>
          </div>
        </div>
        <div className="pt-4" style={{ borderTop: "1px solid #0f1929" }}>
          <p className="font-mono text-xs text-center" style={{ color: "#1e2d4a" }}>
            © 2026 VisionScope · Educational Use Only · NOT FINANCIAL ADVICE · All data simulated
            · For real Reg CF investments, use SEC-registered funding portals only
          </p>
        </div>
      </div>
    </footer>
  );
}
