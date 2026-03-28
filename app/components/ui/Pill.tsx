interface PillProps {
  label: string;
  variant?: "strong" | "moderate" | "caution" | "risk" | "live" | "closed" | "blue" | "amber" | "purple";
  size?: "sm" | "md";
}

export default function Pill({ label, variant = "blue", size = "sm" }: PillProps) {
  const cls = `badge-${variant}`;
  const pad = size === "sm" ? "px-2 py-0.5 text-xs" : "px-3 py-1 text-sm";
  return (
    <span className={`${cls} ${pad} rounded font-mono font-semibold uppercase tracking-wider inline-block`}>
      {label}
    </span>
  );
}
