"use client";

import * as React from "react";
import { Check, ClipboardCopy, Download, FileText, Gauge, History, Printer } from "lucide-react";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDuration, formatPlanTime, slugify } from "@/lib/format";
import type { PlanResponse } from "@/lib/types";

// Models sometimes put <br> inside table cells. Raw HTML is (safely) not rendered, so we
// swap it for a private-use marker and turn that marker back into real line breaks.
const BR_MARKER = "";
const BR_PATTERN = /<br\s*\/?>/gi;

function withLineBreaks(children: React.ReactNode): React.ReactNode {
  return React.Children.map(children, (child) => {
    if (typeof child !== "string" || !child.includes(BR_MARKER)) return child;
    return child.split(BR_MARKER).flatMap((part, index) =>
      index === 0 ? [part] : [<br key={index} />, part],
    );
  });
}

const MARKDOWN_COMPONENTS: Components = {
  td: ({ children }) => <td>{withLineBreaks(children)}</td>,
  th: ({ children }) => <th>{withLineBreaks(children)}</th>,
  p: ({ children }) => <p>{withLineBreaks(children)}</p>,
  li: ({ children }) => <li>{withLineBreaks(children)}</li>,
  a: ({ href, children }) => (
    <a href={href} target="_blank" rel="noopener noreferrer">
      {children}
    </a>
  ),
  table: ({ children }) => (
    <div className="table-wrap">
      <table>{children}</table>
    </div>
  ),
};

function downloadMarkdown(plan: PlanResponse) {
  const blob = new Blob([plan.content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = slugify(plan.title);
  link.click();
  URL.revokeObjectURL(url);
}

export function PlanView({ plan }: { plan: PlanResponse }) {
  const [copied, setCopied] = React.useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(plan.content);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch {
      toast.error("Clipboard access was blocked by the browser.");
    }
  };

  return (
    <Card>
      <CardHeader className="flex flex-row flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <CardTitle className="flex items-center gap-2 font-heading text-2xl">
            <FileText className="size-5 shrink-0 text-primary" aria-hidden />
            {plan.title}
          </CardTitle>
          <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <span>Created {formatPlanTime(plan.created_at)}</span>
            <Badge variant="secondary" className="gap-1">
              <Gauge aria-hidden />
              {formatDuration(plan.duration_seconds)} to generate
            </Badge>
            <Badge variant="secondary" className="gap-1">
              <History aria-hidden />
              {plan.word_count.toLocaleString()} words
            </Badge>
          </div>
        </div>
        <div className="flex flex-wrap gap-2" data-print="hide">
          <Button variant="outline" size="sm" onClick={copy}>
            {copied ? (
              <Check className="text-emerald-600" aria-hidden />
            ) : (
              <ClipboardCopy aria-hidden />
            )}
            {copied ? "Copied" : "Copy"}
          </Button>
          <Button variant="outline" size="sm" onClick={() => downloadMarkdown(plan)}>
            <Download aria-hidden />
            Markdown
          </Button>
          <Button variant="outline" size="sm" onClick={() => window.print()}>
            <Printer aria-hidden />
            Print / PDF
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <article className="plan-prose max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]} components={MARKDOWN_COMPONENTS}>
            {plan.content.replace(BR_PATTERN, BR_MARKER)}
          </ReactMarkdown>
        </article>
      </CardContent>
    </Card>
  );
}
