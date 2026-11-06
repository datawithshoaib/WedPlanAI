"use client";

import { CircleCheck, CircleX, Loader2, WifiOff } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import type { HealthResponse } from "@/lib/types";

interface RuntimeStatusProps {
  health: HealthResponse | null;
  loading: boolean;
  offline: boolean;
}

export function RuntimeStatus({ health, loading, offline }: RuntimeStatusProps) {
  if (loading && !health) {
    return (
      <Badge variant="outline" className="gap-1.5 text-muted-foreground">
        <Loader2 className="size-3 animate-spin" aria-hidden />
        Connecting…
      </Badge>
    );
  }

  if (offline || !health) {
    return (
      <Badge variant="destructive" className="gap-1.5" title="The FastAPI backend is not reachable">
        <WifiOff className="size-3" aria-hidden />
        Backend offline
      </Badge>
    );
  }

  const missing = [
    !health.planner_ready && "GROQ_API_KEY",
    !health.research_ready && "TAVILY_API_KEY",
  ].filter(Boolean);

  if (missing.length) {
    return (
      <Badge variant="secondary" className="gap-1.5" title={`Missing: ${missing.join(", ")}`}>
        <CircleX className="size-3" aria-hidden />
        Keys missing
      </Badge>
    );
  }

  return (
    <Badge className="gap-1.5 bg-emerald-700 text-white" title={`Model: ${health.model}`}>
      <CircleCheck className="size-3" aria-hidden />
      Planner ready
    </Badge>
  );
}
