"use client";

import * as React from "react";
import { CalendarDays, FileText, Loader2, MapPin, Plus, Search, Trash2, Users, WifiOff } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";

import { ConfirmButton } from "@/components/confirm-button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { BACKEND_START_HINT, clearAllPlans, deletePlan, listPlans } from "@/lib/api";
import { formatLongDate, formatPlanTime } from "@/lib/format";
import type { PlanSummary } from "@/lib/types";

export function PlanMeta({ plan }: { plan: PlanSummary }) {
  return (
    <span className="mt-0.5 flex flex-wrap items-center gap-x-3 gap-y-0.5 text-xs text-muted-foreground">
      {plan.wedding_location && (
        <span className="flex items-center gap-1">
          <MapPin className="size-3" aria-hidden />
          {plan.wedding_location}
        </span>
      )}
      {plan.wedding_date && (
        <span className="flex items-center gap-1">
          <CalendarDays className="size-3" aria-hidden />
          {formatLongDate(plan.wedding_date)}
        </span>
      )}
      {plan.guest_count != null && (
        <span className="flex items-center gap-1">
          <Users className="size-3" aria-hidden />
          {plan.guest_count}
        </span>
      )}
    </span>
  );
}

export function PlansList() {
  const [plans, setPlans] = React.useState<PlanSummary[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [deletingId, setDeletingId] = React.useState<string | null>(null);
  const [clearing, setClearing] = React.useState(false);
  const [query, setQuery] = React.useState("");

  React.useEffect(() => {
    let cancelled = false;
    listPlans()
      .then((data) => {
        if (!cancelled) setPlans(data.plans);
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load plans");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const filtered = React.useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) return plans;
    return plans.filter((plan) =>
      [plan.title, plan.wedding_location ?? ""].some((field) =>
        field.toLowerCase().includes(needle),
      ),
    );
  }, [plans, query]);

  const handleDelete = async (plan: PlanSummary) => {
    setDeletingId(plan.id);
    try {
      await deletePlan(plan.id);
      setPlans((current) => current.filter((item) => item.id !== plan.id));
      toast.success(`Deleted “${plan.title}”`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to delete plan");
    } finally {
      setDeletingId(null);
    }
  };

  const handleClear = async () => {
    setClearing(true);
    try {
      await clearAllPlans();
      setPlans([]);
      toast.success("All plans cleared");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to clear plans");
    } finally {
      setClearing(false);
    }
  };

  return (
    <Card>
      <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-3">
        <div>
          <CardTitle className="font-heading text-2xl">Plan history</CardTitle>
          <p className="mt-0.5 text-sm text-muted-foreground">
            {loading
              ? "Loading saved plans…"
              : `${plans.length} plan${plans.length === 1 ? "" : "s"} saved on the server`}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link href="/" className={buttonVariants({ size: "sm" })}>
            <Plus aria-hidden />
            New plan
          </Link>
          {plans.length > 0 && (
            <ConfirmButton
              variant="ghost"
              size="sm"
              onConfirm={handleClear}
              disabled={clearing}
              className="text-destructive hover:text-destructive"
              confirmLabel={`Delete all ${plans.length}?`}
            >
              {clearing ? <Loader2 className="animate-spin" aria-hidden /> : <Trash2 aria-hidden />}
              Clear all
            </ConfirmButton>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && (
          <Alert variant="destructive">
            <WifiOff aria-hidden />
            <AlertTitle>Could not load plans</AlertTitle>
            <AlertDescription>
              {error} Start it with <code className="font-mono">{BACKEND_START_HINT}</code>
            </AlertDescription>
          </Alert>
        )}

        {plans.length > 3 && (
          <div className="relative">
            <Search
              className="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground"
              aria-hidden
            />
            <Input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search by couple or location"
              className="pl-8"
              aria-label="Search plans"
            />
          </div>
        )}

        {loading ? (
          <div className="space-y-2.5">
            {[0, 1, 2].map((key) => (
              <div key={key} className="h-16 animate-pulse rounded-lg bg-muted" />
            ))}
          </div>
        ) : plans.length === 0 && !error ? (
          <div className="rounded-lg border border-dashed p-10 text-center">
            <FileText className="mx-auto mb-3 size-8 text-muted-foreground" aria-hidden />
            <p className="text-sm font-semibold">No saved plans yet</p>
            <p className="mx-auto mt-1 max-w-md text-sm text-muted-foreground">
              Generate a wedding plan from the brief form and it will appear here.
            </p>
          </div>
        ) : filtered.length === 0 && plans.length > 0 ? (
          <p className="py-6 text-center text-sm text-muted-foreground">
            No plans match “{query}”.
          </p>
        ) : (
          <ul className="space-y-1.5">
            {filtered.map((plan) => (
              <li
                key={plan.id}
                className="flex items-center gap-3 rounded-lg border bg-card p-3 transition-colors hover:bg-muted/60"
              >
                <Link href={`/plans/${plan.id}`} className="flex min-w-0 flex-1 items-center gap-3">
                  <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    <FileText className="size-4" aria-hidden />
                  </span>
                  <span className="min-w-0">
                    <span className="block truncate text-sm font-semibold">{plan.title}</span>
                    <PlanMeta plan={plan} />
                    <span className="block text-xs text-muted-foreground/80">
                      Generated {formatPlanTime(plan.created_at)} ·{" "}
                      {plan.word_count.toLocaleString()} words
                    </span>
                  </span>
                </Link>
                <Button
                  variant="ghost"
                  size="icon-sm"
                  onClick={() => handleDelete(plan)}
                  disabled={deletingId === plan.id}
                  aria-label={`Delete ${plan.title}`}
                  className="text-muted-foreground hover:text-destructive"
                >
                  {deletingId === plan.id ? (
                    <Loader2 className="animate-spin" aria-hidden />
                  ) : (
                    <Trash2 aria-hidden />
                  )}
                </Button>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
