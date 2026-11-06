"use client";

import * as React from "react";
import {
  Building2,
  Check,
  ClipboardList,
  FileText,
  LayoutDashboard,
  Loader2,
  Route,
  Save,
  TriangleAlert,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDuration } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { ProgressEvent, ProgressStage, ProgressStatus } from "@/lib/types";

export const STEPS: { stage: ProgressStage; label: string; detail: string; icon: typeof Check }[] = [
  {
    stage: "planning",
    label: "Reading the brief",
    detail: "Main planner agent decides what to research",
    icon: ClipboardList,
  },
  {
    stage: "research_venues",
    label: "Venue & vendor research",
    detail: "Worker 1 searches the web for venues, caterers, photographers",
    icon: Building2,
  },
  {
    stage: "research_logistics",
    label: "Logistics & market research",
    detail: "Worker 2 checks local pricing, season, travel, permits",
    icon: Route,
  },
  {
    stage: "writing",
    label: "Writing the plan",
    detail: "Main agent synthesises budget, timeline, risks",
    icon: FileText,
  },
  {
    stage: "structuring",
    label: "Building the dashboard",
    detail: "Extracts budget, timeline and vendors into cards",
    icon: LayoutDashboard,
  },
  { stage: "saving", label: "Saving to history", detail: "Stored on the server", icon: Save },
];

export type StageStatuses = Partial<Record<ProgressStage, ProgressStatus>>;

export function reduceProgress(statuses: StageStatuses, event: ProgressEvent): StageStatuses {
  // Never move a finished stage back to "started" (e.g. a repeated planning event).
  if (event.status === "started" && statuses[event.stage]) return statuses;
  return { ...statuses, [event.stage]: event.status };
}

function useElapsedSeconds(): number {
  const [elapsed, setElapsed] = React.useState(0);
  React.useEffect(() => {
    const started = Date.now();
    const id = window.setInterval(() => setElapsed((Date.now() - started) / 1000), 1000);
    return () => window.clearInterval(id);
  }, []);
  return elapsed;
}

export function GenerationProgress({ statuses }: { statuses: StageStatuses }) {
  const elapsed = useElapsedSeconds();
  const done = STEPS.filter((step) => {
    const status = statuses[step.stage];
    return status === "completed" || status === "failed";
  }).length;

  return (
    <Card aria-live="polite">
      <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-2">
        <CardTitle className="flex items-center gap-2 text-base">
          <Loader2 className="size-4 animate-spin text-primary" aria-hidden />
          Your agents are planning
        </CardTitle>
        <span className="text-xs tabular-nums text-muted-foreground">
          {formatDuration(elapsed)} elapsed · usually about a minute
        </span>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="h-1.5 overflow-hidden rounded-full bg-muted">
          <div
            className="h-full rounded-full bg-primary transition-[width] duration-500"
            style={{ width: `${Math.max(4, (done / STEPS.length) * 100)}%` }}
          />
        </div>
        <ol className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {STEPS.map((step) => {
            const status = statuses[step.stage];
            const Icon =
              status === "completed" ? Check : status === "failed" ? TriangleAlert : step.icon;
            return (
              <li
                key={step.stage}
                className={cn(
                  "flex items-start gap-3 rounded-lg border p-3 transition-colors",
                  status === "started" && "border-primary/40 bg-primary/5",
                  status === "completed" && "bg-muted/40",
                  status === "failed" && "border-amber-500/40 bg-amber-500/5",
                  !status && "opacity-60",
                )}
              >
                <span
                  className={cn(
                    "flex size-7 shrink-0 items-center justify-center rounded-full",
                    status === "completed"
                      ? "bg-emerald-600 text-white"
                      : status === "failed"
                        ? "bg-amber-500 text-white"
                        : "bg-primary/10 text-primary",
                  )}
                >
                  {status === "started" ? (
                    <Loader2 className="size-3.5 animate-spin" aria-hidden />
                  ) : (
                    <Icon className="size-3.5" aria-hidden />
                  )}
                </span>
                <span className="min-w-0">
                  <span className="block text-sm font-semibold">{step.label}</span>
                  <span className="block text-xs text-muted-foreground">
                    {status === "failed" ? "Skipped — the plan continues without it" : step.detail}
                  </span>
                </span>
              </li>
            );
          })}
        </ol>
      </CardContent>
    </Card>
  );
}
