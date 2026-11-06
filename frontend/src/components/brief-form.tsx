"use client";

import * as React from "react";
import { Eraser, HeartHandshake, Loader2, RefreshCw, Sparkles } from "lucide-react";

import { DatePicker } from "@/components/date-picker";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Slider } from "@/components/ui/slider";
import { Textarea } from "@/components/ui/textarea";
import { type BriefErrors, GUEST_LIMITS } from "@/lib/brief";
import { budgetScale, formatPerGuest } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { BriefRequest, OptionsResponse } from "@/lib/types";

interface BriefFormProps {
  brief: BriefRequest;
  onChange: (brief: BriefRequest) => void;
  options: OptionsResponse | null;
  errors: BriefErrors;
  showErrors: boolean;
  disabledReason: string | null;
  busy: boolean;
  onSubmit: () => void;
  onSample: () => void;
  onReset: () => void;
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <div className="mb-3 flex items-center gap-2">
      <span className="size-1.5 rounded-full bg-primary" aria-hidden />
      <h3 className="text-xs font-bold tracking-wider text-foreground uppercase">{children}</h3>
      <Separator className="flex-1" />
    </div>
  );
}

function FieldError({ id, message }: { id: string; message?: string }) {
  if (!message) return null;
  return (
    <p id={id} className="text-xs text-destructive">
      {message}
    </p>
  );
}

function ToggleBadges({
  options,
  selected,
  onChange,
  label,
}: {
  options: string[];
  selected: string[];
  onChange: (next: string[]) => void;
  label: string;
}) {
  const toggle = (option: string) =>
    onChange(
      selected.includes(option) ? selected.filter((item) => item !== option) : [...selected, option],
    );

  return (
    <div className="flex flex-wrap gap-1.5" role="group" aria-label={label}>
      {options.map((option) => {
        const active = selected.includes(option);
        return (
          <button
            key={option}
            type="button"
            onClick={() => toggle(option)}
            aria-pressed={active}
            className={cn(
              "rounded-full border px-3 py-1 text-xs font-semibold transition-colors focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none",
              active
                ? "border-primary/40 bg-primary/12 text-primary"
                : "border-border bg-background text-muted-foreground hover:border-primary/40 hover:text-foreground",
            )}
          >
            {option}
          </button>
        );
      })}
    </div>
  );
}

