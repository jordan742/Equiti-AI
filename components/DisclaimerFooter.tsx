export default function DisclaimerFooter() {
  return (
    <footer className="mt-8 py-6 px-4" style={{ borderTop: "1px solid #1b2540" }}>
      <div className="max-w-5xl mx-auto">
        <p className="font-mono text-xs text-center mb-1" style={{ color: "#4e5f7d" }}>
          VisionScope is an educational analytics platform. NOT financial advice.
          NOT a broker-dealer, investment adviser, or SEC-registered funding portal.
          All data is simulated for educational purposes only.
        </p>
        <p className="font-mono text-xs text-center" style={{ color: "#2a3a5a" }}>
          © 2026 VisionScope · Reg CF (17 CFR Part 227) · Securities Act 4(a)(6) · For informational use only
        </p>
      </div>
    </footer>
  );
}
