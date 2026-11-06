import { daysFromToday, toIsoDate } from "./format";
import type { BriefRequest } from "./types";

export const GUEST_LIMITS = { min: 2, max: 2000 } as const;

export type BriefErrors = Partial<Record<keyof BriefRequest, string>>;

/** Mirrors the backend's validation so problems show inline before submitting. */
export function validateBrief(brief: BriefRequest): BriefErrors {
  const errors: BriefErrors = {};
  if (brief.wedding_location.trim().length < 2) {
    errors.wedding_location = "Add a city or region so the agents know where to research.";
  }
  if (!brief.wedding_date) {
    errors.wedding_date = "Pick a target date.";
  } else if (daysFromToday(brief.wedding_date) < 0) {
    errors.wedding_date = "The date must be today or later.";
  }
  if (
    !Number.isFinite(brief.guest_count) ||
    brief.guest_count < GUEST_LIMITS.min ||
    brief.guest_count > GUEST_LIMITS.max
  ) {
    errors.guest_count = `Enter between ${GUEST_LIMITS.min} and ${GUEST_LIMITS.max} guests.`;
  }
  if (brief.budget_high < brief.budget_low) {
    errors.budget_high = "Maximum budget must be at least the minimum.";
  }
  return errors;
}

/** Used before the backend's sample brief has loaded. */
export function emptyBrief(): BriefRequest {
  const date = new Date();
  date.setDate(date.getDate() + 240);
  return {
    couple_name: "",
    wedding_location: "",
    wedding_date: toIsoDate(date),
    guest_count: 120,
    currency: "USD",
    budget_low: 35000,
    budget_high: 65000,
    ceremony_type: "Ceremony and reception",
    wedding_styles: [],
    planning_priorities: [],
    tone: "Elegant and practical",
    must_haves: "",
    constraints: "",
    traditions: "",
  };
}

/** Merge a (possibly partial) brief from the API over sensible defaults. */
export function normalizeBrief(source: Partial<BriefRequest> | null | undefined): BriefRequest {
  const base = emptyBrief();
  if (!source) return base;
  return {
    ...base,
    ...Object.fromEntries(Object.entries(source).filter(([, value]) => value != null)),
    wedding_date: (source.wedding_date ?? base.wedding_date).slice(0, 10),
    wedding_styles: Array.isArray(source.wedding_styles) ? source.wedding_styles : [],
    planning_priorities: Array.isArray(source.planning_priorities)
      ? source.planning_priorities
      : [],
  };
}
