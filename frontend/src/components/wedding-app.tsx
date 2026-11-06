"use client";

import * as React from "react";
import { ArrowUpRight, RotateCcw, TriangleAlert, WifiOff } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";

import { AgentFlow, FlowFootnote } from "@/components/agent-flow";
import { BriefForm } from "@/components/brief-form";
import {
  GenerationProgress,
  reduceProgress,
  type StageStatuses,
} from "@/components/generation-progress";
import { useHealth } from "@/components/health-provider";
import { PlanResult } from "@/components/plan-result";
import { PlanningLens } from "@/components/planning-lens";
import { RecentPlans } from "@/components/recent-plans";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button, buttonVariants } from "@/components/ui/button";
import { BACKEND_START_HINT, createPlanStreaming, getOptions } from "@/lib/api";
import { emptyBrief, normalizeBrief, validateBrief } from "@/lib/brief";
import type { BriefRequest, OptionsResponse, PlanResponse } from "@/lib/types";

const DRAFT_KEY = "wedplannerai:draft-brief";

function readDraft(): BriefRequest | null {
  try {
    const raw = window.localStorage.getItem(DRAFT_KEY);
    return raw ? normalizeBrief(JSON.parse(raw) as Partial<BriefRequest>) : null;
  } catch {
    return null;
  }
}

function writeDraft(brief: BriefRequest) {
  try {
    window.localStorage.setItem(DRAFT_KEY, JSON.stringify(brief));
  } catch {
    // storage unavailable (private mode, quota) — drafts are a convenience only
  }
}

