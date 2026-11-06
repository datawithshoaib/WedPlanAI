import type {
  BriefRequest,
  HealthResponse,
  OptionsResponse,
  PlanResponse,
  PlanSummaryList,
  ProgressEvent,
  StreamMessage,
} from "./types";

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, "") || "http://localhost:8000";

export const BACKEND_START_HINT = "cd backend && uv run uvicorn wedplanner.api.main:app --reload";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }

  get isNetworkError() {
    return this.status === 0;
  }
}

interface ValidationIssue {
  loc?: (string | number)[];
  msg?: string;
}

/** Turn FastAPI error bodies (string or validation-issue list) into one readable sentence. */
function describeError(detail: unknown, status: number): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail.length) {
    return (detail as ValidationIssue[])
      .map((issue) => {
        const field = issue.loc?.filter((part) => part !== "body").join(".");
        const msg = (issue.msg ?? "is invalid").replace(/^Value error, /, "");
        return field ? `${field.replaceAll("_", " ")}: ${msg}` : msg;
      })
      .join("; ");
  }
  return `Request failed with status ${status}`;
}

async function send(path: string, init?: RequestInit): Promise<Response> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") throw err;
    throw new ApiError(`Could not reach the backend at ${API_URL}. Is it running?`, 0);
  }
  if (!res.ok) {
    let detail: unknown;
    try {
      detail = ((await res.json()) as { detail?: unknown }).detail;
    } catch {
      // non-JSON error body
    }
    throw new ApiError(describeError(detail, res.status), res.status);
  }
  return res;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await send(path, init);
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/api/health");
}

export function getOptions(): Promise<OptionsResponse> {
  return request<OptionsResponse>("/api/options");
}

/**
 * Generate a plan, reporting progress as the agents work.
 * Resolves with the saved plan; rejects with an ApiError on failure.
 */
export async function createPlanStreaming(
  brief: BriefRequest,
  onProgress: (event: ProgressEvent) => void,
  signal?: AbortSignal,
): Promise<PlanResponse> {
  const res = await send("/api/plans/stream", {
    method: "POST",
    body: JSON.stringify(brief),
    signal,
  });
  if (!res.body) throw new ApiError("The server returned an empty response.", res.status);

  const reader = res.body.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = "";

  const handle = (line: string): PlanResponse | undefined => {
    if (!line.trim()) return undefined;
    const message = JSON.parse(line) as StreamMessage;
    if (message.type === "progress") onProgress(message.event);
    else if (message.type === "error") throw new ApiError(message.detail, message.status_code);
    else return message.plan;
    return undefined;
  };

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += value;
    let newline: number;
    while ((newline = buffer.indexOf("\n")) >= 0) {
      const plan = handle(buffer.slice(0, newline));
      buffer = buffer.slice(newline + 1);
      if (plan) return plan;
    }
  }
  const plan = handle(buffer);
  if (plan) return plan;
  throw new ApiError("The connection closed before the plan was finished.", 0);
}

export function listPlans(): Promise<PlanSummaryList> {
  return request<PlanSummaryList>("/api/plans");
}

export function getPlan(planId: string): Promise<PlanResponse> {
  return request<PlanResponse>(`/api/plans/${encodeURIComponent(planId)}`);
}

export function deletePlan(planId: string): Promise<void> {
  return request<void>(`/api/plans/${encodeURIComponent(planId)}`, { method: "DELETE" });
}

export function clearAllPlans(): Promise<void> {
  return request<void>("/api/plans", { method: "DELETE" });
}
