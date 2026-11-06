"use client";

import { CalendarClock, Heart, MapPin, Users } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { daysUntil, formatBudgetRange, formatLongDate, formatPerGuest } from "@/lib/format";
import type { BriefRequest } from "@/lib/types";

interface PlanningLensProps {
  brief: BriefRequest;
}

function LensItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border bg-muted/40 px-3 py-2.5">
      <span className="block text-[0.68rem] font-bold uppercase tracking-wide text-muted-foreground">
        {label}
      </span>
      <span className="mt-1 block text-sm font-semibold leading-tight">{value}</span>
    </div>
  );
}

export function PlanningLens({ brief }: PlanningLensProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Heart className="size-4 text-primary" aria-hidden />
          Planning lens
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-2">
          <LensItem label="Couple" value={brief.couple_name || "Untitled"} />
          <LensItem label="Pace" value={daysUntil(brief.wedding_date)} />
        </div>

        <div className="grid gap-3">
          <div className="flex items-start gap-2 text-sm">
            <MapPin className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden />
            <span className="font-medium">
              {brief.wedding_location || "Location not set"}
            </span>
          </div>
          <div className="flex items-start gap-2 text-sm">
            <CalendarClock className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden />
            <span className="font-medium">
              {formatLongDate(brief.wedding_date)} · {daysUntil(brief.wedding_date)}
            </span>
          </div>
          <div className="flex items-start gap-2 text-sm">
            <Users className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden />
            <span className="font-medium">
              {brief.guest_count.toLocaleString()} guests
            </span>
          </div>
        </div>

        <div className="rounded-lg border bg-gradient-to-br from-primary/10 to-chart-5/10 p-3">
          <span className="block text-[0.68rem] font-bold uppercase tracking-wide text-muted-foreground">
            Budget
          </span>
          <span className="mt-1 block text-base font-bold">
            {formatBudgetRange(brief.budget_low, brief.budget_high, brief.currency)}
          </span>
          <span className="mt-0.5 block text-xs text-muted-foreground">
            {formatPerGuest(brief.budget_low, brief.budget_high, brief.currency, brief.guest_count)}
          </span>
        </div>

        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Style direction
          </p>
          <div className="flex flex-wrap gap-1.5">
            {brief.wedding_styles.length ? (
              brief.wedding_styles.map((style) => (
                <Badge key={style} variant="secondary">
                  {style}
                </Badge>
              ))
            ) : (
              <Badge variant="outline">Flexible style</Badge>
            )}
          </div>
        </div>

        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Priorities
          </p>
          <div className="flex flex-wrap gap-1.5">
            {brief.planning_priorities.length ? (
              brief.planning_priorities.map((priority) => (
                <Badge key={priority} variant="outline">
                  {priority}
                </Badge>
              ))
            ) : (
              <Badge variant="outline">Balanced plan</Badge>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}