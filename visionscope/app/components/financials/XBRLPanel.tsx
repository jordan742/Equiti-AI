import type { Company } from "@/lib/types";
import { fmtCurrency } from "@/lib/formatting";
import SectionBox from "../ui/SectionBox";

const XBRL_TAGS: { tag: string; label: string; field: keyof NonNullable<Company["xbrl"]>; namespace: string }[] = [
  { tag: "us-gaap:Assets",                    label: "Total Assets",             field: "totalAssets",         namespace: "us-gaap" },
  { tag: "us-gaap:AssetsCurrent",             label: "Current Assets",           field: "currentAssets",       namespace: "us-gaap" },
  { tag: "us-gaap:CashAndCashEquivalents",    label: "Cash & Cash Equivalents",  field: "cash",                namespace: "us-gaap" },
  { tag: "us-gaap:AccountsReceivableNet",     label: "Accounts Receivable, Net", field: "accountsReceivable",  namespace: "us-gaap" },
  { tag: "us-gaap:Liabilities",               label: "Total Liabilities",        field: "totalLiabilities",    namespace: "us-gaap" },
  { tag: "us-gaap:LiabilitiesCurrent",        label: "Current Liabilities",      field: "currentLiabilities",  namespace: "us-gaap" },
  { tag: "us-gaap:StockholdersEquity",        label: "Stockholders' Equity",     field: "stockholdersEquity",  namespace: "us-gaap" },
  { tag: "us-gaap:Revenues",                  label: "Revenues",                 field: "revenue",             namespace: "us-gaap" },
  { tag: "us-gaap:CostOfRevenue",             label: "Cost of Revenue",          field: "cogs",                namespace: "us-gaap" },
  { tag: "us-gaap:OperatingExpenses",         label: "Operating Expenses",       field: "operatingExpenses",   namespace: "us-gaap" },
  { tag: "us-gaap:NetIncomeLoss",             label: "Net Income (Loss)",        field: "netIncome",           namespace: "us-gaap" },
];

export default function XBRLPanel({ company: c }: { company: Company }) {
  return (
    <SectionBox title="XBRL Taxonomy" tag={`CIK: ${c.cik} · Form ${c.formType}`}>
      <div className="mb-3 flex items-center gap-2">
        <div className="h-2 w-2 rounded-full" style={{ background: "#00d4aa" }} />
        <span className="font-mono text-xs" style={{ color: "#8899bb" }}>
          SEC EDGAR inline XBRL — US-GAAP taxonomy tags extracted from Form {c.formType} filing
        </span>
      </div>

      <div className="rounded overflow-hidden" style={{ border: "1px solid #1e2d4a" }}>
        {/* Header */}
        <div className="grid grid-cols-12 px-3 py-2" style={{ background: "#060a13", borderBottom: "1px solid #1e2d4a" }}>
          <div className="col-span-1 font-mono text-xs font-bold" style={{ color: "#4a5a7a" }}>#</div>
          <div className="col-span-4 font-mono text-xs font-bold" style={{ color: "#4a5a7a" }}>XBRL Tag</div>
          <div className="col-span-4 font-mono text-xs font-bold" style={{ color: "#4a5a7a" }}>Label</div>
          <div className="col-span-3 font-mono text-xs font-bold text-right" style={{ color: "#4a5a7a" }}>Value (USD)</div>
        </div>

        {XBRL_TAGS.map((t, i) => {
          const value = c.xbrl[t.field] as number;
          const isNeg = value < 0;
          return (
            <div key={t.tag}
              className="grid grid-cols-12 px-3 py-2 items-center"
              style={{ background: i % 2 === 0 ? "#0c1220" : "#060a13", borderBottom: "1px solid #0f1929" }}>
              <div className="col-span-1 font-mono text-xs" style={{ color: "#4a5a7a" }}>{i + 1}</div>
              <div className="col-span-4">
                <span className="font-mono text-xs px-1.5 py-0.5 rounded"
                  style={{ background: "#1e2d4a22", color: "#2e6cf6", fontSize: "10px" }}>
                  {t.tag}
                </span>
              </div>
              <div className="col-span-4 font-mono text-xs" style={{ color: "#c8d8f0" }}>{t.label}</div>
              <div className="col-span-3 font-mono text-xs font-bold text-right"
                style={{ color: isNeg ? "#ff4757" : "#e8edf5" }}>
                {isNeg ? `(${fmtCurrency(Math.abs(value))})` : fmtCurrency(value)}
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-3 p-2 rounded" style={{ background: "#060a13", border: "1px solid #1e2d4a" }}>
        <p className="font-mono text-xs" style={{ color: "#4a5a7a" }}>
          Source: SEC EDGAR · Filing date: {c.filingDate} · CIK: {c.cik} · Form: {c.formType}
          {" · "}Data displayed is sourced from public Form C filings and may differ from audited financials.
        </p>
      </div>
    </SectionBox>
  );
}
