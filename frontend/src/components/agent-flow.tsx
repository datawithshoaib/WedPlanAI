"use client";

import { ArrowDown, Bot, Globe2, Layers3, Search } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const FLOW = [
  {
    icon: Layers3,
    title: "Main planner agent",
    description:
      "Reads the structured brief and synthesizes the final strategy, budget, timeline, and risks.",
  },
  {
    icon: Bot,
    title: "Two research workers",
    description:
      "One researches venues and vendors; the other checks logistics, pricing, and seasonal risks.",
  },
  {
    icon: Search,
    title: "Tavily web research",
    description:
      "Retrieves current, location-aware planning data before any recommendation is synthesized.",
  },
];

export function AgentFlow() {
  return (
    <div className="grid gap-4 sm:grid-cols-3">
      {FLOW.map((stage, index) => (
        <div key={stage.title} className="flex flex-col gap-2">
          <Card className="h-full">
            <CardHeader>
              <div className="mb-1 flex size-9 items-center justify-center rounded-full bg-primary/12 text-primary">
                <stage.icon className="size-4" aria-hidden />
              </div>
              <CardTitle className="text-sm leading-5">{stage.title}</CardTitle>
              <CardDescription className="text-xs leading-5">
                {stage.description}
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-0">
              <span className="text-[0.65rem] font-bold uppercase tracking-wide text-primary">
                Stage {index + 1}
              </span>
            </CardContent>
          </Card>
          {index < FLOW.length - 1 && (
            <div className="flex justify-center py-1 sm:hidden">
              <ArrowDown className="size-4 text-muted-foreground" aria-hidden />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export function FlowFootnote() {
  return (
    <p className="mt-4 flex items-start gap-2 text-xs text-muted-foreground">
      <Globe2 className="mt-0.5 size-3.5 shrink-0" aria-hidden />
      Recommendations are generated from live web research and should be reviewed by a human
      before making bookings, contracts, or financial commitments.
    </p>
  );
}