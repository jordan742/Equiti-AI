export default function LegalDisclaimer() {
  return (
    <div className="rounded-lg p-5" style={{ background: "#0a0f1a", border: "2px solid #1e2d4a" }}>
      <div className="font-mono text-sm font-bold mb-3 text-center uppercase tracking-widest" style={{ color: "#2e6cf6" }}>
        Full Legal Disclaimer
      </div>
      <div className="flex flex-col gap-3 text-xs leading-relaxed" style={{ color: "#8899bb" }}>
        <p>
          <strong style={{ color: "#e8edf5" }}>NOT FINANCIAL ADVICE.</strong>{" "}
          VisionScope is an educational analytics platform designed to help retail investors understand financial concepts
          related to Regulation Crowdfunding (Reg CF) securities. Nothing on this platform constitutes investment advice,
          financial advice, trading advice, or any other type of advice. You should not treat any of the platform's content
          as such.
        </p>
        <p>
          <strong style={{ color: "#e8edf5" }}>NOT A BROKER-DEALER OR INVESTMENT ADVISER.</strong>{" "}
          VisionScope is not registered with the Securities and Exchange Commission (SEC) as a broker-dealer or investment
          adviser. VisionScope is not a registered funding portal under Regulation Crowdfunding. This platform does not
          facilitate securities transactions, hold customer funds, or provide personalized investment recommendations.
        </p>
        <p>
          <strong style={{ color: "#e8edf5" }}>SIMULATED DATA.</strong>{" "}
          All company data, financial metrics, scores, AI analyses, portfolio positions, and marketplace order books
          displayed on this platform are entirely simulated for educational purposes. They do not represent real companies,
          real financial data, real securities offerings, or real transactions of any kind.
        </p>
        <p>
          <strong style={{ color: "#e8edf5" }}>INVESTMENT RISK.</strong>{" "}
          Investing in startup companies through Regulation Crowdfunding involves a high degree of risk. You may lose
          your entire investment. Investments in private companies are illiquid, and there is no guarantee of returns
          or dividends. Past performance does not guarantee future results.
        </p>
        <p>
          <strong style={{ color: "#e8edf5" }}>AI LIMITATIONS.</strong>{" "}
          AI-generated analyses, summaries, and verdicts on this platform are algorithmically generated from structured
          data and do not incorporate real market intelligence, proprietary research, or human professional judgment.
          AI outputs may contain errors, biases, or inaccuracies. Do not rely on AI analyses as the sole basis for
          any investment decision.
        </p>
        <p>
          <strong style={{ color: "#e8edf5" }}>REGULATORY INFORMATION.</strong>{" "}
          Regulation Crowdfunding rules, investor limits, and compliance requirements described on this platform reflect
          the platform developers' interpretation of SEC rules as of the platform's last update and may not reflect
          current regulations. Always consult the SEC website (sec.gov) or a licensed attorney for authoritative
          regulatory guidance.
        </p>
        <div className="mt-2 pt-3" style={{ borderTop: "1px solid #1e2d4a" }}>
          <p className="text-center font-mono" style={{ color: "#4a5a7a" }}>
            © 2026 VisionScope · Educational Analytics Platform · For informational use only
            · Contact: support@visionscope.example.com
          </p>
        </div>
      </div>
    </div>
  );
}
