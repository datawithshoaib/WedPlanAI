"use client";

import * as React from "react";
import { ArrowLeft, FileWarning, Loader2, Trash2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { ConfirmButton } from "@/components/confirm-button";
import { PlanResult } from "@/components/plan-result";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { buttonVariants } from "@/components/ui/button";
import { ApiError, BACKEND_START_HINT, deletePlan, getPlan } from "@/lib/api";
import type { PlanResponse } from "@/lib/types";

export function PlanDetail({ planId }: { planId: string }) {
  const router = useRouter();
  const [plan, setPlan] = React.useState<PlanResponse | null>(null);
  const [error, setError] = React.useState<ApiError | Error | null>(null);
  const [deleting, setDeleting] = React.useState(false);

  React.useEffect(() => {
    let cancelled = false;
    getPlan(planId)
      .then((result) => {
        if (cancelled) return;
        setPlan(result);
        document.title = `${result.title} · WedPlannerAI`;
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err : new Error("Failed to load plan"));
      });
    return () => {
      cancelled = true;
    };
  }, [planId]);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await deletePlan(planId);
      toast.success("Plan deleted");
      router.push("/plans");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to delete plan");
      setDeleting(false);
    }
  };

  const notFound = error instanceof ApiError && error.status === 404;

  return (
    <>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3" data-print="hide">
        <Link href="/plans" className={buttonVariants({ variant: "outline", size: "sm" })}>
          <ArrowLeft aria-hidden />
          Back to history
        </Link>
        {plan && (
          <ConfirmButton
            variant="ghost"
            size="sm"
            onConfirm={handleDelete}
            disabled={deleting}
            className="text-destructive hover:text-destructive"
            confirmLabel="Delete this plan?"
          >
            {deleting ? <Loader2 className="animate-spin" aria-hidden /> : <Trash2 aria-hidden />}
            Delete plan
          </ConfirmButton>
        )}
      </div>

      {error ? (
        <Alert variant="destructive">
          <FileWarning aria-hidden />
          <AlertTitle>{notFound ? "Plan not found" : "Could not load plan"}</AlertTitle>
          <AlertDescription>
            {notFound ? (
              <>
                This plan may have been deleted.{" "}
                <Link href="/plans" className="font-medium underline underline-offset-3">
                  Back to history
                </Link>
              </>
            ) : (
              <>
                {error.message} Start the backend with{" "}
                <code className="font-mono">{BACKEND_START_HINT}</code>
              </>
            )}
          </AlertDescription>
        </Alert>
      ) : plan ? (
        <PlanResult plan={plan} />
      ) : (
        <div className="space-y-3" aria-busy="true">
          <div className="h-28 animate-pulse rounded-xl bg-muted" />
          <div className="h-96 animate-pulse rounded-xl bg-muted" />
        </div>
      )}
    </>
  );
}
