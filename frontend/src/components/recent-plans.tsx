"use client";

import * as React from "react";
import { ArrowRight, FileText } from "lucide-react";
import Link from "next/link";

import { PlanMeta } from "@/components/plans-list";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { listPlans } from "@/lib/api";
import type { PlanSummary } from "@/lib/types";

const LIMIT = 4;

/** The latest few plans from the server; refreshes when `refreshKey` changes. */
export function RecentPlans({ refreshKey }: { refreshKey?: string }) {
  const [plans, setPlans] = React.useState<PlanSummary[] | null>(null);
  const [total, setTotal] = React.useState(0);

  React.useEffect(() => {
    let cancelled = false;
    listPlans()
      .then((data) => {
        if (cancelled) return;
        setPlans(data.plans.slice(0, LIMIT));
        setTotal(data.total);
      })
      .catch(() => {
        if (!cancelled) setPlans([]);
      });
    return () => {
      cancelled = true;
    };
  }, [refreshKey]);

  if (!plans?.length) return null;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-base">Recent plans</CardTitle>
        {total > LIMIT && (
          <Link href="/plans" className="text-xs font-medium text-primary hover:underline">
            View all {total}
          </Link>
        )}
      </CardHeader>
      <CardContent>
        <ul className="-mx-2 space-y-0.5">
          {plans.map((plan) => (
            <li key={plan.id}>
              <Link
                href={`/plans/${plan.id}`}
                className="group flex items-start gap-2 rounded-lg px-2 py-2 transition-colors hover:bg-muted"
              >
                <FileText
                  className="mt-0.5 size-4 shrink-0 text-muted-foreground group-hover:text-primary"
                  aria-hidden
                />
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-sm font-semibold">{plan.title}</span>
                  <PlanMeta plan={plan} />
                </span>
                <ArrowRight
                  className="mt-0.5 size-4 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100"
                  aria-hidden
                />
              </Link>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
