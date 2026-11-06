"use client";

import {
  AlertTriangle,
  CalendarClock,
  FileText,
  HelpCircle,
  MapPin,
  Sparkles,
  Store,
  Wallet,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCurrencyNumber, formatMoney } from "@/lib/format";
import type { PlanStructure } from "@/lib/types";

interface StructuredSummaryProps {
  structure: PlanStructure;
}

export function StructuredSummary({ structure }: StructuredSummaryProps) {
  const hasBudget = structure.budget_allocation.length > 0;
  const hasTimeline = structure.timeline.length > 0;
  const hasRisks = structure.risks.length > 0;
  const hasVendors =
    structure.vendor_recommendations.length > 0 || structure.venue_recommendations.length > 0;
  const hasQuestions = structure.open_questions.length > 0;
  const budgetCurrency = structure.budget_allocation[0]?.currency || "USD";
  const budgetTotal = structure.budget_allocation.reduce((sum, item) => sum + (item.amount || 0), 0);

  if (
    !structure.executive_summary &&
    !hasBudget &&
    !hasTimeline &&
    !hasRisks &&
    !hasVendors &&
    !hasQuestions
  ) {
    return null;
  }

  return (
    <section className="space-y-4">
      <div className="flex items-center gap-2">
        <Sparkles className="size-4 text-primary" aria-hidden />
        <h2 className="font-heading text-2xl font-bold">At a glance</h2>
      </div>

      {structure.executive_summary && (
        <Card>
          <CardContent className="pt-5">
            <p className="text-sm leading-relaxed text-muted-foreground">
              {structure.executive_summary}
            </p>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        {hasBudget && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <Wallet className="size-4 text-primary" aria-hidden />
                Budget allocation
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-baseline justify-between rounded-lg bg-muted/50 px-3 py-2 text-sm">
                <span className="font-medium text-muted-foreground">Allocated total</span>
                <span className="font-bold">{formatCurrencyNumber(budgetTotal, budgetCurrency)}</span>
              </div>
              {structure.budget_allocation.map((item, index) => {
                const currency = item.currency || "USD";
                const share = Math.max(0, Math.min(100, item.share_percent || 0));
                return (
                  <div key={`${item.category}-${index}`}>
                    <div className="flex items-baseline justify-between gap-2 text-sm">
                      <span className="font-medium">{item.category || "Other"}</span>
                      <span className="text-muted-foreground">
                        {formatMoney(item.amount, currency)}
                        {share > 0 && <span className="ml-1.5 text-xs">· {share.toFixed(0)}%</span>}
                      </span>
                    </div>
                    {share > 0 && (
                      <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-muted">
                        <div
                          className="h-full rounded-full bg-primary/70"
                          style={{ width: `${share}%` }}
                        />
                      </div>
                    )}
                  </div>
                );
              })}
            </CardContent>
          </Card>
        )}

        {hasTimeline && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <CalendarClock className="size-4 text-primary" aria-hidden />
                Timeline
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {structure.timeline.map((milestone, index) => (
                <div key={`${milestone.phase}-${index}`}>
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-sm font-semibold">{milestone.phase}</span>
                    {milestone.horizon && (
                      <Badge variant="secondary" className="text-xs">
                        {milestone.horizon}
                      </Badge>
                    )}
                  </div>
                  {milestone.actions.length > 0 && (
                    <ul className="mt-1.5 space-y-1 text-sm text-muted-foreground">
                      {milestone.actions.map((action, actionIndex) => (
                        <li key={actionIndex} className="flex gap-2">
                          <span className="mt-2 size-1 shrink-0 rounded-full bg-primary/60" />
                          <span>{action}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
        )}
      </div>

      {hasVendors && (
        <div className="grid gap-4 lg:grid-cols-2">
          {structure.venue_recommendations.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-sm">
                  <MapPin className="size-4 text-primary" aria-hidden />
                  Venue recommendations
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {structure.venue_recommendations.map((venue, index) => (
                  <div key={`${venue.name}-${index}`} className="rounded-lg border bg-card p-3">
                    <p className="text-sm font-semibold">{venue.name}</p>
                    {venue.location && (
                      <p className="text-xs text-muted-foreground">{venue.location}</p>
                    )}
                    {venue.why_it_fits && (
                      <p className="mt-1 text-sm text-muted-foreground">{venue.why_it_fits}</p>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {structure.vendor_recommendations.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-sm">
                  <Store className="size-4 text-primary" aria-hidden />
                  Vendor shortlist
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {structure.vendor_recommendations.map((vendor, index) => (
                  <div key={`${vendor.name}-${index}`} className="rounded-lg border bg-card p-3">
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-sm font-semibold">{vendor.name}</p>
                      {vendor.category && (
                        <Badge variant="secondary" className="shrink-0 text-xs">
                          {vendor.category}
                        </Badge>
                      )}
                    </div>
                    {vendor.why_recommended && (
                      <p className="mt-1 text-sm text-muted-foreground">{vendor.why_recommended}</p>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {hasRisks && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm">
              <AlertTriangle className="size-4 text-amber-600" aria-hidden />
              Risks and tradeoffs
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {structure.risks.map((item, index) => (
              <div key={`${item.risk}-${index}`} className="rounded-lg border bg-card p-3">
                <p className="text-sm font-semibold">{item.risk}</p>
                {item.mitigation && (
                  <p className="mt-1 text-sm text-muted-foreground">
                    <span className="font-medium text-foreground">Mitigation: </span>
                    {item.mitigation}
                  </p>
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {hasQuestions && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm">
              <HelpCircle className="size-4 text-primary" aria-hidden />
              Open questions for the couple
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="grid gap-2 sm:grid-cols-2">
              {structure.open_questions.map((question, index) => (
                <li key={index} className="flex gap-2 text-sm text-muted-foreground">
                  <FileText className="mt-0.5 size-4 shrink-0 text-primary/60" aria-hidden />
                  <span>{question}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </section>
  );
}