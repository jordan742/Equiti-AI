export function fmtCurrency(n: number, compact = false): string {
  if (compact) {
    if (Math.abs(n) >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
    if (Math.abs(n) >= 1_000)     return `$${(n / 1_000).toFixed(0)}K`;
  }
  return new Intl.NumberFormat("en-US", {
    style: "currency", currency: "USD", maximumFractionDigits: 0,
  }).format(n);
}

export function fmtPct(n: number, decimals = 1): string {
  return `${n >= 0 ? "+" : ""}${n.toFixed(decimals)}%`;
}

export function fmtNum(n: number): string {
  return new Intl.NumberFormat("en-US").format(n);
}

export function fmtMonths(n: number): string {
  if (n < 2) return `${(n * 4.33).toFixed(0)} wks`;
  return `${n.toFixed(1)} mo`;
}

export function fmtPrice(n: number): string {
  return `$${n.toFixed(2)}`;
}
