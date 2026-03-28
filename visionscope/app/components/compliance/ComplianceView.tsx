import { REGULATIONS } from "@/lib/regulations";
import RegulationCard from "./RegulationCard";
import InvestorChecklist from "./InvestorChecklist";
import LegalDisclaimer from "./LegalDisclaimer";
import ComplianceAlerts from "./ComplianceAlerts";

export default function ComplianceView() {
  return (
    <div className="flex flex-col gap-4">
      <ComplianceAlerts />

      {/* Regulations grid */}
      <div>
        <div className="font-mono text-xs font-bold uppercase tracking-wider mb-3 px-1" style={{ color: "#4a5a7a" }}>
          Applicable Regulations ({REGULATIONS.length})
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {REGULATIONS.map((reg) => (
            <RegulationCard key={reg.title} reg={reg} />
          ))}
        </div>
      </div>

      <InvestorChecklist />
      <LegalDisclaimer />
    </div>
  );
}
