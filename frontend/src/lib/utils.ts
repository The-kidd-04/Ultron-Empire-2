export function formatINR(amountCr: number): string {
  if (amountCr >= 1) return `₹${amountCr.toFixed(1)} Cr`;
  if (amountCr >= 0.01) return `₹${(amountCr * 100).toFixed(1)} L`;
  return `₹${(amountCr * 10000000).toLocaleString()}`;
}

export function formatPct(value: number, signed = true): string {
  return signed ? `${value >= 0 ? '+' : ''}${value.toFixed(1)}%` : `${value.toFixed(1)}%`;
}

export function cn(...classes: (string | false | undefined)[]): string {
  return classes.filter(Boolean).join(' ');
}
