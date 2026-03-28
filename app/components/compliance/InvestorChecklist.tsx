"use client";
import { useState } from "react";
import { INVESTOR_CHECKLIST } from "@/lib/regulations";

export default function InvestorChecklist() {
  const [checked, setChecked] = useState<Set<number>>(new Set());

  function toggle(i: number) {
    setChecked((prev) => {
      const next = new Set(prev);
      if (next.has(i)) next.delete(i);
      else next.add(i);
      return next;
    });
  }

  const allChecked = checked.size === INVESTOR_CHECKLIST.length;

  return (
    <div className="rounded-lg p-4" style={{ background: "#0f1929", border: "1px solid #1e2d4a" }}>
      <div className="flex items-center justify-between mb-3">
        <span className="font-mono text-xs font-bold uppercase tracking-wider" style={{ color: "#8899bb" }}>
          Investor Acknowledgment Checklist
        </span>
        <span className="font-mono text-xs" style={{ color: checked.size === INVESTOR_CHECKLIST.length ? "#00d4aa" : "#ffb830" }}>
          {checked.size}/{INVESTOR_CHECKLIST.length}
        </span>
      </div>

      <div className="flex flex-col gap-2">
        {INVESTOR_CHECKLIST.map((item, i) => (
          <label key={i} className="flex items-start gap-3 cursor-pointer rounded p-2 transition-all"
            style={{ background: checked.has(i) ? "#052e1c33" : "transparent" }}
            onClick={() => toggle(i)}>
            <div className="shrink-0 mt-0.5 w-4 h-4 rounded border flex items-center justify-center"
              style={{ background: checked.has(i) ? "#00d4aa" : "transparent", borderColor: checked.has(i) ? "#00d4aa" : "#1e2d4a" }}>
              {checked.has(i) && <span className="text-black text-xs font-bold">✓</span>}
            </div>
            <span className="text-xs leading-relaxed" style={{ color: checked.has(i) ? "#c8f0e0" : "#8899bb" }}>
              {item}
            </span>
          </label>
        ))}
      </div>

      {allChecked && (
        <div className="mt-3 p-3 rounded text-center" style={{ background: "#052e1c", border: "1px solid #00d4aa44" }}>
          <span className="font-mono text-xs font-bold" style={{ color: "#00d4aa" }}>
            ✓ All items acknowledged. You may proceed with your investment research.
          </span>
        </div>
      )}
    </div>
  );
}
