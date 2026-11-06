const LOCALE = "en-US";

function safeCurrency(currency: string): string {
  return /^[A-Z]{3}$/.test(currency) ? currency : "USD";
}

/** Compact money for large values, e.g. "$35K" or "₹1.2M"; exact below 10,000. */
export function formatMoney(value: number, currency: string): string {
  return new Intl.NumberFormat(LOCALE, {
    style: "currency",
    currency: safeCurrency(currency),
    notation: value >= 10_000 ? "compact" : "standard",
    maximumFractionDigits: value >= 10_000 ? 1 : 0,
  }).format(value);
}

/** Full money, e.g. "$35,000". */
export function formatCurrencyNumber(value: number, currency: string): string {
  return new Intl.NumberFormat(LOCALE, {
    style: "currency",
    currency: safeCurrency(currency),
    maximumFractionDigits: 0,
  }).format(value || 0);
}

export function formatBudgetRange(low: number, high: number, currency: string): string {
  return `${formatMoney(low, currency)} – ${formatMoney(high, currency)}`;
}

export function formatPerGuest(low: number, high: number, currency: string, guests: number): string {
  if (!guests) return "Per-guest estimate unavailable";
  return `${formatCurrencyNumber((low + high) / 2 / guests, currency)} per guest (midpoint)`;
}

/** Slider bounds that make sense for each currency's typical wedding spend. */
export function budgetScale(currency: string): { max: number; step: number } {
  switch (currency) {
    case "INR":
      return { max: 20_000_000, step: 100_000 };
    case "AED":
      return { max: 1_000_000, step: 10_000 };
    default:
      return { max: 250_000, step: 5_000 };
  }
}

function parseIsoDate(isoDate: string): Date {
  return new Date(`${isoDate.slice(0, 10)}T00:00:00`);
}

export function daysFromToday(isoDate: string): number {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return Math.round((parseIsoDate(isoDate).getTime() - today.getTime()) / 86_400_000);
}

export function daysUntil(isoDate: string): string {
  const diff = daysFromToday(isoDate);
  if (Number.isNaN(diff)) return "Date not set";
  if (diff === 0) return "Today";
  if (diff === 1) return "Tomorrow";
  if (diff < 0) return `${Math.abs(diff)} days ago`;
  if (diff < 60) return `${diff} days out`;
  const weeks = Math.round(diff / 7);
  return `${weeks} weeks out`;
}

export function formatLongDate(isoDate: string): string {
  const date = parseIsoDate(isoDate);
  if (Number.isNaN(date.getTime())) return "Date not set";
  return date.toLocaleDateString(LOCALE, { month: "short", day: "numeric", year: "numeric" });
}

export function formatPlanTime(isoTimestamp: string): string {
  const date = new Date(isoTimestamp);
  if (Number.isNaN(date.getTime())) return isoTimestamp;
  return date.toLocaleString(LOCALE, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds.toFixed(0)}s`;
  return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`;
}

export function toIsoDate(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

export function slugify(title: string, extension = "md"): string {
  const slug = title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return `${slug.slice(0, 44) || "wedding-plan"}.${extension}`;
}