function OptionSelect({
  id,
  value,
  options,
  onChange,
}: {
  id: string;
  value: string;
  options: string[];
  onChange: (value: string) => void;
}) {
  // Keep a custom value (e.g. from an old saved plan) selectable.
  const items = options.includes(value) || !value ? options : [value, ...options];
  return (
    <Select value={value} onValueChange={(next) => next && onChange(next)}>
      <SelectTrigger id={id} className="w-full">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {items.map((option) => (
          <SelectItem key={option} value={option}>
            {option}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

function MoneyInput({
  id,
  value,
  onChange,
  invalid,
  describedBy,
}: {
  id: string;
  value: number;
  onChange: (value: number) => void;
  invalid?: boolean;
  describedBy?: string;
}) {
  return (
    <Input
      id={id}
      inputMode="numeric"
      value={value ? value.toLocaleString("en-US") : ""}
      onChange={(event) => onChange(Number(event.target.value.replace(/[^\d]/g, "")) || 0)}
      aria-invalid={invalid || undefined}
      aria-describedby={describedBy}
      className="tabular-nums"
    />
  );
}

export function BriefForm({
  brief,
  onChange,
  options,
  errors: allErrors,
  showErrors,
  disabledReason,
  busy,
  onSubmit,
  onSample,
  onReset,
}: BriefFormProps) {
  const errors = showErrors ? allErrors : {};
  const set = <K extends keyof BriefRequest>(key: K, value: BriefRequest[K]) =>
    onChange({ ...brief, [key]: value });

  // Allow the guest field to be empty while typing without sending 0 to the API.
  const [guestText, setGuestText] = React.useState(String(brief.guest_count));
  React.useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- sync when brief is replaced
    setGuestText((current) => (Number(current) === brief.guest_count ? current : String(brief.guest_count)));
  }, [brief.guest_count]);

  const scale = budgetScale(brief.currency);
  const sliderMax = Math.max(scale.max, brief.budget_high);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between text-base">
          <span className="flex items-center gap-2">
            <HeartHandshake className="size-4 text-primary" aria-hidden />
            Wedding brief
          </span>
          <span className="flex gap-1">
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={onReset}
              disabled={busy}
              className="text-muted-foreground"
            >
              <Eraser aria-hidden />
              Clear
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={onSample}
              disabled={busy}
              className="text-muted-foreground"
            >
              <RefreshCw aria-hidden />
              Sample brief
            </Button>
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form
          className="space-y-6"
          noValidate
          onSubmit={(event) => {
            event.preventDefault();
            onSubmit();
          }}
        >
          <fieldset disabled={busy} className="space-y-6">
            <section>
              <SectionTitle>Basics</SectionTitle>
              <div className="grid gap-3">
                <div className="grid gap-3 sm:grid-cols-2">
                  <div className="space-y-1.5">
                    <Label htmlFor="couple_name">Couple or project name</Label>
                    <Input
                      id="couple_name"
                      value={brief.couple_name}
                      onChange={(event) => set("couple_name", event.target.value)}
                      placeholder="Amira and Noah"
                      maxLength={120}
                    />
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="wedding_location">
                      Location <span className="text-destructive">*</span>
                    </Label>
                    <Input
                      id="wedding_location"
                      value={brief.wedding_location}
                      onChange={(event) => set("wedding_location", event.target.value)}
                      placeholder="City, region or country"
                      maxLength={200}
                      aria-invalid={Boolean(errors.wedding_location) || undefined}
                      aria-describedby="wedding_location-error"
                    />
                    <FieldError id="wedding_location-error" message={errors.wedding_location} />
                  </div>
                </div>

                <div className="grid gap-3 sm:grid-cols-3">
                  <div className="space-y-1.5">
                    <Label htmlFor="wedding_date">Target date</Label>
                    <DatePicker
                      id="wedding_date"
                      value={brief.wedding_date}
                      onChange={(value) => set("wedding_date", value)}
                      invalid={Boolean(errors.wedding_date)}
                    />
                    <FieldError id="wedding_date-error" message={errors.wedding_date} />
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="guest_count">Guests</Label>
                    <Input
                      id="guest_count"
                      type="number"
                      inputMode="numeric"
                      min={GUEST_LIMITS.min}
                      max={GUEST_LIMITS.max}
                      value={guestText}
                      onChange={(event) => {
                        setGuestText(event.target.value);
                        set("guest_count", Number(event.target.value) || 0);
                      }}
                      aria-invalid={Boolean(errors.guest_count) || undefined}
                      aria-describedby="guest_count-error"
                    />
                    <FieldError id="guest_count-error" message={errors.guest_count} />
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="ceremony_type">Event scope</Label>
                    <OptionSelect
                      id="ceremony_type"
                      value={brief.ceremony_type}
                      options={options?.ceremony_types ?? []}
                      onChange={(value) => set("ceremony_type", value)}
                    />
                  </div>
                </div>
              </div>
            </section>

            <section>
              <SectionTitle>Budget and tone</SectionTitle>
              <div className="grid gap-4 sm:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]">
                <div className="space-y-3">
                  <div className="space-y-1.5">
                    <Label htmlFor="currency">Currency</Label>
                    <OptionSelect
                      id="currency"
                      value={brief.currency}
                      options={options?.currencies ?? ["USD"]}
                      onChange={(value) => {
                        const next = budgetScale(value);
                        onChange({
                          ...brief,
                          currency: value,
                          budget_low: Math.min(brief.budget_low, next.max),
                          budget_high: Math.min(brief.budget_high, next.max),
                        });
                      }}
                    />
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="tone">Planner tone</Label>
                    <OptionSelect
                      id="tone"
                      value={brief.tone}
                      options={options?.tone_options ?? []}
                      onChange={(value) => set("tone", value)}
                    />
                  </div>
                </div>

                <div className="space-y-3 rounded-lg border bg-muted/40 p-3">
                  <div className="grid grid-cols-2 gap-2">
                    <div className="space-y-1">
                      <Label htmlFor="budget_low" className="text-xs text-muted-foreground">
                        Minimum
                      </Label>
                      <MoneyInput
                        id="budget_low"
                        value={brief.budget_low}
                        onChange={(value) => set("budget_low", value)}
                      />
                    </div>
                    <div className="space-y-1">
                      <Label htmlFor="budget_high" className="text-xs text-muted-foreground">
                        Maximum
                      </Label>
                      <MoneyInput
                        id="budget_high"
                        value={brief.budget_high}
                        onChange={(value) => set("budget_high", value)}
                        invalid={Boolean(errors.budget_high)}
                        describedBy="budget_high-error"
                      />
                    </div>
                  </div>
                  <Slider
                    value={[brief.budget_low, brief.budget_high]}
                    min={0}
                    max={sliderMax}
                    step={scale.step}
                    minStepsBetweenValues={0}
                    aria-label="Budget range"
                    onValueChange={(value) => {
                      if (!Array.isArray(value)) return;
                      onChange({ ...brief, budget_low: value[0], budget_high: value[1] });
                    }}
                  />
                  <FieldError id="budget_high-error" message={errors.budget_high} />
                  <p className="text-xs text-muted-foreground">
                    {formatPerGuest(
                      brief.budget_low,
                      brief.budget_high,
                      brief.currency,
                      brief.guest_count,
                    )}
                  </p>
                </div>
              </div>
            </section>

            <section>
              <SectionTitle>Style and priorities</SectionTitle>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>Style direction</Label>
                  <ToggleBadges
                    label="Style direction"
                    options={options?.style_options ?? []}
                    selected={brief.wedding_styles}
                    onChange={(next) => set("wedding_styles", next)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Planning priorities</Label>
                  <ToggleBadges
                    label="Planning priorities"
                    options={options?.priority_options ?? []}
                    selected={brief.planning_priorities}
                    onChange={(next) => set("planning_priorities", next)}
                  />
                </div>
              </div>
            </section>

            <section>
              <SectionTitle>Notes for the planner</SectionTitle>
              <div className="grid gap-3">
                <div className="space-y-1.5">
                  <Label htmlFor="must_haves">Must-haves</Label>
                  <Textarea
                    id="must_haves"
                    rows={3}
                    maxLength={2000}
                    value={brief.must_haves}
                    onChange={(event) => set("must_haves", event.target.value)}
                    placeholder="e.g. outdoor ceremony, vegetarian menu, live band"
                  />
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  <div className="space-y-1.5">
                    <Label htmlFor="traditions">Traditions and family details</Label>
                    <Textarea
                      id="traditions"
                      rows={4}
                      maxLength={2000}
                      value={brief.traditions}
                      onChange={(event) => set("traditions", event.target.value)}
                      placeholder="Ceremonies, rituals, cultural or religious requirements"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="constraints">Constraints</Label>
                    <Textarea
                      id="constraints"
                      rows={4}
                      maxLength={2000}
                      value={brief.constraints}
                      onChange={(event) => set("constraints", event.target.value)}
                      placeholder="Accessibility, travel limits, things to avoid"
                    />
                  </div>
                </div>
              </div>
            </section>
          </fieldset>

          <div className="space-y-2 pt-1">
            <Button
              type="submit"
              disabled={Boolean(disabledReason) || busy}
              className="h-11 w-full text-base font-semibold"
              size="lg"
            >
              {busy ? (
                <>
                  <Loader2 className="animate-spin" aria-hidden />
                  Researching and planning…
                </>
              ) : (
                <>
                  <Sparkles aria-hidden />
                  Generate wedding plan
                </>
              )}
            </Button>
            {disabledReason && !busy && (
              <p className="text-center text-xs text-destructive">{disabledReason}</p>
            )}
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
