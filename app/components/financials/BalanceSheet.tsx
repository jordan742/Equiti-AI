import type { Company } from "@/lib/types";
import { fmtCurrency } from "@/lib/formatting";
import SectionBox from "../ui/SectionBox";

function Row({ label, value, indent = false, bold = false, color }: {
  label: string; value: number; indent?: boolean; bold?: boolean; color?: string;
}) {
  return (
    <div className={`flex justify-between py-1.5 ${indent ? "pl-4" : ""}`}
      style={{ borderBottom: "1px solid #0c1220" }}>
      <span className="font-mono text-xs" style={{ color: bold ? "#e8edf5" : "#8899bb" }}>{label}</span>
      <span className="font-mono text-xs font-bold" style={{ color: color || (bold ? "#e8edf5" : "#c8d8f0") }}>
        {fmtCurrency(value)}
      </span>
    </div>
  );
}

function SectionHeader({ label }: { label: string }) {
  return (
    <div className="py-1 mt-2 mb-0.5">
      <span className="font-mono text-xs font-bold uppercase tracking-wider" style={{ color: "#2e6cf6" }}>{label}</span>
    </div>
  );
}

export default function BalanceSheet({ company: c }: { company: Company }) {
  const x = c.xbrl;
  const nonCurrentAssets = x.totalAssets - x.currentAssets;
  const nonCurrentLiabilities = x.totalLiabilities - x.currentLiabilities;

  return (
    <SectionBox title="Balance Sheet" tag={`Filing: ${c.filingDate}`}>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {/* Assets */}
        <div>
          <SectionHeader label="Assets" />
          <SectionHeader label="Current Assets" />
          <Row label="Cash & Equivalents" value={x.cash} indent />
          <Row label="Accounts Receivable" value={x.accountsReceivable} indent />
          <Row label="Other Current Assets" value={x.currentAssets - x.cash - x.accountsReceivable} indent />
          <Row label="Total Current Assets" value={x.currentAssets} bold color="#00d4aa" />
          <SectionHeader label="Non-Current Assets" />
          <Row label="Long-term Assets" value={nonCurrentAssets} indent />
          <Row label="Total Assets" value={x.totalAssets} bold color="#2e6cf6" />
        </div>

        {/* Liabilities + Equity */}
        <div>
          <SectionHeader label="Liabilities" />
          <SectionHeader label="Current Liabilities" />
          <Row label="Short-term Debt" value={c.totalDebt > x.currentLiabilities ? x.currentLiabilities * 0.6 : c.totalDebt} indent />
          <Row label="Other Current Liabilities" value={x.currentLiabilities - Math.min(c.totalDebt, x.currentLiabilities * 0.6)} indent />
          <Row label="Total Current Liabilities" value={x.currentLiabilities} bold color="#ff4757" />
          <SectionHeader label="Long-term Liabilities" />
          <Row label="Long-term Debt" value={nonCurrentLiabilities} indent />
          <Row label="Total Liabilities" value={x.totalLiabilities} bold color="#ff4757" />
          <SectionHeader label="Equity" />
          <Row label="Stockholders' Equity" value={x.stockholdersEquity} bold
            color={x.stockholdersEquity >= 0 ? "#00d4aa" : "#ff4757"} />
        </div>
      </div>

      {/* Income statement summary */}
      <div className="mt-4 pt-4" style={{ borderTop: "1px solid #1e2d4a" }}>
        <div className="font-mono text-xs font-bold uppercase tracking-wider mb-2" style={{ color: "#2e6cf6" }}>
          Income Summary (Annual)
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {[
            { label: "Revenue", value: x.revenue, color: "#00d4aa" },
            { label: "COGS", value: x.cogs, color: "#ff4757" },
            { label: "Gross Profit", value: x.revenue - x.cogs, color: "#00d4aa" },
            { label: "OpEx", value: x.operatingExpenses, color: "#ffb830" },
            { label: "Operating Loss", value: x.revenue - x.cogs - x.operatingExpenses, color: "#ff4757" },
            { label: "Net Income", value: x.netIncome, color: x.netIncome >= 0 ? "#00d4aa" : "#ff4757" },
          ].map((item) => (
            <div key={item.label} className="rounded p-2" style={{ background: "#0c1220", border: "1px solid #1e2d4a" }}>
              <div className="font-mono text-xs mb-0.5" style={{ color: "#8899bb" }}>{item.label}</div>
              <div className="font-mono text-xs font-bold" style={{ color: item.color }}>
                {item.value < 0 ? `-${fmtCurrency(Math.abs(item.value), true)}` : fmtCurrency(item.value, true)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </SectionBox>
  );
}