export function WeddingApp() {
  const { health, offline, refresh: refreshHealth } = useHealth();
  const [options, setOptions] = React.useState<OptionsResponse | null>(null);
  const [brief, setBrief] = React.useState<BriefRequest>(emptyBrief);
  const [hydrated, setHydrated] = React.useState(false);
  const [showErrors, setShowErrors] = React.useState(false);
  const [busy, setBusy] = React.useState(false);
  const [progress, setProgress] = React.useState<StageStatuses>({});
  const [plan, setPlan] = React.useState<PlanResponse | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const outputRef = React.useRef<HTMLElement>(null);
  const abortRef = React.useRef<AbortController | null>(null);

  // Load options + sample brief; prefer the visitor's saved draft if there is one.
  React.useEffect(() => {
    let cancelled = false;
    const draft = readDraft();
    getOptions()
      .then((result) => {
        if (cancelled) return;
        setOptions(result);
        setBrief(draft ?? normalizeBrief(result.default_brief));
      })
      .catch(() => {
        if (!cancelled && draft) setBrief(draft);
      })
      .finally(() => {
        if (!cancelled) setHydrated(true);
      });
    return () => {
      cancelled = true;
      abortRef.current?.abort();
    };
  }, []);

  React.useEffect(() => {
    if (hydrated) writeDraft(brief);
  }, [brief, hydrated]);

  const errors = React.useMemo(() => validateBrief(brief), [brief]);

  const disabledReason = offline
    ? "The backend is offline — start it, then press the refresh icon in the header."
    : health && !health.planner_ready
      ? "The server is missing GROQ_API_KEY in backend/.env."
      : health && !health.research_ready
        ? "The server is missing TAVILY_API_KEY in backend/.env."
        : null;

  const handleSubmit = async () => {
    if (Object.keys(errors).length) {
      setShowErrors(true);
      toast.error("Please fix the highlighted fields.");
      document.getElementById(Object.keys(errors)[0])?.focus();
      return;
    }

    const controller = new AbortController();
    abortRef.current = controller;
    setBusy(true);
    setError(null);
    setPlan(null);
    setProgress({});
    window.requestAnimationFrame(() =>
      outputRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }),
    );

    try {
      const result = await createPlanStreaming(
        brief,
        (event) => setProgress((current) => reduceProgress(current, event)),
        controller.signal,
      );
      setPlan(result);
      setShowErrors(false);
      toast.success("Your wedding plan is ready");
    } catch (err) {
      if (controller.signal.aborted) return;
      const message = err instanceof Error ? err.message : "Plan generation failed";
      setError(message);
      toast.error(message);
      void refreshHealth();
    } finally {
      if (abortRef.current === controller) abortRef.current = null;
      setBusy(false);
    }
  };

  const loadSample = () => {
    if (options) setBrief(normalizeBrief(options.default_brief));
    setShowErrors(false);
  };

  const resetBrief = () => {
    setBrief(emptyBrief());
    setShowErrors(false);
  };

  return (
    <>
      <section className="mx-auto max-w-6xl px-4 pt-10 pb-6 sm:px-6">
        <div className="max-w-2xl">
          <p className="text-xs font-bold tracking-[0.2em] text-primary uppercase">
            Multi-agent wedding planner
          </p>
          <h1 className="mt-2 font-heading text-4xl font-bold tracking-tight text-balance sm:text-5xl">
            Your wedding, planned by a team of agents.
          </h1>
          <p className="mt-3 max-w-xl text-muted-foreground">
            Describe your brief and two research agents pull current venue, vendor, and market
            data before the main planner writes a client-ready strategy — budget, timeline,
            risks, and open questions included.
          </p>
        </div>
      </section>

      {offline && (
        <section className="mx-auto max-w-6xl px-4 sm:px-6">
          <Alert variant="destructive" className="mb-6">
            <WifiOff aria-hidden />
            <AlertTitle>Backend unreachable</AlertTitle>
            <AlertDescription>
              Start the API with <code className="font-mono">{BACKEND_START_HINT}</code>
            </AlertDescription>
          </Alert>
        </section>
      )}

      <section className="mx-auto grid max-w-6xl gap-6 px-4 pb-12 sm:px-6 lg:grid-cols-[minmax(0,5fr)_minmax(0,3fr)]">
        <div className="min-w-0">
          <BriefForm
            brief={brief}
            onChange={setBrief}
            options={options}
            errors={errors}
            showErrors={showErrors}
            disabledReason={disabledReason}
            busy={busy}
            onSubmit={handleSubmit}
            onSample={loadSample}
            onReset={resetBrief}
          />
        </div>
        <aside className="min-w-0 space-y-6 lg:sticky lg:top-20 lg:self-start">
          <PlanningLens brief={brief} />
          <RecentPlans refreshKey={plan?.id} />
        </aside>
      </section>

      <section
        ref={outputRef}
        className="mx-auto max-w-6xl scroll-mt-20 px-4 pb-12 sm:px-6"
        aria-label="Generated plan"
      >
        {busy ? (
          <GenerationProgress statuses={progress} />
        ) : error ? (
          <Alert variant="destructive">
            <TriangleAlert aria-hidden />
            <AlertTitle>The plan could not be generated</AlertTitle>
            <AlertDescription className="space-y-3">
              <p>{error}</p>
              <Button variant="outline" size="sm" onClick={handleSubmit}>
                <RotateCcw aria-hidden />
                Try again
              </Button>
            </AlertDescription>
          </Alert>
        ) : plan ? (
          <div className="space-y-4">
            <div className="flex justify-end" data-print="hide">
              <Link
                href={`/plans/${plan.id}`}
                className={buttonVariants({ variant: "outline", size: "sm" })}
              >
                Open saved copy
                <ArrowUpRight aria-hidden />
              </Link>
            </div>
            <PlanResult plan={plan} />
          </div>
        ) : null}
      </section>

      <section className="border-t bg-card/50" data-print="hide">
        <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
          <h2 className="font-heading text-2xl font-bold text-balance">How the planning flow works</h2>
          <p className="mt-1 mb-6 max-w-xl text-sm text-muted-foreground">
            Your structured brief feeds one orchestrator that delegates research to two focused
            search agents before synthesising the final plan.
          </p>
          <AgentFlow />
          <FlowFootnote />
        </div>
      </section>
    </>
  );
}
