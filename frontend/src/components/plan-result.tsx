"use client";

import { ScrollText } from "lucide-react";

import { PlanView } from "@/components/plan-view";
import { StructuredSummary } from "@/components/structured-summary";
import type { PlanResponse } from "@/lib/types";

/** Dashboard + full markdown plan + the brief that produced it. */
export function PlanResult({ plan }: { plan: PlanResponse }) {
  return (
    <div className="space-y-8">
      {plan.structure && <StructuredSummary structure={plan.structure} />}
      <PlanView plan={plan} />
      {plan.requirements && (
        <details className="group rounded-xl border bg-card" data-print="hide">
          <summary className="flex cursor-pointer items-center gap-2 px-4 py-3 text-sm font-semibold">
            <ScrollText className="size-4 text-primary" aria-hidden />
            Brief sent to the planner
          </summary>
          <pre className="border-t bg-muted/40 px-4 py-3 text-xs leading-relaxed whitespace-pre-wrap text-muted-foreground">
            {plan.requirements}
          </pre>
        </details>
      )}
    </div>
  );
}
