type Variant = "live" | "closed" | "safe" | "preferred" | "blue" | "green" | "red" | "amber" | "purple" | "gray";

const STYLES: Record<Variant, { bg: string; color: string; border: string }> = {
  live:      { bg: "#052e1c", color: "#00d4aa", border: "#00d4aa44" },
  closed:    { bg: "#1b2540", color: "#8594b0", border: "#1b2540" },
  safe:      { bg: "#082040", color: "#2e6cf6", border: "#2e6cf644" },
  preferred: { bg: "#1a0e2e", color: "#8b5cf6", border: "#8b5cf644" },
  blue:      { bg: "#082040", color: "#2e6cf6", border: "#2e6cf644" },
  green:     { bg: "#052e1c", color: "#00d4aa", border: "#00d4aa44" },
  red:       { bg: "#2a0909", color: "#ff4757", border: "#ff475744" },
  amber:     { bg: "#2a1600", color: "#ffb830", border: "#ffb83044" },
  purple:    { bg: "#1a0e2e", color: "#8b5cf6", border: "#8b5cf644" },
  gray:      { bg: "#0f1520", color: "#8594b0", border: "#1b2540" },
};

export default function Pill({ label, variant = "gray", small }: { label: string; variant?: Variant; small?: boolean }) {
  const s = STYLES[variant];
  return (
    <span className="font-mono font-bold uppercase tracking-wider rounded inline-block"
      style={{ background: s.bg, color: s.color, border: `1px solid ${s.border}`, fontSize: small ? 9 : 10, padding: small ? "1px 5px" : "2px 7px" }}>
      {label}
    </span>
  );
}
