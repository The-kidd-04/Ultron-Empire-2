/**
 * Format a number as Indian currency with Cr / L suffixes.
 * Examples: 12.5 -> "12.50 Cr", 0.45 -> "45.00 L"
 */
export function formatINR(crValue: number | undefined | null): string {
  if (crValue == null || isNaN(crValue)) return '--';
  if (crValue >= 1) {
    return `\u20B9${crValue.toFixed(2)} Cr`;
  }
  const lakhs = crValue * 100;
  return `\u20B9${lakhs.toFixed(2)} L`;
}

/**
 * Format a number as Indian Rupees with comma separation (no suffix).
 */
export function formatINRAbsolute(value: number | undefined | null): string {
  if (value == null || isNaN(value)) return '--';
  return '\u20B9' + value.toLocaleString('en-IN', { maximumFractionDigits: 2 });
}

/**
 * Format a date string to a readable form.
 * Input: ISO string or "YYYY-MM-DD"
 */
export function formatDate(dateStr: string | undefined | null): string {
  if (!dateStr) return '--';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

/**
 * Format a relative time string like "2 hours ago".
 */
export function formatTimeAgo(dateStr: string | undefined | null): string {
  if (!dateStr) return '';
  try {
    const now = Date.now();
    const then = new Date(dateStr).getTime();
    const diff = now - then;
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    if (days < 7) return `${days}d ago`;
    return formatDate(dateStr);
  } catch {
    return '';
  }
}

/**
 * Format a percentage value with sign and fixed decimals.
 */
export function formatPercent(value: number | undefined | null, decimals = 2): string {
  if (value == null || isNaN(value)) return '--';
  const sign = value > 0 ? '+' : '';
  return `${sign}${value.toFixed(decimals)}%`;
}
