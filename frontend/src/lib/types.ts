export interface BriefRequest {
  couple_name: string;
  wedding_location: string;
  wedding_date: string;
  guest_count: number;
  currency: string;
  budget_low: number;
  budget_high: number;
  ceremony_type: string;
  wedding_styles: string[];
  planning_priorities: string[];
  tone: string;
  must_haves: string;
  constraints: string;
  traditions: string;
}

export interface PlanStructure {
  executive_summary: string;
  venue_recommendations: VenueRecommendation[];
  vendor_recommendations: VendorRecommendation[];
  budget_allocation: BudgetItem[];
  timeline: TimelineMilestone[];
  risks: RiskItem[];
  open_questions: string[];
}

export interface VenueRecommendation {
  name: string;
  location: string;
  why_it_fits: string;
}

export interface VendorRecommendation {
  category: string;
  name: string;
  why_recommended: string;
}

export interface BudgetItem {
  category: string;
  amount: number;
  currency: string;
  share_percent: number;
}

export interface TimelineMilestone {
  phase: string;
  horizon: string;
  actions: string[];
}

export interface RiskItem {
  risk: string;
  mitigation: string;
}

export interface PlanResponse {
  id: string;
  title: string;
  requirements: string;
  content: string;
  structure: PlanStructure | null;
  duration_seconds: number;
  created_at: string;
  word_count: number;
  brief: Partial<BriefRequest> | null;
}

export interface PlanSummary {
  id: string;
  title: string;
  duration_seconds: number;
  created_at: string;
  word_count: number;
  wedding_location: string | null;
  wedding_date: string | null;
  guest_count: number | null;
}

export interface PlanSummaryList {
  plans: PlanSummary[];
  total: number;
}

export interface OptionsResponse {
  ceremony_types: string[];
  currencies: string[];
  style_options: string[];
  priority_options: string[];
  tone_options: string[];
  default_brief: BriefRequest;
}

export interface HealthResponse {
  status: string;
  planner_ready: boolean;
  research_ready: boolean;
  model: string;
  plan_count: number;
}

export type ProgressStage =
  | "planning"
  | "research_venues"
  | "research_logistics"
  | "writing"
  | "structuring"
  | "saving";

export type ProgressStatus = "started" | "completed" | "failed";

export interface ProgressEvent {
  stage: ProgressStage;
  status: ProgressStatus;
  message: string;
}

export type StreamMessage =
  | { type: "progress"; event: ProgressEvent }
  | { type: "plan"; plan: PlanResponse }
  | { type: "error"; status_code: number; detail: string };
